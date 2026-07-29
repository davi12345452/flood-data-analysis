# PROJETO: Modelo de previsão de cota de cheia no Vale do Taquari (RS)

**Versão 2.** Incorpora os achados da Fase 0 de reconhecimento (executada em 2026-07-28). Fontes mortas foram removidas, rotas alternativas foram adicionadas, e duas restrições novas mudam o desenho do modelo. Leia a seção "Mudanças em relação à v1" antes de começar.

## Seu papel

Você é um engenheiro de dados e ML com experiência em hidrologia operacional. Vamos construir um pipeline reprodutível que prevê a **cota (nível) do rio Taquari** nas cidades do baixo vale a partir de chuva observada e vazão defluente das usinas do rio das Antas.

Projeto de pesquisa pessoal, não sistema de alerta. Nada aqui deve ser usado para decisão de evacuação.

---

## Mudanças em relação à v1

1. **A API legada da ANA morreu.** Toda a árvore `/hidroweb/rest/api/` passou a exigir token. O caminho de prototipagem sem credencial não existe mais. Removido.
2. **O serviço** `snirh.gov.br/dadoshidrometereologicos` **também é credenciado** (mesmo fluxo OAuth). Não é atalho. Removido.
3. **Entraram rotas alternativas para cota:** rede estadual do RS (Sala de Situação e SMAD RS) e o HIDRO-Telemetria legado.
4. **ONS confirmado como melhor fonte de defluência**, mas horário só desde 2019. Isso limita a janela de treino e **força um modelo pequeno**. Ver Fase 7.
5. **Regra crítica nova sobre falha de sensor durante cheias.** Ver "Armadilha 0". É a mudança mais importante deste documento.
6. **INMET bloqueado por fingerprinting TLS**, com solução conhecida.
7. **Nova Fase 0.5** antes da ingestão.

---

## Regras de trabalho (não negociáveis)

1. **Trabalhe em fases.** Ao final de cada uma, pare, mostre o resultado e espere confirmação.
2. **Nunca invente dados.** Se uma API falhar ou um endpoint mudar, reporte o erro real. Sem fallback sintético silencioso.
3. **Cache agressivo.** Todo download vira Parquet em `data/raw/`. Nenhum script de análise depende de rede.
4. **Idempotência.** Rodar duas vezes não duplica nem corrompe.
5. **Proveniência.** Cada arquivo em `data/raw/` tem `.meta.json` ao lado com URL, timestamp, parâmetros e contagem de registros.
6. **Commits pequenos** ao fim de cada fase.
7. **Lógica em módulos testáveis**, não em notebooks. Notebooks só para exploração descartável.
8. Se uma premissa deste documento estiver errada, **me avise em vez de contornar**.

---

## Contexto de domínio (assuma como verdadeiro)

**Bacia Taquari-Antas, RS.**

- Área de drenagem de cerca de 26.400 km². Curso principal de cerca de 530 km. Trecho com problema de inundação de cerca de 185 km, da confluência Antas-Carreiro até a foz no Jacuí.
- Escoamento superficial dominante. Fluxo subterrâneo contribui com apenas cerca de 20% da descarga total, por encostas íngremes, drenagem radial e solos argilosos rasos de baixa permeabilidade. **A bacia responde rápido e a chuva recente domina o sinal.**
- Precipitação anual entre 1.600 e 1.800 mm, bem distribuída ao longo do ano. **Não use features de sazonalidade ingênua.**
- Antecedência efetiva do sistema de alerta atual: cerca de **12h para Muçum e Encantado**, cerca de **8h para Estrela e Lajeado**. Teto realista para modelo alimentado só com chuva observada.

**Complexo CERAN (Monte Claro, Castro Alves, 14 de Julho), rio das Antas.**

- Usinas a fio d'água, **sem reservatório de regularização**. Não amortecem nem agravam cheia. Vazão afluente é integralmente defluída.
- Trate a defluência como **observação de vazão de montante bem instrumentada**, nunca como variável de controle. Não formule cenários de comportas.
- Como preditor é valiosa: entrega a onda já formada com horas de antecedência sobre Muçum.
- Em 02/05/2024 a vazão pela 14 de Julho foi estimada em mais de 15.000 m³/s e a estrutura sofreu rompimento parcial. **Dados desse período são anômalos. Sinalize, não impute.**

**Eventos de referência:** setembro/2023, novembro/2023, abril-maio/2024. O de maio/2024 é o maior registrado.

---

## Fontes de dados (status verificado na Fase 0)

### A. Alvo: cota

**A.1. Boletins do SACE (SGB) — ✅ funciona, prioridade máxima**

Fonte principal do alvo enquanto não houver credencial da ANA, e benchmark externo permanente.

- Índice: [`https://www.sgb.gov.br/sace/boletins.php?idbacia=9`](https://www.sgb.gov.br/sace/boletins.php?idbacia=9)
- O diretório `boletins/Taquari/` devolve 403, mas o índice lista links diretos para os PDFs em `boletins/Taquari/<YYYYMMDD_HH...>.pdf`
- Paginação via tablesorter. Data e hora no nome do arquivo.
- Cada boletim traz **cotas observadas** nas estações e a **previsão oficial emitida na época**. Extraia as duas coisas em tabelas separadas.

**A.2. Rede estadual do RS — ✅ investigar, rota alternativa mais promissora**

Rede independente da ANA, mesmo tipo de dado, com ferramenta de download de histórico documentada em uso pelo próprio DRHS/Sema.

- Sala de Situação: [`http://www.saladesituacao.rs.gov.br/`](http://www.saladesituacao.rs.gov.br/), aba **"Dados"**, download de histórico de precipitação e nível
- SMAD RS: [`http://www.smad.rs.gov.br/`](http://www.smad.rs.gov.br/), mapa de estações do RS, gráficos de nível e chuva, download de histórico, atualização horária

**A.3. HIDRO-Telemetria legado (ANA) — ✅ investigar**

Aplicação [ASP.NET](http://ASP.NET) separada da árvore REST que morreu. Ainda linkada pela Sema em julho de 2026.

- [`http://www.snirh.gov.br/hidrotelemetria/Mapa.aspx`](http://www.snirh.gov.br/hidrotelemetria/Mapa.aspx)
- [`https://www.snirh.gov.br/hidrotelemetria/gerarGrafico.aspx`](https://www.snirh.gov.br/hidrotelemetria/gerarGrafico.aspx)
- Provavelmente monta a série via querystring ou postback. Capture no DevTools.

**A.4. ANA HidroWebService (oficial) — 🔑 credencial pendente**

- Swagger: [`https://www.ana.gov.br/hidrowebservice/swagger-ui.html`](https://www.ana.gov.br/hidrowebservice/swagger-ui.html)
- Auth: `GET /EstacoesTelemetricas/OAUth/v1`, token com validade de **60 minutos**, implemente refresh automático
- Série: `GET /EstacoesTelemetricas/HidroinfoanaSerieTelemetricaAdotada/v1`
- Manual: [`https://www.gov.br/ana/pt-br/assuntos/monitoramento-e-eventos-criticos/monitoramento-hidrologico/orientacoes-manuais/manuais/manual-hidrowebservice_publica.pdf`](https://www.gov.br/ana/pt-br/assuntos/monitoramento-e-eventos-criticos/monitoramento-hidrologico/orientacoes-manuais/manuais/manual-hidrowebservice_publica.pdf)
- Deixe o cliente pronto e testável por trás de flag. Quando a credencial chegar, é só ligar.

**A.5. Portal HidroWeb, download em lote — ✅ manual, passo diário**

- [`https://www.snirh.gov.br/hidroweb/serieshistoricas`](https://www.snirh.gov.br/hidroweb/serieshistoricas)
- Série convencional consistida, resolução diária. Serve para contexto histórico longo e estatística de extremos, **não para horizonte de 12h**. Baixe assim mesmo.

**Estações alvo, de montante para jusante:**


| Estação          | Código    | Papel                                                             |
| ---------------- | --------- | ----------------------------------------------------------------- |
| Santa Tereza     | 86472600  | montante                                                          |
| Linha José Julio | 86472000  | montante (só cota de atenção e alerta, **sem cota de inundação**) |
| Muçum            | 86510000  | alvo principal, resposta mais rápida                              |
| Encantado        | confirmar | alvo principal                                                    |
| Estrela          | confirmar | alvo, referência para Cruzeiro do Sul                             |
| Lajeado          | confirmar | alvo                                                              |
| Taquari          | 86950000  | jusante, exutório                                                 |


Confirme cada código no inventário antes de usar. Não chute.

**Cotas de referência:** extrair de [`https://rigeo.sgb.gov.br/bitstream/doc/24429/1/cotas_sace_taquari_mucum_artigo.pdf`](https://rigeo.sgb.gov.br/bitstream/doc/24429/1/cotas_sace_taquari_mucum_artigo.pdf) (✅ verificado) e versionar em `data/reference/cotas_referencia.csv`.

### B. Chuva

**B.1. MERGE / CPTEC — ✅ funciona, grade, prioridade alta**

Cobre a cabeceira na Serra, onde a rede de pluviômetros é rala.

- Horário: [`https://ftp.cptec.inpe.br/modelos/tempo/MERGE/GPM/HOURLY/{ano}/{mes}/{dia}/MERGE_CPTEC_{YYYYMMDDHH}.grib2`](https://ftp.cptec.inpe.br/modelos/tempo/MERGE/GPM/HOURLY/{ano}/{mes}/{dia}/MERGE_CPTEC_{YYYYMMDDHH}.grib2)
- Diário: [`https://ftp.cptec.inpe.br/modelos/tempo/MERGE/GPM/DAILY/`](https://ftp.cptec.inpe.br/modelos/tempo/MERGE/GPM/DAILY/)
- **Procure o arquivo histórico único 1998-2024 antes de fazer loop de downloads.**
- README: [`https://ftp.cptec.inpe.br/modelos/tempo/MERGE/GPM/MERGE_READ-ME.pdf`](https://ftp.cptec.inpe.br/modelos/tempo/MERGE/GPM/MERGE_READ-ME.pdf). Metadados: [`https://data.inpe.br/dados/merge/`](https://data.inpe.br/dados/merge/)
- GRIB2. Use `xarray` + `cfgrib`, recorte com `rioxarray`.
- Combina IMERG V07B com observações de superfície, incluindo dados do ONS. Em regiões de rede densa supera os produtos globais.

**B.2. CEMADEN — ⚠️ semi-manual, melhor resolução temporal (10 min)**

Duas saídas, nesta ordem:

1. **Reverso do mapa interativo.** Abra [`https://mapainterativo.cemaden.gov.br/`](https://mapainterativo.cemaden.gov.br/), DevTools, aba Network, clique numa estação e capture a XHR real. Os endpoints antigos (`sws.cemaden.gov.br/PED/rest/...`, `mapainterativo/graficorec/...`) estão mortos, mas o frontend consome algo.
2. **Fluxo por e-mail como custo único.** Arquivo mensal por UF. RS de 2014 a 2026 são cerca de 150 requisições. Depois fica em Parquet para sempre. Numa bacia que responde em horas, os 10 minutos de resolução justificam o trabalho.

Dados são **brutos, sem tratamento, em UTC**.

**B.3. INMET — ❌ bloqueado por fingerprinting TLS, solução conhecida**

Sintoma (DNS resolve, connection reset em curl e urllib mesmo com user-agent de navegador) indica que o WAF inspeciona o ClientHello.

- **Solução:** `curl_cffi` no Python, com `requests.get(url, impersonate="chrome")`. Resolve na maioria dos casos.
- Se persistir, é bloqueio de ASN: rode a ingestão de uma VM.
- **Substituto se não valer o esforço:** **BR-DWGD** (Xavier et al., GitHub/Zenodo), grade diária de 0.1° construída a partir de pluviômetros do INMET e da ANA.
- Endpoints: [`https://portal.inmet.gov.br/dadoshistoricos`](https://portal.inmet.gov.br/dadoshistoricos), [`https://bdmep.inmet.gov.br/`](https://bdmep.inmet.gov.br/), [`https://portal.inmet.gov.br/paginas/catalogoaut`](https://portal.inmet.gov.br/paginas/catalogoaut)
- **Prioridade baixa.** CEMADEN mais MERGE cobrem chuva.

**B.4. Grades globais (comparação e preenchimento)**

ERA5-Land horário via Copernicus CDS (traz umidade do solo e ET, úteis como condição antecedente), GPM IMERG V07 via NASA GES DISC, CHIRPS.

### C. Barragens e setor elétrico

**C.1. ONS Dados Abertos — ✅ confirmado, fonte primária**

- CKAN: [`https://dados.ons.org.br`](https://dados.ons.org.br)
- Dataset `dados_hidrologicos_ho` (Dados Hidráulicos por Reservatório, base horária): Parquet/CSV/XLSX no S3, cobertura **desde 2019-01**
- As três usinas da CERAN estão presentes: `MONTE CLARO`, `CASTRO ALVES`, `14 DE JULHO`
- Colunas úteis: `val_vazaoafluente`, `val_vazaodefluente`, `val_vazaoturbinada`, `val_vazaovertida`, `val_nivelmontante`
- Complementar com `dados-hidrologicos-res` (base diária, histórico mais longo)
- **Dados não consistidos** (réplica do que os agentes enviam). Exigem QC.

**C.2. CERAN — descartado**

[`https://ceran.com.br/`](https://ceran.com.br/) responde mas não tem endpoint de dados conhecido. O ONS já cobre a necessidade. Só volte aqui se aparecer lacuna real.

### D. Estáticos e geoespaciais

- **MDE:** Copernicus DEM GLO-30 (preferido), FABDEM (SRTM com dossel e edificações removidos, melhor para hidrologia), Topodata/INPE, NASADEM
- **Ottobacias:** Base Hidrográfica Ottocodificada da ANA, em [`https://metadados.snirh.gov.br`](https://metadados.snirh.gov.br) (✅ responde, geoserviços a mapear na Fase 3)
- **MapBiomas:** uso e cobertura do solo, série anual desde 1985
- **Solos:** mapa pedológico IBGE/EMBRAPA
- **IBGE:** malha municipal e setores censitários

### E. Validação independente

- **RIGEO / SGB** ([`https://rigeo.sgb.gov.br`](https://rigeo.sgb.gov.br)): levantamento de marcas de cheia de maio/2024
- **S2ID (MIDR):** decretos de emergência e formulários de danos por município e data
- **Sentinel-1 SAR** (Copernicus Data Space ou ASF): lâmina d'água durante os eventos, independente de nuvem
- **Copernicus EMS Rapid Mapping:** maio/2024 teve ativação com produtos de delineação prontos
- **IBGE PEERS:** Pesquisa Especial sobre as Enchentes de 2024, 39 municípios do RS

### F. Bibliotecas

`curl_cffi` (para o INMET), `httpx`, `tenacity`, `xarray` + `cfgrib`, `rioxarray`, `geopandas`, `pysheds` ou `whitebox`, `polars` ou `pandas`, `pyarrow`, `scikit-learn`, `lightgbm`.

Avalie `hydrobr` e `AgenciBr` antes de adotar. Se estiverem desatualizados, escreva o cliente na mão. Não fique refém de pacote abandonado.

---

## Estrutura

```
.
├── data/
│   ├── raw/          # download bruto + .meta.json, nunca editado
│   ├── interim/      # pós-QC
│   ├── processed/    # dataset supervisionado
│   └── reference/    # cotas de referência, shapefiles, metadados de estações
├── src/
│   ├── ingest/       # sace.py, ons.py, merge.py, cemaden.py, ana.py, sema_rs.py
│   ├── qc/
│   ├── features/
│   ├── models/
│   └── eval/
├── notebooks/
├── tests/
├── reports/
├── config/           # estações, janelas, horizontes, hiperparâmetros em YAML
└── README.md

```

Configuração em YAML. Códigos de estação, janelas de acumulado e horizontes são parâmetros, não constantes no código.

---

## Fases

### Fase 0.5. Desbloqueio (comece por aqui)

Quatro tarefas curtas, em paralelo:

1. **Disparar o e-mail à ANA** solicitando credencial do HidroWebService, conforme o manual. Não bloqueie nada esperando resposta.
2. **Testar** `curl_cffi` **contra o INMET** com `impersonate="chrome"`. Reporte se resolveu.
3. **Capturar a XHR do CEMADEN** no mapa interativo e documentar o endpoint encontrado (ou concluir que não há e assumir o fluxo por e-mail).
4. **Investigar as rotas alternativas de cota:** `gerarGrafico.aspx` do HIDRO-Telemetria, aba "Dados" da Sala de Situação, e o SMAD RS. Documentar qual delas entrega série horária programaticamente.

Saída: `reports/00b_[desbloqueio.md](http://desbloqueio.md)`. **Pare e me mostre.**

### Fase 1. Ingestão

Um módulo por fonte, com retry, backoff e cache. Baixar o máximo de histórico disponível. Materializar em Parquet particionado por estação e ano.

Ordem de implementação: **ONS → MERGE → SACE → (o que a Fase 0.5 destravar)**. Essa tripla já fecha um dataset utilizável.

Saída: relatório de cobertura por estação com período disponível, percentual de lacunas e resolução temporal real.

### Fase 2. QC e alinhamento temporal

Detectar e **marcar, nunca apagar**: zeros travados, saltos impossíveis, sensores mortos, duplicatas, timestamps fora de ordem.

**Aplicar a Armadilha 0 (abaixo) integralmente nesta fase.**

Padronizar tudo para UTC e converter para America/Sao_Paulo em uma única fronteira explícita. CEMADEN e MERGE são UTC, ANA e Sema variam. Erro de fuso aqui destrói o projeto em silêncio.

Reamostrar para grade horária comum. Documentar a regra de agregação de cada variável (soma para chuva, instantâneo ou média para nível).

### Fase 3. Delineamento e agregação espacial

Delinear sub-bacias a partir do MDE, ou usar as ottobacias da ANA se forem adequadas. Agregar chuva por sub-bacia (Thiessen para pluviômetros, média de células para MERGE). Produzir série de chuva média por sub-bacia por hora.

### Fase 4. Features

- Acumulados de chuva em janelas de 1, 3, 6, 12, 24, 48, 72 e 120h, por sub-bacia
- Índice de precipitação antecedente (API) com múltiplas constantes de decaimento, como proxy de umidade do solo. Opcionalmente umidade do solo do ERA5-Land
- Cota atual e derivadas primeira e segunda das estações de montante
- Vazão defluente das três UHEs e derivadas
- Tempo desde a última ultrapassagem da cota de atenção
- **Disponibilidade de dado por estação** (ver Armadilha 0)
- **Sem sazonalidade ingênua**
- Documente cada feature com uma frase de justificativa física em `reports/04_[features.md](http://features.md)`

**Restrição de contagem:** dado o volume de treino (ver Fase 7), mantenha o conjunto final enxuto. Se passar de algumas dezenas de features, justifique.

### Fase 5. Dataset supervisionado

- **Alvo:** cota em Muçum, Encantado, Lajeado e Estrela, em horizontes de 3, 6, 12 e 24h
- **Amostragem por evento**, não série contínua. Janelas em torno de ultrapassagens da cota de atenção, mais uma amostra de períodos normais para o modelo aprender o regime base. Justifique a proporção
- **Split estritamente cronológico.** Nunca aleatório. Autocorrelação horária vaza informação de forma brutal
- **Decisão sobre 2023 e 2024: me consulte antes de fixar.** Proposta padrão é validação cruzada por evento com relatório separado para os extremos. Se virarem holdout puro, o modelo nunca viu nada daquela magnitude e vai falhar exatamente onde importa

### Fase 6. Baselines (obrigatório, bloqueante)

1. Persistência: a cota atual se mantém
2. Regressão linear com lags de cota de montante
3. Propagação simples com tempo de viagem constante
4. **Os boletins históricos do SACE como benchmark externo**

Registre os números. **Nenhum modelo avança sem bater os quatro.**

### Fase 7. Modelo

**LightGBM raso, com regularização forte.** O ONS horário começa em 2019, o que dá cerca de 7 anos de janela útil. Com amostragem por evento, isso são aproximadamente 20 a 40 eventos.

Consequências, não negociáveis:

- Redes recorrentes (LSTM, TCN) estão **fora de escopo**. Não há volume que as sustente
- Profundidade e número de folhas baixos, `min_data_in_leaf` alto
- Validação por evento, não por hora, para não superestimar desempenho

**Mitigação opcional:** montar dataset secundário mais longo e mais grosso (ONS diário `dados-hidrologicos-res` mais HidroWeb diário) e testar se pré-treinar nele ajuda. Reporte com honestidade se não ajudar.

### Fase 8. Avaliação

- **Métricas contínuas:** NSE, KGE, RMSE, MAE. **KGE e NSE obrigatórias**, não só RMSE
- **Métricas de detecção** para ultrapassagem da cota de inundação: POD, FAR, CSI, viés de frequência
- **Avaliação separada dos picos.** RMSE bonito na média é irrelevante se o modelo erra o pico. Reporte erro no valor de pico e erro no tempo do pico, evento a evento
- **Cobertura de dado por evento** (ver Armadilha 0). Se o modelo só é avaliado onde o dado existe, e o dado some nos picos, a métrica está medindo o caso fácil. Reporte explicitamente o percentual de horas de pico com dado válido
- Dispersão previsto versus observado por horizonte. Hidrogramas de 2023 e 2024 com previsão sobreposta
- Importância de features, comparada com a literatura da bacia: chuva máxima de 5 dias, elevação e chuva máxima de 1 dia foram os preditores mais influentes em um estudo de 2025 na mesma bacia

### Fase 9. Relatório final

`reports/[final.md](http://final.md)`: o que funcionou, o que não funcionou, limitações honestas, e o que seria necessário para ir além.

---

## Armadilhas

### Armadilha 0. Falha de sensor concentrada nos picos (a mais grave)

Documentação técnica do DRHS/Sema sobre estações da região observa que **o maior número de falhas, registradas como nível zero, ocorre justamente durante os períodos de cheia.**

Ou seja: **os sensores falham preferencialmente nos momentos que você quer prever.** Isso é censura não aleatória e é fatal se passar despercebido.

Regras obrigatórias:

1. **Zero de nível nunca é dado válido.** É `NaN` explícito, sempre. Vale para todas as fontes
2. **Nunca impute lacuna de cheia com interpolação.** Você fabrica picos suavizados e o modelo aprende a subestimar exatamente onde não pode errar
3. **Disponibilidade de sensor entra como variável de avaliação.** Reporte o percentual de horas de pico com dado válido, por evento e por estação
4. **Cruze estações redundantes** (ANA, Sema/SMAD, CEMADEN no mesmo trecho) para recuperar o que uma perdeu. Documente a regra de precedência
5. Considere disponibilidade também como **feature**: a ausência de dado numa estação de montante é, ela própria, informação sobre magnitude

### Armadilha 1. Curva-chave extrapolada

Em 2023 e 2024 as cotas saíram muito além do intervalo medido. Vazão nesses picos é extrapolação, não medição. **Treine em cota, não em vazão**, ao menos para os extremos. Use vazão só onde é confiável, como feature de montante.

### Armadilha 2. Desbalanceamento severo

A maior parte da série é rio em regime normal. Um trabalho de 2025 nesta bacia mostrou que restringir os dados de treino a partir da cota de atenção melhorou os resultados em cerca de 86% no horizonte de 4h.

### Armadilha 3. Vazamento temporal

Split cronológico sempre. Nenhuma normalização, imputação ou seleção de feature pode ver o futuro. Fit do scaler só no treino.

### Armadilha 4. Fuso horário

CEMADEN e MERGE em UTC, ANA, Sema e INMET variam. Padronize cedo e teste explicitamente.

### Armadilha 5. Teto de horizonte

Com chuva observada, cerca de 12h para Muçum e 8h para Estrela. Ir além exige chuva prevista (ETA e BRAMS do CPTEC, ou GFS/ECMWF open data), e a incerteza dominante passa a ser meteorológica. **Não prometa 48h com dados observados.**

### Armadilha 6. Rompimento da 14 de Julho em 02/05/2024

Dados de operação daquele período são anômalos e possivelmente lacunares. Sinalize, não impute em silêncio.

### Armadilha 7. Estação sem cota de inundação

Linha José Julio tem só atenção e alerta. Caso especial. Não invente limiar.

### Armadilha 8. ONS não consistido

Os dados horários do ONS são réplica do que os agentes enviam, sem consistência. Aplique o mesmo rigor de QC que aplicaria a sensor de campo.

---

## Definição de pronto

- `make all` reconstrói todo o pipeline do zero a partir do cache
- Testes cobrindo QC, alinhamento temporal, regra de zero-como-NaN e construção de features
- Relatório final comparando o modelo aos quatro baselines, com desempenho nos eventos de 2023 e 2024 e cobertura de dado por evento
- README explicando como obter a credencial da ANA e rodar o projeto
- [`LIMITACOES.md`](http://LIMITACOES.md) explícito, dizendo que isto não é sistema de alerta

---

## Comece agora

Execute a **Fase 0.5**. Ao final, apresente `reports/00b_[desbloqueio.md](http://desbloqueio.md)` com o resultado das quatro tarefas e uma recomendação de qual fonte de cota adotar como primária na Fase 1. Não avance sem meu ok.