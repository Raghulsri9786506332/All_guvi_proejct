"""Persist validated stock data in SQLite for SQL and Power BI use."""
from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd


def write_database(data: pd.DataFrame, sectors: pd.DataFrame, destination: str | Path) -> None:
    """Replace the SQLite daily_prices and sectors tables atomically."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    try:
        with closing(sqlite3.connect(temporary)) as connection:
            with connection:
                data.to_sql("daily_prices", connection, if_exists="replace", index=False)
                sectors.to_sql("sectors", connection, if_exists="replace", index=False)
                connection.execute(
                    "CREATE INDEX IF NOT EXISTS idx_daily_prices_symbol_date "
                    "ON daily_prices(symbol, date)"
                )
                connection.execute(
                    "CREATE VIEW IF NOT EXISTS stock_latest AS "
                    "SELECT d.* FROM daily_prices d "
                    "JOIN (SELECT symbol, MAX(date) AS latest_date "
                    "FROM daily_prices GROUP BY symbol) latest "
                    "ON d.symbol = latest.symbol AND d.date = latest.latest_date"
                )
        temporary.replace(destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def export_symbol_csvs(data: pd.DataFrame, destination: str | Path) -> int:
    """Write one CSV per stock symbol and return the number of files written."""
    root = Path(destination)
    root.mkdir(parents=True, exist_ok=True)
    count = 0
    for symbol, group in data.groupby("symbol", sort=True):
        safe_symbol = "".join(char for char in str(symbol) if char.isalnum() or char in "-_.")
        if not safe_symbol:
            continue
        group.sort_values("date").to_csv(root / f"{safe_symbol}.csv", index=False)
        count += 1
    return count
