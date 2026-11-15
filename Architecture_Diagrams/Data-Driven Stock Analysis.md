# Data-Driven Stock Analysis — Architecture

```mermaid
flowchart TD
    YAML[YAML input<br/>or ZIP of YAML files]
    SectorCSV[Optional sectors.csv]
    Env[STOCK_DATA_PATH<br/>optional source override]
    Find[stock_analysis.pipeline.source_path]
    CLI[scripts/process_data.py]
    Dashboard[Streamlit app.py]
    Pipeline[stock_analysis.pipeline.process_source]
    Ingest[stock_analysis.ingestion<br/>read / normalize / validate]
    Report[Validation report<br/>accepted and rejected rows]
    Data[(Normalized OHLCV DataFrame)]
    Analytics[stock_analysis.analytics<br/>returns / volatility / monthly / correlation]
    Sector[Sector performance]
    Export[stock_analysis.database.export_symbol_csvs]
    SQLite[stock_analysis.database.write_database]
    DB[(SQLite<br/>daily_prices / sectors)]
    View[stock_latest SQL view<br/>JOIN with latest date per symbol]
    CSVs[(CSV per stock symbol)]
    JSON[validation_report.json]
    Charts[Dashboard charts and tables]
    User[Analyst]

    YAML --> Find
    Env --> Find
    Find --> Pipeline
    SectorCSV --> Pipeline
    CLI --> Pipeline
    Dashboard --> Pipeline
    Pipeline --> Ingest --> Data
    Ingest --> Report --> JSON
    Data --> Analytics
    Data --> Export --> CSVs
    Data --> SQLite --> DB
    SectorCSV --> Sector
    Analytics --> Sector
    Sector --> Charts
    Analytics --> Charts
    DB --> View
    User --> Dashboard
    Charts --> User
```

## Data flow

1. `source_path()` selects a configured YAML/ZIP source or searches the expected raw-data locations.
2. `load_yaml()` and `normalize_records()` turn nested source records into consistent symbol/date/OHLCV rows and produce a validation report.
3. `calculate_metrics()` validates prices and calculates stock, monthly, and market metrics.
4. The pipeline exports one sorted CSV per symbol, writes SQLite tables and a `stock_latest` view, and saves `validation_report.json`.
5. The Streamlit dashboard presents the processed metrics and charts.

## Notes

- The processing CLI and Streamlit dashboard both use `process_source()` as the common pipeline.
- SQLite persistence is separate from dashboard analytics. The SQL view joins each symbol's daily records to its latest available date.
- Source data is required; the project should not fabricate market observations. Results are historical analysis, not investment advice.
