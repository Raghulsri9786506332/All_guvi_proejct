# Data-Driven Stock Analysis

## What this project does

This Streamlit dashboard analyzes daily stock OHLCV data. It reads YAML data (including YAML files inside a ZIP), validates and normalizes records, calculates return and risk metrics, exports per-stock CSV files, and stores the normalized data in SQLite.

Read the project's original [README](../../Data-Driven%20Stock%20Analysis/README.md) for the complete data format and metric definitions.

More guides: [setup](./SETUP.md), [file list](./FILES.md), [function explanations](./FUNCTIONS.md), and [tests](./TESTS.md).

## Setup and run

From the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Provide a source YAML or ZIP in `data/raw/`, or set `STOCK_DATA_PATH` to its path. An optional `sectors.csv` can map each stock symbol to a sector. Then run:

```powershell
python -m streamlit run app.py
```

To process data without opening the dashboard:

```powershell
python scripts/process_data.py
```

Tests:

```powershell
python -m pytest
```

## Python file and function overview

- `app.py` — Streamlit dashboard. `load_project_data(path, modified, sectors_modified)` caches loading/processing based on source and file modification times; the rest of the file builds filters, charts, and tables.
- `scripts/process_data.py` — command-line wrapper for processing data. `main()` reads `--source`, `--sectors`, and `--output`, calls the pipeline, and prints the validation report.
- `stock_analysis/ingestion.py` — converts YAML or ZIP contents into normalized stock rows and loads optional sectors:
  - `_key(value)` normalizes field names for matching.
  - `_field_map(record)` maps source field variants to standard fields.
  - `_is_symbol_key(value)` detects a symbol-like key.
  - `_records(node, path)` walks nested YAML structures and yields observation records.
  - `_context_symbol(path)` and `_context_date(path)` infer symbol/date from nested keys.
  - `_as_frame(raw_records)` builds a DataFrame from extracted rows.
  - `_parse_date(value)` converts a value to a timestamp.
  - `normalize_records(document)` returns cleaned stock rows and a validation report.
  - `load_yaml(path)` reads YAML or supported ZIP sources and normalizes them.
  - `find_yaml(directory)` locates a supported source in a directory.
  - `load_sectors(path)` loads an optional symbol-to-sector mapping.
- `stock_analysis/analytics.py` — calculates stock metrics:
  - `_validated_prices(data)` checks required fields, types, positive closes, non-negative volume, and duplicates.
  - `calculate_metrics(data)` returns cleaned daily rows, per-stock summaries, monthly returns, market summary, and daily-return correlations.
  - `sector_performance(stocks, sectors)` calculates average annual return by mapped sector.
  - `monthly_leaders(monthly, month, top_n)` returns the strongest and weakest stocks for one month.
- `stock_analysis/database.py` — stores processed results. `write_database(data, sectors, destination)` writes SQLite tables and a `stock_latest` view through a temporary database; `export_symbol_csvs(data, destination)` writes one sorted CSV per symbol.
- `stock_analysis/pipeline.py` — coordinates the project workflow. `source_path()` chooses the configured/default source; `process_source(...)` loads, validates, exports, writes SQLite, and saves the validation report.
- `stock_analysis/__init__.py` — package marker; no main workflow function.
- `tests/conftest.py` — shared test configuration or fixtures.
- `tests/test_stock_analysis.py` — tests ingestion, validation, metric calculations, sector analytics, and persistence.

See the separate [function guide](./FUNCTIONS.md) for descriptions of every project function.

## Outputs

The processing pipeline writes per-symbol CSV files, `stock_analysis.sqlite3`, and `validation_report.json` under `data/processed/`. These are generated outputs, not source modules.

## Key SQL concept

This project uses SQLite rather than MySQL. The database writer creates tables and a `stock_latest` view. That view uses a SQL `JOIN` between daily rows and each symbol's latest date to return the latest observation per symbol.
