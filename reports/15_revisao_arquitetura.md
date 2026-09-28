# Revisão de arquitetura — 28/09/2026

Foram corrigidos a substituição global do histórico na ingestão live, o tratamento
de chuva ausente como zero, a sobreposição temporal na avaliação, a falta de
vínculo entre política validada e seus insumos e a ordem implícita do Makefile.

A atualização preserva observações de estações e meses que não responderam;
réguas atrasadas têm seu próprio ponto de retomada. QC ONS é compartilhado entre
batch/live. Respostas com download mais recente têm precedência em cada
observação, independentemente do modo de coleta. Cache bruto possui hashes.

Chuva espacial e acumulados horários exigem cobertura completa. O API tem memória
exponencial finita até peso de 1%, com NaN durante a influência de lacunas. CV e
early stopping removem intervalos que compartilham rótulos ou contexto horário
com o teste. Buscas de alvos e lags usam timestamps exatos.

Treino e inferência foram separados. Modelos reutilizáveis, políticas e execuções
possuem identificadores e proveniência. Manifestos incompatíveis são rejeitados;
arquivos são gravados atomicamente e execuções incompletas não são publicadas.
O Make declara suas dependências e coordena escritores com o live.

Detalhes e reprodução em [docs/architecture.md](../docs/architecture.md).

## Reavaliação histórica

Usamos os interims locais e as mesmas janelas amostradas. Não houve download nem
redetecção de eventos. O pool atual já continha observações além do pool antigo;
isso recuperou 75 linhas por estação nas janelas existentes. Os números abaixo
refletem o conjunto das correções, a purga também no early stopping e a semente
explícita dos modelos; não isolam causalmente o efeito de uma mudança.

Os interims de chuva foram reaproveitados: esta rodada não reconstrói todos os
GRIBs históricos, cujo cache bruto completo não está nesta instalação. A nova
regra de cobertura por célula foi verificada com teste da função de agregação;
a cobertura de agregados antigos não pode ser recuperada sem os GRIBs originais.

| alvo      |   linhas_antes |   linhas_depois |   eventos |   rotulos_treino_em_horas_teste_24h |
|:----------|---------------:|----------------:|----------:|------------------------------------:|
| Muçum     |          26217 |           26292 |        59 |                                   0 |
| Encantado |          24038 |           24113 |        57 |                                   0 |
| Estrela   |          16229 |           16304 |        38 |                                   0 |

A inspeção anterior encontrou 947 linhas de treino com rótulo de 24h em horas do
teste (389 Muçum, 340 Encantado, 218 Estrela). Após a purga, esse total é zero.
A CV continua retrospectiva, e não substitui a avaliação cronológica.

## Regressão linear — comparação de MAE (cm)

| alvo      |   h |   MAE_cm_antes |   MAE_cm_depois |
|:----------|----:|---------------:|----------------:|
| Encantado |   3 |          6.491 |           6.515 |
| Encantado |   6 |         18.343 |          18.404 |
| Encantado |  12 |         42.13  |          42.238 |
| Encantado |  24 |         75.751 |          75.589 |
| Estrela   |   3 |          6.986 |           7     |
| Estrela   |   6 |         13.42  |          13.445 |
| Estrela   |  12 |         28.263 |          28.336 |
| Estrela   |  24 |         58.663 |          58.628 |
| Muçum     |   3 |         11.01  |          11.019 |
| Muçum     |   6 |         21.365 |          21.385 |
| Muçum     |  12 |         48.968 |          49.094 |
| Muçum     |  24 |         92.145 |          91.901 |

## GBM completo — comparação

| alvo      |   h |   MAE_cm_antes |   MAE_cm_depois |   NSE_antes |   NSE_depois |
|:----------|----:|---------------:|----------------:|------------:|-------------:|
| Encantado |   3 |         16.886 |          17.817 |       0.973 |        0.962 |
| Encantado |   6 |         20.412 |          20.664 |       0.969 |        0.964 |
| Encantado |  12 |         31.692 |          32.957 |       0.938 |        0.934 |
| Encantado |  24 |         58.662 |          60.362 |       0.767 |        0.757 |
| Estrela   |   3 |         18.842 |          19.321 |       0.91  |        0.909 |
| Estrela   |   6 |         21.177 |          21.853 |       0.925 |        0.919 |
| Estrela   |  12 |         30.088 |          29.993 |       0.883 |        0.881 |
| Estrela   |  24 |         55.159 |          56.393 |       0.686 |        0.679 |
| Muçum     |   3 |         14.722 |          14.734 |       0.981 |        0.981 |
| Muçum     |   6 |         21.32  |          20.94  |       0.968 |        0.969 |
| Muçum     |  12 |         35.743 |          35.869 |       0.935 |        0.934 |
| Muçum     |  24 |         68.013 |          67.771 |       0.778 |        0.78  |

Relatórios 06–08 e suas figuras foram regenerados. Os estudos de eventos e as
emissões históricas mantêm os números efetivamente produzidos naquele momento;
não foram reescritos como se usassem esta revisão.

A cópia local anterior está em `data/processed/architecture_before_20260928/`.


## Validação final

- 107 testes aprovados; Ruff e `git diff --check` sem erros.
- Relatórios 11 e 12 e políticas de modelos regenerados após a última alteração
  de código. Ambos os manifestos conferidos contra seus arquivos atuais, sem
  divergências. A primeira execução de validação foi corretamente rejeitada
  quando o código de ingestão/QC mudou durante a revisão; somente a rodada
  posterior completa foi usada no replay final.
- Avaliação de cenários recalculada no pool atual: 96 linhas no relatório 14,
  sem consultar modelos meteorológicos externos.
- Replay completo gerado sem atualizar fontes e sem registrar emissão real.
- Arquivo reproduzido em seu próprio diretório, usando apenas features, dados,
  modelos e código copiados: 12 previsões e 576 pares de replay idênticos,
  comparados sem tolerância numérica. Os 12 modelos treinados foram preservados.
- Integridade de 93 arquivos verificada pelos hashes do arquivo de execução.

Arquivo local verificado: `data/processed/live_runs/replay_20260928T213203287676Z`.

Comandos principais executados: `pytest tests/ -q`, `ruff check src tests`,
`make -n -j4 all`, reconstrução de features/datasets, baselines e GBM,
avaliação histórica completa, `src.live.evaluate`, `src.live.improve` e
`src.live.run --sem-atualizar`. As etapas de dados/modelos usaram o executor
com lock; a avaliação independente de cenários leu o mesmo pool congelado.
