# dlt + dbt Sandbox: Implementation Spec

> **For code agent**: This document specifies a learning sandbox project. The goal is **familiarization**, not production-readiness. Optimize for clarity and minimal moving parts. Do not over-engineer.

---

## 1. Project Goal

Build a minimal but complete ELT pipeline using **dlt** (extract + load) and **dbt** (transform) on **DuckDB**. The owner will use this repo to understand the core concepts and workflows of both tools before integrating them into a larger lakehouse system.

**Explicit non-goals**:
- No Iceberg, no Trino, no MinIO, no Dagster, no Airflow.
- No Docker. Everything runs locally with Python + DuckDB file.
- No CI/CD, no production hardening.
- No regulatory/compliance framing in code or docs.

If a design choice trades simplicity for "future flexibility", choose simplicity.

---

## 2. Tech Stack (Fixed — do not substitute)

| Layer | Choice | Reason |
|---|---|---|
| Package manager | `uv` | Fast, modern, single tool for env + deps |
| Python | 3.11 or 3.12 | dlt + dbt-duckdb compatibility |
| Ingestion | `dlt[duckdb]` (latest stable) | Python-native, simple |
| Storage | DuckDB (single `.duckdb` file) | Zero infrastructure |
| Transformation | `dbt-core` + `dbt-duckdb` | Same DuckDB file as dlt |
| Data source | Frankfurter API (https://api.frankfurter.app) | Free, no auth, JSON, ECB-backed rates |

**If a dependency version is unclear, use the latest stable as of the build date and pin it in `pyproject.toml`.**

---

## 3. Repository Structure

```
dlt-dbt-sandbox/
├── .gitignore
├── .python-version              # for uv
├── pyproject.toml               # uv-managed
├── README.md                    # see Section 8
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
    ├── seeds/                   # empty for now, but create the dir
    └── tests/                   # empty for now, but create the dir
```

**Rules**:
- `data/sandbox.duckdb` must be gitignored. The `data/` directory itself is kept via `.gitkeep`.
- dbt `profiles.yml` lives **inside** the repo (not in `~/.dbt/`) and uses a relative path. This makes the repo self-contained for learning.
- Set `DBT_PROFILES_DIR=./dbt_project` in the Makefile so dbt picks up the local profile.

---

## 4. dlt Pipeline Spec

**File**: `dlt_pipelines/ecb_rates.py`

**Requirements**:
1. Fetch daily exchange rates from Frankfurter API for **USD, GBP, CHF, JPY, CNY** against EUR base.
2. Fetch historical data: from `2024-01-01` to today, using the `/{date}` endpoint or `/{from}..{to}` range endpoint.
3. Define **two dlt resources** in one source:
   - `daily_rates`: one row per (date, currency, rate) — long format
   - `currencies_meta`: static reference data (currency code, full name) — hand-coded list of ~5 currencies, fine to hardcode
4. Use `write_disposition="merge"` with `primary_key=["date", "currency"]` for `daily_rates` to demonstrate incremental-style behavior.
5. Use `write_disposition="replace"` for `currencies_meta`.
6. Pipeline name: `ecb_rates_pipeline`. Dataset name: `raw_ecb`. Destination: `duckdb` pointing to `data/sandbox.duckdb`.
7. Include `if __name__ == "__main__":` block so the file can be run with `uv run python dlt_pipelines/ecb_rates.py`.
8. Print a short summary at the end (`pipeline.last_trace` or row counts) so the owner can see something happened.

**Code style**:
- Use `@dlt.source` and `@dlt.resource` decorators (the canonical dlt pattern).
- Type hints required on resource functions.
- One-line docstrings on the source and each resource.
- ~80 lines of code total. If it grows beyond 120, simplify.

**Do not**:
- Add retry logic, rate limiting, or fancy error handling beyond what dlt provides by default.
- Parameterize the date range via CLI args. Hardcode it; the owner will edit the file to experiment.
- Add logging configuration. dlt's default logging is fine.

---

## 5. dbt Project Spec

**Profile** (`dbt_project/profiles.yml`):
```yaml
dlt_dbt_sandbox:
  target: dev
  outputs:
    dev:
      type: duckdb
      path: ../data/sandbox.duckdb
      threads: 4
```

**Project config** (`dbt_project/dbt_project.yml`):
- `name: dlt_dbt_sandbox`
- `profile: dlt_dbt_sandbox`
- `models:` config:
  - `staging`: `+materialized: view`
  - `marts`: `+materialized: table`
- Standard dbt 1.7+ layout.

**Packages** (`dbt_project/packages.yml`):
- Include `dbt-labs/dbt_utils` (latest compatible version). The owner will use it for `generate_surrogate_key` or `date_spine` experiments later.

**Sources** (`models/staging/_sources.yml`):
- Declare a source `raw_ecb` with two tables: `daily_rates` and `currencies_meta` (matching what dlt loaded).
- Add 1 test per source table (e.g. `not_null` on `date` for `daily_rates`).

**Staging model** (`models/staging/stg_ecb_rates.sql`):
- Select from `{{ source('raw_ecb', 'daily_rates') }}`.
- Cast types explicitly (date as DATE, rate as DOUBLE).
- Rename columns to snake_case if dlt didn't already.
- Add a `loaded_at` passthrough if dlt populates `_dlt_load_id` — show the owner how dlt's metadata columns surface in dbt.

**Marts**:

`models/marts/dim_currencies.sql`:
- Select from `{{ source('raw_ecb', 'currencies_meta') }}`.
- Simple passthrough with light renaming.

`models/marts/fct_daily_rates.sql`:
- Join `stg_ecb_rates` with `dim_currencies` on currency code.
- Add a computed column: `rate_change_pct` using `LAG(rate) OVER (PARTITION BY currency ORDER BY date)`.
- This demonstrates window functions in dbt — a common real-world pattern.

**Tests** (`models/marts/_marts.yml`):
- `unique` + `not_null` on the composite key of `fct_daily_rates` (use `dbt_utils.unique_combination_of_columns` on `[date, currency]`).
- `not_null` on currency code in `dim_currencies`.
- One `accepted_values` test on currency code listing the 5 supported currencies.

**Total: ~5 SQL files, ~3 YAML files. Keep it tight.**

---

## 6. Makefile (developer ergonomics)

Provide these targets. Each should be a one-liner where possible.

```makefile
.PHONY: install ingest transform docs build clean reset

install:        ## Install dependencies via uv
	uv sync

ingest:         ## Run dlt pipeline to load raw data into DuckDB
	uv run python dlt_pipelines/ecb_rates.py

transform:      ## Run dbt models
	cd dbt_project && uv run dbt run

test:           ## Run dbt tests
	cd dbt_project && uv run dbt test

build:          ## dbt build = run + test in dependency order
	cd dbt_project && uv run dbt build

docs:           ## Generate and serve dbt docs (lineage graph)
	cd dbt_project && uv run dbt docs generate && uv run dbt docs serve

deps:           ## Install dbt packages
	cd dbt_project && uv run dbt deps

all: ingest build  ## Full pipeline: ingest then transform+test

clean:          ## Remove dbt artifacts
	rm -rf dbt_project/target dbt_project/dbt_packages dbt_project/logs

reset:          ## Nuke the DuckDB file (start fresh)
	rm -f data/sandbox.duckdb
```

Make sure `DBT_PROFILES_DIR` is exported in the Makefile or that the `cd dbt_project` covers it via the local `profiles.yml`. Use whichever works cleanly with dbt-core's profile resolution.

---

## 7. pyproject.toml

Minimal `uv`-managed project:

```toml
[project]
name = "dlt-dbt-sandbox"
version = "0.1.0"
description = "Learning sandbox for dlt + dbt on DuckDB"
requires-python = ">=3.11,<3.13"
dependencies = [
    "dlt[duckdb]>=1.0",
    "dbt-core>=1.7",
    "dbt-duckdb>=1.7",
    "requests>=2.31",
]

[dependency-groups]
dev = [
    "ruff>=0.5",
]
```

Pin to **latest stable major versions at build time**. If `dlt` or `dbt-core` has had a breaking version change recently, prefer the most recent stable release and note the version in README.

---

## 8. README.md

Write a README with these sections (concise — total ~150 lines):

1. **What this is** — 2 sentences. Sandbox for learning dlt + dbt. Not production.
2. **Architecture** — one ASCII diagram:
   ```
   Frankfurter API → dlt → DuckDB (raw_ecb schema) → dbt → DuckDB (main schema)
   ```
3. **Setup** — three commands: `uv sync`, `make deps`, `make all`.
4. **Project layout** — paste the tree from Section 3.
5. **What to try (learning prompts)** — a numbered list of ~8 experiments the owner can run to learn. Examples:
   - "Run `make ingest` twice. Inspect the DuckDB tables. What did `merge` disposition do on the second run?"
   - "Change a column type in `stg_ecb_rates.sql`. Run `dbt build`. What happens?"
   - "Add a new currency to the dlt pipeline. Re-run ingest. Did the schema evolve automatically?"
   - "Run `dbt docs serve` and explore the lineage graph. Find your `fct_daily_rates` model."
   - "Break a test on purpose (e.g. change `accepted_values` to exclude USD). Run `dbt test`. Read the failure output."
   - "Change `fct_daily_rates` materialization from `table` to `incremental`. What changes in the generated SQL?"
   - "Inspect `_dlt_load_id` and `_dlt_loads` tables in DuckDB. What metadata does dlt store?"
   - "Run `dlt pipeline ecb_rates_pipeline show` from the CLI. What does it tell you?"
6. **Useful DuckDB CLI commands** — 3-4 commands for inspecting the database directly (`duckdb data/sandbox.duckdb`, `SHOW TABLES`, etc.).
7. **Links** — dlt docs, dbt docs, Frankfurter API docs.

**Tone**: Functional and direct. No marketing language. No "compliance" or "production" framing. This is a learning repo.

---

## 9. .gitignore

```
.venv/
__pycache__/
*.pyc
.python-version

# DuckDB data file
data/*.duckdb
data/*.duckdb.wal

# dbt artifacts
dbt_project/target/
dbt_project/dbt_packages/
dbt_project/logs/

# OS
.DS_Store
```

---

## 10. Acceptance Criteria

The implementation is complete when **all** of the following are true:

- [ ] `uv sync` installs cleanly with no errors.
- [ ] `make deps` installs dbt_utils without errors.
- [ ] `make ingest` runs and creates `data/sandbox.duckdb` with a `raw_ecb` schema containing `daily_rates` and `currencies_meta` tables.
- [ ] `daily_rates` has > 100 rows (at least a year of data for 5 currencies).
- [ ] `make build` runs both `dbt run` and `dbt test` successfully with all tests passing.
- [ ] `make docs` generates and serves the dbt docs site at http://localhost:8080 with a visible lineage graph showing: source → staging → marts.
- [ ] Running `make ingest` a second time does not duplicate data in `daily_rates` (merge disposition works).
- [ ] `make reset && make all` works end-to-end from a clean state.
- [ ] README has all sections from Section 8.

---

## 11. Out of Scope (do not add)

- Authentication, secrets management.
- Multiple environments (dev/prod profiles). Just `dev`.
- Pre-commit hooks, linting CI.
- Docker, docker-compose.
- Any orchestrator (Dagster, Airflow, Prefect).
- Streaming, CDC, Kafka.
- Iceberg, Parquet exports, S3.
- LLM/AI features.
- Dashboards, Superset, Metabase.

If the agent is tempted to add any of the above to "make it more useful", **don't**. The owner will add complexity intentionally in a later phase.

---

## 12. Final Note to Agent

**Prioritize correctness over completeness, and completeness over polish.** A working end-to-end pipeline with 3 models beats a half-finished one with 10 models. Use the acceptance criteria in Section 10 as your definition of done.
