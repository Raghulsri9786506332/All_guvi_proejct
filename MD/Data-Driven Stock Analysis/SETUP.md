# Setup: Data-Driven Stock Analysis

## Install

Open PowerShell in the project folder:

```powershell
cd "C:\Users\raghu\OneDrive\New folder\Guvi Auto code\Data-Driven Stock Analysis"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Add input data

The project expects stock observations in YAML format, either as a YAML file or as a ZIP containing YAML files. Put the input under `data/raw/`, or set `STOCK_DATA_PATH` to an explicit file path. Each observation needs a symbol and date plus OHLCV values (open, high, low, close, and volume). Optional sector data can be supplied as `data/raw/sectors.csv` with `symbol,sector` columns.

This workspace may have a ZIP archive in the project root, but a ZIP archive is not the same as a ready-to-load YAML file. Check its contents and use the source path selected by the pipeline.

## Run the dashboard

```powershell
python -m streamlit run app.py
```

## Process data without the dashboard

```powershell
python scripts/process_data.py
```

The command accepts `--source`, `--sectors`, and `--output` arguments. Generated outputs include per-symbol CSV files, a SQLite database, and a validation report under `data/processed/`.

## Run tests

```powershell
python -m pytest
```

See [FILES.md](./FILES.md) and [FUNCTIONS.md](./FUNCTIONS.md) for the code guide.
