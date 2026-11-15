# File guide: Data-Driven Stock Analysis

- `app.py` — Streamlit dashboard. Displays market summary metrics, stock performance, monthly leaders, sector results, and correlations using processed data.
- `requirements.txt` — Python dependencies for the project.
- `README.md` — main instructions, expected input shape, metric definitions, and dashboard features.
- `scripts/process_data.py` — command-line entry point for validating and processing data.
- `stock_analysis/ingestion.py` — reads YAML and ZIP input, normalizes field names, infers symbol/date context, validates records, and loads sector mappings.
- `stock_analysis/analytics.py` — validates stock prices and calculates returns, volatility, market summaries, monthly results, correlations, and sector metrics.
- `stock_analysis/database.py` — exports per-symbol CSVs and writes stock/sector tables and a latest-price view to SQLite.
- `stock_analysis/pipeline.py` — locates a source and coordinates import, validation, exports, database writing, and report creation.
- `stock_analysis/__init__.py` — Python package marker.
- `tests/conftest.py` — shared pytest setup and fixtures.
- `tests/test_stock_analysis.py` — tests YAML normalization, ZIP import, validation reporting, analytics, sectors, and SQLite/CSV output.

## Data and generated files

- `data/raw/` is the intended location for source YAML/ZIP files and optional `sectors.csv`.
- `data/processed/` contains generated outputs: one CSV per symbol, `stock_analysis.sqlite3`, and `validation_report.json`.
- Generated data files are not Python source. Keep original input data unchanged when testing processing changes.

See [FUNCTIONS.md](./FUNCTIONS.md) for function-by-function explanations.
