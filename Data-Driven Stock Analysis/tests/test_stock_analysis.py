from __future__ import annotations

import sqlite3
import zipfile

import pandas as pd

from stock_analysis.analytics import calculate_metrics, monthly_leaders, sector_performance
from stock_analysis.database import export_symbol_csvs, write_database
from stock_analysis.ingestion import load_yaml, normalize_records


def _sample_data():
    return pd.DataFrame({
        "symbol": ["AAA", "AAA", "AAA", "BBB", "BBB", "BBB"],
        "date": pd.to_datetime([
            "2025-01-02", "2025-01-03", "2025-02-03",
            "2025-01-02", "2025-01-03", "2025-02-03",
        ]),
        "open": [100, 110, 120, 100, 90, 80],
        "high": [112, 122, 132, 102, 92, 82],
        "low": [98, 108, 118, 78, 68, 58],
        "close": [110, 120, 130, 90, 80, 70],
        "volume": [1000, 1100, 1200, 900, 800, 700],
    })


def test_nested_yaml_rows_use_symbol_and_date_context():
    document = {
        "January 2025": {
            "2025-01-02": {
                "RELIANCE": {"open": 100, "high": 105, "low": 98, "close": 103, "volume": 500}
            }
        }
    }
    data, report = normalize_records(document)
    assert len(data) == 1
    assert data.loc[0, "symbol"] == "RELIANCE"
    assert data.loc[0, "date"] == pd.Timestamp("2025-01-02")
    assert report["accepted_rows"] == 1


def test_zip_of_daily_yaml_files_is_combined(tmp_path):
    archive_path = tmp_path / "daily-data.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(
            "data/2025-01/2025-01-02.yaml",
            "- Ticker: AAA\n  date: '2025-01-02 05:30:00'\n"
            "  open: 100\n  high: 105\n  low: 98\n  close: 103\n  volume: 500\n",
        )
        archive.writestr(
            "data/2025-01/2025-01-03.yaml",
            "- Ticker: AAA\n  date: '2025-01-03 05:30:00'\n"
            "  open: 103\n  high: 108\n  low: 102\n  close: 106\n  volume: 600\n",
        )

    data, report = load_yaml(archive_path)
    assert len(data) == 2
    assert data["symbol"].unique().tolist() == ["AAA"]
    assert report["source_files"] == 2
    assert report["accepted_rows"] == 2


def test_invalid_and_duplicate_rows_are_reported():
    document = [
        {"symbol": "AAA", "date": "2025-01-02", "open": 10, "high": 12, "low": 9, "close": 11, "volume": 100},
        {"symbol": "AAA", "date": "2025-01-02", "open": 10, "high": 12, "low": 9, "close": 11.5, "volume": 120},
        {"symbol": "BBB", "date": "not-a-date", "open": 10, "high": 12, "low": 9, "close": 11, "volume": 100},
    ]
    data, report = normalize_records(document)
    assert len(data) == 1
    assert data.loc[0, "close"] == 11.5
    assert report["duplicate_rows_removed"] == 1
    assert report["rejected_rows"] == 1


def test_incomplete_price_rows_are_reported_not_silently_dropped():
    document = [
        {"symbol": "AAA", "date": "2025-01-02", "open": 10, "high": 12, "low": 9, "close": 11},
    ]
    data, report = normalize_records(document)
    assert data.empty
    assert report["records_found"] == 1
    assert report["rejected_rows"] == 1
    assert report["rejection_reasons"]["invalid_price_or_volume"] == 1


def test_annual_return_volatility_and_monthly_leaders():
    result = calculate_metrics(_sample_data())
    stocks = result["stocks"].set_index("symbol")
    assert round(stocks.loc["AAA", "annual_return_pct"], 2) == 18.18
    assert round(stocks.loc["BBB", "annual_return_pct"], 2) == -22.22
    assert stocks.loc["AAA", "volatility_pct"] > 0
    assert result["market"]["green_stocks"] == 1
    assert result["market"]["red_stocks"] == 1
    gainers, losers = monthly_leaders(result["monthly"], pd.Timestamp("2025-01-01"))
    assert gainers.iloc[0]["symbol"] == "AAA"
    assert losers.iloc[0]["symbol"] == "BBB"


def test_sector_averages_and_sqlite_exports(tmp_path):
    result = calculate_metrics(_sample_data())
    sectors = pd.DataFrame({"symbol": ["AAA", "BBB"], "sector": ["Technology", "Finance"]})
    summary = sector_performance(result["stocks"], sectors)
    assert len(summary) == 2
    assert export_symbol_csvs(_sample_data(), tmp_path / "stocks") == 2
    database = tmp_path / "stock_analysis.sqlite3"
    write_database(_sample_data(), sectors, database)
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM daily_prices").fetchone()[0] == 6
        assert connection.execute("SELECT COUNT(*) FROM sectors").fetchone()[0] == 2
        assert connection.execute("SELECT COUNT(*) FROM stock_latest").fetchone()[0] == 2
