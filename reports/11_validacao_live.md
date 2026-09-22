# Validação de previsões de 6, 9 e 12 horas

Todas as previsões partem da cota instantânea em t e apontam para t+h.
Chuva usa features de t−5h, ONS de t−1h, API diário de t−24h e
disponibilidade de sensor de t−1h, tanto no treino quanto na previsão.
Não há preenchimento de lacunas. Atrasos são hipóteses fixas do replay;
não existem arquivos históricos de horário de publicação para comprová-los.
O atraso de transmissão da cota (~15 min na rodada de setembro) também
reduz a antecedência real em relação ao horário nominal da observação.

Treino: somente janelas completas anteriores ao início da janela testada,
com os rótulos também anteriores ao corte. Early stopping apenas no treino.
Comparação nas mesmas horas observáveis para todos os modelos; cobertura
registrada no CSV. Regime alto: cota atual OU futura acima de atenção.
O CSV também contém o regime de subida e o conjunto completo.

Seleção: menor MAE médio por evento em 2023–2025, por estação/horizonte.
Teste separado: eventos de 2026. As médias abaixo dão o mesmo peso a cada
evento; n é a soma dos pares. Eventos sem pares no regime não entram na média.
Persistência mantém a cota atual. Linear usa cota e derivadas próprias e de
montante. GBM nível prevê a cota; GBM delta prevê a variação desde a cota atual.
Nenhum modelo recebe ajuste de viés calculado no evento testado.

O desenvolvimento foi motivado pelo erro já visto em setembro. O replay de
setembro é diagnóstico, não teste cego. A escolha automática usa só 2023–2025.
Estas métricas não validam uso operacional nem estabelecem um teto físico.

## Modelos escolhidos

|   codigo |   h | motor     |   mae_selecao_cm |
|---------:|----:|:----------|-----------------:|
| 86510000 |   6 | gbm_delta |             45.4 |
| 86510000 |   9 | gbm_delta |             75.6 |
| 86510000 |  12 | gbm_delta |             98.7 |
| 86720000 |   6 | linear    |             45.1 |
| 86720000 |   9 | gbm_delta |             66.7 |
| 86720000 |  12 | gbm_delta |            116.1 |
| 86879300 |   6 | linear    |             33.9 |
| 86879300 |   9 | linear    |             55.2 |
| 86879300 |  12 | linear    |             83.5 |

## Teste de 2026: modelos escolhidos sem estes eventos

Três janelas: janeiro, junho/julho e julho. Janeiro não tem pares no regime alto em Encantado/Estrela e tem apenas 1–5 em Muçum. O erro médio por evento deve ser lido junto dessa amostra pequena. Setembro não está nesta tabela.

| alvo      |   h | motor     |   MAE_cm |   pior_MAE_evento_cm |   eventos_com_pares |   pares |
|:----------|----:|:----------|---------:|---------------------:|--------------------:|--------:|
| Encantado |   6 | linear    |     46.1 |                 68.7 |                   2 |     181 |
| Encantado |   9 | gbm_delta |     49.6 |                 76.3 |                   2 |     190 |
| Encantado |  12 | gbm_delta |     76.3 |                120.9 |                   2 |     199 |
| Estrela   |   6 | linear    |     24.4 |                 38.6 |                   2 |     169 |
| Estrela   |   9 | linear    |     40.3 |                 64.1 |                   2 |     178 |
| Estrela   |  12 | linear    |     59.7 |                 92.3 |                   2 |     187 |
| Muçum     |   6 | gbm_delta |     39.9 |                 50.8 |                   3 |     291 |
| Muçum     |   9 | gbm_delta |     63.6 |                 81.1 |                   3 |     304 |
| Muçum     |  12 | gbm_delta |     97.4 |                129.2 |                   3 |     312 |

## Comparação no regime alto (cm)

| particao   | alvo      |   h | motor        |   MAE_cm |   vies_cm |   eventos |    n |
|:-----------|:----------|----:|:-------------|---------:|----------:|----------:|-----:|
| selecao    | Encantado |   6 | gbm_delta    |     49.7 |     -26.1 |        13 |  930 |
| selecao    | Encantado |   6 | gbm_nivel    |     84.7 |     -30.8 |        13 |  930 |
| selecao    | Encantado |   6 | linear       |     45.1 |      -4.4 |        13 |  930 |
| selecao    | Encantado |   6 | persistencia |    137.8 |     -74.1 |        13 |  930 |
| selecao    | Encantado |   9 | gbm_delta    |     66.7 |     -35.5 |        13 |  966 |
| selecao    | Encantado |   9 | gbm_nivel    |     94.6 |     -29.9 |        13 |  966 |
| selecao    | Encantado |   9 | linear       |     91.1 |     -44.1 |        13 |  966 |
| selecao    | Encantado |   9 | persistencia |    160.2 |     -68.3 |        13 |  966 |
| selecao    | Encantado |  12 | gbm_delta    |    116.1 |     -70.8 |        13 | 1007 |
| selecao    | Encantado |  12 | gbm_nivel    |    132.6 |     -63.1 |        13 | 1007 |
| selecao    | Encantado |  12 | linear       |    137.7 |     -81.9 |        13 | 1007 |
| selecao    | Encantado |  12 | persistencia |    219.4 |    -100.2 |        13 | 1007 |
| selecao    | Estrela   |   6 | gbm_delta    |     58.8 |     -32.9 |        12 |  728 |
| selecao    | Estrela   |   6 | gbm_nivel    |    113.2 |     -91   |        12 |  728 |
| selecao    | Estrela   |   6 | linear       |     33.9 |       1.1 |        12 |  728 |
| selecao    | Estrela   |   6 | persistencia |    119.6 |     -63.3 |        12 |  728 |
| selecao    | Estrela   |   9 | gbm_delta    |     94.9 |     -47.3 |        12 |  762 |
| selecao    | Estrela   |   9 | gbm_nivel    |    136.3 |    -108.4 |        12 |  762 |
| selecao    | Estrela   |   9 | linear       |     55.2 |      -6.8 |        12 |  762 |
| selecao    | Estrela   |   9 | persistencia |    168.4 |     -88   |        12 |  762 |
| selecao    | Estrela   |  12 | gbm_delta    |    125.6 |     -55.4 |        12 |  799 |
| selecao    | Estrela   |  12 | gbm_nivel    |    140.5 |    -103   |        12 |  799 |
| selecao    | Estrela   |  12 | linear       |     83.5 |     -31.9 |        12 |  799 |
| selecao    | Estrela   |  12 | persistencia |    197.1 |     -94.6 |        12 |  799 |
| selecao    | Muçum     |   6 | gbm_delta    |     45.4 |     -24.3 |        21 | 1754 |
| selecao    | Muçum     |   6 | gbm_nivel    |     62   |     -37.6 |        21 | 1754 |
| selecao    | Muçum     |   6 | linear       |     50.3 |     -27.8 |        21 | 1754 |
| selecao    | Muçum     |   6 | persistencia |    104.4 |     -52.3 |        21 | 1754 |
| selecao    | Muçum     |   9 | gbm_delta    |     75.6 |     -45   |        21 | 1813 |
| selecao    | Muçum     |   9 | gbm_nivel    |     94.6 |     -65.8 |        21 | 1813 |
| selecao    | Muçum     |   9 | linear       |     89   |     -50.8 |        21 | 1813 |
| selecao    | Muçum     |   9 | persistencia |    142.9 |     -70.3 |        21 | 1813 |
| selecao    | Muçum     |  12 | gbm_delta    |     98.7 |     -62.7 |        21 | 1868 |
| selecao    | Muçum     |  12 | gbm_nivel    |    118.3 |     -87.9 |        21 | 1868 |
| selecao    | Muçum     |  12 | linear       |    120.6 |     -72.3 |        21 | 1868 |
| selecao    | Muçum     |  12 | persistencia |    173   |     -82   |        21 | 1868 |
| teste      | Encantado |   6 | gbm_delta    |     30.1 |      -4.1 |         2 |  181 |
| teste      | Encantado |   6 | gbm_nivel    |     68.1 |      49.7 |         2 |  181 |
| teste      | Encantado |   6 | linear       |     46.1 |     -10.7 |         2 |  181 |
| teste      | Encantado |   6 | persistencia |    125.2 |      -9.9 |         2 |  181 |
| teste      | Encantado |   9 | gbm_delta    |     49.6 |     -16.7 |         2 |  190 |
| teste      | Encantado |   9 | gbm_nivel    |     92.2 |      52.7 |         2 |  190 |
| teste      | Encantado |   9 | linear       |     77.3 |     -25.3 |         2 |  190 |
| teste      | Encantado |   9 | persistencia |    182.5 |     -17.7 |         2 |  190 |
| teste      | Encantado |  12 | gbm_delta    |     76.3 |     -32.3 |         2 |  199 |
| teste      | Encantado |  12 | gbm_nivel    |    112.4 |      33.7 |         2 |  199 |
| teste      | Encantado |  12 | linear       |    112.3 |     -42.6 |         2 |  199 |
| teste      | Encantado |  12 | persistencia |    236.6 |     -27.1 |         2 |  199 |
| teste      | Estrela   |   6 | gbm_delta    |     19.4 |       8.1 |         2 |  169 |
| teste      | Estrela   |   6 | gbm_nivel    |     50.8 |      22.9 |         2 |  169 |
| teste      | Estrela   |   6 | linear       |     24.4 |       0.3 |         2 |  169 |
| teste      | Estrela   |   6 | persistencia |    100   |      -2.7 |         2 |  169 |
| teste      | Estrela   |   9 | gbm_delta    |     36.2 |       6.1 |         2 |  178 |
| teste      | Estrela   |   9 | gbm_nivel    |     57.8 |      12.6 |         2 |  178 |
| teste      | Estrela   |   9 | linear       |     40.3 |      -3.6 |         2 |  178 |
| teste      | Estrela   |   9 | persistencia |    147.4 |      -6   |         2 |  178 |
| teste      | Estrela   |  12 | gbm_delta    |     50.4 |       3.9 |         2 |  187 |
| teste      | Estrela   |  12 | gbm_nivel    |     73.8 |      -1   |         2 |  187 |
| teste      | Estrela   |  12 | linear       |     59.7 |      -7.6 |         2 |  187 |
| teste      | Estrela   |  12 | persistencia |    191.7 |      -9.7 |         2 |  187 |
| teste      | Muçum     |   6 | gbm_delta    |     39.9 |      17.2 |         3 |  291 |
| teste      | Muçum     |   6 | gbm_nivel    |     32.3 |      13.4 |         3 |  291 |
| teste      | Muçum     |   6 | linear       |     25.6 |      -3.1 |         3 |  291 |
| teste      | Muçum     |   6 | persistencia |    126.5 |     -59   |         3 |  291 |
| teste      | Muçum     |   9 | gbm_delta    |     63.6 |     -21.8 |         3 |  304 |
| teste      | Muçum     |   9 | gbm_nivel    |     61.6 |     -13   |         3 |  304 |
| teste      | Muçum     |   9 | linear       |     79.7 |     -31.6 |         3 |  304 |
| teste      | Muçum     |   9 | persistencia |    157   |     -61.3 |         3 |  304 |
| teste      | Muçum     |  12 | gbm_delta    |     97.4 |     -55   |         3 |  312 |
| teste      | Muçum     |  12 | gbm_nivel    |     97.6 |     -43.8 |         3 |  312 |
| teste      | Muçum     |  12 | linear       |    126.8 |     -80.3 |         3 |  312 |
| teste      | Muçum     |  12 | persistencia |    176.9 |     -54.3 |         3 |  312 |

Reprodução: `uv run python -m src.live.evaluate`. Métricas detalhadas: [CSV](11_validacao_live_metricas.csv).
