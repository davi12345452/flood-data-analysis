# Dependências reais; um escritor por vez, inclusive com make -j.
.NOTPARALLEL:
.PHONY: all ingest ingest-ons ingest-ana ingest-sace ingest-merge-daily ingest-merge-events reference coverage qc qc-report spatial spatial-base windows ingest-windows features dataset baselines model evaluation test live-validate revalidate
RUN = uv run python -m src.core.execute
# OFFLINE=1 proíbe HTTP; caches ausentes são erros, nunca downloads implícitos.
OFFLINE ?= 0
export FLOOD_OFFLINE = $(OFFLINE)

all: evaluation qc-report coverage

ingest: ingest-ons ingest-ana ingest-sace ingest-merge-daily ingest-merge-events

ingest-ons:
	$(RUN) src.ingest.ons

ingest-ana:
	$(RUN) src.ingest.ana_soap

ingest-sace:
	$(RUN) src.ingest.sace

ingest-merge-daily:
	$(RUN) src.ingest.merge daily

ingest-merge-events:
	$(RUN) src.ingest.merge events

reference: ingest-sace
	$(RUN) src.ingest.reference

coverage: ingest
	$(RUN) src.ingest.coverage

qc: ingest-ana ingest-ons
	$(RUN) src.qc.ana, src.qc.ons

qc-report: qc reference
	$(RUN) src.qc.report

spatial-base: ingest-merge-daily ingest-merge-events
	$(RUN) src.spatial.stations, src.spatial.basins, src.spatial.merge_agg all

windows: qc reference
	$(RUN) src.dataset.events

ingest-windows: windows
	$(RUN) src.ingest.merge windows

spatial: spatial-base ingest-windows
	$(RUN) src.spatial.merge_agg windows

features: spatial qc reference
	$(RUN) src.features.build

dataset: features windows
	$(RUN) src.dataset.build

baselines: dataset ingest-sace
	$(RUN) src.eval.run_baselines, src.ingest.sace_forecasts, src.eval.sace_benchmark

model: baselines
	$(RUN) src.eval.run_model

evaluation: model
	$(RUN) src.eval.figures, src.eval.run_full_eval

live-validate: dataset
	$(RUN) src.live.evaluate, src.live.improve

# Migração/reavaliação com os interims e janelas já materializados.
# Preserva o conjunto de eventos e funciona sem o cache bruto completo.
revalidate:
	FLOOD_OFFLINE=1 $(RUN) src.features.build, src.dataset.build, src.eval.run_baselines, src.eval.run_model, src.eval.figures, src.eval.run_full_eval, src.live.evaluate, src.live.improve

test:
	uv run pytest tests/ -q
