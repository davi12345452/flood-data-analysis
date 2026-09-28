# Revisão da rodada de 28/09/2026 14:00

Modo: **emissao**. Referência observada: 28/09 14:00 (UTC−3). Emissão registrada em 28/09/2026 14:39:06 local. A antecedência real desconta o tempo desde a observação.

Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. A coluna de cota é uma estimativa pontual, não uma cota de pico. Não é sistema de alerta.

| alvo      | motor          |   h | referencia_local   |   observado_cm | previsto_cm   | validade_local   |   antecedencia_real_h | status              |
|:----------|:---------------|----:|:-------------------|---------------:|:--------------|:-----------------|----------------------:|:--------------------|
| Muçum     | linear         |   3 | 28/09 14:00        |            551 | —             | 28/09 17:00      |                   2.3 | dados_insuficientes |
| Muçum     | gbm_delta      |   6 | 28/09 14:00        |            551 | 810.7         | 28/09 20:00      |                   5.3 | estimativa          |
| Muçum     | gbm_delta      |   9 | 28/09 14:00        |            551 | 850.2         | 28/09 23:00      |                   8.3 | estimativa          |
| Muçum     | gbm_delta      |  12 | 28/09 14:00        |            551 | 860.6         | 29/09 02:00      |                  11.3 | estimativa          |
| Encantado | linear         |   3 | 28/09 14:00        |            459 | 544.2         | 28/09 17:00      |                   2.3 | estimativa          |
| Encantado | ridge_montante |   6 | 28/09 14:00        |            459 | 608.7         | 28/09 20:00      |                   5.3 | estimativa          |
| Encantado | gbm_delta      |   9 | 28/09 14:00        |            459 | 653.7         | 28/09 23:00      |                   8.3 | estimativa          |
| Encantado | gbm_delta      |  12 | 28/09 14:00        |            459 | 717.6         | 29/09 02:00      |                  11.3 | estimativa          |
| Estrela   | linear         |   3 | 28/09 14:00        |           1464 | 1536.7        | 28/09 17:00      |                   2.3 | estimativa          |
| Estrela   | linear         |   6 | 28/09 14:00        |           1464 | 1602.5        | 28/09 20:00      |                   5.3 | estimativa          |
| Estrela   | linear         |   9 | 28/09 14:00        |           1464 | 1656.1        | 28/09 23:00      |                   8.3 | estimativa          |
| Estrela   | linear         |  12 | 28/09 14:00        |           1464 | 1696.0        | 29/09 02:00      |                  11.3 | estimativa          |

## Faixas e diagnóstico

As faixas usam o quantil 90% dos erros de 2025, separado por regime, sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, a velocidade está fora da calibração ou a cobertura dos últimos erros conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). Uma faixa ausente não significa erro zero.

| alvo      |   h | inferior_cm   | superior_cm   | faixa_status                   | cobertura_recente_pct   |   n_faixa_recente |
|:----------|----:|:--------------|:--------------|:-------------------------------|:------------------------|------------------:|
| Muçum     |   3 | —             | —             | faltam dados                   | —                       |                 0 |
| Muçum     |   6 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Muçum     |   9 | —             | —             | erros recentes excedem a faixa | 66.7                    |                 6 |
| Muçum     |  12 | 752.8         | 968.4         | empírica, sem garantia         | 100.0                   |                 6 |
| Encantado |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Encantado |   6 | —             | —             | erros recentes excedem a faixa | 0.0                     |                 6 |
| Encantado |   9 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Encantado |  12 | —             | —             | erros recentes excedem a faixa | 50.0                    |                 6 |
| Estrela   |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Estrela   |   6 | —             | —             | erros recentes excedem a faixa | 0.0                     |                 6 |
| Estrela   |   9 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Estrela   |  12 | —             | —             | erros recentes excedem a faixa | 66.7                    |                 6 |

![Hidrograma revisado](figs/live_v3_20260928_17.png)

## Replay da subida

Referências a partir de 27/09 14:00; somente alvos já observados. Horizontes maiores têm menos pares. Ausência de linha significa ausência de pares, não erro zero.

| alvo      |   h |   MAE_cm |   vies_cm |   n |
|:----------|----:|---------:|----------:|----:|
| Encantado |   3 |     22.9 |     -17.2 |  22 |
| Encantado |   6 |     45.4 |     -43.4 |  19 |
| Encantado |   9 |     71.9 |     -57.1 |  16 |
| Encantado |  12 |     68.5 |     -54.6 |  13 |
| Estrela   |   3 |     11.1 |      -6.1 |  22 |
| Estrela   |   6 |     23.8 |     -18.1 |  19 |
| Estrela   |   9 |     36.5 |     -36.3 |  16 |
| Estrela   |  12 |     52.7 |     -52.7 |  13 |
| Muçum     |   3 |     25.3 |     -16.2 |  22 |
| Muçum     |   6 |     37.5 |     -13.3 |  19 |
| Muçum     |   9 |     67.2 |      -9.3 |  16 |
| Muçum     |  12 |     60.6 |      -2.9 |  13 |

Os candidatos são escolhidos em 2023–2024, confirmados em 2025 e podem ser vetados por regressão em 2026. A comparação completa está em [melhoria e aceitação](12_melhoria_live.md). O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.

Arquivo local da execução: `data/processed/live_runs/emissao_20260928T173906229829Z`. Contém previsões, replay, features, datasets de treino, código e configuração.

## Emissões reais conferidas

| alvo      |   h |   MAE_cm |   n |
|:----------|----:|---------:|----:|
| Encantado |   3 |     33.2 |   4 |
| Encantado |   6 |    137.3 |   2 |
| Encantado |   9 |    258.6 |   2 |
| Encantado |  12 |    313.7 |   2 |
| Estrela   |   3 |     13.1 |   4 |
| Estrela   |   6 |     24.8 |   2 |
| Estrela   |   9 |     28.2 |   2 |
| Estrela   |  12 |     54.8 |   2 |
| Muçum     |   6 |    198.4 |   2 |
| Muçum     |   9 |    250.1 |   2 |
| Muçum     |  12 |    284.4 |   2 |
