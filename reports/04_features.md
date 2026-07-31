# Fase 4 — Features

Pool de **77 features** em `data/processed/features_hourly.parquet` (grade
horária UTC, 2010→hoje onde há dado; chuva horária apenas nas janelas com
MERGE horário — a Fase 5 baixa o MERGE de cada janela amostrada para que
nenhuma feature seja sistematicamente ausente fora de eventos, o que vazaria
"isto é um evento" pela máscara de NaN).

Cada modelo por estação alvo usará um SUBCONJUNTO (só montante físico) — o
pool completo existe para a Fase 5 recortar. Justificativa física de cada
grupo abaixo.

## Decisões estruturais

1. **Chuva exclusivamente do MERGE** (não dos pluviômetros ANA): a rede de 7
   pluviômetros é rala demais para 26 mil km² — a cabeceira na Serra não tem
   nenhum — e duplicar cada janela por fonte dobraria a contagem sem
   informação nova. Os pluviômetros ficam para QC e validação (foi assim que
   a convenção temporal do MERGE foi confirmada).
2. **3 macro-unidades em vez de 7 sub-bacias**: `antas` (12.918 km², contém a
   cascata CERAN), `medio` (incremental Muçum+Encantado, 6.765 km²) e `baixo`
   (incremental Estrela+P.Mariante+Taquari, 6.275 km²). Média ponderada por
   área incremental. Corta 56→24 features de acumulado preservando a
   estrutura espacial que importa: chuva no Antas vira onda com horas de
   antecedência; chuva no médio/baixo vale responde rápido.
3. **Causalidade estrita, testada**: acumulado de janela W em t soma [t-W, t-1]
   (a chuva da hora corrente não é conhecida); API diário só usa períodos de
   24h já encerrados; derivada que toca lacuna vira NaN (teste "futuro não
   altera passado" incluso).
4. **Grade contínua antes de qualquer janela**: horas sem amostra são NaN
   explícito — sem isso, diff/rolling atravessariam lacunas de sensor como se
   fossem 1h, fabricando derivadas erradas exatamente nas falhas da Armadilha 0.

## Grupos de features

### Chuva acumulada (24) — `chuva_{antas,medio,baixo}_{1,3,6,12,24,48,72,120}h`
Escoamento superficial domina a bacia (~80% da descarga) e a resposta é de
horas: os acumulados curtos (1-12h) capturam a chuva que ainda vai virar onda;
24-120h capturam o volume que já encheu a rede de drenagem e a literatura da
bacia aponta chuva máxima de 5 dias e de 1 dia como preditores dominantes.

### Umidade antecedente (6) — `api_{macro}_k{90,98}`
API = Σ k^i·P(d-i), proxy de umidade do solo (solos rasos argilosos: saturação
muda o coeficiente de escoamento). k=0,90 dá memória de ~1-2 semanas; k=0,98 de
~2 meses. Calculado sobre o MERGE diário 1998+, então está disponível para
qualquer amostra do período de treino. (Umidade ERA5-Land ficou como opção
futura; o API é gratuito e causal.)

### Cota e dinâmica por estação (28) — `nivel,dnivel_1h,dnivel_3h,d2nivel × 7`
O nível atual da própria estação é o estado do sistema (baseline de
persistência embutido); o das estações de montante é a onda a caminho —
antecedência física de Muçum para Encantado ~3h, para Estrela/Lajeado ~8h.
`dnivel` é a velocidade da onda (subida de 80 cm/h em Muçum foi o prelúdio de
maio/2024); `d2nivel` distingue onda acelerando de onda saturando.

### Tempo desde atenção (7) — `tempo_desde_atencao_h_{estacao}`
Separa "primeira onda" de "onda sobre rio já cheio" (novembro/2023 foi grave
porque veio semanas depois de setembro). Teto de 90 dias.

### Disponibilidade de sensor (7) — `disp_{estacao}`
Fração de amostras válidas nas últimas 6h. Armadilha 0 como feature: sensores
falham preferencialmente em cheia, então a própria ausência de dado a montante
é sinal de magnitude — e o modelo precisa saber quando as features de cota
estão degradadas.

### Defluência CERAN (5) — `defluente_{mc,ca,qj}`, `ddefluente_qj_{1h,3h}`
Vazão de montante bem instrumentada: a onda do Antas já formada, com horas de
antecedência sobre Muçum (fio d'água, afluência ≈ defluência). Derivadas só na
14 de Julho (última da cascata, sinal integrado) para conter contagem — as
três defluentes entram separadas porque divergências entre elas indicam
problema de dado (não de operação).

## O que ficou de fora, de propósito

- **Sazonalidade** (mês, dia do ano): precipitação bem distribuída no ano —
  proibido pelo idea.md.
- **Vazão da ANA como alvo ou feature além do montante**: curva-chave
  extrapolada nos extremos (Armadilha 1). Cota é a variável de trabalho.
- **Nível montante das UHEs**: reservatórios a fio d'água não regularizam;
  o nível deles é ruído operacional.
- **Chuva prevista**: fora do escopo (teto de horizonte com chuva observada é
  ~12h — Armadilha 5).

## Contagem

24 + 6 + 28 + 7 + 7 + 5 = **77 no pool**. Acima de "algumas dezenas" porque o
pool serve 4 estações alvo; cada modelo recorta ao seu montante físico
(≈35-45 features), e a Fase 7 mede importância e poda.
