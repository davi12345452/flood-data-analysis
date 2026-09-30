# Revisão da rodada de 30/09/2026 14:00

Modo: **emissao**. Referência observada: 30/09 14:00 (UTC−3). Emissão registrada em 30/09/2026 14:40:25 local. A antecedência real desconta o tempo desde a observação.

Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. A coluna de cota é uma estimativa pontual, não uma cota de pico. Não é sistema de alerta.

| alvo      | motor          |   h | referencia_local   |   observado_cm | previsto_cm   | validade_local   |   antecedencia_real_h | status              |
|:----------|:---------------|----:|:-------------------|---------------:|:--------------|:-----------------|----------------------:|:--------------------|
| Muçum     | linear         |   3 | 30/09 14:00        |           1196 | —             | 30/09 17:00      |                   2.3 | dados_insuficientes |
| Muçum     | gbm_delta      |   6 | 30/09 14:00        |           1196 | 1069.5        | 30/09 20:00      |                   5.3 | estimativa          |
| Muçum     | gbm_delta      |   9 | 30/09 14:00        |           1196 | 1011.6        | 30/09 23:00      |                   8.3 | estimativa          |
| Muçum     | gbm_delta      |  12 | 30/09 14:00        |           1196 | 946.0         | 01/10 02:00      |                  11.3 | estimativa          |
| Encantado | linear         |   3 | 30/09 14:00        |           1038 | 947.9         | 30/09 17:00      |                   2.3 | estimativa          |
| Encantado | ridge_montante |   6 | 30/09 14:00        |           1038 | 872.0         | 30/09 20:00      |                   5.3 | estimativa          |
| Encantado | gbm_delta      |   9 | 30/09 14:00        |           1038 | 821.0         | 30/09 23:00      |                   8.3 | estimativa          |
| Encantado | gbm_delta      |  12 | 30/09 14:00        |           1038 | 717.3         | 01/10 02:00      |                  11.3 | estimativa          |
| Estrela   | linear         |   3 | 30/09 14:00        |           2249 | 2187.9        | 30/09 17:00      |                   2.3 | estimativa          |
| Estrela   | linear         |   6 | 30/09 14:00        |           2249 | 2109.2        | 30/09 20:00      |                   5.3 | estimativa          |
| Estrela   | linear         |   9 | 30/09 14:00        |           2249 | 2029.6        | 30/09 23:00      |                   8.3 | estimativa          |
| Estrela   | linear         |  12 | 30/09 14:00        |           2249 | 1954.6        | 01/10 02:00      |                  11.3 | estimativa          |

## Faixas e diagnóstico

As faixas usam o quantil 90% dos erros de 2025, separado por regime, sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, a velocidade está fora da calibração ou a cobertura dos últimos erros conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). Uma faixa ausente não significa erro zero.

| alvo      |   h | inferior_cm   | superior_cm   | faixa_status              | cobertura_recente_pct   |   n_faixa_recente |
|:----------|----:|:--------------|:--------------|:--------------------------|:------------------------|------------------:|
| Muçum     |   3 | —             | —             | faltam dados              | —                       |                 0 |
| Muçum     |   6 | 1023.5        | 1115.5        | empírica, sem garantia    | 100.0                   |                 6 |
| Muçum     |   9 | 935.2         | 1087.9        | empírica, sem garantia    | 100.0                   |                 6 |
| Muçum     |  12 | 839.4         | 1052.5        | empírica, sem garantia    | 100.0                   |                 6 |
| Encantado |   3 | —             | —             | sem calibração            | —                       |                 0 |
| Encantado |   6 | —             | —             | subida fora da calibração | 83.3                    |                 6 |
| Encantado |   9 | —             | —             | subida fora da calibração | 66.7                    |                 6 |
| Encantado |  12 | —             | —             | subida fora da calibração | 100.0                   |                 6 |
| Estrela   |   3 | —             | —             | sem calibração            | —                       |                 0 |
| Estrela   |   6 | 2077.1        | 2141.3        | empírica, sem garantia    | 100.0                   |                 6 |
| Estrela   |   9 | 1978.0        | 2081.2        | empírica, sem garantia    | 100.0                   |                 6 |
| Estrela   |  12 | 1880.9        | 2028.2        | empírica, sem garantia    | 100.0                   |                 6 |

![Hidrograma revisado](figs/live_v3_20260930_17.png)

## Replay da subida

Referências a partir de 29/09 14:00; somente alvos já observados. Horizontes maiores têm menos pares. Ausência de linha significa ausência de pares, não erro zero.

| alvo      |   h |   MAE_cm |   vies_cm |   n |
|:----------|----:|---------:|----------:|----:|
| Encantado |   3 |     14.5 |       6.4 |  22 |
| Encantado |   6 |     28.9 |      28.2 |  19 |
| Encantado |   9 |     81.9 |      52.4 |  16 |
| Encantado |  12 |    108.3 |      85.4 |  13 |
| Estrela   |   3 |      7.3 |      -5.1 |  22 |
| Estrela   |   6 |     15.9 |     -11.3 |  19 |
| Estrela   |   9 |     25.1 |     -15.2 |  16 |
| Estrela   |  12 |     35.8 |     -12.9 |  13 |
| Muçum     |   3 |     14.3 |      12.2 |  22 |
| Muçum     |   6 |     61.7 |      55.1 |  19 |
| Muçum     |   9 |     74.9 |      54.6 |  16 |
| Muçum     |  12 |    124.3 |     123.8 |  13 |

Os candidatos são escolhidos em 2023–2024, confirmados em 2025 e podem ser vetados por regressão em 2026. A comparação completa está em [melhoria e aceitação](12_melhoria_live.md). O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.

Arquivo local da execução: `data/processed/live_runs/emissao_20260930T174025939843Z`. Contém previsões, replay, features, datasets de treino, código e configuração.

## Emissões reais conferidas

| alvo      |   h |   MAE_cm |   n |
|:----------|----:|---------:|----:|
| Encantado |   3 |     31.9 |  29 |
| Encantado |   6 |    106.6 |  26 |
| Encantado |   9 |    131   |  24 |
| Encantado |  12 |    169.4 |  24 |
| Estrela   |   3 |     16.2 |  30 |
| Estrela   |   6 |     48.8 |  27 |
| Estrela   |   9 |     99.6 |  24 |
| Estrela   |  12 |    149   |  24 |
| Muçum     |   3 |     47.9 |   5 |
| Muçum     |   6 |    108.5 |  27 |
| Muçum     |   9 |    187.6 |  24 |
| Muçum     |  12 |    228.8 |  24 |
