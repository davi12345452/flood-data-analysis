# Revisão da rodada de 29/09/2026 08:00

Modo: **emissao**. Referência observada: 29/09 08:00 (UTC−3). Emissão registrada em 29/09/2026 08:39:55 local. A antecedência real desconta o tempo desde a observação.

Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. A coluna de cota é uma estimativa pontual, não uma cota de pico. Não é sistema de alerta.

| alvo      | motor          |   h | referencia_local   |   observado_cm | previsto_cm   | validade_local   |   antecedencia_real_h | status              |
|:----------|:---------------|----:|:-------------------|---------------:|:--------------|:-----------------|----------------------:|:--------------------|
| Muçum     | linear         |   3 | 29/09 08:00        |           1134 | —             | 29/09 11:00      |                   2.3 | dados_insuficientes |
| Muçum     | gbm_delta      |   6 | 29/09 08:00        |           1134 | 1141.5        | 29/09 14:00      |                   5.3 | estimativa          |
| Muçum     | gbm_delta      |   9 | 29/09 08:00        |           1134 | 1152.2        | 29/09 17:00      |                   8.3 | estimativa          |
| Muçum     | gbm_delta      |  12 | 29/09 08:00        |           1134 | 1097.1        | 29/09 20:00      |                  11.3 | estimativa          |
| Encantado | linear         |   3 | 29/09 08:00        |            966 | 961.7         | 29/09 11:00      |                   2.3 | estimativa          |
| Encantado | ridge_montante |   6 | 29/09 08:00        |            966 | 950.2         | 29/09 14:00      |                   5.3 | estimativa          |
| Encantado | gbm_delta      |   9 | 29/09 08:00        |            966 | 975.1         | 29/09 17:00      |                   8.3 | estimativa          |
| Encantado | gbm_delta      |  12 | 29/09 08:00        |            966 | 909.5         | 29/09 20:00      |                  11.3 | estimativa          |
| Estrela   | linear         |   3 | 29/09 08:00        |           2036 | 2037.3        | 29/09 11:00      |                   2.3 | estimativa          |
| Estrela   | linear         |   6 | 29/09 08:00        |           2036 | 2030.8        | 29/09 14:00      |                   5.3 | estimativa          |
| Estrela   | linear         |   9 | 29/09 08:00        |           2036 | 2015.3        | 29/09 17:00      |                   8.3 | estimativa          |
| Estrela   | linear         |  12 | 29/09 08:00        |           2036 | 1991.2        | 29/09 20:00      |                  11.3 | estimativa          |

## Faixas e diagnóstico

As faixas usam o quantil 90% dos erros de 2025, separado por regime, sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, a velocidade está fora da calibração ou a cobertura dos últimos erros conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). Uma faixa ausente não significa erro zero.

| alvo      |   h | inferior_cm   | superior_cm   | faixa_status                   | cobertura_recente_pct   |   n_faixa_recente |
|:----------|----:|:--------------|:--------------|:-------------------------------|:------------------------|------------------:|
| Muçum     |   3 | —             | —             | faltam dados                   | —                       |                 0 |
| Muçum     |   6 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Muçum     |   9 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Muçum     |  12 | —             | —             | erros recentes excedem a faixa | 66.7                    |                 6 |
| Encantado |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Encantado |   6 | 918.6         | 981.8         | empírica, sem garantia         | 100.0                   |                 6 |
| Encantado |   9 | 922.7         | 1027.6        | empírica, sem garantia         | 83.3                    |                 6 |
| Encantado |  12 | 836.8         | 982.3         | empírica, sem garantia         | 100.0                   |                 6 |
| Estrela   |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Estrela   |   6 | 1998.7        | 2062.9        | empírica, sem garantia         | 100.0                   |                 1 |
| Estrela   |   9 | 1963.7        | 2066.9        | empírica, sem garantia         | —                       |                 0 |
| Estrela   |  12 | 1917.5        | 2064.8        | empírica, sem garantia         | 0.0                     |                 1 |

![Hidrograma revisado](figs/live_v3_20260929_11.png)

## Replay da subida

Referências a partir de 28/09 08:00; somente alvos já observados. Horizontes maiores têm menos pares. Ausência de linha significa ausência de pares, não erro zero.

| alvo      |   h |   MAE_cm |   vies_cm |   n |
|:----------|----:|---------:|----------:|----:|
| Encantado |   3 |     28.1 |     -15.6 |  22 |
| Encantado |   6 |     78.5 |     -22.1 |  19 |
| Encantado |   9 |    122.8 |     -22.1 |  16 |
| Encantado |  12 |    148.1 |     -61.8 |  13 |
| Estrela   |   3 |     17.1 |     -13.1 |  22 |
| Estrela   |   6 |     52.8 |     -40.5 |  19 |
| Estrela   |   9 |    113.4 |     -89   |  16 |
| Estrela   |  12 |    193.7 |    -170.9 |  13 |
| Muçum     |   3 |     40.7 |     -26.4 |  22 |
| Muçum     |   6 |     99.5 |      29.7 |  19 |
| Muçum     |   9 |    186.1 |      31.3 |  16 |
| Muçum     |  12 |    213.2 |     -22.8 |  13 |

Os candidatos são escolhidos em 2023–2024, confirmados em 2025 e podem ser vetados por regressão em 2026. A comparação completa está em [melhoria e aceitação](12_melhoria_live.md). O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.

Arquivo local da execução: `data/processed/live_runs/emissao_20260929T113955721091Z`. Contém previsões, replay, features, datasets de treino, código e configuração.

## Emissões reais conferidas

| alvo      |   h |   MAE_cm |   n |
|:----------|----:|---------:|----:|
| Encantado |   3 |     39.8 |  13 |
| Encantado |   6 |    127.4 |  13 |
| Encantado |   9 |    168.6 |  13 |
| Encantado |  12 |    194.3 |  13 |
| Estrela   |   3 |     23   |  13 |
| Estrela   |   6 |     63.3 |  13 |
| Estrela   |   9 |    111.3 |  13 |
| Estrela   |  12 |    161.8 |  13 |
| Muçum     |   3 |     54.7 |   4 |
| Muçum     |   6 |    138.6 |  13 |
| Muçum     |   9 |    213.4 |  13 |
| Muçum     |  12 |    251.9 |  13 |
