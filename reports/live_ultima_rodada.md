# Revisão da rodada de 30/09/2026 12:00

Modo: **emissao**. Referência observada: 30/09 12:00 (UTC−3). Emissão registrada em 30/09/2026 12:40:25 local. A antecedência real desconta o tempo desde a observação.

Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. A coluna de cota é uma estimativa pontual, não uma cota de pico. Não é sistema de alerta.

| alvo      | motor          |   h | referencia_local   |   observado_cm | previsto_cm   | validade_local   |   antecedencia_real_h | status              |
|:----------|:---------------|----:|:-------------------|---------------:|:--------------|:-----------------|----------------------:|:--------------------|
| Muçum     | linear         |   3 | 30/09 12:00        |           1258 | —             | 30/09 15:00      |                   2.3 | dados_insuficientes |
| Muçum     | gbm_delta      |   6 | 30/09 12:00        |           1258 | 1122.3        | 30/09 18:00      |                   5.3 | estimativa          |
| Muçum     | gbm_delta      |   9 | 30/09 12:00        |           1258 | 1037.9        | 30/09 21:00      |                   8.3 | estimativa          |
| Muçum     | gbm_delta      |  12 | 30/09 12:00        |           1258 | 970.2         | 01/10 00:00      |                  11.3 | estimativa          |
| Encantado | linear         |   3 | 30/09 12:00        |           1108 | 1023.0        | 30/09 15:00      |                   2.3 | estimativa          |
| Encantado | ridge_montante |   6 | 30/09 12:00        |           1108 | 949.1         | 30/09 18:00      |                   5.3 | estimativa          |
| Encantado | gbm_delta      |   9 | 30/09 12:00        |           1108 | 901.5         | 30/09 21:00      |                   8.3 | estimativa          |
| Encantado | gbm_delta      |  12 | 30/09 12:00        |           1108 | 774.0         | 01/10 00:00      |                  11.3 | estimativa          |
| Estrela   | linear         |   3 | 30/09 12:00        |           2280 | 2217.7        | 30/09 15:00      |                   2.3 | estimativa          |
| Estrela   | linear         |   6 | 30/09 12:00        |           2280 | 2144.9        | 30/09 18:00      |                   5.3 | estimativa          |
| Estrela   | linear         |   9 | 30/09 12:00        |           2280 | 2072.8        | 30/09 21:00      |                   8.3 | estimativa          |
| Estrela   | linear         |  12 | 30/09 12:00        |           2280 | 2001.9        | 01/10 00:00      |                  11.3 | estimativa          |

## Faixas e diagnóstico

As faixas usam o quantil 90% dos erros de 2025, separado por regime, sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, a velocidade está fora da calibração ou a cobertura dos últimos erros conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). Uma faixa ausente não significa erro zero.

| alvo      |   h | inferior_cm   | superior_cm   | faixa_status              | cobertura_recente_pct   |   n_faixa_recente |
|:----------|----:|:--------------|:--------------|:--------------------------|:------------------------|------------------:|
| Muçum     |   3 | —             | —             | faltam dados              | —                       |                 0 |
| Muçum     |   6 | 1076.3        | 1168.3        | empírica, sem garantia    | 100.0                   |                 6 |
| Muçum     |   9 | 961.6         | 1114.3        | empírica, sem garantia    | 100.0                   |                 6 |
| Muçum     |  12 | 863.6         | 1076.7        | empírica, sem garantia    | 100.0                   |                 6 |
| Encantado |   3 | —             | —             | sem calibração            | —                       |                 0 |
| Encantado |   6 | —             | —             | subida fora da calibração | 100.0                   |                 6 |
| Encantado |   9 | —             | —             | subida fora da calibração | 66.7                    |                 6 |
| Encantado |  12 | —             | —             | subida fora da calibração | 100.0                   |                 6 |
| Estrela   |   3 | —             | —             | sem calibração            | —                       |                 0 |
| Estrela   |   6 | 2112.8        | 2177.0        | empírica, sem garantia    | 100.0                   |                 6 |
| Estrela   |   9 | 2021.1        | 2124.4        | empírica, sem garantia    | 100.0                   |                 6 |
| Estrela   |  12 | 1928.3        | 2075.6        | empírica, sem garantia    | 100.0                   |                 6 |

![Hidrograma revisado](figs/live_v3_20260930_15.png)

## Replay da subida

Referências a partir de 29/09 12:00; somente alvos já observados. Horizontes maiores têm menos pares. Ausência de linha significa ausência de pares, não erro zero.

| alvo      |   h |   MAE_cm |   vies_cm |   n |
|:----------|----:|---------:|----------:|----:|
| Encantado |   3 |     17.3 |       1.8 |  22 |
| Encantado |   6 |     28.8 |      23.5 |  19 |
| Encantado |   9 |    107.7 |      88.8 |  16 |
| Encantado |  12 |    135.5 |     122.7 |  13 |
| Estrela   |   3 |      8.2 |      -6   |  22 |
| Estrela   |   6 |     20.5 |     -16.2 |  19 |
| Estrela   |   9 |     36.9 |     -27   |  16 |
| Estrela   |  12 |     56.6 |     -33.7 |  13 |
| Muçum     |   3 |     18   |       6.5 |  22 |
| Muçum     |   6 |     93.6 |      89   |  19 |
| Muçum     |   9 |    111.8 |     100.5 |  16 |
| Muçum     |  12 |    174.9 |     174.3 |  13 |

Os candidatos são escolhidos em 2023–2024, confirmados em 2025 e podem ser vetados por regressão em 2026. A comparação completa está em [melhoria e aceitação](12_melhoria_live.md). O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.

Arquivo local da execução: `data/processed/live_runs/emissao_20260930T154025344516Z`. Contém previsões, replay, features, datasets de treino, código e configuração.

## Emissões reais conferidas

| alvo      |   h |   MAE_cm |   n |
|:----------|----:|---------:|----:|
| Encantado |   3 |     33.6 |  27 |
| Encantado |   6 |    109.8 |  24 |
| Encantado |   9 |    131   |  24 |
| Encantado |  12 |    169.4 |  24 |
| Estrela   |   3 |     17   |  28 |
| Estrela   |   6 |     52.9 |  24 |
| Estrela   |   9 |     99.6 |  24 |
| Estrela   |  12 |    149   |  24 |
| Muçum     |   3 |     47.9 |   5 |
| Muçum     |   6 |    111.8 |  25 |
| Muçum     |   9 |    187.6 |  24 |
| Muçum     |  12 |    228.8 |  24 |
