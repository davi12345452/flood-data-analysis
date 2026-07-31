# Relatório final — Previsão de cota de cheia no Vale do Taquari

Projeto de pesquisa pessoal, executado nas fases 0–9 entre 28 e 31/07/2026.
**Não é sistema de alerta e nada aqui deve ser usado para decisão de
evacuação** (ver `LIMITACOES.md`). Este documento consolida o que funcionou,
o que não funcionou, e o que seria necessário para ir além. Detalhes em
`reports/0*.md`.

---

## O que foi construído

Pipeline reprodutível (`make all`, ~12 GB de cache local, 61 testes) que:

1. **Ingere** cota telemétrica de 15 min (SOAP legado da ANA, 8 estações,
   2018+), defluência horária das 3 UHEs da CERAN (ONS, 2010+), chuva em
   grade MERGE/CPTEC (diária 1998+, horária nas 95 janelas amostradas) e os
   305 boletins do SACE — tudo com proveniência (`.meta.json`) e cache
   idempotente.
2. **Controla qualidade** com fusos determinados empiricamente (ANA e ONS em
   UTC−3 fixo, validados contra boletim e por cross-correlação física),
   zero-de-nível como NaN com flag, e grade horária UTC comum sem nenhuma
   interpolação de lacuna.
3. **Agrega chuva** por sub-bacia incremental (HydroBASINS lev8, Muçum
   validada em +0,1% contra a área oficial) em 3 macro-unidades físicas.
4. **Monta um dataset supervisionado** por evento: 59 eventos (2018–2026) +
   36 janelas normais, rótulos em 3/6/12/24h para Muçum, Encantado e Estrela
   (que cobre Lajeado, como na prática do SACE).
5. **Avalia com validação cruzada por evento** contra 4 baselines
   obrigatórios, com métricas contínuas (NSE/KGE/RMSE/MAE), de detecção
   (POD/FAR/CSI/viés) e de pico (erro de valor, erro de tempo, cobertura).

## Resultado central

**O melhor modelo depende do horizonte** — e isso é física, não acidente:

| Horizonte | Melhor modelo | NSE (Muçum) | Contra o SACE (pareado) |
|---|---|---|---|
| 3h | regressão linear c/ lags | 0,992 | **vence** (MAE 17,6 vs 46,8 cm em Encantado) |
| 6h | regressão linear c/ lags | 0,975 | comparável |
| 12h | LightGBM | 0,935 | sem previsão oficial para comparar |
| 24h | LightGBM | 0,778 | idem — e NSE cai a 0,24–0,58 no regime alto |

- Em ≤6h a propagação da onda é quase linear: um modelo linear com nível e
  derivadas de montante extrapola melhor que árvores e **bate a previsão
  oficial emitida na época** nas mesmas horas de emissão.
- Em 12–24h chuva e não-linearidade dominam e o GBM ganha com folga dos
  baselines (24h: NSE 0,78 vs 0,60) — mas com a ressalva de pico abaixo.
- O ganho do GBM em 24h **não sobrevive ao regime alto** (NSE 0,24–0,58):
  o teto físico de antecedência (~12h Muçum, ~8h Estrela) com chuva
  observada é real e nenhuma engenharia de feature o move.

## O que funcionou

- **O SOAP legado da ANA** (telemetriaws1) como fonte primária de cota sem
  credencial — 15 min, todas as estações, o evento de mai/2024 inteiro.
- **ONS como defluência**: as 3 UHEs desde 2010, 1,9% de lacunas, e a
  validação física (defluência da 14 de Julho ≈ vazão em José Júlio, r=0,998
  em lag 0) que de quebra fixou o fuso.
- **Validação cruzada por evento com extremos incluídos** (decisão de
  projeto): mai/2024 avaliado por um modelo que nunca o viu responde à
  pergunta operacional real.
- **Disponibilidade de sensor como variável de primeira classe** (Armadilha
  0): flags, feature e denominador de métrica.
- **Verificação empírica de convenções**: fuso da ANA (boletim SACE), fuso do
  ONS (cross-correlação), acumulação do MERGE (correlação com pluviômetros em
  lag 0) — três lugares onde uma suposição silenciosa teria envenenado tudo.

## O que não funcionou (e está registrado, não escondido)

1. **Árvores subestimam picos recordes**: nos eventos de referência o GBM
   errou o valor de pico em −160 a −640 cm. LightGBM não extrapola além do
   máximo de treino — e cheia recorde é, por definição, extrapolação. Para
   picos, a regressão linear em horizonte curto foi mais confiável.
2. **A Armadilha 2 não replicou**: treinar só com nível ≥ atenção (ganho de
   ~86% num estudo de 2025 na bacia) PIOROU nossos resultados mesmo avaliando
   só no regime alto. Hipótese: a amostragem por evento já concentra o treino
   no que importa; o corte só descarta informação de subida.
3. **Censura não aleatória medida**: cobertura de observação de 0,65–0,68 nas
   ±12h dos picos dos eventos de referência (Estrela truncada no máximo
   histórico; Encantado quase todo apagado em mai/2024; ONS transmitiu 9 de
   72 horas no pico). Toda métrica de pico está calculada sobre picos
   possivelmente truncados — o erro real pode ser maior.
4. **Pré-treino no dataset longo diário** (mitigação opcional da Fase 7):
   não executado. Fica como trabalho futuro.

## Premissas do idea.md corrigidas ao longo do caminho (regra 8)

API legada da ANA morta (substituída pelo SOAP legado, vivo); rede estadual
RS fora do ar (DNS morto); ONS horário desde 2010 (não 2019); arquivo
histórico único do MERGE existe (4,1 GB); PDF do RIGEO só tabula Muçum;
Linha José Júlio fica no rio das Antas e hoje tem cota de inundação (2450
cm); não existe estação "Lajeado" no Taquari (Estrela cobre); base horária
do MERGE ainda é V06B; schema do ONS mudou em 2026-02.

## Para ir além (em ordem de retorno provável)

1. **Chuva prevista** (ETA/BRAMS do CPTEC ou GFS/ECMWF open data) — é a única
   forma de romper o teto de ~12h; a incerteza dominante passa a ser
   meteorológica.
2. **Tratamento explícito de extrapolação nos picos**: alvo em diferença
   (Δnivel) em vez de nível absoluto, termo linear híbrido (GBM sobre
   resíduo do linear), ou monotonic constraints — ataca o viés de −600 cm.
3. **Credencial do HidroWebService** (cliente pronto atrás de flag) — série
   consistida, convencional histórica longa e redundância contra o SOAP
   legado, que não tem SLA.
4. **CEMADEN (10 min)** pelo fluxo de e-mail — resolução temporal para a
   cabeceira rápida e redundância de pluviômetro (Armadilha 0).
5. **Pré-treino no diário longo** (ONS 2000+, MERGE 1998+) para o modelo de
   24h — a janela em que faltam eventos de treino.
6. **Quantis em vez de ponto** (LightGBM quantile): banda de incerteza é mais
   honesto que número seco perto do teto de horizonte.

## Balanço

O projeto cumpriu o que o idea.md pediu: pipeline reprodutível de ponta a
ponta, quatro baselines batidos onde o modelo complexo se justifica (12–24h),
benchmark externo superado no horizonte curto pela solução simples, e — talvez
o mais valioso — um mapa quantificado de onde a previsão nesta bacia é
confiável e onde ela é estruturalmente limitada: pelo teto físico de
antecedência, pela extrapolação de recordes e pela censura de sensor
exatamente nos momentos que importam.
