"""End-to-end orchestration: run dlt ingest, then dbt build, in one Python entrypoint.

This is the "no-orchestrator" pattern — what teams write before they reach for Airflow
or Dagster. It's also what you'd put inside a Dagster `@asset` or Airflow `PythonOperator`
body, so the same code carries forward.

Run:
    uv run python orchestration.py
"""

import subprocess
import sys
from pathlib import Path

import dlt

from dlt_pipelines.ecb_rates import ecb_source

ROOT = Path(__file__).parent
DBT_DIR = ROOT / "dbt_project"


def run_dlt() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="ecb_rates_pipeline",
        destination=dlt.destinations.duckdb(str(ROOT / "data" / "sandbox.duckdb")),
        dataset_name="raw_ecb",
    )
    load_info = pipeline.run(ecb_source())
    print(load_info)
    # fail fast if any package failed to load
    if load_info.has_failed_jobs:
        raise RuntimeError(f"dlt load had failed jobs: {load_info}")


def run_dbt(*args: str) -> None:
    cmd = ["uv", "run", "dbt", *args]
    print(f"$ {' '.join(cmd)}  (cwd={DBT_DIR})")
    result = subprocess.run(
        cmd,
        cwd=DBT_DIR,
        env={**__import__("os").environ, "DBT_PROFILES_DIR": "."},
    )
    if result.returncode != 0:
        raise RuntimeError(f"dbt {' '.join(args)} failed (exit {result.returncode})")


def main() -> None:
    run_dlt()
    run_dbt("deps")
    run_dbt("build")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ORCHESTRATION FAILED: {e}", file=sys.stderr)
        sys.exit(1)
