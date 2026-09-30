# Revisão da rodada de 30/09/2026 15:00

Modo: **emissao**. Referência observada: 30/09 15:00 (UTC−3). Emissão registrada em 30/09/2026 15:40:27 local. A antecedência real desconta o tempo desde a observação.

Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. A coluna de cota é uma estimativa pontual, não uma cota de pico. Não é sistema de alerta.

| alvo      | motor          |   h | referencia_local   |   observado_cm | previsto_cm   | validade_local   |   antecedencia_real_h | status              |
|:----------|:---------------|----:|:-------------------|---------------:|:--------------|:-----------------|----------------------:|:--------------------|
| Muçum     | linear         |   3 | 30/09 15:00        |           1163 | —             | 30/09 18:00      |                   2.3 | dados_insuficientes |
| Muçum     | gbm_delta      |   6 | 30/09 15:00        |           1163 | 1039.5        | 30/09 21:00      |                   5.3 | estimativa          |
| Muçum     | gbm_delta      |   9 | 30/09 15:00        |           1163 | 989.8         | 01/10 00:00      |                   8.3 | estimativa          |
| Muçum     | gbm_delta      |  12 | 30/09 15:00        |           1163 | 924.0         | 01/10 03:00      |                  11.3 | estimativa          |
| Encantado | linear         |   3 | 30/09 15:00        |           1004 | 917.9         | 30/09 18:00      |                   2.3 | estimativa          |
| Encantado | ridge_montante |   6 | 30/09 15:00        |           1004 | 842.9         | 30/09 21:00      |                   5.3 | estimativa          |
| Encantado | gbm_delta      |   9 | 30/09 15:00        |           1004 | 802.2         | 01/10 00:00      |                   8.3 | estimativa          |
| Encantado | gbm_delta      |  12 | 30/09 15:00        |           1004 | 702.1         | 01/10 03:00      |                  11.3 | estimativa          |
| Estrela   | linear         |   3 | 30/09 15:00        |           2228 | 2154.2        | 30/09 18:00      |                   2.3 | estimativa          |
| Estrela   | linear         |   6 | 30/09 15:00        |           2228 | 2074.8        | 30/09 21:00      |                   5.3 | estimativa          |
| Estrela   | linear         |   9 | 30/09 15:00        |           2228 | 1996.9        | 01/10 00:00      |                   8.3 | estimativa          |
| Estrela   | linear         |  12 | 30/09 15:00        |           2228 | 1921.5        | 01/10 03:00      |                  11.3 | estimativa          |

## Faixas e diagnóstico

As faixas usam o quantil 90% dos erros de 2025, separado por regime, sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, a velocidade está fora da calibração ou a cobertura dos últimos erros conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). Uma faixa ausente não significa erro zero.

| alvo      |   h | inferior_cm   | superior_cm   | faixa_status              | cobertura_recente_pct   |   n_faixa_recente |
|:----------|----:|:--------------|:--------------|:--------------------------|:------------------------|------------------:|
| Muçum     |   3 | —             | —             | faltam dados              | —                       |                 0 |
| Muçum     |   6 | 993.6         | 1085.5        | empírica, sem garantia    | 100.0                   |                 6 |
| Muçum     |   9 | 913.4         | 1066.1        | empírica, sem garantia    | 100.0                   |                 6 |
| Muçum     |  12 | 817.5         | 1030.6        | empírica, sem garantia    | 100.0                   |                 6 |
| Encantado |   3 | —             | —             | sem calibração            | —                       |                 0 |
| Encantado |   6 | —             | —             | subida fora da calibração | 66.7                    |                 6 |
| Encantado |   9 | —             | —             | subida fora da calibração | 66.7                    |                 6 |
| Encantado |  12 | —             | —             | subida fora da calibração | 100.0                   |                 6 |
| Estrela   |   3 | —             | —             | sem calibração            | —                       |                 0 |
| Estrela   |   6 | 2042.7        | 2106.9        | empírica, sem garantia    | 100.0                   |                 6 |
| Estrela   |   9 | 1945.3        | 2048.5        | empírica, sem garantia    | 100.0                   |                 6 |
| Estrela   |  12 | 1847.8        | 1995.1        | empírica, sem garantia    | 100.0                   |                 6 |

![Hidrograma revisado](figs/live_v3_20260930_18.png)

## Replay da subida

Referências a partir de 29/09 15:00; somente alvos já observados. Horizontes maiores têm menos pares. Ausência de linha significa ausência de pares, não erro zero.

| alvo      |   h |   MAE_cm |   vies_cm |   n |
|:----------|----:|---------:|----------:|----:|
| Encantado |   3 |     14.9 |       7.7 |  22 |
| Encantado |   6 |     30.4 |      29.7 |  19 |
| Encantado |   9 |     72.2 |      40.2 |  16 |
| Encantado |  12 |     99   |      65.3 |  13 |
| Estrela   |   3 |      6.7 |      -4.6 |  22 |
| Estrela   |   6 |     13.8 |      -8.8 |  19 |
| Estrela   |   9 |     20.8 |     -10.6 |  16 |
| Estrela   |  12 |     29.4 |      -6.6 |  13 |
| Muçum     |   3 |     13.7 |      13.6 |  22 |
| Muçum     |   6 |     53.5 |      45.5 |  19 |
| Muçum     |   9 |     65.5 |      45.2 |  16 |
| Muçum     |  12 |    108.6 |     100   |  13 |

Os candidatos são escolhidos em 2023–2024, confirmados em 2025 e podem ser vetados por regressão em 2026. A comparação completa está em [melhoria e aceitação](12_melhoria_live.md). O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.

Arquivo local da execução: `data/processed/live_runs/emissao_20260930T184027732594Z`. Contém previsões, replay, features, datasets de treino, código e configuração.

## Emissões reais conferidas

| alvo      |   h |   MAE_cm |   n |
|:----------|----:|---------:|----:|
| Encantado |   3 |     31.5 |  30 |
| Encantado |   6 |    105.3 |  27 |
| Encantado |   9 |    131   |  24 |
| Encantado |  12 |    169.4 |  24 |
| Estrela   |   3 |     16   |  31 |
| Estrela   |   6 |     47.2 |  28 |
| Estrela   |   9 |     99.6 |  24 |
| Estrela   |  12 |    149   |  24 |
| Muçum     |   3 |     47.9 |   5 |
| Muçum     |   6 |    106.7 |  28 |
| Muçum     |   9 |    180.2 |  25 |
| Muçum     |  12 |    228.8 |  24 |
