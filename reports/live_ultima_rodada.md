# Revisão da rodada de 28/09/2026 19:00

Modo: **emissao**. Referência observada: 28/09 19:00 (UTC−3). Emissão registrada em 28/09/2026 20:15:57 local. A antecedência real desconta o tempo desde a observação.

Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. A coluna de cota é uma estimativa pontual, não uma cota de pico. Não é sistema de alerta.

| alvo      | motor          |   h | referencia_local   |   observado_cm |   previsto_cm | validade_local   |   antecedencia_real_h | status     |
|:----------|:---------------|----:|:-------------------|---------------:|--------------:|:-----------------|----------------------:|:-----------|
| Muçum     | linear         |   3 | 28/09 19:00        |            944 |        1131.6 | 28/09 22:00      |                   1.7 | estimativa |
| Muçum     | gbm_delta      |   6 | 28/09 19:00        |            944 |        1227.7 | 29/09 01:00      |                   4.7 | estimativa |
| Muçum     | gbm_delta      |   9 | 28/09 19:00        |            944 |        1299.1 | 29/09 04:00      |                   7.7 | estimativa |
| Muçum     | gbm_delta      |  12 | 28/09 19:00        |            944 |        1414.4 | 29/09 07:00      |                  10.7 | estimativa |
| Encantado | linear         |   3 | 28/09 19:00        |            725 |         903.9 | 28/09 22:00      |                   1.7 | estimativa |
| Encantado | ridge_montante |   6 | 28/09 19:00        |            725 |        1046.1 | 29/09 01:00      |                   4.7 | estimativa |
| Encantado | gbm_delta      |   9 | 28/09 19:00        |            725 |        1044.2 | 29/09 04:00      |                   7.7 | estimativa |
| Encantado | gbm_delta      |  12 | 28/09 19:00        |            725 |        1092.6 | 29/09 07:00      |                  10.7 | estimativa |
| Estrela   | linear         |   3 | 28/09 19:00        |           1660 |        1789.6 | 28/09 22:00      |                   1.7 | estimativa |
| Estrela   | linear         |   6 | 28/09 19:00        |           1660 |        1915.5 | 29/09 01:00      |                   4.7 | estimativa |
| Estrela   | linear         |   9 | 28/09 19:00        |           1660 |        2020.4 | 29/09 04:00      |                   7.7 | estimativa |
| Estrela   | linear         |  12 | 28/09 19:00        |           1660 |        2095.3 | 29/09 07:00      |                  10.7 | estimativa |

## Faixas e diagnóstico

As faixas usam o quantil 90% dos erros de 2025, separado por regime, sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, a velocidade está fora da calibração ou a cobertura dos últimos erros conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). Uma faixa ausente não significa erro zero.

| alvo      |   h | inferior_cm   | superior_cm   | faixa_status                   | cobertura_recente_pct   |   n_faixa_recente |
|:----------|----:|:--------------|:--------------|:-------------------------------|:------------------------|------------------:|
| Muçum     |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Muçum     |   6 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Muçum     |   9 | —             | —             | erros recentes excedem a faixa | 0.0                     |                 6 |
| Muçum     |  12 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Encantado |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Encantado |   6 | —             | —             | erros recentes excedem a faixa | 0.0                     |                 6 |
| Encantado |   9 | —             | —             | erros recentes excedem a faixa | 0.0                     |                 6 |
| Encantado |  12 | —             | —             | erros recentes excedem a faixa | 0.0                     |                 6 |
| Estrela   |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Estrela   |   6 | —             | —             | poucos exemplos neste regime   | 0.0                     |                 6 |
| Estrela   |   9 | —             | —             | poucos exemplos neste regime   | 0.0                     |                 6 |
| Estrela   |  12 | —             | —             | poucos exemplos neste regime   | 0.0                     |                 6 |

![Hidrograma revisado](figs/live_v3_20260928_22.png)

## Replay da subida

Referências a partir de 27/09 19:00; somente alvos já observados. Horizontes maiores têm menos pares. Ausência de linha significa ausência de pares, não erro zero.

| alvo      |   h |   MAE_cm |   vies_cm |   n |
|:----------|----:|---------:|----------:|----:|
| Encantado |   3 |     30.6 |     -24.9 |  22 |
| Encantado |   6 |     79.4 |     -79.4 |  19 |
| Encantado |   9 |    119.6 |    -106.8 |  16 |
| Encantado |  12 |    147.4 |    -132.1 |  13 |
| Estrela   |   3 |     17.1 |     -12.6 |  22 |
| Estrela   |   6 |     39.8 |     -35   |  19 |
| Estrela   |   9 |     72   |     -72   |  16 |
| Estrela   |  12 |    119.6 |    -119.6 |  13 |
| Muçum     |   3 |     42.3 |     -35.3 |  22 |
| Muçum     |   6 |     59.7 |     -35.9 |  19 |
| Muçum     |   9 |    115.7 |     -61.4 |  16 |
| Muçum     |  12 |    148.2 |     -82.6 |  13 |

Os candidatos são escolhidos em 2023–2024, confirmados em 2025 e podem ser vetados por regressão em 2026. A comparação completa está em [melhoria e aceitação](12_melhoria_live.md). O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.

Arquivo local da execução: `data/processed/live_runs/emissao_20260928T231557021726Z`. Contém previsões, replay, features, datasets de treino, código e configuração.

## Emissões reais conferidas

| alvo      |   h |   MAE_cm |   n |
|:----------|----:|---------:|----:|
| Encantado |   3 |     40.2 |   9 |
| Encantado |   6 |    122   |   6 |
| Encantado |   9 |    227.6 |   4 |
| Encantado |  12 |    313.7 |   2 |
| Estrela   |   3 |     23.5 |   9 |
| Estrela   |   6 |     57   |   6 |
| Estrela   |   9 |     81   |   4 |
| Estrela   |  12 |     54.8 |   2 |
| Muçum     |   3 |    109.2 |   1 |
| Muçum     |   6 |    166.5 |   6 |
| Muçum     |   9 |    276.7 |   4 |
| Muçum     |  12 |    284.4 |   2 |
