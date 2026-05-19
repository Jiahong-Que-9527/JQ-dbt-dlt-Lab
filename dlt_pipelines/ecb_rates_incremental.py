"""Incremental version of the ECB pipeline using dlt.sources.incremental.

Difference from `ecb_rates.py`:
  - Uses `dlt.sources.incremental("date", initial_value="2024-01-01")` to track the
    high-water mark across runs. State is persisted in `_dlt_pipeline_state`.
  - Only fetches days strictly after `incremental.last_value` on each run.
  - First run pulls everything from `initial_value` to today; subsequent runs are tiny.

In production this is how you avoid re-pulling 100% of the upstream on every schedule tick.
"""

import datetime
from typing import Iterator

import dlt
import requests


CURRENCIES = ["USD", "GBP", "CHF", "JPY", "CNY"]


@dlt.resource(
    write_disposition="merge",
    primary_key=["date", "currency"],
    name="daily_rates",
)
def daily_rates(
    cursor=dlt.sources.incremental(
        "date",
        initial_value="2024-01-01",
    ),
) -> Iterator[dict]:
    """Incrementally pull EUR-based daily rates. State carries the max(date) seen so far."""
    start = cursor.last_value or "2024-01-01"
    end = datetime.date.today().isoformat()

    if start >= end:
        # nothing new since last run
        return

    symbols = ",".join(CURRENCIES)
    url = f"https://api.frankfurter.app/{start}..{end}?to={symbols}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    for date_str, rates in data["rates"].items():
        for currency, rate in rates.items():
            yield {"date": date_str, "currency": currency, "rate": rate}


@dlt.source(name="ecb_incremental")
def ecb_incremental_source():
    """ECB rates as an incremental source (date-cursor based)."""
    return [daily_rates()]


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="ecb_rates_incremental",
        destination=dlt.destinations.duckdb("data/sandbox.duckdb"),
        dataset_name="raw_ecb_inc",
    )
    load_info = pipeline.run(ecb_incremental_source())
    print(load_info)
