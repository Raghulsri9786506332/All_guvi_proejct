# Tests: Data-Driven Stock Analysis

Run from the project directory:

```powershell
python -m pytest
```

`tests/test_stock_analysis.py` checks:

- extracting symbol and date context from nested YAML records;
- combining daily YAML files stored inside a ZIP;
- reporting invalid or duplicate rows;
- reporting incomplete OHLCV records rather than silently dropping them;
- annual return, volatility, and monthly leader calculations;
- sector averages and SQLite/CSV exports.

`tests/conftest.py` provides shared test setup. The tests use small generated/sample inputs and should not require real market data files for the unit cases.
