# Data-Driven Stock Analysis

An interactive Streamlit dashboard for analyzing daily Nifty 50 stock data. It
imports the supplied monthly/date-wise YAML data, validates and organizes
records, creates one CSV per symbol, stores normalized data in SQLite, and
visualizes annual and monthly performance.

> **Data note:** The project brief describes a `stock_dataset` and a sector CSV,
> but those datasets were not included with the brief. No market data or
> performance results are fabricated. Add your source files as described below
> to populate the dashboard.

## Features

- Rank the 10 strongest and weakest stocks by first-to-last close return.
- Show green/red stock counts and latest available average close and volume.
- Compare annualized daily-return volatility and compounded cumulative returns.
- Compare mean annual returns by sector when a sector mapping is supplied.
- Explore monthly top five gainers and losers for all available months.
- Inspect pairwise daily-return correlations with an interactive heatmap.
- Validate the input, export a CSV per symbol, and write cleaned records to a
  portable SQLite database for SQL and Power BI workflows.

## Quick start

Python 3.10 or later is recommended.

```powershell
cd "Data-Driven Stock Analysis"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Put the supplied YAML file in `data/raw/` (for example
`data/raw/stock_dataset.yaml`) or put the provided ZIP of daily YAML files there.
The importer reads the YAML directly from the ZIP without extracting it. It
searches for `stock_dataset.yaml`, `stock_dataset.yml`, `stock_dataset.zip`, then
other YAML files or ZIP archives in `data/raw/`. It also detects an attached
`data-*.zip` archive placed in the project root. Alternatively set
`STOCK_DATA_PATH` to an explicit YAML or ZIP file. Each observation should have
daily OHLCV values and a date and symbol either on the record or represented by
its nested keys.

Optional: copy `data/raw/sectors_template.csv` to `data/raw/sectors.csv` and fill
in the sector for each symbol:

```csv
symbol,sector
RELIANCE,Energy
```

Then launch the dashboard:

```powershell
streamlit run app.py
```

Or clean, validate, and export the dataset without opening the dashboard:

```powershell
python scripts/process_data.py
```

The processing command writes:

- `data/processed/stocks/<SYMBOL>.csv` — one sorted file per stock.
- `data/processed/stock_analysis.sqlite3` — `daily_prices` and optional
  `sectors` tables.
- `data/processed/validation_report.json` — accepted/rejected row counts and
  actionable validation messages.

These generated files and input datasets are excluded from Git by default.
Power BI can connect to the SQLite database using an installed SQLite
connector, or import the per-symbol CSV files. The project does not generate a
Power BI `.pbix`; create the report in Power BI Desktop using the same tables.

## Data validation and metric definitions

- Records need a recognizable symbol, date, close, open, high, low, and volume.
  Common field-name variations are normalized. Unparseable records and rows
  with invalid dates, non-positive prices, or negative volume are reported and
  excluded. Duplicate symbol/date observations keep the last valid record.
- Annual return is `(last close / first close - 1) * 100`.
- Daily return is `close.pct_change()`. Annual volatility is its sample standard
  deviation multiplied by `sqrt(252)` and expressed as a percentage.
- Cumulative return compounds daily returns from the first observed close.
- Monthly return is the first-to-last close return within each calendar month.
- Green/red classification uses the sign of annual return; zero-return stocks
  are neutral.
- Market average close and volume are the means of each stock's latest
  observation, so each stock contributes one observation.
- Sector averages use the same annual-return definition and only mapped stocks.

The dashboard is an analytical aid, not investment advice. Historical
performance does not predict future returns.

## Tests

```powershell
python -m pytest
```
