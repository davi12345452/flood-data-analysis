# Revisão da rodada de 29/09/2026 14:00

Modo: **emissao**. Referência observada: 29/09 14:00 (UTC−3). Emissão registrada em 29/09/2026 14:40:38 local. A antecedência real desconta o tempo desde a observação.

Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. A coluna de cota é uma estimativa pontual, não uma cota de pico. Não é sistema de alerta.

| alvo      | motor          |   h | referencia_local   |   observado_cm | previsto_cm   | validade_local   |   antecedencia_real_h | status              |
|:----------|:---------------|----:|:-------------------|---------------:|:--------------|:-----------------|----------------------:|:--------------------|
| Muçum     | linear         |   3 | 29/09 14:00        |           1287 | —             | 29/09 17:00      |                   2.3 | dados_insuficientes |
| Muçum     | gbm_delta      |   6 | 29/09 14:00        |           1287 | 1417.7        | 29/09 20:00      |                   5.3 | estimativa          |
| Muçum     | gbm_delta      |   9 | 29/09 14:00        |           1287 | 1404.3        | 29/09 23:00      |                   8.3 | estimativa          |
| Muçum     | gbm_delta      |  12 | 29/09 14:00        |           1287 | 1360.2        | 30/09 02:00      |                  11.3 | estimativa          |
| Encantado | linear         |   3 | 29/09 14:00        |           1093 | 1204.2        | 29/09 17:00      |                   2.3 | estimativa          |
| Encantado | ridge_montante |   6 | 29/09 14:00        |           1093 | 1264.8        | 29/09 20:00      |                   5.3 | estimativa          |
| Encantado | gbm_delta      |   9 | 29/09 14:00        |           1093 | 1305.7        | 29/09 23:00      |                   8.3 | estimativa          |
| Encantado | gbm_delta      |  12 | 29/09 14:00        |           1093 | 1274.9        | 30/09 02:00      |                  11.3 | estimativa          |
| Estrela   | linear         |   3 | 29/09 14:00        |           2074 | 2111.1        | 29/09 17:00      |                   2.3 | estimativa          |
| Estrela   | linear         |   6 | 29/09 14:00        |           2074 | 2165.2        | 29/09 20:00      |                   5.3 | estimativa          |
| Estrela   | linear         |   9 | 29/09 14:00        |           2074 | 2203.3        | 29/09 23:00      |                   8.3 | estimativa          |
| Estrela   | linear         |  12 | 29/09 14:00        |           2074 | 2216.3        | 30/09 02:00      |                  11.3 | estimativa          |

## Faixas e diagnóstico

As faixas usam o quantil 90% dos erros de 2025, separado por regime, sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, a velocidade está fora da calibração ou a cobertura dos últimos erros conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). Uma faixa ausente não significa erro zero.

| alvo      |   h | inferior_cm   | superior_cm   | faixa_status                   | cobertura_recente_pct   |   n_faixa_recente |
|:----------|----:|:--------------|:--------------|:-------------------------------|:------------------------|------------------:|
| Muçum     |   3 | —             | —             | faltam dados                   | —                       |                 0 |
| Muçum     |   6 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Muçum     |   9 | —             | —             | erros recentes excedem a faixa | 50.0                    |                 6 |
| Muçum     |  12 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Encantado |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Encantado |   6 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Encantado |   9 | —             | —             | erros recentes excedem a faixa | 50.0                    |                 6 |
| Encantado |  12 | —             | —             | erros recentes excedem a faixa | 66.7                    |                 6 |
| Estrela   |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Estrela   |   6 | —             | —             | erros recentes excedem a faixa | 66.7                    |                 6 |
| Estrela   |   9 | 2151.7        | 2254.9        | empírica, sem garantia         | 100.0                   |                 4 |
| Estrela   |  12 | 2142.7        | 2290.0        | empírica, sem garantia         | 100.0                   |                 1 |

![Hidrograma revisado](figs/live_v3_20260929_17.png)

## Replay da subida

Referências a partir de 28/09 14:00; somente alvos já observados. Horizontes maiores têm menos pares. Ausência de linha significa ausência de pares, não erro zero.

| alvo      |   h |   MAE_cm |   vies_cm |   n |
|:----------|----:|---------:|----------:|----:|
| Encantado |   3 |     28.8 |     -16.2 |  22 |
| Encantado |   6 |     58.2 |      -1.8 |  19 |
| Encantado |   9 |     87.9 |      23.1 |  16 |
| Encantado |  12 |     94.4 |      43.2 |  13 |
| Estrela   |   3 |     15   |     -10.3 |  22 |
| Estrela   |   6 |     37.5 |     -22.6 |  19 |
| Estrela   |   9 |     67.7 |     -28.4 |  16 |
| Estrela   |  12 |     99.2 |     -27.3 |  13 |
| Muçum     |   3 |     37.8 |     -23.5 |  22 |
| Muçum     |   6 |     87.7 |      42.3 |  19 |
| Muçum     |   9 |    149.1 |      94.6 |  16 |
| Muçum     |  12 |    179   |     149.5 |  13 |

Os candidatos são escolhidos em 2023–2024, confirmados em 2025 e podem ser vetados por regressão em 2026. A comparação completa está em [melhoria e aceitação](12_melhoria_live.md). O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.

Arquivo local da execução: `data/processed/live_runs/emissao_20260929T174038944871Z`. Contém previsões, replay, features, datasets de treino, código e configuração.

## Emissões reais conferidas

| alvo      |   h |   MAE_cm |   n |
|:----------|----:|---------:|----:|
| Encantado |   3 |     41.6 |  17 |
| Encantado |   6 |    128.5 |  14 |
| Encantado |   9 |    168.6 |  13 |
| Encantado |  12 |    194.3 |  13 |
| Estrela   |   3 |     20.7 |  17 |
| Estrela   |   6 |     61.9 |  14 |
| Estrela   |   9 |    111.3 |  13 |
| Estrela   |  12 |    161.8 |  13 |
| Muçum     |   3 |     54.7 |   4 |
| Muçum     |   6 |    139.1 |  14 |
| Muçum     |   9 |    213.4 |  13 |
| Muçum     |  12 |    251.9 |  13 |
