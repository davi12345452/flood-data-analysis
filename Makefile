# Pipeline reprodutível — cada alvo é idempotente (cache em data/raw/)
.PHONY: all ingest ingest-ons ingest-ana ingest-sace ingest-merge-daily ingest-merge-events reference coverage test

all: ingest reference coverage

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
