# Revisão da rodada de 29/09/2026 16:00

Modo: **emissao**. Referência observada: 29/09 16:00 (UTC−3). Emissão registrada em 29/09/2026 16:42:56 local. A antecedência real desconta o tempo desde a observação.

Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. A coluna de cota é uma estimativa pontual, não uma cota de pico. Não é sistema de alerta.

| alvo      | motor          |   h | referencia_local   |   observado_cm | previsto_cm   | validade_local   |   antecedencia_real_h | status              |
|:----------|:---------------|----:|:-------------------|---------------:|:--------------|:-----------------|----------------------:|:--------------------|
| Muçum     | linear         |   3 | 29/09 16:00        |           1388 | —             | 29/09 19:00      |                   2.3 | dados_insuficientes |
| Muçum     | gbm_delta      |   6 | 29/09 16:00        |           1388 | 1425.4        | 29/09 22:00      |                   5.3 | estimativa          |
| Muçum     | gbm_delta      |   9 | 29/09 16:00        |           1388 | 1386.0        | 30/09 01:00      |                   8.3 | estimativa          |
| Muçum     | gbm_delta      |  12 | 29/09 16:00        |           1388 | 1376.7        | 30/09 04:00      |                  11.3 | estimativa          |
| Encantado | linear         |   3 | 29/09 16:00        |           1175 | 1281.7        | 29/09 19:00      |                   2.3 | estimativa          |
| Encantado | ridge_montante |   6 | 29/09 16:00        |           1175 | 1337.3        | 29/09 22:00      |                   5.3 | estimativa          |
| Encantado | gbm_delta      |   9 | 29/09 16:00        |           1175 | 1318.2        | 30/09 01:00      |                   8.3 | estimativa          |
| Encantado | gbm_delta      |  12 | 29/09 16:00        |           1175 | 1295.4        | 30/09 04:00      |                  11.3 | estimativa          |
| Estrela   | linear         |   3 | 29/09 16:00        |           2109 | 2171.5        | 29/09 19:00      |                   2.3 | estimativa          |
| Estrela   | linear         |   6 | 29/09 16:00        |           2109 | 2236.0        | 29/09 22:00      |                   5.3 | estimativa          |
| Estrela   | linear         |   9 | 29/09 16:00        |           2109 | 2277.2        | 30/09 01:00      |                   8.3 | estimativa          |
| Estrela   | linear         |  12 | 29/09 16:00        |           2109 | 2293.7        | 30/09 04:00      |                  11.3 | estimativa          |

## Faixas e diagnóstico

As faixas usam o quantil 90% dos erros de 2025, separado por regime, sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, a velocidade está fora da calibração ou a cobertura dos últimos erros conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). Uma faixa ausente não significa erro zero.

| alvo      |   h | inferior_cm   | superior_cm   | faixa_status                   | cobertura_recente_pct   |   n_faixa_recente |
|:----------|----:|:--------------|:--------------|:-------------------------------|:------------------------|------------------:|
| Muçum     |   3 | —             | —             | faltam dados                   | —                       |                 0 |
| Muçum     |   6 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Muçum     |   9 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Muçum     |  12 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Encantado |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Encantado |   6 | —             | —             | erros recentes excedem a faixa | 0.0                     |                 6 |
| Encantado |   9 | —             | —             | erros recentes excedem a faixa | 16.7                    |                 6 |
| Encantado |  12 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Estrela   |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Estrela   |   6 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Estrela   |   9 | 2225.6        | 2328.9        | empírica, sem garantia         | 83.3                    |                 6 |
| Estrela   |  12 | 2220.1        | 2367.4        | empírica, sem garantia         | 100.0                   |                 3 |

![Hidrograma revisado](figs/live_v3_20260929_19.png)

## Replay da subida

Referências a partir de 28/09 16:00; somente alvos já observados. Horizontes maiores têm menos pares. Ausência de linha significa ausência de pares, não erro zero.

| alvo      |   h |   MAE_cm |   vies_cm |   n |
|:----------|----:|---------:|----------:|----:|
| Encantado |   3 |     27.4 |     -14.8 |  22 |
| Encantado |   6 |     70   |     -13.6 |  19 |
| Encantado |   9 |    108.6 |      -4.5 |  16 |
| Encantado |  12 |    134.8 |       2.6 |  13 |
| Estrela   |   3 |     13.6 |      -8.8 |  22 |
| Estrela   |   6 |     32.7 |     -17.8 |  19 |
| Estrela   |   9 |     51.9 |     -12.6 |  16 |
| Estrela   |  12 |     64.5 |       7.4 |  13 |
| Muçum     |   3 |     33.8 |     -19.4 |  22 |
| Muçum     |   6 |     88.8 |      28   |  19 |
| Muçum     |   9 |    166.1 |      47.5 |  16 |
| Muçum     |  12 |    207.9 |      84.8 |  13 |

Os candidatos são escolhidos em 2023–2024, confirmados em 2025 e podem ser vetados por regressão em 2026. A comparação completa está em [melhoria e aceitação](12_melhoria_live.md). O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.

Arquivo local da execução: `data/processed/live_runs/emissao_20260929T194256406464Z`. Contém previsões, replay, features, datasets de treino, código e configuração.

## Emissões reais conferidas

| alvo      |   h |   MAE_cm |   n |
|:----------|----:|---------:|----:|
| Encantado |   3 |     41.4 |  19 |
| Encantado |   6 |    132.9 |  16 |
| Encantado |   9 |    168.6 |  13 |
| Encantado |  12 |    194.3 |  13 |
| Estrela   |   3 |     20.1 |  19 |
| Estrela   |   6 |     60.4 |  16 |
| Estrela   |   9 |    111.3 |  13 |
| Estrela   |  12 |    161.8 |  13 |
| Muçum     |   3 |     54.7 |   4 |
| Muçum     |   6 |    137.7 |  16 |
| Muçum     |   9 |    213.4 |  13 |
| Muçum     |  12 |    251.9 |  13 |
