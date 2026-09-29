# Revisão da rodada de 29/09/2026 10:00

Modo: **emissao**. Referência observada: 29/09 10:00 (UTC−3). Emissão registrada em 29/09/2026 10:42:59 local. A antecedência real desconta o tempo desde a observação.

Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. A coluna de cota é uma estimativa pontual, não uma cota de pico. Não é sistema de alerta.

| alvo      | motor          |   h | referencia_local   |   observado_cm | previsto_cm   | validade_local   |   antecedencia_real_h | status              |
|:----------|:---------------|----:|:-------------------|---------------:|:--------------|:-----------------|----------------------:|:--------------------|
| Muçum     | linear         |   3 | 29/09 10:00        |           1142 | —             | 29/09 13:00      |                   2.3 | dados_insuficientes |
| Muçum     | gbm_delta      |   6 | 29/09 10:00        |           1142 | 1271.2        | 29/09 16:00      |                   5.3 | estimativa          |
| Muçum     | gbm_delta      |   9 | 29/09 10:00        |           1142 | 1231.2        | 29/09 19:00      |                   8.3 | estimativa          |
| Muçum     | gbm_delta      |  12 | 29/09 10:00        |           1142 | 1203.9        | 29/09 22:00      |                  11.3 | estimativa          |
| Encantado | linear         |   3 | 29/09 10:00        |            981 | 1002.5        | 29/09 13:00      |                   2.3 | estimativa          |
| Encantado | ridge_montante |   6 | 29/09 10:00        |            981 | 1008.0        | 29/09 16:00      |                   5.3 | estimativa          |
| Encantado | gbm_delta      |   9 | 29/09 10:00        |            981 | 1122.7        | 29/09 19:00      |                   8.3 | estimativa          |
| Encantado | gbm_delta      |  12 | 29/09 10:00        |            981 | 1108.8        | 29/09 22:00      |                  11.3 | estimativa          |
| Estrela   | linear         |   3 | 29/09 10:00        |           2046 | 2054.9        | 29/09 13:00      |                   2.3 | estimativa          |
| Estrela   | linear         |   6 | 29/09 10:00        |           2046 | 2060.7        | 29/09 16:00      |                   5.3 | estimativa          |
| Estrela   | linear         |   9 | 29/09 10:00        |           2046 | 2058.8        | 29/09 19:00      |                   8.3 | estimativa          |
| Estrela   | linear         |  12 | 29/09 10:00        |           2046 | 2045.3        | 29/09 22:00      |                  11.3 | estimativa          |

## Faixas e diagnóstico

As faixas usam o quantil 90% dos erros de 2025, separado por regime, sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, a velocidade está fora da calibração ou a cobertura dos últimos erros conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). Uma faixa ausente não significa erro zero.

| alvo      |   h | inferior_cm   | superior_cm   | faixa_status                   | cobertura_recente_pct   |   n_faixa_recente |
|:----------|----:|:--------------|:--------------|:-------------------------------|:------------------------|------------------:|
| Muçum     |   3 | —             | —             | faltam dados                   | —                       |                 0 |
| Muçum     |   6 | —             | —             | erros recentes excedem a faixa | 50.0                    |                 6 |
| Muçum     |   9 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Muçum     |  12 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Encantado |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Encantado |   6 | 976.4         | 1039.6        | empírica, sem garantia         | 83.3                    |                 6 |
| Encantado |   9 | 1070.2        | 1175.1        | empírica, sem garantia         | 83.3                    |                 6 |
| Encantado |  12 | 1036.0        | 1181.5        | empírica, sem garantia         | 100.0                   |                 6 |
| Estrela   |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Estrela   |   6 | 2028.6        | 2092.8        | empírica, sem garantia         | 100.0                   |                 3 |
| Estrela   |   9 | 2007.1        | 2110.4        | empírica, sem garantia         | —                       |                 0 |
| Estrela   |  12 | 1971.7        | 2119.0        | empírica, sem garantia         | —                       |                 0 |

![Hidrograma revisado](figs/live_v3_20260929_13.png)

## Replay da subida

Referências a partir de 28/09 10:00; somente alvos já observados. Horizontes maiores têm menos pares. Ausência de linha significa ausência de pares, não erro zero.

| alvo      |   h |   MAE_cm |   vies_cm |   n |
|:----------|----:|---------:|----------:|----:|
| Encantado |   3 |     26.9 |     -14.4 |  22 |
| Encantado |   6 |     66.2 |      -9.9 |  19 |
| Encantado |   9 |     98.1 |      12.9 |  16 |
| Encantado |  12 |    107.9 |      12.7 |  13 |
| Estrela   |   3 |     15.3 |     -10.6 |  22 |
| Estrela   |   6 |     47.3 |     -32.4 |  19 |
| Estrela   |   9 |    102   |     -67.2 |  16 |
| Estrela   |  12 |    171.3 |    -121   |  13 |
| Muçum     |   3 |     38.3 |     -24   |  22 |
| Muçum     |   6 |     88.9 |      41.1 |  19 |
| Muçum     |   9 |    161.9 |      81.8 |  16 |
| Muçum     |  12 |    180   |      84.8 |  13 |

Os candidatos são escolhidos em 2023–2024, confirmados em 2025 e podem ser vetados por regressão em 2026. A comparação completa está em [melhoria e aceitação](12_melhoria_live.md). O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.

Arquivo local da execução: `data/processed/live_runs/emissao_20260929T134259083495Z`. Contém previsões, replay, features, datasets de treino, código e configuração.

## Emissões reais conferidas

| alvo      |   h |   MAE_cm |   n |
|:----------|----:|---------:|----:|
| Encantado |   3 |     39.8 |  13 |
| Encantado |   6 |    127.4 |  13 |
| Encantado |   9 |    168.6 |  13 |
| Encantado |  12 |    194.3 |  13 |
| Estrela   |   3 |     23   |  13 |
| Estrela   |   6 |     63.3 |  13 |
| Estrela   |   9 |    111.3 |  13 |
| Estrela   |  12 |    161.8 |  13 |
| Muçum     |   3 |     54.7 |   4 |
| Muçum     |   6 |    138.6 |  13 |
| Muçum     |   9 |    213.4 |  13 |
| Muçum     |  12 |    251.9 |  13 |
