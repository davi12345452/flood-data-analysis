# Revisão da rodada de 29/09/2026 15:00

Modo: **emissao**. Referência observada: 29/09 15:00 (UTC−3). Emissão registrada em 29/09/2026 15:40:50 local. A antecedência real desconta o tempo desde a observação.

Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. A coluna de cota é uma estimativa pontual, não uma cota de pico. Não é sistema de alerta.

| alvo      | motor          |   h | referencia_local   |   observado_cm | previsto_cm   | validade_local   |   antecedencia_real_h | status              |
|:----------|:---------------|----:|:-------------------|---------------:|:--------------|:-----------------|----------------------:|:--------------------|
| Muçum     | linear         |   3 | 29/09 15:00        |           1342 | —             | 29/09 18:00      |                   2.3 | dados_insuficientes |
| Muçum     | gbm_delta      |   6 | 29/09 15:00        |           1342 | 1626.9        | 29/09 21:00      |                   5.3 | estimativa          |
| Muçum     | gbm_delta      |   9 | 29/09 15:00        |           1342 | 1640.3        | 30/09 00:00      |                   8.3 | estimativa          |
| Muçum     | gbm_delta      |  12 | 29/09 15:00        |           1342 | 1484.1        | 30/09 03:00      |                  11.3 | estimativa          |
| Encantado | linear         |   3 | 29/09 15:00        |           1129 | 1221.4        | 29/09 18:00      |                   2.3 | estimativa          |
| Encantado | ridge_montante |   6 | 29/09 15:00        |           1129 | 1270.8        | 29/09 21:00      |                   5.3 | estimativa          |
| Encantado | gbm_delta      |   9 | 29/09 15:00        |           1129 | 1352.1        | 30/09 00:00      |                   8.3 | estimativa          |
| Encantado | gbm_delta      |  12 | 29/09 15:00        |           1129 | 1310.6        | 30/09 03:00      |                  11.3 | estimativa          |
| Estrela   | linear         |   3 | 29/09 15:00        |           2091 | 2150.6        | 29/09 18:00      |                   2.3 | estimativa          |
| Estrela   | linear         |   6 | 29/09 15:00        |           2091 | 2201.6        | 29/09 21:00      |                   5.3 | estimativa          |
| Estrela   | linear         |   9 | 29/09 15:00        |           2091 | 2226.0        | 30/09 00:00      |                   8.3 | estimativa          |
| Estrela   | linear         |  12 | 29/09 15:00        |           2091 | 2230.6        | 30/09 03:00      |                  11.3 | estimativa          |

## Faixas e diagnóstico

As faixas usam o quantil 90% dos erros de 2025, separado por regime, sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, a velocidade está fora da calibração ou a cobertura dos últimos erros conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). Uma faixa ausente não significa erro zero.

| alvo      |   h | inferior_cm   | superior_cm   | faixa_status                   | cobertura_recente_pct   |   n_faixa_recente |
|:----------|----:|:--------------|:--------------|:-------------------------------|:------------------------|------------------:|
| Muçum     |   3 | —             | —             | faltam dados                   | —                       |                 0 |
| Muçum     |   6 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Muçum     |   9 | —             | —             | erros recentes excedem a faixa | 50.0                    |                 6 |
| Muçum     |  12 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Encantado |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Encantado |   6 | —             | —             | erros recentes excedem a faixa | 0.0                     |                 6 |
| Encantado |   9 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Encantado |  12 | —             | —             | erros recentes excedem a faixa | 50.0                    |                 6 |
| Estrela   |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Estrela   |   6 | —             | —             | erros recentes excedem a faixa | 50.0                    |                 6 |
| Estrela   |   9 | 2174.4        | 2277.6        | empírica, sem garantia         | 100.0                   |                 5 |
| Estrela   |  12 | 2156.9        | 2304.2        | empírica, sem garantia         | 100.0                   |                 2 |

![Hidrograma revisado](figs/live_v3_20260929_18.png)

## Replay da subida

Referências a partir de 28/09 15:00; somente alvos já observados. Horizontes maiores têm menos pares. Ausência de linha significa ausência de pares, não erro zero.

| alvo      |   h |   MAE_cm |   vies_cm |   n |
|:----------|----:|---------:|----------:|----:|
| Encantado |   3 |     29   |     -16.4 |  22 |
| Encantado |   6 |     64.1 |      -7.8 |  19 |
| Encantado |   9 |     96.4 |      14.6 |  16 |
| Encantado |  12 |    109.9 |      27.8 |  13 |
| Estrela   |   3 |     14.6 |      -9.9 |  22 |
| Estrela   |   6 |     35.5 |     -20.6 |  19 |
| Estrela   |   9 |     58.6 |     -19.3 |  16 |
| Estrela   |  12 |     79.3 |      -7.4 |  13 |
| Muçum     |   3 |     35.7 |     -21.3 |  22 |
| Muçum     |   6 |     94.4 |      33.7 |  19 |
| Muçum     |   9 |    160.3 |      77.7 |  16 |
| Muçum     |  12 |    192.7 |     123.1 |  13 |

Os candidatos são escolhidos em 2023–2024, confirmados em 2025 e podem ser vetados por regressão em 2026. A comparação completa está em [melhoria e aceitação](12_melhoria_live.md). O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.

Arquivo local da execução: `data/processed/live_runs/emissao_20260929T184050394043Z`. Contém previsões, replay, features, datasets de treino, código e configuração.

## Emissões reais conferidas

| alvo      |   h |   MAE_cm |   n |
|:----------|----:|---------:|----:|
| Encantado |   3 |     42.6 |  18 |
| Encantado |   6 |    130.7 |  15 |
| Encantado |   9 |    168.6 |  13 |
| Encantado |  12 |    194.3 |  13 |
| Estrela   |   3 |     20.5 |  18 |
| Estrela   |   6 |     61.3 |  15 |
| Estrela   |   9 |    111.3 |  13 |
| Estrela   |  12 |    161.8 |  13 |
| Muçum     |   3 |     54.7 |   4 |
| Muçum     |   6 |    139.1 |  15 |
| Muçum     |   9 |    213.4 |  13 |
| Muçum     |  12 |    251.9 |  13 |
