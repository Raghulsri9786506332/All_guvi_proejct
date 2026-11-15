"""Orchestrate source loading, validation, CSV exports, and SQLite persistence."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from stock_analysis.database import export_symbol_csvs, write_database
from stock_analysis.ingestion import find_yaml, load_sectors, load_yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
DATABASE_PATH = OUTPUT_DIR / "stock_analysis.sqlite3"


def source_path() -> Path | None:
    configured = os.environ.get("STOCK_DATA_PATH")
    if configured:
        return Path(configured).expanduser()
    raw_source = find_yaml(RAW_DIR)
    if raw_source is not None:
        return raw_source
    root_archives = sorted(PROJECT_ROOT.glob("data-*.zip"))
    return root_archives[0] if root_archives else None


def process_source(
    source: str | Path | None = None,
    sectors_path: str | Path | None = None,
    output_dir: str | Path = OUTPUT_DIR,
) -> tuple[Any, Any, dict[str, Any]]:
    """Load, validate, export, and persist the configured market data."""
    source = Path(source) if source else source_path()
    if source is None or not source.is_file():
        raise FileNotFoundError(
            "No stock YAML file found. Add your source as "
            f"`{RAW_DIR / 'stock_dataset.yaml'}` or set STOCK_DATA_PATH."
        )
    data, report = load_yaml(source)
    sector_file = Path(sectors_path) if sectors_path else RAW_DIR / "sectors.csv"
    sectors = load_sectors(sector_file)
    output_dir = Path(output_dir)
    csv_count = export_symbol_csvs(data, output_dir / "stocks")
    write_database(data, sectors, output_dir / "stock_analysis.sqlite3")
    report["symbols_exported"] = csv_count
    report["sector_mappings"] = len(sectors)
    report_path = output_dir / "validation_report.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    return data, sectors, report
