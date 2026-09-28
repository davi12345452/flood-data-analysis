# Fase 7 — LightGBM (CV por evento, mesmas regras dos baselines)

Config: raso e regularizado (config/model.yaml). NaN nativo, sem imputação.
Early stopping nas janelas finais do treino de cada fold, também com purga
temporal. Features com chuva incompleta permanecem NaN. Variante
`gbm_restrito` treina só com nível >= atenção (Armadilha 2); teste idêntico.

## Comparação com os baselines (pooled, todos os eventos)

| alvo      |   h | modelo         |    NSE |   KGE |   RMSE_cm |   MAE_cm |   cobertura |     n |
|:----------|----:|:---------------|-------:|------:|----------:|---------:|------------:|------:|
| Encantado |   3 | regressao_lags |  0.996 | 0.998 |      14.4 |      6.5 |        93.6 | 15042 |
| Encantado |   3 | persistencia   |  0.98  | 0.989 |      34.6 |     18.3 |        96.4 | 15499 |
| Encantado |   3 | gbm            |  0.962 | 0.941 |      48.7 |     17.8 |        97.4 | 15663 |
| Encantado |   3 | propagacao     |  0.916 | 0.926 |      72.1 |     59.1 |        96   | 15436 |
| Encantado |   3 | gbm_restrito   | -0.087 | 0.256 |     260.1 |    227.1 |        97.4 | 15663 |
| Encantado |   6 | regressao_lags |  0.976 | 0.986 |      37.5 |     18.4 |        93.4 | 15009 |
| Encantado |   6 | gbm            |  0.964 | 0.969 |      47.1 |     20.7 |        97.5 | 15670 |
| Encantado |   6 | persistencia   |  0.93  | 0.965 |      64.7 |     34.9 |        96.2 | 15463 |
| Encantado |   6 | propagacao     |  0.867 | 0.895 |      90.6 |     66.3 |        96   | 15433 |
| Encantado |   6 | gbm_restrito   |  0.018 | 0.307 |     247   |    214.6 |        97.5 | 15670 |
| Encantado |  12 | gbm            |  0.934 | 0.949 |      63.8 |     33   |        97.5 | 15676 |
| Encantado |  12 | regressao_lags |  0.881 | 0.927 |      82.6 |     42.2 |        93   | 14951 |
| Encantado |  12 | persistencia   |  0.775 | 0.888 |     115.1 |     62.5 |        95.8 | 15404 |
| Encantado |  12 | propagacao     |  0.72  | 0.792 |     131.6 |     83.6 |        95.9 | 15421 |
| Encantado |  12 | gbm_restrito   |  0.073 | 0.376 |     239.3 |    200.7 |        97.5 | 15676 |
| Encantado |  24 | gbm            |  0.757 | 0.791 |     122   |     60.4 |        97.6 | 15690 |
| Encantado |  24 | regressao_lags |  0.57  | 0.707 |     157.1 |     75.6 |        92.6 | 14890 |
| Encantado |  24 | propagacao     |  0.412 | 0.544 |     190.4 |    109.5 |        95.9 | 15410 |
| Encantado |  24 | persistencia   |  0.358 | 0.682 |     193.5 |    103.5 |        95.4 | 15337 |
| Encantado |  24 | gbm_restrito   | -0.141 | 0.338 |     264.4 |    214.4 |        97.6 | 15690 |
| Estrela   |   3 | regressao_lags |  0.997 | 0.997 |      10.3 |      7   |        88   |  9470 |
| Estrela   |   3 | persistencia   |  0.985 | 0.988 |      28.8 |     14.9 |        95.9 | 10316 |
| Estrela   |   3 | gbm            |  0.909 | 0.866 |      72.7 |     19.3 |        97   | 10442 |
| Estrela   |   3 | propagacao     |  0.846 | 0.798 |      75.7 |     51.5 |        90.1 |  9699 |
| Estrela   |   3 | gbm_restrito   |  0.121 | 0.598 |     225.4 |    204.9 |        97   | 10442 |
| Estrela   |   6 | regressao_lags |  0.988 | 0.99  |      20.4 |     13.4 |        87.9 |  9463 |
| Estrela   |   6 | persistencia   |  0.944 | 0.967 |      55.1 |     27.2 |        95.7 | 10296 |
| Estrela   |   6 | gbm            |  0.919 | 0.888 |      68.5 |     21.9 |        97.1 | 10446 |
| Estrela   |   6 | propagacao     |  0.835 | 0.793 |      79   |     54.2 |        90.2 |  9706 |
| Estrela   |   6 | gbm_restrito   |  0.345 | 0.669 |     194.5 |    170.9 |        97.1 | 10446 |
| Estrela   |  12 | regressao_lags |  0.931 | 0.949 |      49.5 |     28.3 |        87.8 |  9447 |
| Estrela   |  12 | gbm            |  0.881 | 0.848 |      82.8 |     30   |        97.1 | 10452 |
| Estrela   |  12 | persistencia   |  0.805 | 0.895 |     101.8 |     47   |        95.4 | 10269 |
| Estrela   |  12 | propagacao     |  0.729 | 0.721 |     102.4 |     65.4 |        90.2 |  9702 |
| Estrela   |  12 | gbm_restrito   |  0.488 | 0.756 |     171.7 |    131.8 |        97.1 | 10452 |
| Estrela   |  24 | gbm            |  0.679 | 0.736 |     135.9 |     56.4 |        97.3 | 10467 |
| Estrela   |  24 | regressao_lags |  0.618 | 0.707 |     118   |     58.6 |        87.6 |  9429 |
| Estrela   |  24 | persistencia   |  0.437 | 0.696 |     173   |     79.8 |        95.2 | 10246 |
| Estrela   |  24 | propagacao     |  0.402 | 0.452 |     150.5 |     82.4 |        90.1 |  9696 |
| Estrela   |  24 | gbm_restrito   |  0.141 | 0.678 |     222.3 |    155.5 |        97.3 | 10467 |
| Muçum     |   3 | regressao_lags |  0.992 | 0.996 |      24.2 |     11   |        74.2 | 13422 |
| Muçum     |   3 | gbm            |  0.981 | 0.959 |      41.6 |     14.7 |        98.9 | 17892 |
| Muçum     |   3 | persistencia   |  0.98  | 0.99  |      42.7 |     23.6 |        98.4 | 17808 |
| Muçum     |   3 | propagacao     |  0.962 | 0.974 |      54   |     35.3 |        75.8 | 13711 |
| Muçum     |   3 | gbm_restrito   |  0.529 | 0.512 |     207.6 |    160.8 |        98.9 | 17892 |
| Muçum     |   6 | regressao_lags |  0.975 | 0.986 |      43.2 |     21.4 |        74   | 13386 |
| Muçum     |   6 | gbm            |  0.969 | 0.955 |      52.8 |     20.9 |        98.8 | 17889 |
| Muçum     |   6 | propagacao     |  0.942 | 0.962 |      66.7 |     37.9 |        75.7 | 13706 |
| Muçum     |   6 | persistencia   |  0.932 | 0.966 |      78.8 |     44.6 |        98.2 | 17773 |
| Muçum     |   6 | gbm_restrito   |  0.564 | 0.547 |     199.4 |    155.1 |        98.8 | 17889 |
| Muçum     |  12 | gbm            |  0.934 | 0.938 |      77   |     35.9 |        98.8 | 17883 |
| Muçum     |  12 | regressao_lags |  0.881 | 0.926 |      95.9 |     49.1 |        73.7 | 13336 |
| Muçum     |  12 | propagacao     |  0.809 | 0.873 |     122.3 |     66.8 |        75.6 | 13688 |
| Muçum     |  12 | persistencia   |  0.794 | 0.897 |     136.5 |     78.1 |        97.9 | 17718 |
| Muçum     |  12 | gbm_restrito   |  0.541 | 0.56  |     203.9 |    158.6 |        98.8 | 17883 |
| Muçum     |  24 | gbm            |  0.78  | 0.778 |     140.3 |     67.8 |        98.8 | 17877 |
| Muçum     |  24 | regressao_lags |  0.597 | 0.725 |     177.7 |     91.9 |        73.5 | 13310 |
| Muçum     |  24 | propagacao     |  0.507 | 0.645 |     197.6 |    107.3 |        75.5 | 13666 |
| Muçum     |  24 | persistencia   |  0.458 | 0.732 |     220.6 |    124.4 |        97.7 | 17690 |
| Muçum     |  24 | gbm_restrito   |  0.418 | 0.511 |     228.5 |    176.8 |        98.8 | 17877 |

## Veredito — o GBM bate os baselines internos? (critério: NSE pooled)

| alvo      |   h |   NSE_gbm | melhor_baseline   |   NSE_baseline | gbm_vence   |
|:----------|----:|----------:|:------------------|---------------:|:------------|
| Encantado |   3 |     0.962 | regressao_lags    |          0.996 | False       |
| Encantado |   6 |     0.964 | regressao_lags    |          0.976 | False       |
| Encantado |  12 |     0.934 | regressao_lags    |          0.881 | True        |
| Encantado |  24 |     0.757 | regressao_lags    |          0.57  | True        |
| Estrela   |   3 |     0.909 | regressao_lags    |          0.997 | False       |
| Estrela   |   6 |     0.919 | regressao_lags    |          0.988 | False       |
| Estrela   |  12 |     0.881 | regressao_lags    |          0.931 | False       |
| Estrela   |  24 |     0.679 | regressao_lags    |          0.618 | True        |
| Muçum     |   3 |     0.981 | regressao_lags    |          0.992 | False       |
| Muçum     |   6 |     0.969 | regressao_lags    |          0.975 | False       |
| Muçum     |  12 |     0.934 | regressao_lags    |          0.881 | True        |
| Muçum     |  24 |     0.78  | regressao_lags    |          0.597 | True        |

A tabela acima identifica o vencedor em cada estação/horizonte. As métricas
foram recalculadas com purga temporal e chuva incompleta preservada como NaN.
O protocolo é retrospectivo; a avaliação cronológica está no relatório live.

## Armadilha 2, teste justo — só horas com ALVO >= atenção

| alvo      |   h | modelo       |   NSE |   KGE |   RMSE_cm |   MAE_cm |   cobertura |    n |
|:----------|----:|:-------------|------:|------:|----------:|---------:|------------:|-----:|
| Encantado |   3 | gbm          | 0.87  | 0.884 |     112.3 |     52.2 |         100 | 2665 |
| Encantado |   3 | gbm_restrito | 0.892 | 0.839 |     102.5 |     55.1 |         100 | 2665 |
| Encantado |   6 | gbm          | 0.887 | 0.926 |     104.7 |     57.7 |         100 | 2665 |
| Encantado |   6 | gbm_restrito | 0.893 | 0.862 |     102   |     61.7 |         100 | 2665 |
| Encantado |  12 | gbm          | 0.817 | 0.889 |     133.2 |     85.1 |         100 | 2665 |
| Encantado |  12 | gbm_restrito | 0.77  | 0.792 |     149.3 |     95.6 |         100 | 2665 |
| Encantado |  24 | gbm          | 0.251 | 0.574 |     269.4 |    179.2 |         100 | 2665 |
| Encantado |  24 | gbm_restrito | 0.319 | 0.502 |     256.8 |    173   |         100 | 2665 |
| Estrela   |   3 | gbm          | 0.759 | 0.766 |     190.4 |     85   |         100 | 1466 |
| Estrela   |   3 | gbm_restrito | 0.802 | 0.703 |     172.6 |     93.5 |         100 | 1466 |
| Estrela   |   6 | gbm          | 0.791 | 0.783 |     177.6 |     90.3 |         100 | 1466 |
| Estrela   |   6 | gbm_restrito | 0.796 | 0.742 |     175.1 |     93.2 |         100 | 1466 |
| Estrela   |  12 | gbm          | 0.708 | 0.737 |     209.6 |    116.7 |         100 | 1466 |
| Estrela   |  12 | gbm_restrito | 0.683 | 0.719 |     218.3 |    134.3 |         100 | 1466 |
| Estrela   |  24 | gbm          | 0.222 | 0.477 |     342.3 |    240.1 |         100 | 1466 |
| Estrela   |  24 | gbm_restrito | 0.193 | 0.423 |     348.5 |    248.4 |         100 | 1466 |
| Muçum     |   3 | gbm          | 0.954 | 0.918 |      73.3 |     29.7 |         100 | 5313 |
| Muçum     |   3 | gbm_restrito | 0.903 | 0.823 |     106   |     39.8 |         100 | 5313 |
| Muçum     |   6 | gbm          | 0.927 | 0.91  |      92.1 |     41.6 |         100 | 5313 |
| Muçum     |   6 | gbm_restrito | 0.913 | 0.853 |     100.3 |     46.7 |         100 | 5313 |
| Muçum     |  12 | gbm          | 0.853 | 0.887 |     130.6 |     68.7 |         100 | 5313 |
| Muçum     |  12 | gbm_restrito | 0.856 | 0.829 |     129.3 |     70   |         100 | 5313 |
| Muçum     |  24 | gbm          | 0.489 | 0.654 |     243.3 |    141.4 |         100 | 5313 |
| Muçum     |  24 | gbm_restrito | 0.59  | 0.653 |     217.9 |    129.1 |         100 | 5313 |

A comparação entre treino completo e restrito deve ser lida nas métricas
recalculadas acima. Estes resultados não estabelecem um teto físico de
antecedência nem uma garantia operacional.

## Só eventos de referência (set/2023, nov/2023, mai/2024)

| alvo      |   h | modelo       |   NSE |   KGE |   RMSE_cm |   MAE_cm |   cobertura |    n |
|:----------|----:|:-------------|------:|------:|----------:|---------:|------------:|-----:|
| Encantado |   3 | gbm          | 0.915 | 0.782 |     135.9 |     54.3 |        89.2 |  840 |
| Encantado |   3 | gbm_restrito | 0.604 | 0.434 |     293.2 |    246.6 |        89.2 |  840 |
| Encantado |   6 | gbm          | 0.951 | 0.864 |     103.3 |     47   |        88.6 |  835 |
| Encantado |   6 | gbm_restrito | 0.671 | 0.49  |     267.6 |    226.3 |        88.6 |  835 |
| Encantado |  12 | gbm          | 0.927 | 0.848 |     126.4 |     61.9 |        87.3 |  822 |
| Encantado |  12 | gbm_restrito | 0.7   | 0.528 |     256.2 |    219.9 |        87.3 |  822 |
| Encantado |  24 | gbm          | 0.727 | 0.66  |     245.1 |    122.2 |        84.7 |  798 |
| Encantado |  24 | gbm_restrito | 0.503 | 0.415 |     331.2 |    262.2 |        84.7 |  798 |
| Estrela   |   3 | gbm          | 0.807 | 0.693 |     230.6 |     92.7 |        84.6 |  932 |
| Estrela   |   3 | gbm_restrito | 0.714 | 0.557 |     280.8 |    224.6 |        84.6 |  932 |
| Estrela   |   6 | gbm          | 0.842 | 0.712 |     208.9 |     86.7 |        84.1 |  927 |
| Estrela   |   6 | gbm_restrito | 0.777 | 0.626 |     248.7 |    187   |        84.1 |  927 |
| Estrela   |  12 | gbm          | 0.796 | 0.671 |     238.3 |    104.4 |        83   |  915 |
| Estrela   |  12 | gbm_restrito | 0.75  | 0.615 |     264.2 |    184.7 |        83   |  915 |
| Estrela   |  24 | gbm          | 0.571 | 0.484 |     348.1 |    172.2 |        80.9 |  892 |
| Estrela   |  24 | gbm_restrito | 0.596 | 0.5   |     337.7 |    214.2 |        80.9 |  892 |
| Muçum     |   3 | gbm          | 0.959 | 0.862 |      99.8 |     39.3 |        98.6 | 1857 |
| Muçum     |   3 | gbm_restrito | 0.805 | 0.637 |     217.8 |    135.6 |        98.6 | 1857 |
| Muçum     |   6 | gbm          | 0.937 | 0.831 |     123.7 |     49.3 |        98.6 | 1857 |
| Muçum     |   6 | gbm_restrito | 0.852 | 0.697 |     189.5 |    117.8 |        98.6 | 1857 |
| Muçum     |  12 | gbm          | 0.902 | 0.784 |     153.7 |     68.6 |        98.6 | 1857 |
| Muçum     |  12 | gbm_restrito | 0.84  | 0.685 |     196.6 |    124   |        98.6 | 1857 |
| Muçum     |  24 | gbm          | 0.745 | 0.659 |     246.3 |    121.5 |        98.6 | 1857 |
| Muçum     |  24 | gbm_restrito | 0.708 | 0.576 |     263.7 |    165.3 |        98.6 | 1857 |

## Importância de features (ganho médio entre folds, top 8, h=12, variante cheia)

| alvo      |   h | feature                  |   ganho_medio |
|:----------|----:|:-------------------------|--------------:|
| Encantado |  12 | defluente_ca             |        0.3847 |
| Encantado |  12 | nivel_en                 |        0.1845 |
| Encantado |  12 | defluente_mc             |        0.1664 |
| Encantado |  12 | nivel_mu                 |        0.098  |
| Encantado |  12 | chuva_antas_24h          |        0.0378 |
| Encantado |  12 | chuva_medio_24h          |        0.0148 |
| Encantado |  12 | chuva_medio_48h          |        0.0128 |
| Encantado |  12 | chuva_antas_12h          |        0.0111 |
| Estrela   |  12 | nivel_mu                 |        0.5715 |
| Estrela   |  12 | defluente_mc             |        0.0871 |
| Estrela   |  12 | chuva_antas_48h          |        0.0849 |
| Estrela   |  12 | nivel_st                 |        0.044  |
| Estrela   |  12 | nivel_es                 |        0.0263 |
| Estrela   |  12 | chuva_antas_72h          |        0.0213 |
| Estrela   |  12 | chuva_antas_24h          |        0.0186 |
| Estrela   |  12 | chuva_baixo_24h          |        0.0118 |
| Muçum     |  12 | nivel_mu                 |        0.5836 |
| Muçum     |  12 | tempo_desde_atencao_h_mu |        0.0943 |
| Muçum     |  12 | defluente_mc             |        0.0765 |
| Muçum     |  12 | chuva_antas_24h          |        0.0574 |
| Muçum     |  12 | defluente_qj             |        0.0372 |
| Muçum     |  12 | chuva_medio_24h          |        0.025  |
| Muçum     |  12 | defluente_ca             |        0.0208 |
| Muçum     |  12 | chuva_antas_12h          |        0.0204 |

Alinha com a literatura da bacia (2025): predomínio de nível/dinâmica de
montante e acumulados longos de chuva (chuva_*_24-120h ≈ "chuva máxima de
1-5 dias" do estudo).

## Fora de escopo (mantido)

LSTM/TCN permanecem fora (volume não sustenta); o pré-treino no dataset
diário longo (mitigação opcional) não foi executado nesta fase — fica
registrado como trabalho futuro no relatório final.
