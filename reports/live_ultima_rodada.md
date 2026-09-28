# Revisão da rodada de 28/09/2026 15:00

Modo: **emissao**. Referência observada: 28/09 15:00 (UTC−3). Emissão registrada em 28/09/2026 15:38:54 local. A antecedência real desconta o tempo desde a observação.

Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. A coluna de cota é uma estimativa pontual, não uma cota de pico. Não é sistema de alerta.

| alvo      | motor          |   h | referencia_local   |   observado_cm | previsto_cm   | validade_local   |   antecedencia_real_h | status              |
|:----------|:---------------|----:|:-------------------|---------------:|:--------------|:-----------------|----------------------:|:--------------------|
| Muçum     | linear         |   3 | 28/09 15:00        |            624 | —             | 28/09 18:00      |                   2.4 | dados_insuficientes |
| Muçum     | gbm_delta      |   6 | 28/09 15:00        |            624 | 953.1         | 28/09 21:00      |                   5.4 | estimativa          |
| Muçum     | gbm_delta      |   9 | 28/09 15:00        |            624 | 945.5         | 29/09 00:00      |                   8.4 | estimativa          |
| Muçum     | gbm_delta      |  12 | 28/09 15:00        |            624 | 919.8         | 29/09 03:00      |                  11.4 | estimativa          |
| Encantado | linear         |   3 | 28/09 15:00        |            492 | 601.4         | 28/09 18:00      |                   2.4 | estimativa          |
| Encantado | ridge_montante |   6 | 28/09 15:00        |            492 | 681.4         | 28/09 21:00      |                   5.4 | estimativa          |
| Encantado | gbm_delta      |   9 | 28/09 15:00        |            492 | 742.0         | 29/09 00:00      |                   8.4 | estimativa          |
| Encantado | gbm_delta      |  12 | 28/09 15:00        |            492 | 771.1         | 29/09 03:00      |                  11.4 | estimativa          |
| Estrela   | linear         |   3 | 28/09 15:00        |           1495 | 1577.1        | 28/09 18:00      |                   2.4 | estimativa          |
| Estrela   | linear         |   6 | 28/09 15:00        |           1495 | 1644.3        | 28/09 21:00      |                   5.4 | estimativa          |
| Estrela   | linear         |   9 | 28/09 15:00        |           1495 | 1697.4        | 29/09 00:00      |                   8.4 | estimativa          |
| Estrela   | linear         |  12 | 28/09 15:00        |           1495 | 1737.4        | 29/09 03:00      |                  11.4 | estimativa          |

## Faixas e diagnóstico

As faixas usam o quantil 90% dos erros de 2025, separado por regime, sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, a velocidade está fora da calibração ou a cobertura dos últimos erros conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). Uma faixa ausente não significa erro zero.

| alvo      |   h | inferior_cm   | superior_cm   | faixa_status                   | cobertura_recente_pct   |   n_faixa_recente |
|:----------|----:|:--------------|:--------------|:-------------------------------|:------------------------|------------------:|
| Muçum     |   3 | —             | —             | faltam dados                   | —                       |                 0 |
| Muçum     |   6 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Muçum     |   9 | —             | —             | erros recentes excedem a faixa | 50.0                    |                 6 |
| Muçum     |  12 | 732.8         | 1106.7        | empírica, sem garantia         | 83.3                    |                 6 |
| Encantado |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Encantado |   6 | —             | —             | erros recentes excedem a faixa | 0.0                     |                 6 |
| Encantado |   9 | —             | —             | erros recentes excedem a faixa | 0.0                     |                 6 |
| Encantado |  12 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Estrela   |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Estrela   |   6 | —             | —             | subida fora da calibração      | 0.0                     |                 6 |
| Estrela   |   9 | —             | —             | subida fora da calibração      | 16.7                    |                 6 |
| Estrela   |  12 | —             | —             | subida fora da calibração      | 50.0                    |                 6 |

![Hidrograma revisado](figs/live_v3_20260928_18.png)

## Replay da subida

Referências a partir de 27/09 15:00; somente alvos já observados. Horizontes maiores têm menos pares. Ausência de linha significa ausência de pares, não erro zero.

| alvo      |   h |   MAE_cm |   vies_cm |   n |
|:----------|----:|---------:|----------:|----:|
| Encantado |   3 |     24.5 |     -18.8 |  22 |
| Encantado |   6 |     53   |     -51.9 |  19 |
| Encantado |   9 |     81.5 |     -66.6 |  16 |
| Encantado |  12 |     79.3 |     -65.4 |  13 |
| Estrela   |   3 |     11.6 |      -6.6 |  22 |
| Estrela   |   6 |     26.2 |     -20.5 |  19 |
| Estrela   |   9 |     42.4 |     -42.2 |  16 |
| Estrela   |  12 |     66.9 |     -66.9 |  13 |
| Muçum     |   3 |     28.2 |     -20.7 |  22 |
| Muçum     |   6 |     44   |     -21.8 |  19 |
| Muçum     |   9 |     74   |     -16.1 |  16 |
| Muçum     |  12 |     63.3 |      -5.5 |  13 |

Os candidatos são escolhidos em 2023–2024, confirmados em 2025 e podem ser vetados por regressão em 2026. A comparação completa está em [melhoria e aceitação](12_melhoria_live.md). O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.

Arquivo local da execução: `data/processed/live_runs/emissao_20260928T183854733788Z`. Contém previsões, replay, features, datasets de treino, código e configuração.

## Emissões reais conferidas

| alvo      |   h |   MAE_cm |   n |
|:----------|----:|---------:|----:|
| Encantado |   3 |     33.2 |   4 |
| Encantado |   6 |    117   |   4 |
| Encantado |   9 |    258.6 |   2 |
| Encantado |  12 |    313.7 |   2 |
| Estrela   |   3 |     13.1 |   4 |
| Estrela   |   6 |     39.2 |   4 |
| Estrela   |   9 |     28.2 |   2 |
| Estrela   |  12 |     54.8 |   2 |
| Muçum     |   6 |    155.2 |   4 |
| Muçum     |   9 |    250.1 |   2 |
| Muçum     |  12 |    284.4 |   2 |
