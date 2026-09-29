# Revisão da rodada de 29/09/2026 13:00

Modo: **emissao**. Referência observada: 29/09 13:00 (UTC−3). Emissão registrada em 29/09/2026 13:40:32 local. A antecedência real desconta o tempo desde a observação.

Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. A coluna de cota é uma estimativa pontual, não uma cota de pico. Não é sistema de alerta.

| alvo      | motor          |   h | referencia_local   |   observado_cm | previsto_cm   | validade_local   |   antecedencia_real_h | status              |
|:----------|:---------------|----:|:-------------------|---------------:|:--------------|:-----------------|----------------------:|:--------------------|
| Muçum     | linear         |   3 | 29/09 13:00        |           1239 | —             | 29/09 16:00      |                   2.3 | dados_insuficientes |
| Muçum     | gbm_delta      |   6 | 29/09 13:00        |           1239 | 1501.8        | 29/09 19:00      |                   5.3 | estimativa          |
| Muçum     | gbm_delta      |   9 | 29/09 13:00        |           1239 | 1500.5        | 29/09 22:00      |                   8.3 | estimativa          |
| Muçum     | gbm_delta      |  12 | 29/09 13:00        |           1239 | 1403.8        | 30/09 01:00      |                  11.3 | estimativa          |
| Encantado | linear         |   3 | 29/09 13:00        |           1049 | 1155.2        | 29/09 16:00      |                   2.3 | estimativa          |
| Encantado | ridge_montante |   6 | 29/09 13:00        |           1049 | 1216.2        | 29/09 19:00      |                   5.3 | estimativa          |
| Encantado | gbm_delta      |   9 | 29/09 13:00        |           1049 | 1351.5        | 29/09 22:00      |                   8.3 | estimativa          |
| Encantado | gbm_delta      |  12 | 29/09 13:00        |           1049 | 1297.6        | 30/09 01:00      |                  11.3 | estimativa          |
| Estrela   | linear         |   3 | 29/09 13:00        |           2066 | 2095.6        | 29/09 16:00      |                   2.3 | estimativa          |
| Estrela   | linear         |   6 | 29/09 13:00        |           2066 | 2139.1        | 29/09 19:00      |                   5.3 | estimativa          |
| Estrela   | linear         |   9 | 29/09 13:00        |           2066 | 2173.4        | 29/09 22:00      |                   8.3 | estimativa          |
| Estrela   | linear         |  12 | 29/09 13:00        |           2066 | 2185.8        | 30/09 01:00      |                  11.3 | estimativa          |

## Faixas e diagnóstico

As faixas usam o quantil 90% dos erros de 2025, separado por regime, sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, a velocidade está fora da calibração ou a cobertura dos últimos erros conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). Uma faixa ausente não significa erro zero.

| alvo      |   h | inferior_cm   | superior_cm   | faixa_status                   | cobertura_recente_pct   |   n_faixa_recente |
|:----------|----:|:--------------|:--------------|:-------------------------------|:------------------------|------------------:|
| Muçum     |   3 | —             | —             | faltam dados                   | —                       |                 0 |
| Muçum     |   6 | —             | —             | erros recentes excedem a faixa | 50.0                    |                 6 |
| Muçum     |   9 | —             | —             | erros recentes excedem a faixa | 50.0                    |                 6 |
| Muçum     |  12 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Encantado |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Encantado |   6 | —             | —             | erros recentes excedem a faixa | 33.3                    |                 6 |
| Encantado |   9 | —             | —             | erros recentes excedem a faixa | 50.0                    |                 6 |
| Encantado |  12 | 1087.4        | 1507.8        | empírica, sem garantia         | 83.3                    |                 6 |
| Estrela   |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Estrela   |   6 | 2107.0        | 2171.3        | empírica, sem garantia         | 83.3                    |                 6 |
| Estrela   |   9 | 2121.7        | 2225.0        | empírica, sem garantia         | 100.0                   |                 3 |
| Estrela   |  12 | 2112.1        | 2259.4        | empírica, sem garantia         | —                       |                 0 |

![Hidrograma revisado](figs/live_v3_20260929_16.png)

## Replay da subida

Referências a partir de 28/09 13:00; somente alvos já observados. Horizontes maiores têm menos pares. Ausência de linha significa ausência de pares, não erro zero.

| alvo      |   h |   MAE_cm |   vies_cm |   n |
|:----------|----:|---------:|----------:|----:|
| Encantado |   3 |     27.2 |     -14.6 |  22 |
| Encantado |   6 |     55.5 |       0.8 |  19 |
| Encantado |   9 |     82.8 |      28.2 |  16 |
| Encantado |  12 |     79.8 |      57.9 |  13 |
| Estrela   |   3 |     15   |     -10.3 |  22 |
| Estrela   |   6 |     40.1 |     -25.2 |  19 |
| Estrela   |   9 |     76.9 |     -37.6 |  16 |
| Estrela   |  12 |    120.6 |     -48.7 |  13 |
| Muçum     |   3 |     38   |     -23.7 |  22 |
| Muçum     |   6 |     82.9 |      47   |  19 |
| Muçum     |   9 |    140.1 |     103.6 |  16 |
| Muçum     |  12 |    174.4 |     154.2 |  13 |

Os candidatos são escolhidos em 2023–2024, confirmados em 2025 e podem ser vetados por regressão em 2026. A comparação completa está em [melhoria e aceitação](12_melhoria_live.md). O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.

Arquivo local da execução: `data/processed/live_runs/emissao_20260929T164032043320Z`. Contém previsões, replay, features, datasets de treino, código e configuração.

## Emissões reais conferidas

| alvo      |   h |   MAE_cm |   n |
|:----------|----:|---------:|----:|
| Encantado |   3 |     39.4 |  16 |
| Encantado |   6 |    127.4 |  13 |
| Encantado |   9 |    168.6 |  13 |
| Encantado |  12 |    194.3 |  13 |
| Estrela   |   3 |     20.9 |  16 |
| Estrela   |   6 |     63.3 |  13 |
| Estrela   |   9 |    111.3 |  13 |
| Estrela   |  12 |    161.8 |  13 |
| Muçum     |   3 |     54.7 |   4 |
| Muçum     |   6 |    138.6 |  13 |
| Muçum     |   9 |    213.4 |  13 |
| Muçum     |  12 |    251.9 |  13 |
