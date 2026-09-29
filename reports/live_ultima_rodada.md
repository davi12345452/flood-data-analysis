# Revisão da rodada de 29/09/2026 17:00

Modo: **emissao**. Referência observada: 29/09 17:00 (UTC−3). Emissão registrada em 29/09/2026 17:40:34 local. A antecedência real desconta o tempo desde a observação.

Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. A coluna de cota é uma estimativa pontual, não uma cota de pico. Não é sistema de alerta.

| alvo      | motor          |   h | referencia_local   |   observado_cm | previsto_cm   | validade_local   |   antecedencia_real_h | status              |
|:----------|:---------------|----:|:-------------------|---------------:|:--------------|:-----------------|----------------------:|:--------------------|
| Muçum     | linear         |   3 | 29/09 17:00        |           1426 | —             | 29/09 20:00      |                   2.3 | dados_insuficientes |
| Muçum     | gbm_delta      |   6 | 29/09 17:00        |           1426 | 1463.4        | 29/09 23:00      |                   5.3 | estimativa          |
| Muçum     | gbm_delta      |   9 | 29/09 17:00        |           1426 | 1413.5        | 30/09 02:00      |                   8.3 | estimativa          |
| Muçum     | gbm_delta      |  12 | 29/09 17:00        |           1426 | 1385.2        | 30/09 05:00      |                  11.3 | estimativa          |
| Encantado | linear         |   3 | 29/09 17:00        |           1215 | 1301.4        | 29/09 20:00      |                   2.3 | estimativa          |
| Encantado | ridge_montante |   6 | 29/09 17:00        |           1215 | 1342.4        | 29/09 23:00      |                   5.3 | estimativa          |
| Encantado | gbm_delta      |   9 | 29/09 17:00        |           1215 | 1277.4        | 30/09 02:00      |                   8.3 | estimativa          |
| Encantado | gbm_delta      |  12 | 29/09 17:00        |           1215 | 1225.3        | 30/09 05:00      |                  11.3 | estimativa          |
| Estrela   | linear         |   3 | 29/09 17:00        |           2134 | 2207.8        | 29/09 20:00      |                   2.3 | estimativa          |
| Estrela   | linear         |   6 | 29/09 17:00        |           2134 | 2269.7        | 29/09 23:00      |                   5.3 | estimativa          |
| Estrela   | linear         |   9 | 29/09 17:00        |           2134 | 2306.2        | 30/09 02:00      |                   8.3 | estimativa          |
| Estrela   | linear         |  12 | 29/09 17:00        |           2134 | 2320.3        | 30/09 05:00      |                  11.3 | estimativa          |

## Faixas e diagnóstico

As faixas usam o quantil 90% dos erros de 2025, separado por regime, sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, a velocidade está fora da calibração ou a cobertura dos últimos erros conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). Uma faixa ausente não significa erro zero.

| alvo      |   h | inferior_cm   | superior_cm   | faixa_status                   | cobertura_recente_pct   |   n_faixa_recente |
|:----------|----:|:--------------|:--------------|:-------------------------------|:------------------------|------------------:|
| Muçum     |   3 | —             | —             | faltam dados                   | —                       |                 0 |
| Muçum     |   6 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Muçum     |   9 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Muçum     |  12 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Encantado |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Encantado |   6 | —             | —             | erros recentes excedem a faixa | 0.0                     |                 6 |
| Encantado |   9 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Encantado |  12 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Estrela   |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Estrela   |   6 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Estrela   |   9 | —             | —             | erros recentes excedem a faixa | 66.7                    |                 6 |
| Estrela   |  12 | —             | —             | erros recentes excedem a faixa | 75.0                    |                 4 |

![Hidrograma revisado](figs/live_v3_20260929_20.png)

## Replay da subida

Referências a partir de 28/09 17:00; somente alvos já observados. Horizontes maiores têm menos pares. Ausência de linha significa ausência de pares, não erro zero.

| alvo      |   h |   MAE_cm |   vies_cm |   n |
|:----------|----:|---------:|----------:|----:|
| Encantado |   3 |     26.2 |     -13.6 |  22 |
| Encantado |   6 |     74.8 |     -21   |  19 |
| Encantado |   9 |    114.4 |     -27   |  16 |
| Encantado |  12 |    155.1 |     -35.5 |  13 |
| Estrela   |   3 |     11.9 |      -7.1 |  22 |
| Estrela   |   6 |     30.3 |     -15.4 |  19 |
| Estrela   |   9 |     48.1 |      -8.8 |  16 |
| Estrela   |  12 |     58.1 |      13.8 |  13 |
| Muçum     |   3 |     32   |     -17.7 |  22 |
| Muçum     |   6 |     84.4 |      23.6 |  19 |
| Muçum     |   9 |    166.1 |      18.3 |  16 |
| Muçum     |  12 |    226.7 |      37.3 |  13 |

Os candidatos são escolhidos em 2023–2024, confirmados em 2025 e podem ser vetados por regressão em 2026. A comparação completa está em [melhoria e aceitação](12_melhoria_live.md). O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.

Arquivo local da execução: `data/processed/live_runs/emissao_20260929T204034808110Z`. Contém previsões, replay, features, datasets de treino, código e configuração.

## Emissões reais conferidas

| alvo      |   h |   MAE_cm |   n |
|:----------|----:|---------:|----:|
| Encantado |   3 |     39.9 |  20 |
| Encantado |   6 |    136.2 |  17 |
| Encantado |   9 |    173.6 |  14 |
| Encantado |  12 |    194.3 |  13 |
| Estrela   |   3 |     20.3 |  20 |
| Estrela   |   6 |     61.1 |  17 |
| Estrela   |   9 |    111.8 |  14 |
| Estrela   |  12 |    161.8 |  13 |
| Muçum     |   3 |     54.7 |   4 |
| Muçum     |   6 |    135.5 |  17 |
| Muçum     |   9 |    217.7 |  14 |
| Muçum     |  12 |    251.9 |  13 |
