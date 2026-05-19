"""ECB exchange rates ingestion: fetches EUR-based daily rates from Frankfurter API."""

import datetime
from typing import Iterator

import dlt
import requests


CURRENCIES = ["USD", "GBP", "CHF", "JPY", "CNY"]

CURRENCY_NAMES = {
    "USD": "US Dollar",
    "GBP": "British Pound",
    "CHF": "Swiss Franc",
    "JPY": "Japanese Yen",
    "CNY": "Chinese Yuan",
}


@dlt.resource(write_disposition="replace", name="currencies_meta")
def currencies_meta() -> Iterator[dict]:
    """Static reference data: currency code and full name."""
    for code, name in CURRENCY_NAMES.items():
        yield {"code": code, "name": name}


@dlt.resource(
    write_disposition="merge",
    primary_key=["date", "currency"],
    name="daily_rates",
)
def daily_rates() -> Iterator[dict]:
    """Daily EUR-based exchange rates in long format (one row per date/currency)."""
    symbols = ",".join(CURRENCIES)
    start = "2024-01-01"
    end = datetime.date.today().isoformat()
    url = f"https://api.frankfurter.app/{start}..{end}?to={symbols}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    for date_str, rates in data["rates"].items():
        for currency, rate in rates.items():
            yield {"date": date_str, "currency": currency, "rate": rate}


@dlt.source(name="ecb")
def ecb_source():
    """ECB rates source: daily_rates + currencies_meta."""
    return [daily_rates(), currencies_meta()]


if __name__ == "__main__":
    pipeline = dlt.pipeline(
        pipeline_name="ecb_rates_pipeline",
        destination=dlt.destinations.duckdb("data/sandbox.duckdb"),
        dataset_name="raw_ecb",
    )
    load_info = pipeline.run(ecb_source())
    print(load_info)
