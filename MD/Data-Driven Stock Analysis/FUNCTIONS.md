# Functions: Data-Driven Stock Analysis

## Dashboard and command-line entry point

- `app.py` — `load_project_data(path, modified, sectors_modified)` caches the results of loading/processing using the chosen input path and modification times. The rest of the file builds the Streamlit interface at module level.
- `scripts/process_data.py` — `main()` reads `--source`, `--sectors`, and `--output`, calls the processing pipeline, and prints its validation report.

## YAML and sector ingestion (`stock_analysis/ingestion.py`)

- `_key(value)` normalizes a field name so common spelling and formatting differences can be matched.
- `_field_map(record)` maps keys in a source record to the standard stock fields.
- `_is_symbol_key(value)` checks whether a nested key looks like a stock symbol.
- `_records(node, path=())` walks nested YAML and yields candidate observation records.
- `_context_symbol(path)` and `_context_date(path)` try to get a symbol or date from the nested YAML path.
- `_as_frame(raw_records)` converts extracted dictionaries into a DataFrame.
- `_parse_date(value)` parses supported date values into timestamps.
- `normalize_records(document)` returns normalized valid rows plus a report of invalid or duplicate records.
- `load_yaml(path)` reads a YAML file or a supported ZIP archive, then normalizes its content.
- `find_yaml(directory)` looks for a supported source in a directory.
- `load_sectors(path)` loads an optional symbol-to-sector CSV mapping.

## Analytics (`stock_analysis/analytics.py`)

- `_validated_prices(data)` checks required columns, normalizes symbols, parses dates and numbers, removes invalid values, sorts records, and handles duplicate symbol/date rows.
- `calculate_metrics(data)` returns cleaned daily observations, per-stock annual summaries, monthly returns, a market summary, and a daily-return correlation matrix.
- `sector_performance(stocks, sectors)` joins symbol summaries to sector mappings and calculates average return and stock count per sector.
- `monthly_leaders(monthly, month, top_n=5)` returns the strongest and weakest stocks for one month.

## Saving output (`stock_analysis/database.py`)

- `write_database(data, sectors, destination)` writes the `daily_prices` and `sectors` tables to a temporary SQLite database, creates an index and `stock_latest` view, then replaces the destination database.
- `export_symbol_csvs(data, destination)` creates one date-sorted CSV per stock symbol and returns the number of files written.

## Processing pipeline (`stock_analysis/pipeline.py`)

- `source_path()` chooses a source from the `STOCK_DATA_PATH` environment variable, the raw-data folder, or a root-level `data-*.zip` archive.
- `process_source(source, sectors_path, output_dir)` loads and validates the source, loads optional sectors, writes CSV/SQLite outputs, and saves the validation report. It returns the data, sectors, and report.

## Test helpers

- `tests/conftest.py` — shared pytest configuration and fixtures.
- `tests/test_stock_analysis.py` — contains `_sample_data()` to prepare a small test dataset and tests for ingestion, invalid/duplicate rows, calculations, sector summaries, and export behavior.

## Metrics to explain

- Annual return: `(last close / first close - 1) * 100`.
- Daily return: percentage change in close from the previous observation.
- Annualized volatility: sample standard deviation of daily returns multiplied by `sqrt(252)`.
- Monthly return: first-to-last close return within one calendar month.

These are historical calculations and are not investment advice.
