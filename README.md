# flood-data-analysis

Modelo de previsão de cota de cheia no Vale do Taquari (RS), a partir de chuva observada e
vazão defluente das usinas do rio das Antas.

> **Este é um projeto de pesquisa pessoal. NÃO é um sistema de alerta oficial e nada aqui
> deve ser usado para decisão de evacuação.** Ver `LIMITACOES.md`.

## Estado: concluído (Fases 0–9)

**Resultado em uma linha:** regressão linear com lags bate tudo (inclusive a previsão
oficial do SACE, pareada nas mesmas horas) em horizontes ≤6h; LightGBM raso vence em
12–24h mas subestima picos recordes; o teto físico de ~12h com chuva observada é real
e está medido.

- **Síntese e balanço:** [`reports/final.md`](reports/final.md)
- **Limitações medidas:** [`LIMITACOES.md`](LIMITACOES.md)
- Trilha completa: `reports/00_fontes.md` → `08_avaliacao.md` (uma por fase),
  figuras em `reports/figs/`.

## Setup

Requer [uv](https://docs.astral.sh/uv/) e, para o LightGBM/GRIB2 no macOS,
`brew install libomp eccodes`:

```bash
uv sync --all-extras   # base + geo (xarray/cfgrib/geopandas) + ml (lightgbm) + dev
```

## Uso

```bash
make all          # reconstrói todo o pipeline a partir do cache (ordem correta)
make test         # 61 testes (QC, alinhamento temporal, zero-como-NaN, features...)

# alvos individuais, na ordem do pipeline:
make ingest       # download bruto (idempotente; ~12 GB na primeira vez)
make reference    # cotas de referência (SACE×RIGEO, validação cruzada)
make coverage     # relatório de cobertura por estação
make qc qc-report # QC, fusos, grade horária UTC
make spatial      # sub-bacias + agregação do MERGE
make features     # pool de 77 features causais
make dataset      # eventos + janelas + datasets supervisionados
make baselines    # persistência, regressão, propagação, SACE
make model        # LightGBM em CV por evento
make evaluation   # detecção, picos, hidrogramas, SACE pareado
```

Reexecutar qualquer alvo é seguro: tudo é cache-first e idempotente. Nenhum script de
análise depende de rede depois do `make ingest`.

## Credenciais da ANA (HidroWebService — opcional)

O projeto funciona sem credencial (fonte primária: webservice SOAP legado, aberto).
A API oficial exige credencial individual solicitada por e-mail — ver o
[manual do HidroWebService](https://www.gov.br/ana/pt-br/assuntos/monitoramento-e-eventos-criticos/monitoramento-hidrologico/orientacoes-manuais/manuais/manual-hidrowebservice_publica.pdf)
e o rascunho pronto em `reports/email_ana_credencial.md`. Com a credencial, crie um
`.env` na raiz (não versionado):

```
ANA_IDENTIFICADOR=...
ANA_SENHA=...
```

O cliente (`src/ingest/ana_hws.py`) liga sozinho quando o `.env` existe. A API legada
REST do HidroWeb **foi desativada** (verificado em 2026-07-28: 401 em toda a árvore
`/hidroweb/rest/api/`).

## Estrutura

```
data/raw/        download bruto + .meta.json de proveniência, nunca editado
data/interim/    pós-QC (grade horária UTC) e chuva agregada por sub-bacia
data/processed/  features, datasets supervisionados, previsões por fold
data/reference/  cotas de referência, sub-bacias (GPKG), coordenadas
src/ingest/      um módulo por fonte (ana_soap, ana_hws, ons, merge, sace...)
src/qc/          flags, fusos e alinhamento temporal
src/spatial/     delineamento e agregação espacial
src/features/    engenharia de features (causalidade testada)
src/dataset/     eventos, janelas e montagem supervisionada
src/models/      baselines e LightGBM
src/eval/        métricas, CV por evento, figuras e relatórios
config/          estações, janelas, horizontes e hiperparâmetros em YAML
reports/         relatórios por fase + final.md
```
