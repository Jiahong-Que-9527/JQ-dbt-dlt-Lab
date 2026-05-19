# dlt + dbt Sandbox

Learning sandbox for dlt + dbt on DuckDB. Not production.

---

## Architecture

```
Frankfurter API → dlt → DuckDB (raw_ecb schema) → dbt → DuckDB (main schema)
```

- **dlt** fetches EUR-based exchange rates from the [Frankfurter API](https://api.frankfurter.app) and loads them into a local DuckDB file.
- **dbt** reads from that same file, applies transformations, and writes clean models back into DuckDB.

Versions used: dlt 1.27.0, dbt-core 1.11.10, dbt-duckdb 1.10.1, DuckDB 1.5.2.

---

## Setup

```bash
uv sync        # install Python dependencies
make deps      # install dbt packages (dbt_utils)
make all       # ingest raw data + run dbt build
```

---

## Project layout

```
dlt-dbt-sandbox/
├── .gitignore
├── .python-version              # for uv
├── pyproject.toml               # uv-managed
├── README.md
├── Makefile                     # convenience targets
├── data/
│   └── .gitkeep                 # sandbox.duckdb lives here (gitignored)
├── dlt_pipelines/
│   ├── __init__.py
│   └── ecb_rates.py             # the dlt pipeline
└── dbt_project/
    ├── dbt_project.yml
    ├── profiles.yml             # points to ../data/sandbox.duckdb
    ├── packages.yml             # dbt_utils
    ├── models/
    │   ├── staging/
    │   │   ├── _sources.yml     # declare dlt-loaded tables as sources
    │   │   ├── _staging.yml     # tests + descriptions
    │   │   └── stg_ecb_rates.sql
    │   └── marts/
    │       ├── _marts.yml
    │       ├── fct_daily_rates.sql
    │       └── dim_currencies.sql
    ├── seeds/
    └── tests/
```

---

## Makefile targets

| Target | What it does |
|---|---|
| `make install` | `uv sync` — install Python deps |
| `make deps` | `dbt deps` — install dbt_utils |
| `make ingest` | Run dlt pipeline, load raw data |
| `make build` | `dbt build` = run + test all models |
| `make test` | `dbt test` only |
| `make docs` | Generate + serve dbt lineage docs |
| `make all` | `ingest` then `build` |
| `make clean` | Remove dbt artifacts |
| `make reset` | Delete DuckDB file (start fresh) |

---

## What to try (learning prompts)

1. Run `make ingest` twice. Inspect the DuckDB tables. What did `merge` disposition do on the second run?
2. Change a column type in `stg_ecb_rates.sql`. Run `dbt build`. What happens?
3. Add a new currency to the dlt pipeline. Re-run ingest. Did the schema evolve automatically?
4. Run `make docs` and explore the lineage graph. Find your `fct_daily_rates` model.
5. Break a test on purpose (e.g. change `accepted_values` to exclude USD). Run `make test`. Read the failure output.
6. Change `fct_daily_rates` materialization from `table` to `incremental`. What changes in the generated SQL?
7. Inspect `_dlt_load_id` and `_dlt_loads` tables in DuckDB. What metadata does dlt store?
8. Run `dlt pipeline ecb_rates_pipeline show` from the CLI. What does it tell you?

---

## Useful DuckDB CLI commands

```sql
-- Open the database
duckdb data/sandbox.duckdb

-- See all schemas
SHOW DATABASES;

-- Raw tables loaded by dlt
SHOW TABLES FROM raw_ecb;

-- dbt output tables
SHOW TABLES;

-- Inspect data
SELECT * FROM main.fct_daily_rates LIMIT 5;
SELECT * FROM raw_ecb.daily_rates LIMIT 5;

-- dlt metadata
SELECT * FROM raw_ecb._dlt_loads;
```

---

## Links

- [dlt documentation](https://dlthub.com/docs)
- [dbt documentation](https://docs.getdbt.com)
- [Frankfurter API](https://api.frankfurter.app)
