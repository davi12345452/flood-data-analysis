# PROJETO: Modelo de previsão de cota de cheia no Vale do Taquari (RS)

## Seu papel

Você é um engenheiro de dados e ML com experiência em hidrologia operacional. Vamos construir, do zero, um pipeline reprodutível que prevê a **cota (nível) do rio Taquari** nas cidades do baixo vale a partir de chuva observada e vazão defluente das usinas do rio das Antas.

Este é um projeto de pesquisa pessoal, não um sistema de alerta oficial. Nada aqui deve ser usado para decisão de evacuação.

---

## Regras de trabalho (não negociáveis)

1. **Trabalhe em fases.** Ao final de cada fase, pare, mostre o que foi produzido e espere confirmação antes de seguir. Não emende três fases em um commit.
2. **Nunca invente dados.** Se uma API falhar, um endpoint mudar ou uma estação não existir, reporte o erro real. Não gere dados sintéticos como fallback silencioso.
3. **Cache agressivo.** Todo download vira Parquet em `data/raw/`. Nenhum script de análise pode depender de rede. Reexecutar deve ser instantâneo.
4. **Idempotência.** Todo script pode rodar duas vezes sem duplicar nem corromper nada.
5. **Log de proveniência.** Cada arquivo em `data/raw/` tem um `.meta.json` ao lado com URL de origem, timestamp do download, parâmetros da query e contagem de registros.
6. **Commits pequenos** com mensagem descritiva ao fim de cada fase.
7. **Sem notebooks como fonte da verdade.** Lógica vai em módulos Python testáveis. Notebooks só para exploração descartável, em `notebooks/`.
8. Se você identificar que uma premissa deste prompt está errada (endpoint morto, estação inexistente, código trocado), **me avise em vez de contornar**.

---

## Contexto de domínio (assuma como verdadeiro)

**Bacia Taquari-Antas, Rio Grande do Sul.**

- Área de drenagem aproximada de 26.400 km². Curso principal de cerca de 530 km. O trecho com problema de inundação tem cerca de 185 km, da confluência Antas-Carreiro até a foz no rio Jacuí.
- Escoamento superficial dominante. O fluxo subterrâneo contribui com apenas cerca de 20% da descarga total, por causa de encostas íngremes, padrão de drenagem radial e solos argilosos rasos de baixa permeabilidade. Consequência prática: **a bacia responde rápido e a chuva recente domina o sinal**.
- Precipitação média anual entre 1.600 e 1.800 mm, bem distribuída ao longo do ano. Não há estação seca marcada, então sazonalidade simples não é boa feature.
- Antecedência efetiva do sistema de alerta atual: cerca de **12 horas para Muçum e Encantado**, e cerca de **8 horas para Estrela e Lajeado**. Esse é o teto realista para um modelo alimentado só com chuva observada.

**Complexo hidrelétrico do rio das Antas (CERAN): UHE Monte Claro, UHE Castro Alves, UHE 14 de Julho.**

- São usinas a fio d'água, **sem reservatório de regularização**. Não amortecem cheia e não a agravam. As vazões afluentes são integralmente defluídas.
- Implicação de modelagem: trate a defluência como **observação de vazão de montante bem instrumentada**, nunca como variável de controle operacional. Não formule cenários de "abertura de comportas".
- Como preditor ela é valiosa, porque entrega a onda de cheia já formada com horas de antecedência sobre Muçum.
- Em 2 de maio de 2024 a vazão pela barragem 14 de Julho foi estimada em mais de 15.000 m³/s, e a estrutura sofreu rompimento parcial da parte superior. Trate dados de 2024 dessas estações com desconfiança e verifique lacunas.

**Eventos de referência:** setembro de 2023, novembro de 2023 e abril-maio de 2024. O de maio de 2024 é o maior registrado. Esses são os eventos que importam.

---

## Fontes de dados

### A. Alvo: cota e vazão fluviométrica

**ANA / SNIRH HidroWeb.**

- Portal de séries históricas: [https://www.snirh.gov.br/hidroweb/serieshistoricas](https://www.snirh.gov.br/hidroweb/serieshistoricas)
- **API oficial (HidroWebService):** [https://www.ana.gov.br/hidrowebservice/swagger-ui.html](https://www.ana.gov.br/hidrowebservice/swagger-ui.html)
  - Autenticação: `GET /EstacoesTelemetricas/OAUth/v1`, devolve `tokenautenticacao` com validade de **60 minutos**. Implemente refresh automático.
  - Série telemétrica: `GET /EstacoesTelemetricas/HidroinfoanaSerieTelemetricaAdotada/v1`
  - Credencial precisa ser solicitada por e-mail à ANA. Manual: [https://www.gov.br/ana/pt-br/assuntos/monitoramento-e-eventos-criticos/monitoramento-hidrologico/orientacoes-manuais/manuais/manual-hidrowebservice_publica.pdf](https://www.gov.br/ana/pt-br/assuntos/monitoramento-e-eventos-criticos/monitoramento-hidrologico/orientacoes-manuais/manuais/manual-hidrowebservice_publica.pdf)
  - **Se eu ainda não tiver credencial, me avise na Fase 0** e siga pela API legada abaixo.
- **API legada (sem token, para prototipagem):**
  - [`https://www.snirh.gov.br/hidroweb/rest/api/estacaotelemetrica?id={codigo}`](https://www.snirh.gov.br/hidroweb/rest/api/estacaotelemetrica?id={codigo}) devolve o id interno
  - [`https://www.snirh.gov.br/hidroweb/rest/api/documento/gerarTelemetricas?codigosEstacoes={id}&tipoArquivo={n}&periodoInicial={dd/MM/yyyy}&periodoFinal={dd/MM/yyyy}`](https://www.snirh.gov.br/hidroweb/rest/api/documento/gerarTelemetricas?codigosEstacoes={id}&tipoArquivo={n}&periodoInicial={dd/MM/yyyy}&periodoFinal={dd/MM/yyyy})

**Estações alvo, de montante para jusante:**


| Estação          | Código                 | Papel                                                 |
| ---------------- | ---------------------- | ----------------------------------------------------- |
| Santa Tereza     | 86472600               | montante, rio Taquari                                 |
| Linha José Julio | 86472000               | montante (sem cota de inundação, só atenção e alerta) |
| Muçum            | 86510000               | alvo principal, resposta mais rápida                  |
| Encantado        | (buscar no inventário) | alvo principal                                        |
| Estrela          | (buscar)               | alvo, referência para Cruzeiro do Sul                 |
| Lajeado          | (buscar)               | alvo                                                  |
| Taquari          | 86950000               | jusante, exutório                                     |


Confirme cada código no inventário da ANA antes de usar. Não chute.

**Cotas de referência (atenção, alerta, inundação) por estação:** tabuladas em [https://rigeo.sgb.gov.br/bitstream/doc/24429/1/cotas_sace_taquari_mucum_artigo.pdf](https://rigeo.sgb.gov.br/bitstream/doc/24429/1/cotas_sace_taquari_mucum_artigo.pdf). Extraia e versione como CSV em `data/reference/cotas_referencia.csv`. São os limiares dos rótulos de classificação.

### B. Chuva

**CEMADEN (10 minutos, rede densa, prioridade alta).**

- Download: [https://mapainterativo.cemaden.gov.br/](https://mapainterativo.cemaden.gov.br/) (seleciona UF, município, mês, ano; o arquivo chega por link no e-mail)
- Dados **brutos, sem tratamento**, em **UTC**. Exigem QC.

**ANA pluviométricas:** mesma API do item A, rotas pluviométricas.

**INMET.**

- Históricos anuais em CSV: [https://portal.inmet.gov.br/dadoshistoricos](https://portal.inmet.gov.br/dadoshistoricos)
- BDMEP (convencionais desde 1961): [https://bdmep.inmet.gov.br/](https://bdmep.inmet.gov.br/)
- Catálogo de automáticas: [https://portal.inmet.gov.br/paginas/catalogoaut](https://portal.inmet.gov.br/paginas/catalogoaut)
- Dados de automáticas são brutos, sem consistência, horários, com janela de 90 dias no serviço em tempo real.

**MERGE / CPTEC (grade, cobre a cabeceira na Serra onde a rede é rala).**

- FTP horário: [https://ftp.cptec.inpe.br/modelos/tempo/MERGE/GPM/HOURLY/{ano}/{mes}/{dia}/MERGE_CPTEC_{YYYYMMDDHH}.grib2](https://ftp.cptec.inpe.br/modelos/tempo/MERGE/GPM/HOURLY/{ano}/{mes}/{dia}/MERGE_CPTEC_{YYYYMMDDHH}.grib2)
- FTP diário: [https://ftp.cptec.inpe.br/modelos/tempo/MERGE/GPM/DAILY/](https://ftp.cptec.inpe.br/modelos/tempo/MERGE/GPM/DAILY/)
- Existe arquivo único com todo o histórico de 1998 a 2024. Procure e prefira ele ao loop de downloads.
- Metadados: [https://data.inpe.br/dados/merge/](https://data.inpe.br/dados/merge/) e o README em [https://ftp.cptec.inpe.br/modelos/tempo/MERGE/GPM/MERGE_READ-ME.pdf](https://ftp.cptec.inpe.br/modelos/tempo/MERGE/GPM/MERGE_READ-ME.pdf)
- Formato GRIB2. Use `xarray` + `cfgrib`, recorte pela bacia com `rioxarray`.
- Combina IMERG V07B com observações de superfície, incluindo dados do ONS. Em regiões de rede observacional densa tem desempenho superior aos produtos globais.

**Grades globais (comparação e preenchimento):** ERA5-Land horário via Copernicus CDS (traz também umidade do solo e ET, úteis como condição antecedente), GPM IMERG V07 via NASA GES DISC, CHIRPS.

### C. Barragens e setor elétrico

- **CERAN:** [https://ceran.com.br/](https://ceran.com.br/) publica níveis de reservatório e vazões de operação das três usinas. Investigue se há endpoint ou só páginas HTML, e faça scraping educado (rate limit, user-agent identificável).
- **ONS Dados Abertos:** [https://dados.ons.org.br](https://dados.ons.org.br). Vazões naturais, afluentes e defluentes por usina, histórico longo, download programático. Esta é provavelmente a fonte mais limpa.
- **ANEEL / SIGEL:** ficha técnica das usinas, áreas de drenagem incrementais, características do vertedouro.

### D. Estáticos e geoespaciais

- **MDE:** Copernicus DEM GLO-30 (preferido), FABDEM (SRTM com dossel e edificações removidos, melhor para hidrologia), Topodata/INPE, NASADEM.
- **Ottobacias:** Base Hidrográfica Ottocodificada da ANA, em [https://metadados.snirh.gov.br](https://metadados.snirh.gov.br). Use para agregar chuva por sub-bacia em vez de por ponto.
- **MapBiomas:** uso e cobertura do solo, série anual desde 1985.
- **Solos:** mapa pedológico IBGE/EMBRAPA.
- **IBGE:** malha municipal e setores censitários.

### E. Validação independente e benchmark

- **Boletins históricos do SACE Taquari:** [https://www.sgb.gov.br/sace/boletins/Taquari/](https://www.sgb.gov.br/sace/boletins/Taquari/). São a **previsão oficial emitida na época**. Raspe e use como baseline externo. Se o modelo não bater isso, ele não serve.
- **RIGEO / SGB:** [https://rigeo.sgb.gov.br](https://rigeo.sgb.gov.br). Contém o levantamento de marcas de cheia de maio de 2024.
- **S2ID (MIDR):** decretos de emergência e formulários de danos por município e data.
- **Sentinel-1 SAR** (Copernicus Data Space ou ASF): delimitação de lâmina d'água durante os eventos, independente de nuvem.
- **Copernicus EMS Rapid Mapping:** o evento de maio de 2024 teve ativação com produtos de delineação prontos.
- **IBGE PEERS:** Pesquisa Especial sobre as Enchentes de 2024, 39 municípios do RS.

### F. Bibliotecas que poupam trabalho

`hydrobr` e `AgenciBr` (wrappers de ANA/INMET/MERGE), `xarray` + `cfgrib`, `rioxarray`, `geopandas`, `pysheds` ou `whitebox` para delinear sub-bacias, `polars` ou `pandas`, `scikit-learn`, `lightgbm`, `pytorch` se for para sequência.

Avalie os wrappers antes de adotar. Se estiverem desatualizados, escreva o cliente na mão. Não fique refém de pacote abandonado.

---

## Estrutura esperada

```
.
├── data/
│   ├── raw/          # download bruto + .meta.json, nunca editado
│   ├── interim/      # pós-QC
│   ├── processed/    # dataset supervisionado final
│   └── reference/    # cotas de referência, shapefiles, metadados de estações
├── src/
│   ├── ingest/       # um módulo por fonte (ana.py, cemaden.py, merge.py, ons.py)
│   ├── qc/
│   ├── features/
│   ├── models/
│   └── eval/
├── notebooks/
├── tests/
├── reports/
├── config/           # estações, janelas, hiperparâmetros em YAML
└── README.md

```

Configuração em YAML, não hardcoded. Códigos de estação, janelas de acumulado e horizontes de previsão são parâmetros.

---

## Fases

**Fase 0. Setup e reconhecimento.** Estrutura do repo, ambiente, dependências. Testar conectividade de cada fonte com uma requisição mínima. Produzir um relatório em `reports/00_[fontes.md](http://fontes.md)` dizendo, para cada fonte: funciona / precisa credencial / endpoint mudou / requer scraping. **Pare aqui e me mostre.**

**Fase 1. Ingestão.** Um módulo por fonte, com retry, backoff e cache. Baixar tudo o que existir para o período mais longo disponível, no mínimo 2010 até hoje. Materializar em Parquet particionado por estação e ano. Relatório de cobertura: por estação, período disponível, percentual de lacunas, resolução temporal real.

**Fase 2. QC e alinhamento temporal.** Detectar e marcar (não apagar) zeros travados, saltos impossíveis, sensores mortos, duplicatas, timestamps fora de ordem. **Padronizar tudo para UTC** e depois converter para America/Sao_Paulo em uma única fronteira explícita. CEMADEN e MERGE são UTC, ANA nem sempre. Erro de fuso aqui destrói o projeto silenciosamente. Reamostrar para uma grade horária comum. Documentar a regra de agregação de cada variável (soma para chuva, instantâneo ou média para nível).

**Fase 3. Delineamento e agregação espacial.** Delinear sub-bacias a partir do MDE, ou usar as ottobacias da ANA se forem adequadas. Agregar chuva por sub-bacia (Thiessen para pluviômetros, média de células para MERGE). Produzir uma série de chuva média por sub-bacia por hora.

**Fase 4. Features.**

- Acumulados de chuva em janelas de 1, 3, 6, 12, 24, 48, 72 e 120 horas, por sub-bacia.
- Índice de precipitação antecedente (API) com múltiplas constantes de decaimento, como proxy de umidade do solo. Opcionalmente umidade do solo do ERA5-Land.
- Cota atual e derivadas primeira e segunda das estações de montante.
- Vazão defluente das três UHEs e suas derivadas.
- Tempo desde a última ultrapassagem de cota de atenção.
- **Sem features de sazonalidade ingênua.** A precipitação é bem distribuída no ano.
- Documente cada feature com uma frase de justificativa física em `reports/04_[features.md](http://features.md)`.

**Fase 5. Dataset supervisionado.**

- Alvo: cota em Muçum, Encantado, Lajeado e Estrela, em horizontes de 3, 6, 12 e 24 horas.
- **Amostragem por evento**, não série contínua. Extraia janelas em torno de ultrapassagens da cota de atenção, mais uma amostra de períodos normais para o modelo aprender o regime base. Justifique a proporção escolhida.
- **Split estritamente cronológico.** Nunca aleatório. Autocorrelação horária vaza informação de forma brutal.
- Defina explicitamente o tratamento de 2023 e 2024. Proposta padrão: validação cruzada por evento, com um relatório separado só para os extremos. Se forem holdout puro, o modelo nunca viu nada daquela magnitude e vai falhar exatamente onde importa. Me consulte antes de fixar isso.

**Fase 6. Baselines (obrigatório antes de qualquer modelo complexo).**

1. Persistência: a cota atual se mantém.
2. Regressão linear com lags de cota de montante.
3. Modelo de propagação simples com tempo de viagem constante.
4. Os boletins históricos do SACE como benchmark externo. Registre os números. **Nenhum modelo avança sem bater os quatro.**

**Fase 7. Modelo.** Comece por gradient boosting (LightGBM) com as features tabulares. Só vá para sequência (LSTM, TCN) se o boosting saturar e você conseguir mostrar que o ganho é real, não ruído de validação. O nome do projeto diz "modelo pequeno": respeite isso.

**Fase 8. Avaliação.**

- Métricas contínuas: NSE, KGE, RMSE, MAE. **KGE e NSE são obrigatórias**, não só RMSE.
- Métricas de detecção para ultrapassagem de cota de inundação: POD, FAR, CSI, viés de frequência.
- **Avaliação separada para os picos.** Um RMSE bonito na média é irrelevante se o modelo erra o pico. Reporte erro no valor de pico e erro no tempo do pico, evento a evento.
- Diagrama de dispersão previsto versus observado por horizonte, e hidrogramas dos eventos de 2023 e 2024 com previsão sobreposta.
- Análise de importância de features e comparação com o que a literatura da bacia encontrou: chuva máxima de 5 dias, elevação e chuva máxima de 1 dia foram os preditores mais influentes em um estudo de 2025 na mesma bacia.

**Fase 9. Relatório final** em `reports/[final.md](http://final.md)`: o que funcionou, o que não funcionou, limitações honestas, e o que seria necessário para ir além.

---

## Armadilhas específicas desta bacia

1. **Curva-chave extrapolada.** Nos eventos de 2023 e 2024 as cotas saíram muito além do intervalo medido. A vazão nesses picos é extrapolação, não medição. **Treine em cota, não em vazão**, pelo menos para os extremos. Use vazão só onde ela é confiável, como feature de montante.
2. **Desbalanceamento severo.** A maior parte da série é rio em regime normal. Um trabalho de 2025 nesta bacia mostrou que restringir os dados de treino a partir da cota de atenção melhorou os resultados em cerca de 86% no horizonte de 4 horas. Leve isso a sério.
3. **Vazamento temporal.** Split cronológico sempre. Nenhuma normalização, imputação ou seleção de feature pode ver o futuro. Fit do scaler só no treino.
4. **Fuso horário.** CEMADEN e MERGE em UTC, ANA e INMET variam. Padronize cedo, teste explicitamente.
5. **Teto de horizonte.** Com chuva observada, cerca de 12 horas para Muçum e 8 para Estrela. Ir além exige chuva prevista (ETA e BRAMS do CPTEC, ou GFS/ECMWF open data), e aí a incerteza dominante passa a ser meteorológica, não hidrológica. Não prometa 48 horas com dados observados.
6. **Rompimento da 14 de Julho em 02/05/2024.** Os dados de operação daquele período são anômalos e possivelmente lacunares. Sinalize, não impute em silêncio.
7. **Estação sem cota de inundação.** Linha José Julio tem só atenção e alerta. Trate como caso especial, não force um limiar inventado.

---

## Definição de pronto

- `make all` (ou equivalente) reconstrói todo o pipeline do zero a partir do cache.
- Testes cobrindo QC, alinhamento temporal e construção de features.
- Relatório final com números comparando o modelo aos quatro baselines, incluindo desempenho nos eventos de 2023 e 2024.
- README explicando como obter as credenciais da ANA e rodar o projeto.
- Um [`LIMITACOES.md`](http://LIMITACOES.md) explícito, dizendo que isto não é sistema de alerta.

---

## Comece agora

Execute a Fase 0. Ao final, me apresente o `reports/00_[fontes.md](http://fontes.md)` e a lista de bloqueios (credenciais faltando, endpoints mortos, fontes que exigem scraping). Não avance para a Fase 1 sem meu ok.