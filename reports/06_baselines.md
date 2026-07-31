# Fase 6 — Baselines (validação cruzada por evento)

Protocolo: fold = evento (59 folds), treino = demais janelas, métricas pooled
sobre todos os folds. `cobertura` = fração de pares obs/pred válidos — onde é
baixa, a métrica mede só o caso fácil (Armadilha 0).

Baselines: **persistencia** (cota atual se mantém), **regressao_lags** (linear
com nível e derivadas da própria estação e do montante imediato),
**propagacao** (montante deslocado pelo tempo de viagem estimado no treino,
reescalado linearmente). O benchmark externo (SACE) está na seção final.

## Métricas pooled — todos os eventos

| alvo      |   h | baseline       |   NSE |   KGE |   RMSE_cm |   MAE_cm |   cobertura |     n |
|:----------|----:|:---------------|------:|------:|----------:|---------:|------------:|------:|
| Encantado |   3 | persistencia   | 0.98  | 0.989 |      34.6 |     18.3 |        96.4 | 15424 |
| Encantado |   3 | propagacao     | 0.918 | 0.927 |      71.5 |     58.4 |        96   | 15361 |
| Encantado |   3 | regressao_lags | 0.996 | 0.998 |      14.5 |      6.5 |        93.5 | 14967 |
| Encantado |   6 | persistencia   | 0.931 | 0.965 |      64.8 |     34.9 |        96.2 | 15385 |
| Encantado |   6 | propagacao     | 0.87  | 0.897 |      90.1 |     65.8 |        96   | 15355 |
| Encantado |   6 | regressao_lags | 0.976 | 0.986 |      37.5 |     18.3 |        93.3 | 14931 |
| Encantado |  12 | persistencia   | 0.776 | 0.888 |     115.3 |     62.5 |        95.7 | 15320 |
| Encantado |  12 | propagacao     | 0.722 | 0.794 |     131.3 |     83.2 |        95.9 | 15337 |
| Encantado |  12 | regressao_lags | 0.881 | 0.928 |      82.6 |     42.1 |        92.9 | 14867 |
| Encantado |  24 | persistencia   | 0.36  | 0.682 |     193.8 |    103.5 |        95.3 | 15241 |
| Encantado |  24 | propagacao     | 0.415 | 0.546 |     190.4 |    109.3 |        95.7 | 15314 |
| Encantado |  24 | regressao_lags | 0.57  | 0.707 |     157.5 |     75.8 |        92.5 | 14794 |
| Estrela   |   3 | persistencia   | 0.985 | 0.988 |      28.9 |     14.9 |        95.8 | 10241 |
| Estrela   |   3 | propagacao     | 0.848 | 0.8   |      75.1 |     51.4 |        90.1 |  9624 |
| Estrela   |   3 | regressao_lags | 0.997 | 0.997 |      10.2 |      7   |        87.9 |  9395 |
| Estrela   |   6 | persistencia   | 0.944 | 0.967 |      55.3 |     27.2 |        95.6 | 10218 |
| Estrela   |   6 | propagacao     | 0.836 | 0.792 |      79.2 |     54.3 |        90.1 |  9628 |
| Estrela   |   6 | regressao_lags | 0.988 | 0.99  |      20.4 |     13.4 |        87.8 |  9385 |
| Estrela   |  12 | persistencia   | 0.806 | 0.895 |     102   |     47   |        95.3 | 10185 |
| Estrela   |  12 | propagacao     | 0.73  | 0.721 |     102.6 |     65.5 |        90   |  9618 |
| Estrela   |  12 | regressao_lags | 0.932 | 0.949 |      49.6 |     28.3 |        87.6 |  9363 |
| Estrela   |  24 | persistencia   | 0.443 | 0.698 |     172.8 |     79.5 |        95   | 10150 |
| Estrela   |  24 | propagacao     | 0.403 | 0.452 |     151   |     82.7 |        89.8 |  9600 |
| Estrela   |  24 | regressao_lags | 0.619 | 0.707 |     118.4 |     58.7 |        87.3 |  9333 |
| Muçum     |   3 | persistencia   | 0.98  | 0.99  |      42.7 |     23.5 |        98.4 | 17733 |
| Muçum     |   3 | propagacao     | 0.964 | 0.975 |      52.7 |     35.2 |        75.7 | 13641 |
| Muçum     |   3 | regressao_lags | 0.992 | 0.996 |      24.3 |     11   |        74.1 | 13347 |
| Muçum     |   6 | persistencia   | 0.932 | 0.966 |      78.8 |     44.5 |        98.2 | 17695 |
| Muçum     |   6 | propagacao     | 0.943 | 0.963 |      66.7 |     37.9 |        75.6 | 13628 |
| Muçum     |   6 | regressao_lags | 0.975 | 0.986 |      43.3 |     21.4 |        73.8 | 13308 |
| Muçum     |  12 | persistencia   | 0.794 | 0.897 |     136.6 |     78.1 |        97.8 | 17634 |
| Muçum     |  12 | propagacao     | 0.809 | 0.874 |     122.5 |     66.8 |        75.5 | 13604 |
| Muçum     |  12 | regressao_lags | 0.881 | 0.926 |      96.1 |     49   |        73.5 | 13252 |
| Muçum     |  24 | persistencia   | 0.459 | 0.732 |     221   |    124.5 |        97.6 | 17594 |
| Muçum     |  24 | propagacao     | 0.507 | 0.645 |     198.1 |    107.7 |        75.3 | 13570 |
| Muçum     |  24 | regressao_lags | 0.597 | 0.725 |     178.2 |     92.1 |        73.3 | 13214 |

## Só os eventos de referência (set/2023, nov/2023, mai/2024)

| alvo      |   h | baseline       |   NSE |   KGE |   RMSE_cm |   MAE_cm |   cobertura |    n |
|:----------|----:|:---------------|------:|------:|----------:|---------:|------------:|-----:|
| Encantado |   3 | persistencia   | 0.98  | 0.959 |      64.6 |     33   |        84.4 |  795 |
| Encantado |   3 | propagacao     | 0.951 | 0.881 |     104   |     81.9 |        88.6 |  835 |
| Encantado |   3 | regressao_lags | 0.997 | 0.994 |      24.3 |     11.7 |        80.3 |  756 |
| Encantado |   6 | persistencia   | 0.935 | 0.929 |     116   |     61.8 |        83.3 |  785 |
| Encantado |   6 | propagacao     | 0.892 | 0.833 |     153.8 |    103.8 |        88.1 |  830 |
| Encantado |   6 | regressao_lags | 0.982 | 0.975 |      59.1 |     31   |        79   |  744 |
| Encantado |  12 | persistencia   | 0.813 | 0.879 |     191.2 |    108.7 |        81.1 |  764 |
| Encantado |  12 | propagacao     | 0.736 | 0.722 |     241.1 |    145.5 |        86.7 |  817 |
| Encantado |  12 | regressao_lags | 0.907 | 0.894 |     132.8 |     72.8 |        77.3 |  728 |
| Encantado |  24 | persistencia   | 0.393 | 0.666 |     349.5 |    196.2 |        79.8 |  752 |
| Encantado |  24 | propagacao     | 0.453 | 0.5   |     348   |    206.7 |        84.3 |  794 |
| Encantado |  24 | regressao_lags | 0.589 | 0.641 |     288.8 |    154.2 |        75.8 |  714 |
| Estrela   |   3 | persistencia   | 0.99  | 0.984 |      52.2 |     27.3 |        78.9 |  869 |
| Estrela   |   3 | propagacao     | 0.88  | 0.765 |     106.2 |     55.3 |        68.1 |  751 |
| Estrela   |   3 | regressao_lags | 0.997 | 0.987 |      14.9 |      8.8 |        63.1 |  695 |
| Estrela   |   6 | persistencia   | 0.961 | 0.964 |     101.7 |     51.4 |        77.4 |  853 |
| Estrela   |   6 | propagacao     | 0.832 | 0.695 |     134.8 |     67.8 |        68.6 |  756 |
| Estrela   |   6 | regressao_lags | 0.985 | 0.966 |      36.9 |     19.2 |        62.9 |  693 |
| Estrela   |  12 | persistencia   | 0.86  | 0.909 |     190.7 |     92.9 |        75.2 |  829 |
| Estrela   |  12 | propagacao     | 0.669 | 0.54  |     201.8 |     98.6 |        68   |  749 |
| Estrela   |  12 | regressao_lags | 0.908 | 0.875 |      96   |     44.7 |        62   |  683 |
| Estrela   |  24 | persistencia   | 0.621 | 0.775 |     316.1 |    163   |        72.9 |  803 |
| Estrela   |  24 | propagacao     | 0.26  | 0.256 |     304.1 |    146.4 |        66.3 |  731 |
| Estrela   |  24 | regressao_lags | 0.476 | 0.483 |     251.1 |    118.3 |        60.3 |  664 |
| Muçum     |   3 | persistencia   | 0.984 | 0.99  |      62.5 |     31.9 |        98.2 | 1849 |
| Muçum     |   3 | propagacao     | 0.981 | 0.944 |      62.5 |     45.2 |        57.7 | 1087 |
| Muçum     |   3 | regressao_lags | 0.996 | 0.989 |      28.5 |     14.5 |        56.6 | 1065 |
| Muçum     |   6 | persistencia   | 0.945 | 0.971 |     116.3 |     61.2 |        98   | 1846 |
| Muçum     |   6 | propagacao     | 0.953 | 0.923 |     100.7 |     54.1 |        57.7 | 1087 |
| Muçum     |   6 | regressao_lags | 0.979 | 0.967 |      67.8 |     31.8 |        56.4 | 1062 |
| Muçum     |  12 | persistencia   | 0.837 | 0.918 |     198.9 |    110.4 |        97.7 | 1840 |
| Muçum     |  12 | propagacao     | 0.834 | 0.825 |     195.7 |     98.4 |        57.7 | 1087 |
| Muçum     |  12 | regressao_lags | 0.895 | 0.885 |     155.3 |     72   |        56.1 | 1056 |
| Muçum     |  24 | persistencia   | 0.558 | 0.779 |     327   |    191.1 |        97.1 | 1829 |
| Muçum     |  24 | propagacao     | 0.565 | 0.614 |     322.5 |    174   |        57.8 | 1088 |
| Muçum     |  24 | regressao_lags | 0.684 | 0.696 |     274.5 |    141.7 |        55.6 | 1047 |

## Leitura

Os números que o modelo da Fase 7 precisa bater, por alvo e horizonte, são o
MELHOR baseline de cada linha — tipicamente persistência em h=3 e
regressão/propagação em h=12-24.


## Baseline 4 — Previsões oficiais do SACE (benchmark externo)

Previsões em prosa (2022+, horizonte explícito de 4-6h) comparadas com a cota
observada da ANA no timestamp alvo. São previsões emitidas EM EVENTOS (o SACE
só publica boletim quando o rio ameaça), então o regime é o difícil — não
compare diretamente com as métricas pooled acima, que incluem recessões e
antecedências; a comparação justa (mesmas horas) fica para a Fase 8.

| alvo      |   horizonte_h |   NSE |   KGE |   RMSE_cm |   MAE_cm |   cobertura |   n |
|:----------|--------------:|------:|------:|----------:|---------:|------------:|----:|
| Encantado |             4 | 0.967 | 0.949 |      68   |     33.9 |        73.5 |  86 |
| Estrela   |             4 | 0.985 | 0.882 |      28.1 |     16.9 |       100   |   7 |
| Estrela   |             6 | 0.95  | 0.959 |      74   |     47   |        75.4 |  95 |
| Muçum     |             4 | 0.687 | 0.843 |     216.4 |     65.4 |        96.7 | 119 |

Interpretação: MAE de ~30-60 cm em horizonte de 4-6h emitida durante eventos é
a régua operacional. O modelo da Fase 7, avaliado NAS MESMAS horas de emissão,
precisa entregar erro comparável ou menor.
