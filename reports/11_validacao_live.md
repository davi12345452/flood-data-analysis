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
| 86510000 |   6 | gbm_delta |             45.5 |
| 86510000 |   9 | gbm_delta |             75.7 |
| 86510000 |  12 | gbm_delta |             98.9 |
| 86720000 |   6 | linear    |             45.1 |
| 86720000 |   9 | gbm_delta |             66   |
| 86720000 |  12 | gbm_delta |            116.1 |
| 86879300 |   6 | linear    |             33.9 |
| 86879300 |   9 | linear    |             55.2 |
| 86879300 |  12 | linear    |             83.5 |

## Teste de 2026: modelos escolhidos sem estes eventos

Três janelas: janeiro, junho/julho e julho. Janeiro não tem pares no regime alto em Encantado/Estrela e tem apenas 1–5 em Muçum. O erro médio por evento deve ser lido junto dessa amostra pequena. Setembro não está nesta tabela.

| alvo      |   h | motor     |   MAE_cm |   pior_MAE_evento_cm |   eventos_com_pares |   pares |
|:----------|----:|:----------|---------:|---------------------:|--------------------:|--------:|
| Encantado |   6 | linear    |     45.5 |                 67.6 |                   2 |     184 |
| Encantado |   9 | gbm_delta |     47.2 |                 71.5 |                   2 |     193 |
| Encantado |  12 | gbm_delta |     74.4 |                118.7 |                   2 |     202 |
| Estrela   |   6 | linear    |     24.3 |                 38.3 |                   2 |     171 |
| Estrela   |   9 | linear    |     39.9 |                 63.3 |                   2 |     180 |
| Estrela   |  12 | linear    |     59.1 |                 91.2 |                   2 |     189 |
| Muçum     |   6 | gbm_delta |     41.3 |                 62.5 |                   3 |     344 |
| Muçum     |   9 | gbm_delta |     62.3 |                 86.9 |                   3 |     357 |
| Muçum     |  12 | gbm_delta |     93.5 |                130.5 |                   3 |     365 |

## Comparação no regime alto (cm)

| particao   | alvo      |   h | motor        |   MAE_cm |   vies_cm |   eventos |    n |
|:-----------|:----------|----:|:-------------|---------:|----------:|----------:|-----:|
| selecao    | Encantado |   6 | gbm_delta    |     49.8 |     -26.8 |        13 |  930 |
| selecao    | Encantado |   6 | gbm_nivel    |     88.9 |     -33.6 |        13 |  930 |
| selecao    | Encantado |   6 | linear       |     45.1 |      -4.4 |        13 |  930 |
| selecao    | Encantado |   6 | persistencia |    137.8 |     -74.1 |        13 |  930 |
| selecao    | Encantado |   9 | gbm_delta    |     66   |     -34.9 |        13 |  966 |
| selecao    | Encantado |   9 | gbm_nivel    |     96.1 |     -34   |        13 |  966 |
| selecao    | Encantado |   9 | linear       |     91.1 |     -44.1 |        13 |  966 |
| selecao    | Encantado |   9 | persistencia |    160.2 |     -68.3 |        13 |  966 |
| selecao    | Encantado |  12 | gbm_delta    |    116.1 |     -72.8 |        13 | 1007 |
| selecao    | Encantado |  12 | gbm_nivel    |    136.7 |     -72.4 |        13 | 1007 |
| selecao    | Encantado |  12 | linear       |    137.7 |     -81.9 |        13 | 1007 |
| selecao    | Encantado |  12 | persistencia |    219.4 |    -100.2 |        13 | 1007 |
| selecao    | Estrela   |   6 | gbm_delta    |     58.9 |     -31.9 |        12 |  728 |
| selecao    | Estrela   |   6 | gbm_nivel    |    115.7 |     -94.1 |        12 |  728 |
| selecao    | Estrela   |   6 | linear       |     33.9 |       1.1 |        12 |  728 |
| selecao    | Estrela   |   6 | persistencia |    119.6 |     -63.3 |        12 |  728 |
| selecao    | Estrela   |   9 | gbm_delta    |     94.4 |     -47.3 |        12 |  762 |
| selecao    | Estrela   |   9 | gbm_nivel    |    140   |    -110.9 |        12 |  762 |
| selecao    | Estrela   |   9 | linear       |     55.2 |      -6.8 |        12 |  762 |
| selecao    | Estrela   |   9 | persistencia |    168.4 |     -88   |        12 |  762 |
| selecao    | Estrela   |  12 | gbm_delta    |    124.8 |     -56.2 |        12 |  799 |
| selecao    | Estrela   |  12 | gbm_nivel    |    145.1 |    -105.3 |        12 |  799 |
| selecao    | Estrela   |  12 | linear       |     83.5 |     -31.9 |        12 |  799 |
| selecao    | Estrela   |  12 | persistencia |    197.1 |     -94.6 |        12 |  799 |
| selecao    | Muçum     |   6 | gbm_delta    |     45.5 |     -24.8 |        21 | 1754 |
| selecao    | Muçum     |   6 | gbm_nivel    |     68.1 |     -49.3 |        21 | 1754 |
| selecao    | Muçum     |   6 | linear       |     50.3 |     -27.8 |        21 | 1754 |
| selecao    | Muçum     |   6 | persistencia |    104.4 |     -52.3 |        21 | 1754 |
| selecao    | Muçum     |   9 | gbm_delta    |     75.7 |     -46.6 |        21 | 1813 |
| selecao    | Muçum     |   9 | gbm_nivel    |    100.4 |     -79.5 |        21 | 1813 |
| selecao    | Muçum     |   9 | linear       |     89   |     -50.8 |        21 | 1813 |
| selecao    | Muçum     |   9 | persistencia |    142.9 |     -70.3 |        21 | 1813 |
| selecao    | Muçum     |  12 | gbm_delta    |     98.9 |     -64.1 |        21 | 1868 |
| selecao    | Muçum     |  12 | gbm_nivel    |    126.5 |     -99.3 |        21 | 1868 |
| selecao    | Muçum     |  12 | linear       |    120.6 |     -72.3 |        21 | 1868 |
| selecao    | Muçum     |  12 | persistencia |    173   |     -82   |        21 | 1868 |
| teste      | Encantado |   6 | gbm_delta    |     27.4 |      -3.8 |         2 |  184 |
| teste      | Encantado |   6 | gbm_nivel    |     72.7 |      57   |         2 |  184 |
| teste      | Encantado |   6 | linear       |     45.5 |     -10.5 |         2 |  184 |
| teste      | Encantado |   6 | persistencia |    123.6 |      -9.3 |         2 |  184 |
| teste      | Encantado |   9 | gbm_delta    |     47.2 |     -15   |         2 |  193 |
| teste      | Encantado |   9 | gbm_nivel    |     97.9 |      63.2 |         2 |  193 |
| teste      | Encantado |   9 | linear       |     76.3 |     -24.8 |         2 |  193 |
| teste      | Encantado |   9 | persistencia |    180.4 |     -16.8 |         2 |  193 |
| teste      | Encantado |  12 | gbm_delta    |     74.4 |     -32.4 |         2 |  202 |
| teste      | Encantado |  12 | gbm_nivel    |    103.6 |      26.8 |         2 |  202 |
| teste      | Encantado |  12 | linear       |    111   |     -41.8 |         2 |  202 |
| teste      | Encantado |  12 | persistencia |    234   |     -26   |         2 |  202 |
| teste      | Estrela   |   6 | gbm_delta    |     36.7 |       5   |         2 |  171 |
| teste      | Estrela   |   6 | gbm_nivel    |     47.3 |      19.2 |         2 |  171 |
| teste      | Estrela   |   6 | linear       |     24.3 |       0.5 |         2 |  171 |
| teste      | Estrela   |   6 | persistencia |     99.4 |      -2.2 |         2 |  171 |
| teste      | Estrela   |   9 | gbm_delta    |     68.9 |      -0.6 |         2 |  180 |
| teste      | Estrela   |   9 | gbm_nivel    |     61.6 |      17.7 |         2 |  180 |
| teste      | Estrela   |   9 | linear       |     39.9 |      -3.4 |         2 |  180 |
| teste      | Estrela   |   9 | persistencia |    146.3 |      -5.4 |         2 |  180 |
| teste      | Estrela   |  12 | gbm_delta    |     77.6 |       2.7 |         2 |  189 |
| teste      | Estrela   |  12 | gbm_nivel    |     77.9 |      18.8 |         2 |  189 |
| teste      | Estrela   |  12 | linear       |     59.1 |      -7.4 |         2 |  189 |
| teste      | Estrela   |  12 | persistencia |    190.3 |      -9   |         2 |  189 |
| teste      | Muçum     |   6 | gbm_delta    |     41.3 |      20.5 |         3 |  344 |
| teste      | Muçum     |   6 | gbm_nivel    |     33.3 |       5   |         3 |  344 |
| teste      | Muçum     |   6 | linear       |     22.9 |      -1.7 |         3 |  344 |
| teste      | Muçum     |   6 | persistencia |    119.1 |     -56   |         3 |  344 |
| teste      | Muçum     |   9 | gbm_delta    |     62.3 |     -16.9 |         3 |  357 |
| teste      | Muçum     |   9 | gbm_nivel    |     57.7 |      -6.8 |         3 |  357 |
| teste      | Muçum     |   9 | linear       |     75.7 |     -29.1 |         3 |  357 |
| teste      | Muçum     |   9 | persistencia |    146.3 |     -56.8 |         3 |  357 |
| teste      | Muçum     |  12 | gbm_delta    |     93.5 |     -50.6 |         3 |  365 |
| teste      | Muçum     |  12 | gbm_nivel    |     90.6 |     -42.5 |         3 |  365 |
| teste      | Muçum     |  12 | linear       |    120.9 |     -76.1 |         3 |  365 |
| teste      | Muçum     |  12 | persistencia |    163   |     -48.4 |         3 |  365 |

Reprodução: `uv run python -m src.live.evaluate`. Métricas detalhadas: [CSV](11_validacao_live_metricas.csv).
