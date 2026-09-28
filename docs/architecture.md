# Arquitetura e contratos

O projeto é um monólito modular executado por etapas, com Parquet como interface
entre ingestão, QC, agregação espacial, features, datasets e avaliação. A execução
ao vivo reutiliza as transformações e os modelos do histórico.

## Dados e atualizações

- Observações usam UTC, timestamps alinhados à hora, chaves únicas por estação ou
  usina e nomes com unidades (`_cm`, `_mm`, `_m3s`). `core.contracts` verifica essas
  condições e rejeita infinitos.
- Atualizações substituem somente chaves efetivamente recebidas. Falha de rede,
  mês ausente ou estação sem resposta preservam o histórico. Um NaN explícito
  recebido continua sendo NaN; ele não é preenchido por uma observação antiga.
- A busca ANA avança por estação, considerando o mês no fuso da fonte. As
  respostas tabulares são mantidas em `data/raw/ana_live/` com proveniência.
- O QC do ONS é uma única função, usada no batch e no live. Atualizações brutas
  recebem metadados e os leitores históricos reconhecem as versões live. A
  resposta com download mais recente vence em cada timestamp, independentemente
  de ter sido obtida pelo batch ou pelo live.
- `core.storage` escreve arquivos temporários únicos e publica por rename. As
  etapas do Make e `live.run` usam o mesmo lock local para evitar escritores
  simultâneos. Execuções diretas de módulos individuais devem ocorrer sem outro
  escritor; prefira `python -m src.core.execute modulo`.

## Ausência de chuva

A agregação de células exige cobertura completa da sub-bacia, e a média por
macro-unidade exige todas as sub-bacias e suas áreas válidas. Ausência parcial ou
total produz NaN. Acumulados horários exigem todas as horas da janela.

O API usa soma exponencial com memória finita: contribuições com peso abaixo de
1% são descartadas. Isso dá 44 dias para k=0,90 e 228 dias para k=0,98. Uma lacuna
invalida o API enquanto estiver dentro dessa memória; o estado inicial anterior
ao histórico é zero. Esse critério permite recuperar a feature depois de um
intervalo conhecido, sem tratar chuva ausente como chuva zero. O cálculo mantém
a regra de usar apenas períodos diários encerrados.

## Validação temporal

A CV histórica continua sendo retrospectiva por evento. Antes de treinar,
remove exemplos cujo intervalo de informação intersecta o teste: o contexto
horário máximo de chuva (120h) e os rótulos até o maior horizonte do dataset.
A mesma purga é aplicada ao split interno de early stopping. Isso elimina
rótulos de treino em horas do teste e sobreposição do contexto horário próximo;
não transforma a CV retrospectiva em um teste cronológico ou torna independentes
processos hidrológicos de longa memória.

Datasets e lags usam buscas por timestamp exato. Buracos na grade nunca encurtam
um horizonte nem aproximam janelas que estavam afastadas no tempo.

O live usa somente janelas inteiras anteriores ao corte, incluindo a maturação
do rótulo. A seleção e a aceitação mantêm as partições documentadas nos relatórios
11 e 12; 2026 continua sendo aceitação já inspecionada, não teste cego.

## Versões e inferência

`core.provenance` vincula cada validação a:

- hashes do código científico, configurações, referências, datasets e `uv.lock`;
- esquema e conteúdo do histórico de features até o último alvo de treino,
  incluindo os antecedentes usados pelas latências;
- versões efetivamente instaladas de Python e bibliotecas numéricas.

Acrescentar horas posteriores ao conjunto validado é permitido. Alterar seu
histórico, esquema, código ou configuração exige refazer a validação. O manifesto
12 também aponta para o hash do manifesto 11. Um manifesto 12 incompatível é
rejeitado, sem troca silenciosa pelo 11.

Manifestos completos ficam em `reports/model_versions/<sha256>.json`; os arquivos
11 e 12 são ponteiros de conveniência. O experimento de melhoria também verifica
se suas previsões base pertencem ao manifesto usado na seleção.

`models.forecast` separa treino (`fit`) de inferência (`Forecast.predict`).
O live reutiliza artefatos em `data/processed/model_cache/` quando treino,
configuração, código e ambiente são idênticos. O identificador do modelo acompanha
cada previsão e o artefato é copiado para o arquivo da execução.

## Arquivo de execução

A execução é construída em `.pending_*`. Apenas depois de copiar previsões,
features, modelos, datasets, referências, código, configuração e hashes o
diretório recebe o nome `emissao_*` ou `replay_*`. Leitores não veem execuções
parciais. O `meta.json` registra `estado: completo` e o ambiente numérico.

O layout das dependências é preservado dentro do arquivo. Para reproduzir uma
nova execução arquivada, use o ambiente registrado, entre no diretório da
execução e rode:

```bash
python -m src.live.run --sem-atualizar --frame features.parquet
```

O replay recebe uma nova pasta e nunca conta como emissão. Arquivos antigos
continuam disponíveis para conferência, mas antecedem essas garantias de layout.

## Comandos

`make all` declara as dependências completas; `make model` prepara suas entradas.
O Make é serial mesmo com `-j`, porque várias etapas consolidam os mesmos dados.
Downloads de referência/geometria e de chuva das janelas podem acontecer depois
da ingestão inicial. `OFFLINE=1` bloqueia HTTP nos adaptadores comuns, sem baixar
recursos faltantes; cache incompleto pode impedir uma reconstrução integral.

Para recalcular as métricas mantendo interims e janelas já materializados:

```bash
make revalidate
```

Esse alvo não busca fontes nem redefine os eventos. Recria features e datasets,
avalia baselines/GBM, gera figuras e relatórios e refaz as políticas live. É também
a rota para instalações que mantêm interims históricos, mas não todo o cache GRIB.
`make live-validate` prepara o dataset e refaz a política live no pipeline completo.
