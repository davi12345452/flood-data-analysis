# Revisão da rodada de 28/09/2026 18:00

Modo: **emissao**. Referência observada: 28/09 18:00 (UTC−3). Emissão registrada em 28/09/2026 19:04:15 local. A antecedência real desconta o tempo desde a observação.

Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. A coluna de cota é uma estimativa pontual, não uma cota de pico. Não é sistema de alerta.

| alvo      | motor          |   h | referencia_local   |   observado_cm |   previsto_cm | validade_local   |   antecedencia_real_h | status     |
|:----------|:---------------|----:|:-------------------|---------------:|--------------:|:-----------------|----------------------:|:-----------|
| Muçum     | linear         |   3 | 28/09 18:00        |            859 |        1072.9 | 28/09 21:00      |                   1.9 | estimativa |
| Muçum     | gbm_delta      |   6 | 28/09 18:00        |            859 |        1249   | 29/09 00:00      |                   4.9 | estimativa |
| Muçum     | gbm_delta      |   9 | 28/09 18:00        |            859 |        1317.2 | 29/09 03:00      |                   7.9 | estimativa |
| Muçum     | gbm_delta      |  12 | 28/09 18:00        |            859 |        1215   | 29/09 06:00      |                  10.9 | estimativa |
| Encantado | linear         |   3 | 28/09 18:00        |            657 |         811.9 | 28/09 21:00      |                   1.9 | estimativa |
| Encantado | ridge_montante |   6 | 28/09 18:00        |            657 |        1056.8 | 29/09 00:00      |                   4.9 | estimativa |
| Encantado | gbm_delta      |   9 | 28/09 18:00        |            657 |         933.9 | 29/09 03:00      |                   7.9 | estimativa |
| Encantado | gbm_delta      |  12 | 28/09 18:00        |            657 |         939.5 | 29/09 06:00      |                  10.9 | estimativa |
| Estrela   | linear         |   3 | 28/09 18:00        |           1614 |        1750.6 | 28/09 21:00      |                   1.9 | estimativa |
| Estrela   | linear         |   6 | 28/09 18:00        |           1614 |        1861.6 | 29/09 00:00      |                   4.9 | estimativa |
| Estrela   | linear         |   9 | 28/09 18:00        |           1614 |        1950.5 | 29/09 03:00      |                   7.9 | estimativa |
| Estrela   | linear         |  12 | 28/09 18:00        |           1614 |        2018.1 | 29/09 06:00      |                  10.9 | estimativa |

## Faixas e diagnóstico

As faixas usam o quantil 90% dos erros de 2025, separado por regime, sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, a velocidade está fora da calibração ou a cobertura dos últimos erros conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). Uma faixa ausente não significa erro zero.

| alvo      |   h | inferior_cm   | superior_cm   | faixa_status                   | cobertura_recente_pct   |   n_faixa_recente |
|:----------|----:|:--------------|:--------------|:-------------------------------|:------------------------|------------------:|
| Muçum     |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Muçum     |   6 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Muçum     |   9 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Muçum     |  12 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Encantado |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Encantado |   6 | —             | —             | erros recentes excedem a faixa | 0.0                     |                 6 |
| Encantado |   9 | —             | —             | erros recentes excedem a faixa | 0.0                     |                 6 |
| Encantado |  12 | —             | —             | erros recentes excedem a faixa | 0.0                     |                 6 |
| Estrela   |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Estrela   |   6 | —             | —             | poucos exemplos neste regime   | 0.0                     |                 6 |
| Estrela   |   9 | —             | —             | poucos exemplos neste regime   | 0.0                     |                 6 |
| Estrela   |  12 | —             | —             | poucos exemplos neste regime   | 16.7                    |                 6 |

![Hidrograma revisado](figs/live_v3_20260928_21.png)

## Replay da subida

Referências a partir de 27/09 18:00; somente alvos já observados. Horizontes maiores têm menos pares. Ausência de linha significa ausência de pares, não erro zero.

| alvo      |   h |   MAE_cm |   vies_cm |   n |
|:----------|----:|---------:|----------:|----:|
| Encantado |   3 |     29.7 |     -24.1 |  22 |
| Encantado |   6 |     75.5 |     -75.5 |  19 |
| Encantado |   9 |    106.9 |     -94.1 |  16 |
| Encantado |  12 |    130.1 |    -114.9 |  13 |
| Estrela   |   3 |     14.6 |      -9.6 |  22 |
| Estrela   |   6 |     35.4 |     -29.7 |  19 |
| Estrela   |   9 |     64   |     -63.8 |  16 |
| Estrela   |  12 |    106.9 |    -106.9 |  13 |
| Muçum     |   3 |     40.2 |     -33.2 |  22 |
| Muçum     |   6 |     57.7 |     -33.8 |  19 |
| Muçum     |   9 |     98.1 |     -39.9 |  16 |
| Muçum     |  12 |    124.9 |     -51.1 |  13 |

Os candidatos são escolhidos em 2023–2024, confirmados em 2025 e podem ser vetados por regressão em 2026. A comparação completa está em [melhoria e aceitação](12_melhoria_live.md). O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.

Arquivo local da execução: `data/processed/live_runs/emissao_20260928T220415049278Z`. Contém previsões, replay, features, datasets de treino, código e configuração.

## Emissões reais conferidas

| alvo      |   h |   MAE_cm |   n |
|:----------|----:|---------:|----:|
| Encantado |   3 |     40.6 |   8 |
| Encantado |   6 |    117   |   4 |
| Encantado |   9 |    227.6 |   4 |
| Encantado |  12 |    313.7 |   2 |
| Estrela   |   3 |     18.8 |   8 |
| Estrela   |   6 |     39.2 |   4 |
| Estrela   |   9 |     81   |   4 |
| Estrela   |  12 |     54.8 |   2 |
| Muçum     |   3 |    109.2 |   1 |
| Muçum     |   6 |    155.2 |   4 |
| Muçum     |   9 |    276.7 |   4 |
| Muçum     |  12 |    284.4 |   2 |
