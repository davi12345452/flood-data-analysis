# Pipeline reprodutível — cada alvo é idempotente (cache em data/raw/)
.PHONY: all ingest ingest-ons ingest-ana ingest-sace ingest-merge-daily ingest-merge-events reference coverage qc qc-report spatial test

all: ingest reference coverage qc qc-report spatial features dataset baselines

qc:
	uv run python -m src.qc.ana
	uv run python -m src.qc.ons

qc-report:
	uv run python -m src.qc.report

spatial:
	uv run python -m src.spatial.stations
	uv run python -m src.spatial.basins
	uv run python -m src.spatial.merge_agg all

ingest: ingest-ons ingest-ana ingest-sace ingest-merge-daily ingest-merge-events

ingest-ons:
	uv run python -m src.ingest.ons

ingest-ana:
	uv run python -m src.ingest.ana_soap

ingest-sace:
	uv run python -m src.ingest.sace

ingest-merge-daily:
	uv run python -m src.ingest.merge daily

ingest-merge-events:
	uv run python -m src.ingest.merge events

reference:
	uv run python -m src.ingest.reference

coverage:
	uv run python -m src.ingest.coverage

test:
	uv run pytest tests/ -q

features:
	uv run python -m src.features.build

dataset:
	uv run python -m src.dataset.events
	uv run python -m src.ingest.merge windows
	uv run python -m src.spatial.merge_agg windows
	uv run python -m src.features.build
	uv run python -m src.dataset.build

baselines:
	uv run python -m src.eval.run_baselines
	uv run python -m src.ingest.sace_forecasts
	uv run python -m src.eval.sace_benchmark
