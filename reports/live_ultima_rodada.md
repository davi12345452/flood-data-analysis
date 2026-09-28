# Revisão da rodada de 28/09/2026 09:00

Modo: **emissao**. Referência observada: 28/09 09:00 (UTC−3). Emissão registrada em 28/09/2026 09:33:27 local. A antecedência real desconta o tempo desde a observação.

Horizontes contados desde a referência da própria estação; chuva e ONS mantêm seus atrasos no treino e na inferência. Alterações de modelo passam por comparação por fase da cheia. A coluna de cota é uma estimativa pontual, não uma cota de pico. Não é sistema de alerta.

| alvo      | motor          |   h | referencia_local   |   observado_cm | previsto_cm   | validade_local   |   antecedencia_real_h | status              |
|:----------|:---------------|----:|:-------------------|---------------:|:--------------|:-----------------|----------------------:|:--------------------|
| Muçum     | linear         |   3 | 28/09 09:00        |            431 | —             | 28/09 12:00      |                   2.4 | dados_insuficientes |
| Muçum     | gbm_delta      |   6 | 28/09 09:00        |            431 | 512.1         | 28/09 15:00      |                   5.4 | estimativa          |
| Muçum     | gbm_delta      |   9 | 28/09 09:00        |            431 | 555.7         | 28/09 18:00      |                   8.4 | estimativa          |
| Muçum     | gbm_delta      |  12 | 28/09 09:00        |            431 | 597.7         | 28/09 21:00      |                  11.4 | estimativa          |
| Encantado | linear         |   3 | 28/09 09:00        |            305 | 355.7         | 28/09 12:00      |                   2.4 | estimativa          |
| Encantado | ridge_montante |   6 | 28/09 09:00        |            305 | 395.4         | 28/09 15:00      |                   5.4 | estimativa          |
| Encantado | gbm_delta      |   9 | 28/09 09:00        |            305 | 460.3         | 28/09 18:00      |                   8.4 | estimativa          |
| Encantado | gbm_delta      |  12 | 28/09 09:00        |            305 | 478.6         | 28/09 21:00      |                  11.4 | estimativa          |
| Estrela   | linear         |   3 | 28/09 09:00        |           1355 | 1399.0        | 28/09 12:00      |                   2.4 | estimativa          |
| Estrela   | linear         |   6 | 28/09 09:00        |           1355 | 1441.4        | 28/09 15:00      |                   5.4 | estimativa          |
| Estrela   | linear         |   9 | 28/09 09:00        |           1355 | 1480.3        | 28/09 18:00      |                   8.4 | estimativa          |
| Estrela   | linear         |  12 | 28/09 09:00        |           1355 | 1511.3        | 28/09 21:00      |                  11.4 | estimativa          |

## Faixas e diagnóstico

As faixas usam o quantil 90% dos erros de 2025, separado por regime, sem garantia de cobertura. Não são publicadas quando há menos de 30 pares, a velocidade está fora da calibração ou a cobertura dos últimos erros conhecidos cai abaixo de 80% (mínimo três pares nas últimas seis horas). Uma faixa ausente não significa erro zero.

| alvo      |   h | inferior_cm   | superior_cm   | faixa_status                   | cobertura_recente_pct   |   n_faixa_recente |
|:----------|----:|:--------------|:--------------|:-------------------------------|:------------------------|------------------:|
| Muçum     |   3 | —             | —             | faltam dados                   | —                       |                 0 |
| Muçum     |   6 | 465.5         | 558.7         | empírica, sem garantia         | 100.0                   |                 6 |
| Muçum     |   9 | —             | —             | erros recentes excedem a faixa | 50.0                    |                 6 |
| Muçum     |  12 | 490.0         | 705.5         | empírica, sem garantia         | 83.3                    |                 6 |
| Encantado |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Encantado |   6 | —             | —             | erros recentes excedem a faixa | 66.7                    |                 6 |
| Encantado |   9 | 407.4         | 513.3         | empírica, sem garantia         | 83.3                    |                 6 |
| Encantado |  12 | 406.7         | 550.4         | empírica, sem garantia         | 100.0                   |                 6 |
| Estrela   |   3 | —             | —             | sem calibração                 | —                       |                 0 |
| Estrela   |   6 | 1409.3        | 1473.5        | empírica, sem garantia         | 83.3                    |                 6 |
| Estrela   |   9 | 1428.6        | 1531.9        | empírica, sem garantia         | 100.0                   |                 6 |
| Estrela   |  12 | 1437.6        | 1584.9        | empírica, sem garantia         | 100.0                   |                 6 |

![Hidrograma revisado](figs/live_v3_20260928_12.png)

## Replay da subida

Referências a partir de 27/09 09:00; somente alvos já observados. Horizontes maiores têm menos pares. Ausência de linha significa ausência de pares, não erro zero.

| alvo      |   h |   MAE_cm |   vies_cm |   n |
|:----------|----:|---------:|----------:|----:|
| Encantado |   3 |     16.4 |      -6.7 |  22 |
| Encantado |   6 |     16.3 |     -12.7 |  19 |
| Encantado |   9 |     38.2 |      -1.6 |  16 |
| Encantado |  12 |     34.5 |     -15.5 |  13 |
| Estrela   |   3 |      9.4 |      -4.2 |  22 |
| Estrela   |   6 |     14.2 |      -8.6 |  19 |
| Estrela   |   9 |     15.2 |     -13.2 |  16 |
| Estrela   |  12 |     27.6 |     -24.6 |  13 |
| Muçum     |   3 |     17.3 |      -2.3 |  22 |
| Muçum     |   6 |     25.6 |       6.1 |  19 |
| Muçum     |   9 |     53.2 |      15.1 |  16 |
| Muçum     |  12 |     59.6 |      -4.4 |  13 |

Os candidatos são escolhidos em 2023–2024, confirmados em 2025 e podem ser vetados por regressão em 2026. A comparação completa está em [melhoria e aceitação](12_melhoria_live.md). O replay assume atrasos fixos e não recompõe a publicação real de cada fonte.

Arquivo local da execução: `data/processed/live_runs/emissao_20260928T123327670034Z`. Contém previsões, replay, features, datasets de treino, código e configuração.

## Emissões reais conferidas

| alvo      |   h |   MAE_cm |   n |
|:----------|----:|---------:|----:|
| Encantado |   3 |     32.1 |   2 |
| Encantado |   6 |    137.3 |   2 |
| Encantado |   9 |    258.6 |   2 |
| Encantado |  12 |    313.7 |   2 |
| Estrela   |   3 |     10.1 |   2 |
| Estrela   |   6 |     24.8 |   2 |
| Estrela   |   9 |     28.2 |   2 |
| Estrela   |  12 |     54.8 |   2 |
| Muçum     |   6 |    198.4 |   2 |
| Muçum     |   9 |    250.1 |   2 |
| Muçum     |  12 |    284.4 |   2 |
