.PHONY: install deps ingest transform test build docs lab all clean reset

install:		## Install dependencies via uv
	uv sync

deps:			## Install dbt packages
	cd dbt_project && DBT_PROFILES_DIR=. uv run dbt deps

ingest:			## Run dlt pipeline to load raw data into DuckDB
	uv run python dlt_pipelines/ecb_rates.py

transform:		## Run dbt models
	cd dbt_project && DBT_PROFILES_DIR=. uv run dbt run

test:			## Run dbt tests
	cd dbt_project && DBT_PROFILES_DIR=. uv run dbt test

build:			## dbt build = run + test in dependency order
	cd dbt_project && DBT_PROFILES_DIR=. uv run dbt build

docs:			## Generate and serve dbt docs (lineage graph)
	cd dbt_project && DBT_PROFILES_DIR=. uv run dbt docs generate && DBT_PROFILES_DIR=. uv run dbt docs serve

lab:			## Launch JupyterLab for experiments/ notebooks
	uv run jupyter lab --notebook-dir=experiments

all: ingest build	## Full pipeline: ingest then transform+test

clean:			## Remove dbt artifacts
	rm -rf dbt_project/target dbt_project/dbt_packages dbt_project/logs

reset:			## Nuke the DuckDB file (start fresh)
	rm -f data/sandbox.duckdb
