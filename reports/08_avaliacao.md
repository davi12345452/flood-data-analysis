# Fase 8 — Avaliação completa

Fonte: previsões por fold da CV por evento (Fases 6-7), sem retreino.
Figuras: `figs/dispersao_*.png` (previsto×observado por horizonte) e
`figs/hidrograma_ev*.png` (eventos de referência com previsão sobreposta).

## Detecção de ultrapassagem da cota de inundação (hora a hora)

POD = acertos/(acertos+perdas); FAR = falsos/(alarmes); CSI combina ambos;
viés >1 = alarmista, <1 = conservador. `horas_obs_acima` mostra o quão raro é
o que se tenta detectar.

| alvo      |   h | modelo         |   POD |   FAR |   CSI |   vies_freq |   horas_obs_acima |     n |
|:----------|----:|:---------------|------:|------:|------:|------------:|------------------:|------:|
| Encantado |   3 | gbm            | 0.861 | 0.124 | 0.767 |       0.983 |               287 | 15588 |
| Encantado |   3 | persistencia   | 0.879 | 0.112 | 0.791 |       0.989 |               272 | 15424 |
| Encantado |   3 | regressao_lags | 0.983 | 0.041 | 0.943 |       1.025 |               236 | 14967 |
| Encantado |   6 | gbm            | 0.826 | 0.141 | 0.727 |       0.962 |               287 | 15592 |
| Encantado |   6 | persistencia   | 0.76  | 0.231 | 0.619 |       0.989 |               263 | 15385 |
| Encantado |   6 | regressao_lags | 0.921 | 0.102 | 0.834 |       1.026 |               229 | 14931 |
| Encantado |  12 | gbm            | 0.777 | 0.22  | 0.637 |       0.997 |               287 | 15592 |
| Encantado |  12 | persistencia   | 0.551 | 0.455 | 0.377 |       1.012 |               254 | 15320 |
| Encantado |  12 | regressao_lags | 0.746 | 0.217 | 0.618 |       0.952 |               228 | 14867 |
| Encantado |  24 | gbm            | 0.39  | 0.253 | 0.345 |       0.523 |               287 | 15594 |
| Encantado |  24 | persistencia   | 0.221 | 0.782 | 0.123 |       1.016 |               253 | 15241 |
| Encantado |  24 | regressao_lags | 0.312 | 0.483 | 0.242 |       0.604 |               240 | 14794 |
| Estrela   |   3 | gbm            | 0.884 | 0.033 | 0.858 |       0.914 |               499 | 10367 |
| Estrela   |   3 | persistencia   | 0.913 | 0.065 | 0.859 |       0.977 |               473 | 10241 |
| Estrela   |   3 | regressao_lags | 0.98  | 0.009 | 0.971 |       0.988 |               346 |  9395 |
| Estrela   |   6 | gbm            | 0.942 | 0.041 | 0.906 |       0.982 |               499 | 10368 |
| Estrela   |   6 | persistencia   | 0.829 | 0.134 | 0.734 |       0.957 |               467 | 10218 |
| Estrela   |   6 | regressao_lags | 0.954 | 0.021 | 0.935 |       0.974 |               347 |  9385 |
| Estrela   |  12 | gbm            | 0.9   | 0.156 | 0.771 |       1.066 |               499 | 10368 |
| Estrela   |  12 | persistencia   | 0.665 | 0.272 | 0.533 |       0.914 |               463 | 10185 |
| Estrela   |  12 | regressao_lags | 0.85  | 0.067 | 0.801 |       0.91  |               346 |  9363 |
| Estrela   |  24 | gbm            | 0.595 | 0.337 | 0.457 |       0.898 |               499 | 10371 |
| Estrela   |  24 | persistencia   | 0.426 | 0.497 | 0.3   |       0.848 |               467 | 10150 |
| Estrela   |  24 | regressao_lags | 0.437 | 0.251 | 0.381 |       0.583 |               348 |  9333 |
| Muçum     |   3 | gbm            | 0.518 | 0.184 | 0.464 |       0.635 |               137 | 17817 |
| Muçum     |   3 | persistencia   | 0.874 | 0.113 | 0.787 |       0.985 |               135 | 17733 |
| Muçum     |   3 | regressao_lags | 0.988 | 0     | 0.988 |       0.988 |                80 | 13347 |
| Muçum     |   6 | gbm            | 0.533 | 0.18  | 0.477 |       0.65  |               137 | 17811 |
| Muçum     |   6 | persistencia   | 0.765 | 0.218 | 0.63  |       0.978 |               136 | 17695 |
| Muçum     |   6 | regressao_lags | 0.929 | 0.025 | 0.908 |       0.953 |                85 | 13308 |
| Muçum     |  12 | gbm            | 0.46  | 0.315 | 0.38  |       0.672 |               137 | 17799 |
| Muçum     |  12 | persistencia   | 0.559 | 0.433 | 0.392 |       0.985 |               136 | 17634 |
| Muçum     |  12 | regressao_lags | 0.809 | 0.153 | 0.706 |       0.955 |                89 | 13252 |
| Muçum     |  24 | gbm            | 0.095 | 0.133 | 0.094 |       0.109 |               137 | 17781 |
| Muçum     |  24 | persistencia   | 0.25  | 0.746 | 0.144 |       0.985 |               136 | 17594 |
| Muçum     |  24 | regressao_lags | 0.322 | 0.453 | 0.254 |       0.589 |                90 | 13214 |

## Erro de pico, evento a evento (picos ≥ cota de atenção)

Resumo (média entre eventos; `vies_valor` <0 = subestima o pico — o erro que
mata; `cobertura_pico` <1 = sensor falhou perto do pico e o número mede menos
do que parece — Armadilha 0):

| alvo      |   h | modelo         |   n_eventos |   vies_valor_cm |   mae_valor_cm |   mae_tempo_h |   cobertura_pico |
|:----------|----:|:---------------|------------:|----------------:|---------------:|--------------:|-----------------:|
| Encantado |   3 | gbm            |          38 |           -9.7  |          66.03 |          2.63 |             0.96 |
| Encantado |   3 | regressao_lags |          38 |            8.66 |          18.63 |          4.34 |             0.96 |
| Encantado |   6 | gbm            |          38 |           14.99 |          76.64 |          3.63 |             0.95 |
| Encantado |   6 | regressao_lags |          38 |           42.69 |          53.79 |          8.05 |             0.95 |
| Encantado |  12 | gbm            |          39 |           65.12 |         108.27 |          3.82 |             0.94 |
| Encantado |  12 | regressao_lags |          39 |           37.12 |         151.14 |         20.26 |             0.94 |
| Encantado |  24 | gbm            |          39 |           27.08 |         201.22 |          7.51 |             0.94 |
| Encantado |  24 | regressao_lags |          39 |           30.71 |         178.06 |         28.44 |             0.94 |
| Estrela   |   3 | gbm            |          21 |          -72.09 |         106.8  |          4.1  |             0.91 |
| Estrela   |   3 | regressao_lags |          20 |          -41.22 |          53.75 |         13.75 |             0.95 |
| Estrela   |   6 | gbm            |          21 |          -10.03 |         109.82 |          4.05 |             0.91 |
| Estrela   |   6 | regressao_lags |          20 |          -28.02 |          52.35 |          3.8  |             0.95 |
| Estrela   |  12 | gbm            |          21 |           23.5  |         132.67 |         15.43 |             0.91 |
| Estrela   |  12 | regressao_lags |          20 |           22.99 |          72.08 |         17.85 |             0.95 |
| Estrela   |  24 | gbm            |          21 |          -35.63 |         219.77 |         29.43 |             0.91 |
| Estrela   |  24 | regressao_lags |          20 |          -70.81 |         216.56 |         26.8  |             0.95 |
| Muçum     |   3 | gbm            |          57 |            4.84 |          44.83 |          2.82 |             0.98 |
| Muçum     |   3 | regressao_lags |          49 |          -11.55 |          48.44 |         12.12 |             0.97 |
| Muçum     |   6 | gbm            |          57 |           18.69 |          62.15 |          4.04 |             0.96 |
| Muçum     |   6 | regressao_lags |          49 |           13.15 |          72.65 |         11.27 |             0.96 |
| Muçum     |  12 | gbm            |          57 |           46.82 |          98.51 |         10.74 |             0.95 |
| Muçum     |  12 | regressao_lags |          49 |           24.98 |         146.08 |         12.92 |             0.95 |
| Muçum     |  24 | gbm            |          57 |           10    |         165.87 |         25.98 |             0.94 |
| Muçum     |  24 | regressao_lags |          49 |          -26.15 |         147.03 |         27.41 |             0.93 |

### Só os eventos de referência (set/2023, nov/2023, mai/2024)

| alvo      |   h | modelo         |   n_eventos |   vies_valor_cm |   mae_valor_cm |   mae_tempo_h |   cobertura_pico |
|:----------|----:|:---------------|------------:|----------------:|---------------:|--------------:|-----------------:|
| Encantado |   3 | gbm            |           3 |         -165.33 |         165.33 |          4    |             0.65 |
| Encantado |   3 | regressao_lags |           3 |           24.8  |          40.53 |          1    |             0.65 |
| Encantado |   6 | gbm            |           3 |         -201.95 |         201.95 |          2    |             0.65 |
| Encantado |   6 | regressao_lags |           3 |           61.73 |          61.73 |          0.67 |             0.65 |
| Encantado |  12 | gbm            |           3 |         -159.85 |         159.85 |          1.33 |             0.65 |
| Encantado |  12 | regressao_lags |           3 |         -562.23 |         562.23 |          4.67 |             0.65 |
| Encantado |  24 | gbm            |           3 |         -643.27 |         643.27 |          7.33 |             0.65 |
| Encantado |  24 | regressao_lags |           3 |         -591.6  |         650.79 |         11.67 |             0.65 |
| Estrela   |   3 | gbm            |           3 |         -426.6  |         426.6  |         13.33 |             0.68 |
| Estrela   |   3 | regressao_lags |           3 |         -306.51 |         306.51 |         85.33 |             0.68 |
| Estrela   |   6 | gbm            |           3 |         -338.93 |         339.43 |         12.33 |             0.68 |
| Estrela   |   6 | regressao_lags |           3 |         -234.53 |         234.53 |         13    |             0.68 |
| Estrela   |  12 | gbm            |           3 |         -189.06 |         378.48 |         84.67 |             0.68 |
| Estrela   |  12 | regressao_lags |           3 |         -120.63 |         160.36 |         10.67 |             0.68 |
| Estrela   |  24 | gbm            |           3 |         -738.09 |         738.09 |         86    |             0.68 |
| Estrela   |  24 | regressao_lags |           3 |         -879.96 |         879.96 |          8.33 |             0.68 |
| Muçum     |   3 | gbm            |           4 |         -194.26 |         194.26 |          4    |             0.86 |
| Muçum     |   3 | regressao_lags |           4 |           23.83 |          43.95 |          4.25 |             0.86 |
| Muçum     |   6 | gbm            |           4 |         -215.1  |         215.1  |          5.5  |             0.86 |
| Muçum     |   6 | regressao_lags |           4 |           81.68 |          85.98 |          3.75 |             0.86 |
| Muçum     |  12 | gbm            |           4 |         -244.15 |         264.42 |          6    |             0.82 |
| Muçum     |  12 | regressao_lags |           4 |         -188.46 |         473.69 |          4.25 |             0.82 |
| Muçum     |  24 | gbm            |           4 |         -528.51 |         575.42 |         88.25 |             0.76 |
| Muçum     |  24 | regressao_lags |           4 |         -431.3  |         559.17 |         67    |             0.76 |

Detalhe por evento em `data/processed/picos_por_evento.parquet`.

## Modelo × SACE nas mesmas horas de emissão

Comparação pareada: mesmas horas de referência dos boletins (2022+). SACE
h=4 contra modelo h=3 (vantagem para o SACE) e h=6 contra h=6. MAE contra a
mesma observação.

| alvo      |   h_sace |   h_modelo | modelo         |   n_pareado |   MAE_modelo_cm |   MAE_sace_cm |
|:----------|---------:|-----------:|:---------------|------------:|----------------:|--------------:|
| Encantado |        4 |          3 | gbm            |          87 |            68.2 |          46.8 |
| Encantado |        4 |          3 | regressao_lags |          87 |            17.6 |          46.8 |
| Estrela   |        4 |          3 | gbm            |           7 |            78.2 |          11.6 |
| Estrela   |        4 |          3 | regressao_lags |           7 |             6.8 |          11.6 |
| Estrela   |        6 |          6 | gbm            |          97 |           101.8 |          47   |
| Estrela   |        6 |          6 | regressao_lags |          97 |            34.7 |          47   |
| Muçum     |        4 |          3 | gbm            |         120 |            50.5 |          75.8 |
| Muçum     |        4 |          3 | regressao_lags |         120 |            24.6 |          75.8 |

## Ressalvas de leitura (obrigatórias)

1. **Cobertura no pico**: onde `cobertura_pico` < 0,9, o erro de pico está
   calculado sobre um pico possivelmente truncado pelo sensor. Em mai/2024
   isso atinge Encantado e Estrela em cheio.
2. **Detecção**: com poucas horas acima da inundação em CV, POD/FAR têm
   variância alta; leia com o `horas_obs_acima` ao lado.
3. **Curva-chave**: tudo aqui é cota, nunca vazão (Armadilha 1).
