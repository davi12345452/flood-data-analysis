# Revisão da rodada de 30/09/2026 13:00

Modo: **emissao**. Referência observada: 30/09 13:00 (UTC−3). Emissão registrada em 30/09/2026 13:40:27 local. A antecedência real desconta o tempo desde a observação.

Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. A coluna de cota é uma estimativa pontual, não uma cota de pico. Não é sistema de alerta.

| alvo      | motor          |   h | referencia_local   |   observado_cm | previsto_cm   | validade_local   |   antecedencia_real_h | status              |
|:----------|:---------------|----:|:-------------------|---------------:|:--------------|:-----------------|----------------------:|:--------------------|
| Muçum     | linear         |   3 | 30/09 13:00        |           1227 | —             | 30/09 16:00      |                   2.3 | dados_insuficientes |
| Muçum     | gbm_delta      |   6 | 30/09 13:00        |           1227 | 1091.3        | 30/09 19:00      |                   5.3 | estimativa          |
| Muçum     | gbm_delta      |   9 | 30/09 13:00        |           1227 | 1010.9        | 30/09 22:00      |                   8.3 | estimativa          |
| Muçum     | gbm_delta      |  12 | 30/09 13:00        |           1227 | 957.6         | 01/10 01:00      |                  11.3 | estimativa          |
| Encantado | linear         |   3 | 30/09 13:00        |           1074 | 988.5         | 30/09 16:00      |                   2.3 | estimativa          |
| Encantado | ridge_montante |   6 | 30/09 13:00        |           1074 | 915.3         | 30/09 19:00      |                   5.3 | estimativa          |
| Encantado | gbm_delta      |   9 | 30/09 13:00        |           1074 | 860.5         | 30/09 22:00      |                   8.3 | estimativa          |
| Encantado | gbm_delta      |  12 | 30/09 13:00        |           1074 | 729.4         | 01/10 01:00      |                  11.3 | estimativa          |
| Estrela   | linear         |   3 | 30/09 13:00        |           2263 | 2196.6        | 30/09 16:00      |                   2.3 | estimativa          |
| Estrela   | linear         |   6 | 30/09 13:00        |           2263 | 2120.2        | 30/09 19:00      |                   5.3 | estimativa          |
| Estrela   | linear         |   9 | 30/09 13:00        |           2263 | 2044.4        | 30/09 22:00      |                   8.3 | estimativa          |
| Estrela   | linear         |  12 | 30/09 13:00        |           2263 | 1970.7        | 01/10 01:00      |                  11.3 | estimativa          |

## Faixas e diagnóstico

As faixas usam o quantil 90% dos erros de 2025, separado por regime, sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, a velocidade está fora da calibração ou a cobertura dos últimos erros conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). Uma faixa ausente não significa erro zero.

| alvo      |   h | inferior_cm   | superior_cm   | faixa_status              | cobertura_recente_pct   |   n_faixa_recente |
|:----------|----:|:--------------|:--------------|:--------------------------|:------------------------|------------------:|
| Muçum     |   3 | —             | —             | faltam dados              | —                       |                 0 |
| Muçum     |   6 | 1045.3        | 1137.3        | empírica, sem garantia    | 100.0                   |                 6 |
| Muçum     |   9 | 934.5         | 1087.2        | empírica, sem garantia    | 100.0                   |                 6 |
| Muçum     |  12 | 851.0         | 1064.1        | empírica, sem garantia    | 100.0                   |                 6 |
| Encantado |   3 | —             | —             | sem calibração            | —                       |                 0 |
| Encantado |   6 | —             | —             | subida fora da calibração | 100.0                   |                 6 |
| Encantado |   9 | —             | —             | subida fora da calibração | 66.7                    |                 6 |
| Encantado |  12 | —             | —             | subida fora da calibração | 100.0                   |                 6 |
| Estrela   |   3 | —             | —             | sem calibração            | —                       |                 0 |
| Estrela   |   6 | 2088.0        | 2152.3        | empírica, sem garantia    | 100.0                   |                 6 |
| Estrela   |   9 | 1992.8        | 2096.0        | empírica, sem garantia    | 100.0                   |                 6 |
| Estrela   |  12 | 1897.1        | 2044.4        | empírica, sem garantia    | 100.0                   |                 6 |

![Hidrograma revisado](figs/live_v3_20260930_16.png)

## Replay da subida

Referências a partir de 29/09 13:00; somente alvos já observados. Horizontes maiores têm menos pares. Ausência de linha significa ausência de pares, não erro zero.

| alvo      |   h |   MAE_cm |   vies_cm |   n |
|:----------|----:|---------:|----------:|----:|
| Encantado |   3 |     15.1 |       5.1 |  22 |
| Encantado |   6 |     27.6 |      26.9 |  19 |
| Encantado |   9 |     95   |      71.5 |  16 |
| Encantado |  12 |    123.1 |     107.1 |  13 |
| Estrela   |   3 |      7.8 |      -5.6 |  22 |
| Estrela   |   6 |     18.2 |     -13.9 |  19 |
| Estrela   |   9 |     29.1 |     -19.2 |  16 |
| Estrela   |  12 |     44.6 |     -21.7 |  13 |
| Muçum     |   3 |     15.4 |      10.1 |  22 |
| Muçum     |   6 |     76.6 |      72   |  19 |
| Muçum     |   9 |     91   |      77.5 |  16 |
| Muçum     |  12 |    150.2 |     149.6 |  13 |

Os candidatos são escolhidos em 2023–2024, confirmados em 2025 e podem ser vetados por regressão em 2026. A comparação completa está em [melhoria e aceitação](12_melhoria_live.md). O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.

Arquivo local da execução: `data/processed/live_runs/emissao_20260930T164027192379Z`. Contém previsões, replay, features, datasets de treino, código e configuração.

## Emissões reais conferidas

| alvo      |   h |   MAE_cm |   n |
|:----------|----:|---------:|----:|
| Encantado |   3 |     32.8 |  28 |
| Encantado |   6 |    107.7 |  25 |
| Encantado |   9 |    131   |  24 |
| Encantado |  12 |    169.4 |  24 |
| Estrela   |   3 |     16.7 |  29 |
| Estrela   |   6 |     50.6 |  26 |
| Estrela   |   9 |     99.6 |  24 |
| Estrela   |  12 |    149   |  24 |
| Muçum     |   3 |     47.9 |   5 |
| Muçum     |   6 |    110.5 |  26 |
| Muçum     |   9 |    187.6 |  24 |
| Muçum     |  12 |    228.8 |  24 |
