.PHONY: install deps ingest ingest-incremental ingest-nested transform test build docs lab all orchestrate snapshot seed freshness clean reset

install:		## Install dependencies via uv
	uv sync

deps:			## Install dbt packages
	cd dbt_project && DBT_PROFILES_DIR=. uv run dbt deps

ingest:			## Run main dlt pipeline (ecb_rates)
	uv run python dlt_pipelines/ecb_rates.py

ingest-incremental:	## Run incremental-cursor variant of the ECB pipeline (experiment 09)
	uv run python dlt_pipelines/ecb_rates_incremental.py

ingest-nested:		## Run JSONPlaceholder users pipeline (experiment 12)
	uv run python dlt_pipelines/users_nested.py

transform:		## dbt run only
	cd dbt_project && DBT_PROFILES_DIR=. uv run dbt run

test:			## dbt test only
	cd dbt_project && DBT_PROFILES_DIR=. uv run dbt test

build:			## dbt build = seed + snapshot + run + test
	cd dbt_project && DBT_PROFILES_DIR=. uv run dbt build

seed:			## dbt seed only (experiment 17)
	cd dbt_project && DBT_PROFILES_DIR=. uv run dbt seed

snapshot:		## dbt snapshot only (experiment 16)
	cd dbt_project && DBT_PROFILES_DIR=. uv run dbt snapshot

freshness:		## dbt source freshness (experiment 20)
	cd dbt_project && DBT_PROFILES_DIR=. uv run dbt source freshness

docs:			## Generate + serve dbt docs (lineage graph)
	cd dbt_project && DBT_PROFILES_DIR=. uv run dbt docs generate && DBT_PROFILES_DIR=. uv run dbt docs serve

lab:			## Launch JupyterLab for experiments/ notebooks
	uv run jupyter lab --notebook-dir=experiments

orchestrate:		## End-to-end Python entrypoint (experiment 15/26)
	uv run python orchestration.py

all: ingest build	## Full pipeline: ingest + dbt build

clean:			## Remove dbt artifacts
	rm -rf dbt_project/target dbt_project/dbt_packages dbt_project/logs prod_state

reset:			## Nuke the DuckDB file (start fresh)
	rm -f data/sandbox.duckdb data/sandbox.duckdb.wal
	rm -rf data/lake
