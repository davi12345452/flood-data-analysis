# Fase 7 — LightGBM (CV por evento, mesmas regras dos baselines)

Config: raso e regularizado (config/model.yaml). NaN nativo, sem imputação.
Early stopping nas janelas finais do treino de cada fold. Variante
`gbm_restrito` treina só com nível >= atenção (Armadilha 2); teste idêntico.

## Comparação com os baselines (pooled, todos os eventos)

| alvo      |   h | modelo         |    NSE |   KGE |   RMSE_cm |   MAE_cm |   cobertura |     n |
|:----------|----:|:---------------|-------:|------:|----------:|---------:|------------:|------:|
| Encantado |   3 | regressao_lags |  0.996 | 0.998 |      14.5 |      6.5 |        93.5 | 14967 |
| Encantado |   3 | persistencia   |  0.98  | 0.989 |      34.6 |     18.3 |        96.4 | 15424 |
| Encantado |   3 | gbm            |  0.973 | 0.955 |      41.2 |     16.9 |        97.4 | 15588 |
| Encantado |   3 | propagacao     |  0.918 | 0.927 |      71.5 |     58.4 |        96   | 15361 |
| Encantado |   3 | gbm_restrito   | -0.066 | 0.266 |     258.2 |    225.4 |        97.4 | 15588 |
| Encantado |   6 | regressao_lags |  0.976 | 0.986 |      37.5 |     18.3 |        93.3 | 14931 |
| Encantado |   6 | gbm            |  0.969 | 0.976 |      44.2 |     20.4 |        97.4 | 15592 |
| Encantado |   6 | persistencia   |  0.931 | 0.965 |      64.8 |     34.9 |        96.2 | 15385 |
| Encantado |   6 | propagacao     |  0.87  | 0.897 |      90.1 |     65.8 |        96   | 15355 |
| Encantado |   6 | gbm_restrito   |  0.027 | 0.312 |     246.3 |    214.4 |        97.4 | 15592 |
| Encantado |  12 | gbm            |  0.938 | 0.967 |      62.1 |     31.7 |        97.4 | 15592 |
| Encantado |  12 | regressao_lags |  0.881 | 0.928 |      82.6 |     42.1 |        92.9 | 14867 |
| Encantado |  12 | persistencia   |  0.776 | 0.888 |     115.3 |     62.5 |        95.7 | 15320 |
| Encantado |  12 | propagacao     |  0.722 | 0.794 |     131.3 |     83.2 |        95.9 | 15337 |
| Encantado |  12 | gbm_restrito   |  0.115 | 0.395 |     234.4 |    195.8 |        97.4 | 15592 |
| Encantado |  24 | gbm            |  0.767 | 0.807 |     119.7 |     58.7 |        97.5 | 15594 |
| Encantado |  24 | regressao_lags |  0.57  | 0.707 |     157.5 |     75.8 |        92.5 | 14794 |
| Encantado |  24 | propagacao     |  0.415 | 0.546 |     190.4 |    109.3 |        95.7 | 15314 |
| Encantado |  24 | persistencia   |  0.36  | 0.682 |     193.8 |    103.5 |        95.3 | 15241 |
| Encantado |  24 | gbm_restrito   | -0.119 | 0.356 |     262.5 |    210.6 |        97.5 | 15594 |
| Estrela   |   3 | regressao_lags |  0.997 | 0.997 |      10.2 |      7   |        87.9 |  9395 |
| Estrela   |   3 | persistencia   |  0.985 | 0.988 |      28.9 |     14.9 |        95.8 | 10241 |
| Estrela   |   3 | gbm            |  0.91  | 0.858 |      72.5 |     18.8 |        97   | 10367 |
| Estrela   |   3 | propagacao     |  0.848 | 0.8   |      75.1 |     51.4 |        90.1 |  9624 |
| Estrela   |   3 | gbm_restrito   | -0.07  | 0.558 |     249.5 |    231.9 |        97   | 10367 |
| Estrela   |   6 | regressao_lags |  0.988 | 0.99  |      20.4 |     13.4 |        87.8 |  9385 |
| Estrela   |   6 | persistencia   |  0.944 | 0.967 |      55.3 |     27.2 |        95.6 | 10218 |
| Estrela   |   6 | gbm            |  0.925 | 0.891 |      66.1 |     21.2 |        97   | 10368 |
| Estrela   |   6 | propagacao     |  0.836 | 0.792 |      79.2 |     54.3 |        90.1 |  9628 |
| Estrela   |   6 | gbm_restrito   |  0.353 | 0.68  |     194   |    171.7 |        97   | 10368 |
| Estrela   |  12 | regressao_lags |  0.932 | 0.949 |      49.6 |     28.3 |        87.6 |  9363 |
| Estrela   |  12 | gbm            |  0.883 | 0.87  |      82.5 |     30.1 |        97   | 10368 |
| Estrela   |  12 | persistencia   |  0.806 | 0.895 |     102   |     47   |        95.3 | 10185 |
| Estrela   |  12 | propagacao     |  0.73  | 0.721 |     102.6 |     65.5 |        90   |  9618 |
| Estrela   |  12 | gbm_restrito   |  0.389 | 0.741 |     188.4 |    149.8 |        97   | 10368 |
| Estrela   |  24 | gbm            |  0.686 | 0.73  |     135   |     55.2 |        97.1 | 10371 |
| Estrela   |  24 | regressao_lags |  0.619 | 0.707 |     118.4 |     58.7 |        87.3 |  9333 |
| Estrela   |  24 | persistencia   |  0.443 | 0.698 |     172.8 |     79.5 |        95   | 10150 |
| Estrela   |  24 | propagacao     |  0.403 | 0.452 |     151   |     82.7 |        89.8 |  9600 |
| Estrela   |  24 | gbm_restrito   |  0.126 | 0.677 |     225.1 |    157   |        97.1 | 10371 |
| Muçum     |   3 | regressao_lags |  0.992 | 0.996 |      24.3 |     11   |        74.1 | 13347 |
| Muçum     |   3 | gbm            |  0.981 | 0.96  |      41.9 |     14.7 |        98.9 | 17817 |
| Muçum     |   3 | persistencia   |  0.98  | 0.99  |      42.7 |     23.5 |        98.4 | 17733 |
| Muçum     |   3 | propagacao     |  0.964 | 0.975 |      52.7 |     35.2 |        75.7 | 13641 |
| Muçum     |   3 | gbm_restrito   |  0.503 | 0.496 |     213.7 |    167.2 |        98.9 | 17817 |
| Muçum     |   6 | regressao_lags |  0.975 | 0.986 |      43.3 |     21.4 |        73.8 | 13308 |
| Muçum     |   6 | gbm            |  0.968 | 0.954 |      54.1 |     21.3 |        98.8 | 17811 |
| Muçum     |   6 | propagacao     |  0.943 | 0.963 |      66.7 |     37.9 |        75.6 | 13628 |
| Muçum     |   6 | persistencia   |  0.932 | 0.966 |      78.8 |     44.5 |        98.2 | 17695 |
| Muçum     |   6 | gbm_restrito   |  0.526 | 0.519 |     208.2 |    163.6 |        98.8 | 17811 |
| Muçum     |  12 | gbm            |  0.935 | 0.941 |      76.9 |     35.7 |        98.8 | 17799 |
| Muçum     |  12 | regressao_lags |  0.881 | 0.926 |      96.1 |     49   |        73.5 | 13252 |
| Muçum     |  12 | propagacao     |  0.809 | 0.874 |     122.5 |     66.8 |        75.5 | 13604 |
| Muçum     |  12 | persistencia   |  0.794 | 0.897 |     136.6 |     78.1 |        97.8 | 17634 |
| Muçum     |  12 | gbm_restrito   |  0.539 | 0.561 |     204.7 |    159.4 |        98.8 | 17799 |
| Muçum     |  24 | gbm            |  0.778 | 0.782 |     141.3 |     68   |        98.7 | 17781 |
| Muçum     |  24 | regressao_lags |  0.597 | 0.725 |     178.2 |     92.1 |        73.3 | 13214 |
| Muçum     |  24 | propagacao     |  0.507 | 0.645 |     198.1 |    107.7 |        75.3 | 13570 |
| Muçum     |  24 | persistencia   |  0.459 | 0.732 |     221   |    124.5 |        97.6 | 17594 |
| Muçum     |  24 | gbm_restrito   |  0.436 | 0.528 |     225.3 |    172.2 |        98.7 | 17781 |

## Veredito — o GBM bate os baselines internos? (critério: NSE pooled)

| alvo      |   h |   NSE_gbm | melhor_baseline   |   NSE_baseline | gbm_vence   |
|:----------|----:|----------:|:------------------|---------------:|:------------|
| Encantado |   3 |     0.973 | regressao_lags    |          0.996 | False       |
| Encantado |   6 |     0.969 | regressao_lags    |          0.976 | False       |
| Encantado |  12 |     0.938 | regressao_lags    |          0.881 | True        |
| Encantado |  24 |     0.767 | regressao_lags    |          0.57  | True        |
| Estrela   |   3 |     0.91  | regressao_lags    |          0.997 | False       |
| Estrela   |   6 |     0.925 | regressao_lags    |          0.988 | False       |
| Estrela   |  12 |     0.883 | regressao_lags    |          0.932 | False       |
| Estrela   |  24 |     0.686 | regressao_lags    |          0.619 | True        |
| Muçum     |   3 |     0.981 | regressao_lags    |          0.992 | False       |
| Muçum     |   6 |     0.968 | regressao_lags    |          0.975 | False       |
| Muçum     |  12 |     0.935 | regressao_lags    |          0.881 | True        |
| Muçum     |  24 |     0.778 | regressao_lags    |          0.597 | True        |

**Leitura honesta:** a regressão linear vence em h=3-6 (e Estrela h=12) — no
curto prazo a propagação é quase linear e árvore não extrapola tão bem. O GBM
se paga nos horizontes longos (12-24h), onde a chuva e a não-linearidade
importam. Consequência para uso: **modelo por horizonte** (linear em <=6h,
GBM em >=12h) é a configuração defensável — não uma derrota do pipeline, mas
o resultado clássico de rio com resposta quase linear no curto prazo.

## Armadilha 2, teste justo — só horas com ALVO >= atenção

| alvo      |   h | modelo       |   NSE |   KGE |   RMSE_cm |   MAE_cm |   cobertura |    n |
|:----------|----:|:-------------|------:|------:|----------:|---------:|------------:|-----:|
| Encantado |   3 | gbm          | 0.911 | 0.924 |      93   |     48   |         100 | 2665 |
| Encantado |   3 | gbm_restrito | 0.895 | 0.849 |     100.7 |     55.8 |         100 | 2665 |
| Encantado |   6 | gbm          | 0.905 | 0.936 |      95.8 |     54.5 |         100 | 2665 |
| Encantado |   6 | gbm_restrito | 0.89  | 0.867 |     103.1 |     64.1 |         100 | 2665 |
| Encantado |  12 | gbm          | 0.829 | 0.911 |     128.9 |     83   |         100 | 2665 |
| Encantado |  12 | gbm_restrito | 0.771 | 0.81  |     149.1 |     95.6 |         100 | 2665 |
| Encantado |  24 | gbm          | 0.291 | 0.594 |     262.1 |    173   |         100 | 2665 |
| Encantado |  24 | gbm_restrito | 0.279 | 0.502 |     264.4 |    177   |         100 | 2665 |
| Estrela   |   3 | gbm          | 0.762 | 0.759 |     189.4 |     82.7 |         100 | 1466 |
| Estrela   |   3 | gbm_restrito | 0.799 | 0.701 |     173.9 |     94.7 |         100 | 1466 |
| Estrela   |   6 | gbm          | 0.806 | 0.794 |     170.7 |     87.5 |         100 | 1466 |
| Estrela   |   6 | gbm_restrito | 0.799 | 0.737 |     174   |     96.6 |         100 | 1466 |
| Estrela   |  12 | gbm          | 0.713 | 0.748 |     207.9 |    119.6 |         100 | 1466 |
| Estrela   |  12 | gbm_restrito | 0.673 | 0.722 |     222   |    138.1 |         100 | 1466 |
| Estrela   |  24 | gbm          | 0.242 | 0.481 |     337.9 |    233   |         100 | 1466 |
| Estrela   |  24 | gbm_restrito | 0.149 | 0.419 |     357.9 |    257.1 |         100 | 1466 |
| Muçum     |   3 | gbm          | 0.953 | 0.916 |      74.1 |     30.2 |         100 | 5267 |
| Muçum     |   3 | gbm_restrito | 0.898 | 0.812 |     108.8 |     42.7 |         100 | 5267 |
| Muçum     |   6 | gbm          | 0.923 | 0.909 |      94.7 |     42.7 |         100 | 5267 |
| Muçum     |   6 | gbm_restrito | 0.891 | 0.827 |     112.7 |     51.6 |         100 | 5267 |
| Muçum     |  12 | gbm          | 0.854 | 0.892 |     130.5 |     68.3 |         100 | 5267 |
| Muçum     |  12 | gbm_restrito | 0.855 | 0.836 |     130.1 |     70.5 |         100 | 5267 |
| Muçum     |  24 | gbm          | 0.484 | 0.656 |     245.3 |    142.8 |         100 | 5267 |
| Muçum     |  24 | gbm_restrito | 0.581 | 0.657 |     221   |    131.5 |         100 | 5267 |

Restringir o treino a >= atenção **não ajudou** neste desenho (exceção
marginal: Muçum 24h). Plausível: nossa amostragem por evento já concentra o
treino no regime alto; o corte só joga fora informação de subida. A premissa
importada do estudo de 2025 não se replica aqui — registrado.

Nota sobria: no regime alto em h=24, NSE cai para 0,24-0,58 em todos os
modelos — consistente com o teto físico de antecedência (~12h Muçum, ~8h
Estrela) com chuva observada (Armadilha 5).

## Só eventos de referência (set/2023, nov/2023, mai/2024)

| alvo      |   h | modelo       |   NSE |   KGE |   RMSE_cm |   MAE_cm |   cobertura |    n |
|:----------|----:|:-------------|------:|------:|----------:|---------:|------------:|-----:|
| Encantado |   3 | gbm          | 0.972 | 0.895 |      78.3 |     31.8 |        89.2 |  840 |
| Encantado |   3 | gbm_restrito | 0.616 | 0.436 |     289   |    243.3 |        89.2 |  840 |
| Encantado |   6 | gbm          | 0.967 | 0.878 |      84.8 |     41.3 |        88.6 |  835 |
| Encantado |   6 | gbm_restrito | 0.665 | 0.487 |     270.3 |    228.5 |        88.6 |  835 |
| Encantado |  12 | gbm          | 0.921 | 0.834 |     131.6 |     65.1 |        87.3 |  822 |
| Encantado |  12 | gbm_restrito | 0.705 | 0.534 |     254.1 |    217.6 |        87.3 |  822 |
| Encantado |  24 | gbm          | 0.725 | 0.648 |     246.3 |    120.7 |        84.7 |  798 |
| Encantado |  24 | gbm_restrito | 0.522 | 0.436 |     324.8 |    255.9 |        84.7 |  798 |
| Estrela   |   3 | gbm          | 0.808 | 0.693 |     230.1 |     91.7 |        84.6 |  932 |
| Estrela   |   3 | gbm_restrito | 0.718 | 0.547 |     279.2 |    228.1 |        84.6 |  932 |
| Estrela   |   6 | gbm          | 0.855 | 0.722 |     200.7 |     84.2 |        84.1 |  927 |
| Estrela   |   6 | gbm_restrito | 0.771 | 0.621 |     251.8 |    192.3 |        84.1 |  927 |
| Estrela   |  12 | gbm          | 0.801 | 0.677 |     235.5 |    103   |        83   |  915 |
| Estrela   |  12 | gbm_restrito | 0.744 | 0.604 |     267.2 |    190.6 |        83   |  915 |
| Estrela   |  24 | gbm          | 0.573 | 0.481 |     347.3 |    172.3 |        80.9 |  892 |
| Estrela   |  24 | gbm_restrito | 0.596 | 0.5   |     338   |    212.9 |        80.9 |  892 |
| Muçum     |   3 | gbm          | 0.957 | 0.858 |     102.3 |     40.1 |        98.6 | 1857 |
| Muçum     |   3 | gbm_restrito | 0.808 | 0.64  |     216.2 |    133.6 |        98.6 | 1857 |
| Muçum     |   6 | gbm          | 0.933 | 0.823 |     127.7 |     50.9 |        98.6 | 1857 |
| Muçum     |   6 | gbm_restrito | 0.82  | 0.655 |     209.2 |    128.5 |        98.6 | 1857 |
| Muçum     |  12 | gbm          | 0.913 | 0.807 |     144.6 |     64.5 |        98.6 | 1857 |
| Muçum     |  12 | gbm_restrito | 0.852 | 0.71  |     189.2 |    120.4 |        98.6 | 1857 |
| Muçum     |  24 | gbm          | 0.768 | 0.683 |     235.1 |    116   |        98.6 | 1857 |
| Muçum     |  24 | gbm_restrito | 0.727 | 0.611 |     255.1 |    157.7 |        98.6 | 1857 |

## Importância de features (ganho médio entre folds, top 8, h=12, variante cheia)

| alvo      |   h | feature                  |   ganho_medio |
|:----------|----:|:-------------------------|--------------:|
| Encantado |  12 | defluente_ca             |        0.3541 |
| Encantado |  12 | nivel_en                 |        0.1809 |
| Encantado |  12 | defluente_mc             |        0.1792 |
| Encantado |  12 | nivel_mu                 |        0.1036 |
| Encantado |  12 | chuva_antas_24h          |        0.0341 |
| Encantado |  12 | chuva_medio_24h          |        0.0213 |
| Encantado |  12 | tempo_desde_atencao_h_mu |        0.0166 |
| Encantado |  12 | chuva_medio_48h          |        0.013  |
| Estrela   |  12 | nivel_mu                 |        0.504  |
| Estrela   |  12 | defluente_mc             |        0.0946 |
| Estrela   |  12 | chuva_antas_48h          |        0.0717 |
| Estrela   |  12 | chuva_antas_72h          |        0.0686 |
| Estrela   |  12 | nivel_st                 |        0.0605 |
| Estrela   |  12 | nivel_es                 |        0.031  |
| Estrela   |  12 | chuva_antas_24h          |        0.0179 |
| Estrela   |  12 | chuva_baixo_24h          |        0.0133 |
| Muçum     |  12 | nivel_mu                 |        0.5787 |
| Muçum     |  12 | tempo_desde_atencao_h_mu |        0.0894 |
| Muçum     |  12 | defluente_mc             |        0.0826 |
| Muçum     |  12 | chuva_antas_24h          |        0.0577 |
| Muçum     |  12 | defluente_qj             |        0.0335 |
| Muçum     |  12 | chuva_medio_24h          |        0.0262 |
| Muçum     |  12 | chuva_antas_48h          |        0.025  |
| Muçum     |  12 | defluente_ca             |        0.0241 |

Alinha com a literatura da bacia (2025): predomínio de nível/dinâmica de
montante e acumulados longos de chuva (chuva_*_24-120h ≈ "chuva máxima de
1-5 dias" do estudo).

## Fora de escopo (mantido)

LSTM/TCN permanecem fora (volume não sustenta); o pré-treino no dataset
diário longo (mitigação opcional) não foi executado nesta fase — fica
registrado como trabalho futuro no relatório final.
