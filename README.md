# flood-data-analysis

Modelo de previsão de cota de cheia no Vale do Taquari (RS), a partir de chuva observada e
vazão defluente das usinas do rio das Antas.

> **Este é um projeto de pesquisa pessoal. NÃO é um sistema de alerta oficial e nada aqui
> deve ser usado para decisão de evacuação.** Ver `LIMITACOES.md`.

## Estado atual

**Fase 0 concluída** — reconhecimento de fontes. Ver `reports/00_fontes.md` para o status
detalhado de cada fonte e a lista de bloqueios.

## Setup

Requer [uv](https://docs.astral.sh/uv/):

```bash
uv sync --extra dev        # base + testes
uv sync --all-extras       # inclui geo (xarray/cfgrib/geopandas) e ml (lightgbm)
```

## Credenciais da ANA (HidroWebService)

A API oficial da ANA exige credencial individual, solicitada por e-mail à ANA — ver o
[manual do HidroWebService](https://www.gov.br/ana/pt-br/assuntos/monitoramento-e-eventos-criticos/monitoramento-hidrologico/orientacoes-manuais/manuais/manual-hidrowebservice_publica.pdf).
Com a credencial em mãos, crie um `.env` na raiz (não versionado):

```
ANA_IDENTIFICADOR=...
ANA_SENHA=...
```

A API legada do HidroWeb (sem token) **foi desativada** — verificado em 2026-07-28; toda a
árvore `/hidroweb/rest/api/` devolve 401.

## Estrutura

```
data/raw/        download bruto + .meta.json de proveniência, nunca editado
data/interim/    pós-QC
data/processed/  dataset supervisionado final
data/reference/  cotas de referência, shapefiles, metadados de estações
src/ingest/      um módulo por fonte (ana, cemaden, merge, ons, sace)
src/qc/          controle de qualidade e alinhamento temporal
src/features/    engenharia de features
src/models/      baselines e modelo
src/eval/        métricas e relatórios
config/          estações, janelas e horizontes em YAML
reports/         relatórios por fase
```
