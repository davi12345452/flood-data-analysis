# Revisão da rodada de 29/09/2026 11:00

Modo: **emissao**. Referência observada: 29/09 11:00 (UTC−3). Emissão registrada em 29/09/2026 11:42:20 local. A antecedência real desconta o tempo desde a observação.

Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. A coluna de cota é uma estimativa pontual, não uma cota de pico. Não é sistema de alerta.

| alvo      | motor          |   h | referencia_local   |   observado_cm | previsto_cm   | validade_local   |   antecedencia_real_h | status              |
|:----------|:---------------|----:|:-------------------|---------------:|:--------------|:-----------------|----------------------:|:--------------------|
| Muçum     | linear         |   3 | 29/09 11:00        |           1156 | —             | 29/09 14:00      |                   2.3 | dados_insuficientes |
| Muçum     | gbm_delta      |   6 | 29/09 11:00        |           1156 | 1325.8        | 29/09 17:00      |                   5.3 | estimativa          |
| Muçum     | gbm_delta      |   9 | 29/09 11:00        |           1156 | 1314.5        | 29/09 20:00      |                   8.3 | estimativa          |
| Muçum     | gbm_delta      |  12 | 29/09 11:00        |           1156 | 1263.1        | 29/09 23:00      |                  11.3 | estimativa          |
| Encantado | linear         |   3 | 29/09 11:00        |            992 | 1017.2        | 29/09 14:00      |                   2.3 | estimativa          |
| Encantado | ridge_montante |   6 | 29/09 11:00        |            992 | 1026.5        | 29/09 17:00      |                   5.3 | estimativa          |
| Encantado | gbm_delta      |   9 | 29/09 11:00        |            992 | 1168.2        | 29/09 20:00      |                   8.3 | estimativa          |
| Encantado | gbm_delta      |  12 | 29/09 11:00        |            992 | 1108.2        | 29/09 23:00      |                  11.3 | estimativa          |
| Estrela   | linear         |   3 | 29/09 11:00        |           2049 | 2056.4        | 29/09 14:00      |                   2.3 | estimativa          |
| Estrela   | linear         |   6 | 29/09 11:00        |           2049 | 2062.5        | 29/09 17:00      |                   5.3 | estimativa          |
| Estrela   | linear         |   9 | 29/09 11:00        |           2049 | 2057.8        | 29/09 20:00      |                   8.3 | estimativa          |
| Estrela   | linear         |  12 | 29/09 11:00        |           2049 | 2041.0        | 29/09 23:00      |                  11.3 | estimativa          |

## Faixas e diagnóstico

As faixas usam o quantil 90% dos erros de 2025, separado por regime, sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, a velocidade está fora da calibração ou a cobertura dos últimos erros conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). Uma faixa ausente não significa erro zero.

| alvo      |   h | inferior_cm   | superior_cm   | faixa_status                   | cobertura_recente_pct   |   n_faixa_recente |
|:----------|----:|:--------------|:--------------|:-------------------------------|:------------------------|------------------:|
| Muçum     |   3 | —             | —             | faltam dados                   | —                       |                 0 |
| Muçum     |   6 | —             | —             | erros recentes excedem a faixa | 50.0                    |                 6 |
| Muçum     |   9 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Muçum     |  12 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Encantado |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Encantado |   6 | —             | —             | erros recentes excedem a faixa | 66.7                    |                 6 |
| Encantado |   9 | —             | —             | erros recentes excedem a faixa | 66.7                    |                 6 |
| Encantado |  12 | 1035.5        | 1181.0        | empírica, sem garantia         | 83.3                    |                 6 |
| Estrela   |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Estrela   |   6 | 2030.4        | 2094.6        | empírica, sem garantia         | 100.0                   |                 4 |
| Estrela   |   9 | 2006.2        | 2109.5        | empírica, sem garantia         | 100.0                   |                 1 |
| Estrela   |  12 | 1967.3        | 2114.6        | empírica, sem garantia         | —                       |                 0 |

![Hidrograma revisado](figs/live_v3_20260929_14.png)

## Replay da subida

Referências a partir de 28/09 11:00; somente alvos já observados. Horizontes maiores têm menos pares. Ausência de linha significa ausência de pares, não erro zero.

| alvo      |   h |   MAE_cm |   vies_cm |   n |
|:----------|----:|---------:|----------:|----:|
| Encantado |   3 |     26.6 |     -14.1 |  22 |
| Encantado |   6 |     60.6 |      -4.3 |  19 |
| Encantado |   9 |     87.5 |      23.5 |  16 |
| Encantado |  12 |     92   |      41.4 |  13 |
| Estrela   |   3 |     15.8 |     -11.1 |  22 |
| Estrela   |   6 |     45.7 |     -30.8 |  19 |
| Estrela   |   9 |     95   |     -58.1 |  16 |
| Estrela   |  12 |    157.9 |     -98   |  13 |
| Muçum     |   3 |     36.7 |     -22.4 |  22 |
| Muçum     |   6 |     81.4 |      48.6 |  19 |
| Muçum     |   9 |    143.7 |     100.1 |  16 |
| Muçum     |  12 |    177.8 |     131.9 |  13 |

Os candidatos são escolhidos em 2023–2024, confirmados em 2025 e podem ser vetados por regressão em 2026. A comparação completa está em [melhoria e aceitação](12_melhoria_live.md). O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.

Arquivo local da execução: `data/processed/live_runs/emissao_20260929T144220346636Z`. Contém previsões, replay, features, datasets de treino, código e configuração.

## Emissões reais conferidas

| alvo      |   h |   MAE_cm |   n |
|:----------|----:|---------:|----:|
| Encantado |   3 |     39.1 |  14 |
| Encantado |   6 |    127.4 |  13 |
| Encantado |   9 |    168.6 |  13 |
| Encantado |  12 |    194.3 |  13 |
| Estrela   |   3 |     22.2 |  14 |
| Estrela   |   6 |     63.3 |  13 |
| Estrela   |   9 |    111.3 |  13 |
| Estrela   |  12 |    161.8 |  13 |
| Muçum     |   3 |     54.7 |   4 |
| Muçum     |   6 |    138.6 |  13 |
| Muçum     |   9 |    213.4 |  13 |
| Muçum     |  12 |    251.9 |  13 |
