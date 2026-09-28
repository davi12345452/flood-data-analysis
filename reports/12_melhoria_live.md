# Melhoria de previsões durante o evento

Foram comparados o modelo da revisão anterior e uma regressão Ridge da
variação de cota usando todas as réguas do subconjunto físico a montante.
Ridge usa alpha=100, padronização só no treino e recorre ao linear anterior
quando faltam réguas adicionais. Nenhuma cota é interpolada.
Também foi testado GBM da variação com acumulados de chuva dos postos ANA
de 1/3/6/12/24h, apenas estações próprias e de montante, com quatro leituras
por hora. A hora corrente nunca entra: usa-se somente chuva de horas completas.
Chuva de posto não substitui a média de bacia; oferece sinal recente adicional.

Para cada modelo, foram testados ajuste desligado ou média dos erros já
observados nas últimas 6/12h, com ganho 0,5/1 e ao menos três pares. O erro
de uma previsão de horizonte h só pode entrar h horas após sua referência.
O ajuste expira se faltarem erros recentes; não atravessa apagões por ffill.

A base v2 foi congelada da revisão anterior (escolhida com 2023–2025).
As alterações são escolhidas em 2023–2024: exigem reduzir MAE médio por
evento em pelo menos 3% no regime alto e na subida, sem piorar a descida em
mais de 5%. O candidato passa por confirmação em 2025: não pode piorar alta
ou subida nem piorar descida em mais de 5%. Se falhar, mantém-se a base, sem
tentar o segundo colocado. 2025 também calibra as faixas, portanto não é
teste independente. Em 2026, uma verificação de aceitação pode VETAR a troca
se o MAE piorar mais de 5% em alta, subida, descida ou subida rápida; não se
busca outro candidato nesse conjunto. Portanto 2026 deixou de ser um teste
independente da versão promovida. Os resultados completos, inclusive os
candidatos rejeitados, estão no CSV. Desenvolvimento iniciado após observar
setembro e 2026: comparação retrospectiva, não teste prospectivo cego.

Faixas: quantil 90% do erro absoluto em 2025, separado por subida rápida
(derivada atual acima do p99 do treino daquele evento) ou demais horas.
Com menos de 30 pares no regime, não se publica faixa para esse regime.
Dependência temporal e mudança de regime impedem garantia de cobertura.
O teste de cobertura em 2026 abaixo mede essa limitação explicitamente.

As métricas de ponto são pareadas nas mesmas horas, com médias por evento.
Regime alto inclui cota atual ou futura acima de atenção; subida/descida
usam a derivada observada na referência. Faixas são avaliadas por hora.

## Configuração escolhida

|   codigo |   h | motor          | ajuste   |   ganho |   janela_h |   min_amostras | motor_anterior   | candidato_motor   | candidato_ajuste   | confirmado_2025   | motor_testado_2026   | ajuste_testado_2026   | aceito_2026   |
|---------:|----:|:---------------|:---------|--------:|-----------:|---------------:|:-----------------|:------------------|:-------------------|:------------------|:---------------------|:----------------------|:--------------|
| 86510000 |   6 | gbm_delta      | original |       0 |          6 |              3 | gbm_delta        | gbm_postos        | original           | True              | gbm_postos           | original              | False         |
| 86510000 |   9 | gbm_delta      | original |       0 |          6 |              3 | gbm_delta        | gbm_postos        | original           | True              | gbm_postos           | original              | False         |
| 86510000 |  12 | gbm_delta      | original |       0 |          6 |              3 | gbm_delta        | gbm_postos        | original           | True              | gbm_postos           | original              | False         |
| 86720000 |   6 | ridge_montante | original |       0 |          6 |              3 | linear           | ridge_montante    | original           | True              | ridge_montante       | original              | True          |
| 86720000 |   9 | gbm_delta      | original |       0 |          6 |              3 | gbm_delta        | gbm_postos        | original           | True              | gbm_postos           | original              | False         |
| 86720000 |  12 | gbm_delta      | original |       0 |          6 |              3 | gbm_delta        | gbm_postos        | original           | True              | gbm_postos           | original              | False         |
| 86879300 |   6 | linear         | original |       0 |          6 |              3 | linear           | linear            | original           | True              | linear               | original              | True          |
| 86879300 |   9 | linear         | original |       0 |          6 |              3 | linear           | linear            | original           | True              | linear               | original              | True          |
| 86879300 |  12 | linear         | original |       0 |          6 |              3 | linear           | linear            | original           | True              | linear               | original              | True          |

## Versão aceita: comparação retrospectiva em 2026

| particao   | alvo      |   h | regime   |   MAE_novo_cm |   MAE_anterior_cm |   ganho_pct |
|:-----------|:----------|----:|:---------|--------------:|------------------:|------------:|
| teste      | Encantado |   6 | alto     |          28.5 |              45.5 |        37.4 |
| teste      | Encantado |   6 | descida  |          15.9 |              27.5 |        42.1 |
| teste      | Encantado |   6 | rapida   |          35.9 |              77.3 |        53.6 |
| teste      | Encantado |   6 | subida   |          46.2 |              70.7 |        34.7 |
| teste      | Encantado |   9 | alto     |          47.3 |              47.3 |         0   |
| teste      | Encantado |   9 | descida  |          17.6 |              17.6 |         0   |
| teste      | Encantado |   9 | rapida   |          59   |              59   |         0   |
| teste      | Encantado |   9 | subida   |          85.6 |              85.6 |         0   |
| teste      | Encantado |  12 | alto     |          74.2 |              74.2 |         0   |
| teste      | Encantado |  12 | descida  |          30.7 |              30.7 |         0   |
| teste      | Encantado |  12 | rapida   |          85   |              85   |         0   |
| teste      | Encantado |  12 | subida   |         129.6 |             129.6 |         0   |
| teste      | Estrela   |   6 | alto     |          24.3 |              24.3 |         0   |
| teste      | Estrela   |   6 | descida  |          18   |              18   |         0   |
| teste      | Estrela   |   6 | rapida   |          38.8 |              38.8 |         0   |
| teste      | Estrela   |   6 | subida   |          31.6 |              31.6 |         0   |
| teste      | Estrela   |   9 | alto     |          39.9 |              39.9 |         0   |
| teste      | Estrela   |   9 | descida  |          23.5 |              23.5 |         0   |
| teste      | Estrela   |   9 | rapida   |          55.8 |              55.8 |         0   |
| teste      | Estrela   |   9 | subida   |          56.7 |              56.7 |         0   |
| teste      | Estrela   |  12 | alto     |          59.1 |              59.1 |         0   |
| teste      | Estrela   |  12 | descida  |          30   |              30   |         0   |
| teste      | Estrela   |  12 | rapida   |          68.8 |              68.8 |         0   |
| teste      | Estrela   |  12 | subida   |          86.2 |              86.2 |         0   |
| teste      | Muçum     |   6 | alto     |          37.3 |              37.3 |         0   |
| teste      | Muçum     |   6 | descida  |          18.7 |              18.7 |         0   |
| teste      | Muçum     |   6 | rapida   |          54.1 |              54.1 |         0   |
| teste      | Muçum     |   6 | subida   |          54.2 |              54.2 |         0   |
| teste      | Muçum     |   9 | alto     |          63.2 |              63.2 |         0   |
| teste      | Muçum     |   9 | descida  |          53   |              53   |         0   |
| teste      | Muçum     |   9 | rapida   |          82.4 |              82.4 |         0   |
| teste      | Muçum     |   9 | subida   |          82.6 |              82.6 |         0   |
| teste      | Muçum     |  12 | alto     |          92.3 |              92.3 |         0   |
| teste      | Muçum     |  12 | descida  |          74   |              74   |         0   |
| teste      | Muçum     |  12 | rapida   |          83   |              83   |         0   |
| teste      | Muçum     |  12 | subida   |         133.8 |             133.8 |         0   |

## Cobertura bruta das faixas em 2026

A tabela mede a faixa calibrada antes dos bloqueios de publicação. Na rodada, faixas também são omitidas fora das velocidades vistas na calibração ou quando menos de 80% dos últimos erros conhecidos cabem nas faixas (mínimo três pares nas últimas seis horas). Isso não corrige a previsão pontual nem cria garantia estatística.

| alvo      |   h | subida_rapida   |   cobertura |    n |   n_com_faixa |   margem_cm |
|:----------|----:|:----------------|------------:|-----:|--------------:|------------:|
| Encantado |   6 | False           |       0.862 | 1021 |          1021 |      31.598 |
| Encantado |   6 | True            |       1     |   37 |            37 |     165.174 |
| Encantado |   9 | False           |       0.883 | 1018 |          1018 |      53.669 |
| Encantado |   9 | True            |       0.892 |   37 |            37 |     180.816 |
| Encantado |  12 | False           |       0.879 | 1015 |          1015 |      71.732 |
| Encantado |  12 | True            |       0.838 |   37 |            37 |     198.161 |
| Estrela   |   6 | False           |       0.837 | 1039 |          1039 |      32.121 |
| Estrela   |   6 | True            |     nan     |   27 |             0 |     nan     |
| Estrela   |   9 | False           |       0.862 | 1036 |          1036 |      51.618 |
| Estrela   |   9 | True            |     nan     |   27 |             0 |     nan     |
| Estrela   |  12 | False           |       0.88  | 1033 |          1033 |      73.652 |
| Estrela   |  12 | True            |     nan     |   27 |             0 |     nan     |
| Muçum     |   6 | False           |       0.899 |  992 |           992 |      48.094 |
| Muçum     |   6 | True            |       0.868 |   38 |            38 |     151.209 |
| Muçum     |   9 | False           |       0.886 |  989 |           989 |      78.369 |
| Muçum     |   9 | True            |       0.816 |   38 |            38 |     184.136 |
| Muçum     |  12 | False           |       0.905 |  986 |           986 |     107.566 |
| Muçum     |  12 | True            |       0.816 |   38 |            38 |     214.432 |

Reprodução: `uv run python -m src.live.improve`. [Métricas por evento](12_melhoria_metricas.csv), [comparação por partição](12_melhoria_comparacao.csv).
