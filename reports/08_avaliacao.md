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
| Encantado |   3 | gbm            | 0.864 | 0.148 | 0.752 |       1.014 |               287 | 15663 |
| Encantado |   3 | persistencia   | 0.879 | 0.112 | 0.791 |       0.989 |               272 | 15499 |
| Encantado |   3 | regressao_lags | 0.983 | 0.041 | 0.943 |       1.025 |               236 | 15042 |
| Encantado |   6 | gbm            | 0.812 | 0.15  | 0.71  |       0.955 |               287 | 15670 |
| Encantado |   6 | persistencia   | 0.76  | 0.231 | 0.619 |       0.989 |               263 | 15463 |
| Encantado |   6 | regressao_lags | 0.921 | 0.102 | 0.834 |       1.026 |               229 | 15009 |
| Encantado |  12 | gbm            | 0.753 | 0.179 | 0.647 |       0.916 |               287 | 15676 |
| Encantado |  12 | persistencia   | 0.551 | 0.455 | 0.377 |       1.012 |               254 | 15404 |
| Encantado |  12 | regressao_lags | 0.746 | 0.213 | 0.62  |       0.947 |               228 | 14951 |
| Encantado |  24 | gbm            | 0.324 | 0.285 | 0.287 |       0.453 |               287 | 15690 |
| Encantado |  24 | persistencia   | 0.221 | 0.782 | 0.123 |       1.016 |               253 | 15337 |
| Encantado |  24 | regressao_lags | 0.312 | 0.483 | 0.242 |       0.604 |               240 | 14890 |
| Estrela   |   3 | gbm            | 0.884 | 0.056 | 0.84  |       0.936 |               499 | 10442 |
| Estrela   |   3 | persistencia   | 0.913 | 0.065 | 0.859 |       0.977 |               473 | 10316 |
| Estrela   |   3 | regressao_lags | 0.98  | 0.009 | 0.971 |       0.988 |               346 |  9470 |
| Estrela   |   6 | gbm            | 0.926 | 0.063 | 0.872 |       0.988 |               499 | 10446 |
| Estrela   |   6 | persistencia   | 0.829 | 0.134 | 0.734 |       0.957 |               467 | 10296 |
| Estrela   |   6 | regressao_lags | 0.954 | 0.021 | 0.935 |       0.974 |               347 |  9463 |
| Estrela   |  12 | gbm            | 0.87  | 0.096 | 0.796 |       0.962 |               499 | 10452 |
| Estrela   |  12 | persistencia   | 0.665 | 0.272 | 0.533 |       0.914 |               463 | 10269 |
| Estrela   |  12 | regressao_lags | 0.85  | 0.064 | 0.803 |       0.908 |               346 |  9447 |
| Estrela   |  24 | gbm            | 0.583 | 0.363 | 0.438 |       0.916 |               499 | 10467 |
| Estrela   |  24 | persistencia   | 0.426 | 0.505 | 0.297 |       0.861 |               467 | 10246 |
| Estrela   |  24 | regressao_lags | 0.44  | 0.254 | 0.382 |       0.589 |               348 |  9429 |
| Muçum     |   3 | gbm            | 0.533 | 0.18  | 0.477 |       0.65  |               137 | 17892 |
| Muçum     |   3 | persistencia   | 0.874 | 0.113 | 0.787 |       0.985 |               135 | 17808 |
| Muçum     |   3 | regressao_lags | 0.988 | 0     | 0.988 |       0.988 |                80 | 13422 |
| Muçum     |   6 | gbm            | 0.569 | 0.161 | 0.513 |       0.679 |               137 | 17889 |
| Muçum     |   6 | persistencia   | 0.765 | 0.218 | 0.63  |       0.978 |               136 | 17773 |
| Muçum     |   6 | regressao_lags | 0.929 | 0.025 | 0.908 |       0.953 |                85 | 13386 |
| Muçum     |  12 | gbm            | 0.431 | 0.352 | 0.349 |       0.664 |               137 | 17883 |
| Muçum     |  12 | persistencia   | 0.559 | 0.433 | 0.392 |       0.985 |               136 | 17718 |
| Muçum     |  12 | regressao_lags | 0.809 | 0.153 | 0.706 |       0.955 |                89 | 13336 |
| Muçum     |  24 | gbm            | 0.058 | 0.111 | 0.058 |       0.066 |               137 | 17877 |
| Muçum     |  24 | persistencia   | 0.25  | 0.746 | 0.144 |       0.985 |               136 | 17690 |
| Muçum     |  24 | regressao_lags | 0.322 | 0.453 | 0.254 |       0.589 |                90 | 13310 |

## Erro de pico, evento a evento (picos ≥ cota de atenção)

Resumo (média entre eventos; `vies_valor` <0 = subestima o pico — o erro que
mata; `cobertura_pico` <1 = sensor falhou perto do pico e o número mede menos
do que parece — Armadilha 0):

| alvo      |   h | modelo         |   n_eventos |   vies_valor_cm |   mae_valor_cm |   mae_tempo_h |   cobertura_pico |
|:----------|----:|:---------------|------------:|----------------:|---------------:|--------------:|-----------------:|
| Encantado |   3 | gbm            |          38 |          -25.49 |          77.54 |          3.13 |             0.96 |
| Encantado |   3 | regressao_lags |          38 |            8.62 |          18.59 |          4.34 |             0.96 |
| Encantado |   6 | gbm            |          38 |            5.15 |          85.85 |          3.84 |             0.95 |
| Encantado |   6 | regressao_lags |          38 |           42.51 |          53.62 |          8.05 |             0.95 |
| Encantado |  12 | gbm            |          39 |           44.54 |         108.75 |          4.13 |             0.94 |
| Encantado |  12 | regressao_lags |          39 |           36.24 |         150.44 |         20.26 |             0.94 |
| Encantado |  24 | gbm            |          39 |            0.02 |         195.39 |         13.21 |             0.94 |
| Encantado |  24 | regressao_lags |          39 |           28.78 |         176.47 |         28.44 |             0.94 |
| Estrela   |   3 | gbm            |          21 |          -48.59 |          95.46 |          3.67 |             0.91 |
| Estrela   |   3 | regressao_lags |          20 |          -41.23 |          53.74 |         13.75 |             0.95 |
| Estrela   |   6 | gbm            |          21 |          -10.13 |          99.13 |          4    |             0.91 |
| Estrela   |   6 | regressao_lags |          20 |          -28.02 |          52.35 |          3.8  |             0.95 |
| Estrela   |  12 | gbm            |          21 |           22.92 |         134.81 |         16.52 |             0.91 |
| Estrela   |  12 | regressao_lags |          20 |           22.86 |          72.25 |         17.85 |             0.95 |
| Estrela   |  24 | gbm            |          21 |           -2.41 |         256.32 |         28.76 |             0.91 |
| Estrela   |  24 | regressao_lags |          20 |          -70.88 |         216.83 |         26.8  |             0.95 |
| Muçum     |   3 | gbm            |          57 |            9.55 |          44.4  |          2.42 |             0.98 |
| Muçum     |   3 | regressao_lags |          49 |          -11.6  |          48.42 |         12.12 |             0.97 |
| Muçum     |   6 | gbm            |          57 |           20.45 |          62.1  |          3.84 |             0.96 |
| Muçum     |   6 | regressao_lags |          49 |           12.98 |          72.56 |         11.27 |             0.96 |
| Muçum     |  12 | gbm            |          57 |           43.98 |          89.22 |         10.37 |             0.95 |
| Muçum     |  12 | regressao_lags |          49 |           24.29 |         145.54 |         12.92 |             0.95 |
| Muçum     |  24 | gbm            |          57 |           -5.6  |         163.17 |         27.61 |             0.94 |
| Muçum     |  24 | regressao_lags |          49 |          -27.09 |         146.49 |         27.51 |             0.93 |

### Só os eventos de referência (set/2023, nov/2023, mai/2024)

| alvo      |   h | modelo         |   n_eventos |   vies_valor_cm |   mae_valor_cm |   mae_tempo_h |   cobertura_pico |
|:----------|----:|:---------------|------------:|----------------:|---------------:|--------------:|-----------------:|
| Encantado |   3 | gbm            |           3 |         -382.69 |         382.69 |          8    |             0.65 |
| Encantado |   3 | regressao_lags |           3 |           24.67 |          40.42 |          1    |             0.65 |
| Encantado |   6 | gbm            |           3 |         -271.51 |         271.51 |          4.67 |             0.65 |
| Encantado |   6 | regressao_lags |           3 |           61.13 |          61.13 |          0.67 |             0.65 |
| Encantado |  12 | gbm            |           3 |         -137.03 |         141.26 |          0.67 |             0.65 |
| Encantado |  12 | regressao_lags |           3 |         -562.97 |         562.97 |          4.67 |             0.65 |
| Encantado |  24 | gbm            |           3 |         -661.45 |         661.45 |          7.33 |             0.65 |
| Encantado |  24 | regressao_lags |           3 |         -592.9  |         650.62 |         11.67 |             0.65 |
| Estrela   |   3 | gbm            |           3 |         -410.34 |         410.34 |         12.67 |             0.68 |
| Estrela   |   3 | regressao_lags |           3 |         -306.45 |         306.45 |         85.33 |             0.68 |
| Estrela   |   6 | gbm            |           3 |         -318.38 |         318.38 |          9.67 |             0.68 |
| Estrela   |   6 | regressao_lags |           3 |         -234.45 |         234.45 |         13    |             0.68 |
| Estrela   |  12 | gbm            |           3 |         -193    |         373.5  |         84.33 |             0.68 |
| Estrela   |  12 | regressao_lags |           3 |         -121.76 |         160.23 |         10.67 |             0.68 |
| Estrela   |  24 | gbm            |           3 |         -743.05 |         743.05 |         86    |             0.68 |
| Estrela   |  24 | regressao_lags |           3 |         -880.94 |         880.94 |          8.33 |             0.68 |
| Muçum     |   3 | gbm            |           4 |         -166.42 |         170.26 |          3.5  |             0.86 |
| Muçum     |   3 | regressao_lags |           4 |           23.61 |          44.04 |          4.25 |             0.86 |
| Muçum     |   6 | gbm            |           4 |         -202.51 |         210.09 |          5.25 |             0.86 |
| Muçum     |   6 | regressao_lags |           4 |           80.63 |          85.95 |          3.75 |             0.86 |
| Muçum     |  12 | gbm            |           4 |         -238.38 |         263.86 |          6    |             0.82 |
| Muçum     |  12 | regressao_lags |           4 |         -190.17 |         473.59 |          4.25 |             0.82 |
| Muçum     |  24 | gbm            |           4 |         -593.04 |         663.48 |         88.5  |             0.76 |
| Muçum     |  24 | regressao_lags |           4 |         -432.29 |         559.98 |         67    |             0.76 |

Detalhe por evento em `data/processed/picos_por_evento.parquet`.

## Modelo × SACE nas mesmas horas de emissão

Comparação pareada: mesmas horas de referência dos boletins (2022+). SACE
h=4 contra modelo h=3 (vantagem para o SACE) e h=6 contra h=6. MAE contra a
mesma observação.

| alvo      |   h_sace |   h_modelo | modelo         |   n_pareado |   MAE_modelo_cm |   MAE_sace_cm |
|:----------|---------:|-----------:|:---------------|------------:|----------------:|--------------:|
| Encantado |        4 |          3 | gbm            |          87 |            96.8 |          46.8 |
| Encantado |        4 |          3 | regressao_lags |          87 |            17.6 |          46.8 |
| Estrela   |        4 |          3 | gbm            |           7 |            90.7 |          11.6 |
| Estrela   |        4 |          3 | regressao_lags |           7 |             6.8 |          11.6 |
| Estrela   |        6 |          6 | gbm            |          97 |           107   |          47   |
| Estrela   |        6 |          6 | regressao_lags |          97 |            34.8 |          47   |
| Muçum     |        4 |          3 | gbm            |         120 |            46.8 |          75.8 |
| Muçum     |        4 |          3 | regressao_lags |         120 |            24.6 |          75.8 |

## Ressalvas de leitura (obrigatórias)

1. **Cobertura no pico**: onde `cobertura_pico` < 0,9, o erro de pico está
   calculado sobre um pico possivelmente truncado pelo sensor. Em mai/2024
   isso atinge Encantado e Estrela em cheio.
2. **Detecção**: com poucas horas acima da inundação em CV, POD/FAR têm
   variância alta; leia com o `horas_obs_acima` ao lado.
3. **Curva-chave**: tudo aqui é cota, nunca vazão (Armadilha 1).
