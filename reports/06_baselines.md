# Fase 6 — Baselines (validação cruzada por evento)

Protocolo: fold = evento, treino = demais janelas com exclusão dos intervalos
de informação que cruzam o teste (rótulos futuros e contexto horário de 120h).
Validação retrospectiva, não simulação cronológica. Métricas pooled sobre os folds. `cobertura` = fração de pares obs/pred válidos — onde é
baixa, a métrica mede só o caso fácil (Armadilha 0).

Baselines: **persistencia** (cota atual se mantém), **regressao_lags** (linear
com nível e derivadas da própria estação e do montante imediato),
**propagacao** (montante deslocado pelo tempo de viagem estimado no treino,
reescalado linearmente). O benchmark externo (SACE) está na seção final.

## Métricas pooled — todos os eventos

| alvo      |   h | baseline       |   NSE |   KGE |   RMSE_cm |   MAE_cm |   cobertura |     n |
|:----------|----:|:---------------|------:|------:|----------:|---------:|------------:|------:|
| Encantado |   3 | persistencia   | 0.98  | 0.989 |      34.6 |     18.3 |        96.4 | 15499 |
| Encantado |   3 | propagacao     | 0.916 | 0.926 |      72.1 |     59.1 |        96   | 15436 |
| Encantado |   3 | regressao_lags | 0.996 | 0.998 |      14.4 |      6.5 |        93.6 | 15042 |
| Encantado |   6 | persistencia   | 0.93  | 0.965 |      64.7 |     34.9 |        96.2 | 15463 |
| Encantado |   6 | propagacao     | 0.867 | 0.895 |      90.6 |     66.3 |        96   | 15433 |
| Encantado |   6 | regressao_lags | 0.976 | 0.986 |      37.5 |     18.4 |        93.4 | 15009 |
| Encantado |  12 | persistencia   | 0.775 | 0.888 |     115.1 |     62.5 |        95.8 | 15404 |
| Encantado |  12 | propagacao     | 0.72  | 0.792 |     131.6 |     83.6 |        95.9 | 15421 |
| Encantado |  12 | regressao_lags | 0.881 | 0.927 |      82.6 |     42.2 |        93   | 14951 |
| Encantado |  24 | persistencia   | 0.358 | 0.682 |     193.5 |    103.5 |        95.4 | 15337 |
| Encantado |  24 | propagacao     | 0.412 | 0.544 |     190.4 |    109.5 |        95.9 | 15410 |
| Encantado |  24 | regressao_lags | 0.57  | 0.707 |     157.1 |     75.6 |        92.6 | 14890 |
| Estrela   |   3 | persistencia   | 0.985 | 0.988 |      28.8 |     14.9 |        95.9 | 10316 |
| Estrela   |   3 | propagacao     | 0.846 | 0.798 |      75.7 |     51.5 |        90.1 |  9699 |
| Estrela   |   3 | regressao_lags | 0.997 | 0.997 |      10.3 |      7   |        88   |  9470 |
| Estrela   |   6 | persistencia   | 0.944 | 0.967 |      55.1 |     27.2 |        95.7 | 10296 |
| Estrela   |   6 | propagacao     | 0.835 | 0.793 |      79   |     54.2 |        90.2 |  9706 |
| Estrela   |   6 | regressao_lags | 0.988 | 0.99  |      20.4 |     13.4 |        87.9 |  9463 |
| Estrela   |  12 | persistencia   | 0.805 | 0.895 |     101.8 |     47   |        95.4 | 10269 |
| Estrela   |  12 | propagacao     | 0.729 | 0.721 |     102.4 |     65.4 |        90.2 |  9702 |
| Estrela   |  12 | regressao_lags | 0.931 | 0.949 |      49.5 |     28.3 |        87.8 |  9447 |
| Estrela   |  24 | persistencia   | 0.437 | 0.696 |     173   |     79.8 |        95.2 | 10246 |
| Estrela   |  24 | propagacao     | 0.402 | 0.452 |     150.5 |     82.4 |        90.1 |  9696 |
| Estrela   |  24 | regressao_lags | 0.618 | 0.707 |     118   |     58.6 |        87.6 |  9429 |
| Muçum     |   3 | persistencia   | 0.98  | 0.99  |      42.7 |     23.6 |        98.4 | 17808 |
| Muçum     |   3 | propagacao     | 0.962 | 0.974 |      54   |     35.3 |        75.8 | 13711 |
| Muçum     |   3 | regressao_lags | 0.992 | 0.996 |      24.2 |     11   |        74.2 | 13422 |
| Muçum     |   6 | persistencia   | 0.932 | 0.966 |      78.8 |     44.6 |        98.2 | 17773 |
| Muçum     |   6 | propagacao     | 0.942 | 0.962 |      66.7 |     37.9 |        75.7 | 13706 |
| Muçum     |   6 | regressao_lags | 0.975 | 0.986 |      43.2 |     21.4 |        74   | 13386 |
| Muçum     |  12 | persistencia   | 0.794 | 0.897 |     136.5 |     78.1 |        97.9 | 17718 |
| Muçum     |  12 | propagacao     | 0.809 | 0.873 |     122.3 |     66.8 |        75.6 | 13688 |
| Muçum     |  12 | regressao_lags | 0.881 | 0.926 |      95.9 |     49.1 |        73.7 | 13336 |
| Muçum     |  24 | persistencia   | 0.458 | 0.732 |     220.6 |    124.4 |        97.7 | 17690 |
| Muçum     |  24 | propagacao     | 0.507 | 0.645 |     197.6 |    107.3 |        75.5 | 13666 |
| Muçum     |  24 | regressao_lags | 0.597 | 0.725 |     177.7 |     91.9 |        73.5 | 13310 |

## Só os eventos de referência (set/2023, nov/2023, mai/2024)

| alvo      |   h | baseline       |   NSE |   KGE |   RMSE_cm |   MAE_cm |   cobertura |    n |
|:----------|----:|:---------------|------:|------:|----------:|---------:|------------:|-----:|
| Encantado |   3 | persistencia   | 0.98  | 0.959 |      64.6 |     33   |        84.4 |  795 |
| Encantado |   3 | propagacao     | 0.95  | 0.881 |     104.2 |     82.1 |        88.6 |  835 |
| Encantado |   3 | regressao_lags | 0.997 | 0.994 |      24.4 |     11.7 |        80.3 |  756 |
| Encantado |   6 | persistencia   | 0.935 | 0.929 |     116   |     61.8 |        83.3 |  785 |
| Encantado |   6 | propagacao     | 0.892 | 0.833 |     154   |    104   |        88.1 |  830 |
| Encantado |   6 | regressao_lags | 0.982 | 0.975 |      59.1 |     31   |        79   |  744 |
| Encantado |  12 | persistencia   | 0.813 | 0.879 |     191.2 |    108.7 |        81.1 |  764 |
| Encantado |  12 | propagacao     | 0.736 | 0.722 |     241.3 |    145.6 |        86.7 |  817 |
| Encantado |  12 | regressao_lags | 0.906 | 0.894 |     133   |     72.9 |        77.3 |  728 |
| Encantado |  24 | persistencia   | 0.393 | 0.666 |     349.5 |    196.2 |        79.8 |  752 |
| Encantado |  24 | propagacao     | 0.452 | 0.499 |     348.2 |    206.8 |        84.3 |  794 |
| Encantado |  24 | regressao_lags | 0.588 | 0.641 |     289   |    154.4 |        75.8 |  714 |
| Estrela   |   3 | persistencia   | 0.99  | 0.984 |      52.2 |     27.3 |        78.9 |  869 |
| Estrela   |   3 | propagacao     | 0.869 | 0.754 |     112.7 |     57.6 |        68.1 |  751 |
| Estrela   |   3 | regressao_lags | 0.997 | 0.987 |      14.9 |      8.8 |        63.1 |  695 |
| Estrela   |   6 | persistencia   | 0.961 | 0.964 |     101.7 |     51.4 |        77.4 |  853 |
| Estrela   |   6 | propagacao     | 0.832 | 0.695 |     134.8 |     68   |        68.6 |  756 |
| Estrela   |   6 | regressao_lags | 0.985 | 0.966 |      36.8 |     19.2 |        62.9 |  693 |
| Estrela   |  12 | persistencia   | 0.86  | 0.909 |     190.7 |     92.9 |        75.2 |  829 |
| Estrela   |  12 | propagacao     | 0.669 | 0.54  |     201.8 |     98.7 |        68   |  749 |
| Estrela   |  12 | regressao_lags | 0.908 | 0.874 |      96   |     44.7 |        62   |  683 |
| Estrela   |  24 | persistencia   | 0.621 | 0.775 |     316.1 |    163   |        72.9 |  803 |
| Estrela   |  24 | propagacao     | 0.259 | 0.256 |     304.2 |    146.4 |        66.3 |  731 |
| Estrela   |  24 | regressao_lags | 0.477 | 0.483 |     251   |    118.3 |        60.3 |  664 |
| Muçum     |   3 | persistencia   | 0.984 | 0.99  |      62.5 |     31.9 |        98.2 | 1849 |
| Muçum     |   3 | propagacao     | 0.979 | 0.941 |      66.4 |     45.5 |        57.7 | 1086 |
| Muçum     |   3 | regressao_lags | 0.996 | 0.989 |      28.5 |     14.5 |        56.6 | 1065 |
| Muçum     |   6 | persistencia   | 0.945 | 0.971 |     116.3 |     61.2 |        98   | 1846 |
| Muçum     |   6 | propagacao     | 0.952 | 0.922 |     100.9 |     54.5 |        57.7 | 1087 |
| Muçum     |   6 | regressao_lags | 0.979 | 0.966 |      67.8 |     31.9 |        56.4 | 1062 |
| Muçum     |  12 | persistencia   | 0.837 | 0.918 |     198.9 |    110.4 |        97.7 | 1840 |
| Muçum     |  12 | propagacao     | 0.833 | 0.823 |     195.9 |     98.6 |        57.7 | 1087 |
| Muçum     |  12 | regressao_lags | 0.895 | 0.884 |     155.4 |     72.2 |        56.1 | 1056 |
| Muçum     |  24 | persistencia   | 0.558 | 0.779 |     327   |    191.1 |        97.1 | 1829 |
| Muçum     |  24 | propagacao     | 0.564 | 0.612 |     322.8 |    174.3 |        57.8 | 1088 |
| Muçum     |  24 | regressao_lags | 0.684 | 0.696 |     274.5 |    141.9 |        55.6 | 1047 |

## Leitura

Os números que o modelo da Fase 7 precisa bater, por alvo e horizonte, são o
MELHOR baseline de cada linha — tipicamente persistência em h=3 e
regressão/propagação em h=12-24.
