# Data-Driven Stock Analysis: 100 Technical Interview Questions and Answers

These answers describe the implementation in the `Data-Driven Stock Analysis`
project and its README. The project expects daily market observations supplied
as YAML or a ZIP containing YAML files; no market dataset or measured results
are included with the project itself. It is an analysis tool, not investment
advice.

1. **What does this project do?**  
   It loads daily stock OHLCV observations, normalizes and validates them, calculates return and volatility statistics, and presents results in a Streamlit dashboard. It also exports one CSV per symbol, stores normalized observations in SQLite, and writes a JSON validation report. All outputs depend on the user-provided data.

2. **What is the high-level architecture?**  
   `stock_analysis.ingestion` reads YAML/ZIP data and optional sector mappings. `stock_analysis.pipeline` coordinates ingestion, exports, and persistence. `stock_analysis.analytics` computes metrics. `stock_analysis.database` handles CSV and SQLite outputs. `app.py` renders the Streamlit interface, while `scripts/process_data.py` exposes the processing pipeline as a CLI.

3. **What are the main input and output directories?**  
   Inputs normally live in `data/raw/`; optional sector mappings are in `data/raw/sectors.csv`. By default, processed data goes to `data/processed/`, with per-symbol files under `stocks/`, a SQLite database, and a validation report. These are configurable in part through pipeline function arguments and CLI options.

4. **What does OHLCV mean here?**  
   OHLCV means open, high, low, close, and volume for a daily observation. The project requires all five values plus a symbol and date. The normalized price columns are named `open`, `high`, `low`, `close`, and `volume`.

5. **How is a typical observation represented?**  
   It may be a record with symbol and date fields alongside the OHLCV values, or a record nested under date and symbol keys. For example, the test suite uses a nested path for `RELIANCE` on `2025-01-02`; `normalize_records()` recovers the missing symbol and date from that context.

6. **Which market-data inputs are supported?**  
   `load_yaml()` accepts a standalone YAML/YML file or a ZIP archive whose members are YAML/YML files. A ZIP is read directly without extracting its contents. The application does not fetch live market prices or call an exchange API.

7. **Does the repository include usable stock prices?**  
   The README explicitly says the brief's stock dataset and sector CSV were not included and that no results are fabricated. The project directory may contain an attached ZIP archive, but interview answers and dashboard results should only claim what the loaded user-supplied data actually establishes.

8. **Does “Nifty 50” mean the code enforces those 50 constituents?**  
   No. The app description and README frame the use case as Nifty 50 analysis, but the normalizer accepts recognizable symbols rather than checking membership in an official constituent list. The symbols and coverage therefore depend on the supplied data.

9. **What are the main Python dependencies?**  
   The code uses pandas for tabular data, NumPy for annualization calculations, PyYAML for parsing, SQLite through Python's standard `sqlite3` module, Streamlit for the UI, and Plotly for charts. `requirements.txt` is the project manifest; install it as described in the README.

10. **How does the dashboard obtain its data?**  
    `app.py` calls `source_path()` to locate a source, then calls the cached `load_project_data()` wrapper. That wrapper invokes `process_source()`, which in turn loads, validates, exports, and persists the data before returning raw records, sectors, and a report for analytics.

11. **How does `source_path()` choose the source?**  
    In `stock_analysis.pipeline`, it first honors the `STOCK_DATA_PATH` environment variable. Otherwise it calls `find_yaml()` on `data/raw/`, and finally looks for a root-level `data-*.zip`. If no usable file is found, the pipeline reports a clear missing-input error.

12. **What is the input search priority in `find_yaml()`?**  
    `find_yaml()` first checks `stock_dataset.yaml`, `stock_dataset.yml`, and `stock_dataset.zip`. It then selects the first sorted YAML/YML file, or, if none exists, the first sorted ZIP in the raw-data folder. This deterministic preference helps avoid arbitrary file selection when several candidates exist.

13. **How can a user override automatic source discovery?**  
    Set `STOCK_DATA_PATH` to an explicit YAML or ZIP path, or pass `--source` to `scripts/process_data.py`. The command-line argument is passed directly to `process_source()` and therefore takes precedence over its default discovery behavior.

14. **How does ZIP ingestion work?**  
    `load_yaml()` opens the archive with `zipfile.ZipFile`, sorts YAML/YML members by filename, reads each member's bytes, and parses them with `yaml.safe_load()`. It combines parsed documents and passes the combined structure to `normalize_records()`. No extraction directory is required.

15. **Why use `yaml.safe_load()`?**  
    It parses YAML data without constructing arbitrary Python objects, which is an important safe default for external input. The loader also converts YAML parser errors into useful `ValueError` messages, including the archive member name when parsing a ZIP.

16. **What ZIP guardrails are implemented?**  
    `load_yaml()` limits an archive to `MAX_ARCHIVE_YAML_FILES` (5,000) YAML members and `MAX_ARCHIVE_UNCOMPRESSED_BYTES` (100 MiB) total uncompressed YAML size. It also rejects archives with no YAML members and translates malformed ZIP errors into a clearer message.

17. **How are nested YAML structures traversed?**  
    The private `_records()` function recursively walks dictionaries and lists. When it sees a dictionary containing recognizable fields, it yields that record plus its key path. This permits records nested by month, date, and symbol instead of requiring a flat list.

18. **How does the importer infer a missing symbol?**  
    If a record lacks an explicit symbol, `normalize_records()` asks `_context_symbol()` to search its key path from the inside outward. `_is_symbol_key()` filters date-like keys, month names, generic labels, and keys outside the allowed symbol pattern before accepting a candidate.

19. **How does the importer infer a missing date?**  
    When the record has no date field, `_context_date()` scans the nested key path from the deepest level outward and returns a key that matches `DATE_KEY`. `_parse_date()` then parses the value, handles ordinal suffixes such as “2nd,” and normalizes dates to midnight.

20. **How are field-name variations handled?**  
    `FIELD_ALIASES` maps common alternatives to canonical fields. For example, `ticker` maps to `symbol`, `trade_date` to `date`, `open_price` to `open`, and `adjusted_close` to `close`. `_key()` normalizes capitalization and punctuation before `_field_map()` checks those aliases.

21. **What if field names use different capitalization or punctuation?**  
    `_key()` lowercases a field name and replaces non-alphanumeric runs with underscores. As a result, variations such as spaces or hyphens can match canonical aliases after normalization, provided the resulting name is among the aliases defined in `FIELD_ALIASES`.

22. **How does the parser decide whether a dictionary is a record?**  
    `_records()` runs `_field_map()` and yields the dictionary when it contains at least one recognized required field or `close`. This broad discovery rule lets incomplete rows reach validation, where they can be counted and explained instead of being silently ignored.

23. **How are input values converted to canonical types?**  
    `normalize_records()` uppercases and trims symbols, parses dates with `_parse_date()`, and converts OHLCV values using `pandas.to_numeric()`. Numeric text has commas, dollar signs, and rupee signs removed first, so common formatted values can be accepted.

24. **What happens when a record is missing a required column?**  
    `_as_frame()` creates any absent required columns and fills them with missing values. The checks in `normalize_records()` then identify missing or invalid values, increment rejection counts, and exclude those records from the clean output.

25. **What validation checks are performed?**  
    The normalizer checks for a missing symbol, invalid date, missing or non-numeric price/volume, non-positive OHLC prices, negative volume, and an inconsistent high/low relationship. Invalid rows are excluded and the report records counts by reason.

26. **What does “inconsistent high/low” mean in the implementation?**  
    A row fails if its high is below any of the open, low, or close values, or its low is above any of the open, high, or close values. The check enforces that the daily range contains the recorded open and close and that high is not below low.

27. **Does validation require positive volume?**  
    No. `normalize_records()` rejects negative volume but accepts zero volume. Prices must be strictly positive. This distinction is explicit in the validation expressions and matters when describing accepted data quality rules.

28. **How are duplicate symbol/date records treated?**  
    After invalid rows are removed, `normalize_records()` deduplicates on `(symbol, date)` and keeps the last valid record in input traversal order. It reports the number removed as `duplicate_rows_removed` and sorts the surviving observations by symbol and date.

29. **Are rejection-reason counts mutually exclusive?**  
    Not necessarily. The code counts each validation mask separately, then combines masks to determine whether a row is invalid. One row can therefore contribute to multiple reason counts, while `rejected_rows` counts invalid rows once.

30. **What is included in the validation report?**  
    It includes `records_found`, `accepted_rows`, `rejected_rows`, `duplicate_rows_removed`, and counts under `rejection_reasons`. `load_yaml()` adds the source path and, for ZIP input, `source_files`; `process_source()` adds `symbols_exported` and `sector_mappings`.

31. **When does `load_yaml()` fail instead of returning an empty frame?**  
    It raises a `ValueError` when the archive has no YAML files, when it is malformed, when a YAML member cannot be parsed, or when normalization yields no valid OHLCV rows. This prevents downstream charts and database outputs from silently treating an unusable source as a successful run.

32. **How do the ingestion tests verify nested data handling?**  
    `test_nested_yaml_rows_use_symbol_and_date_context()` supplies a January 2025 → date → `RELIANCE` nested mapping without explicit symbol/date fields in the leaf record. It asserts the recovered values and that the row is counted as accepted.

33. **How do the ZIP tests verify multi-file ingestion?**  
    `test_zip_of_daily_yaml_files_is_combined()` builds an archive with two dated YAML members for symbol `AAA`. It checks that both rows are loaded, the symbol is retained, and the report counts two source files and two accepted rows.

34. **What is the analytics pipeline inside `calculate_metrics()`?**  
    It validates and sorts the prices, computes per-symbol daily returns and cumulative returns, builds one row of summary metrics per symbol, derives market-level latest-observation statistics, calculates monthly returns, and finally computes a daily-return correlation matrix.

35. **What does `_validated_prices()` in analytics validate?**  
    It requires `symbol`, `date`, `close`, and `volume`, converts their types, removes rows missing those values, and filters non-positive closes and negative volumes. It sorts by symbol/date and deduplicates symbol/date pairs, keeping the last row. Full OHLC checks are handled earlier in ingestion.

36. **What formula defines daily return?**  
    For each symbol, `calculate_metrics()` uses `close.pct_change()`, which is `(today’s close / prior observed close) - 1`. The first observed daily return for a symbol is missing because there is no earlier close in that input series.

37. **What formula defines the project’s annual return?**  
    The per-symbol summary uses `(last_close / first_close - 1) * 100`. This is a first-to-last return over the available observation window; the code does not convert it into a one-year annualized return based on the number of elapsed years.

38. **Why is the app’s annual return not necessarily a calendar-year return?**  
    `calculate_metrics()` groups the entire dataset by symbol and compares its first and last closes. It does not group those summary rows by calendar year. The dashboard calls the section “Yearly performance,” so users should interpret it as the available-period first-to-last return unless the source itself covers one year.

39. **How is volatility calculated?**  
    The code takes the sample standard deviation of non-missing daily returns (`std(ddof=1)`), multiplies it by `sqrt(252)`, and multiplies by 100. The result is annualized volatility in percent, using 252 trading days as the convention.

40. **Why does the volatility formula use `ddof=1`?**  
    `ddof=1` computes sample standard deviation, which estimates variability from a finite sample rather than treating the observations as a complete population. The code annualizes this estimate; the convention should be kept in mind when comparing with systems using population standard deviation or a different trading-day count.

41. **What if a stock has too few daily returns to estimate volatility?**  
    If a symbol has one or zero non-missing daily returns, `calculate_metrics()` reports `0.0` volatility for that symbol. That is a fallback value, not evidence that the stock has no risk; it means the available return sample is insufficient for the sample-standard-deviation calculation.

42. **How is cumulative return calculated?**  
    The code fills the first missing daily return with zero, compounds `(1 + daily_return)` within each symbol using `cumprod()`, subtracts one, and converts the result to percent. It expresses cumulative performance relative to the first observed close.

43. **Why use compounding rather than adding daily returns?**  
    Returns compound multiplicatively: a 10% gain followed by a 10% loss produces `1.10 × 0.90 - 1 = -1%`, not zero. The `cumprod()` calculation in `calculate_metrics()` preserves this sequential investment-growth relationship.

44. **How are monthly returns calculated?**  
    The code assigns each observation to a calendar month using `date.dt.to_period("M")`, groups by month and symbol, and compares the first and last close observed in that group. The result is `(last_close / first_close - 1) * 100`.

45. **Does monthly return include a prior month’s closing price?**  
    No. It is an intra-month first-observation-to-last-observation calculation, not a month-end-to-previous-month-end calculation. If a month has a single observation, its first and last close are the same and its calculated return is zero.

46. **How are gainers, losers, and neutral stocks classified?**  
    The `market` series counts symbols with positive annual return as green, negative as red, and exactly zero as neutral. The classification is based on the calculated first-to-last return, not on the sign of the most recent daily move.

47. **How does the project calculate market average close and volume?**  
    It selects the latest available row per symbol and averages those rows’ close and volume values. Each symbol contributes once, even if its last observation date differs from another symbol’s; this is not an index-weighted or volume-weighted market statistic.

48. **How is “latest observation” selected for each symbol?**  
    After sorting by date, the analytics code groups by symbol and takes the last row with `groupby(...).tail(1)`. It then reports the maximum of those selected dates as the market-level latest date.

49. **How is return correlation calculated?**  
    Daily returns are pivoted to a date-by-symbol table, then pandas `corr(min_periods=2)` computes pairwise Pearson correlations. A pair needs at least two overlapping non-missing return observations; otherwise the correlation may be missing.

50. **What should a user understand about correlation heatmaps?**  
    The heatmap compares historical daily-return co-movement across overlapping dates. Correlation is not causation, can vary over time, and may be unreliable with short or sparse overlap. `app.py` uses a fixed color range from -1 to 1 and explains when fewer than two stocks are available.

51. **How does `monthly_leaders()` choose top gainers and losers?**  
    It selects rows matching the requested month, sorts by `monthly_return_pct`, takes the first `top_n` as gainers, and the last `top_n` as losers. Its default `top_n` is five; the losers are returned in ascending return order.

52. **What can be misleading about ranking monthly winners and losers?**  
    A month may contain fewer than five symbols, so each list can be shorter than five. The result also depends on each symbol’s available observations in that calendar month and does not guarantee every symbol has a complete month of trading data.

53. **How is sector analysis enabled?**  
    Supply `data/raw/sectors.csv` with `symbol,sector` columns, or pass an alternative path through the CLI `--sectors` option. `load_sectors()` normalizes symbol/sector fields and returns an empty mapping when the optional file is absent.

54. **What sector column aliases does `load_sectors()` accept?**  
    It accepts `symbol`, `ticker`, or `stock_symbol` for the symbol field and `sector` or `industry` for the sector field, after normalizing column names. It raises a `ValueError` if either kind of column is missing.

55. **How are duplicate sector mappings handled?**  
    `load_sectors()` uppercases and trims symbols, trims sector values, removes missing rows, and keeps the last mapping for each symbol. Rows whose sector is an empty string are then excluded.

56. **How are sector returns aggregated?**  
    `sector_performance()` inner-joins stock summaries with sector mappings on symbol, groups by sector, and calculates the mean `annual_return_pct` plus the number of unique mapped symbols. Sectors without a mapped stock do not appear.

57. **What limitation comes from using an inner join for sectors?**  
    Unmapped stocks are excluded from sector averages, as are sector symbols that have no matching stock summary. The output describes only the matched set and should not be presented as complete coverage unless mappings are complete.

58. **What does the app show when no sector data is available?**  
    The dashboard displays an informational message asking for a `symbol,sector` mapping file rather than drawing an empty chart. The analytics function also returns an empty frame with the expected sector-summary columns when either input is empty.

59. **What is the purpose of `process_source()`?**  
    It is the pipeline orchestrator: it resolves the source path, calls `load_yaml()` and `load_sectors()`, writes per-symbol CSV files, writes the SQLite database, extends the validation report, saves JSON, and returns the normalized data, sectors, and report.

60. **What are the default pipeline output files?**  
    `process_source()` defaults to `data/processed/`. It writes `stocks/<SYMBOL>.csv`, `stock_analysis.sqlite3`, and `validation_report.json`. The CLI README also documents these outputs for `python scripts/process_data.py`.

61. **How does the standalone processing command work?**  
    `scripts/process_data.py` defines `main()` with `argparse`, inserts the project root on `sys.path`, and calls `process_source()`. It prints the returned report as formatted JSON, so the data pipeline can run without opening Streamlit.

62. **Which CLI options are supported?**  
    `--source` selects the YAML or ZIP input; `--sectors` selects the optional sector CSV; `--output` overrides the processed output directory. With no source argument, environment-variable and default discovery rules apply.

63. **How does `process_source()` handle a missing input?**  
    It raises `FileNotFoundError` with guidance to add `data/raw/stock_dataset.yaml` or set `STOCK_DATA_PATH`. This occurs before CSV, database, or validation-report output is generated.

64. **How are per-symbol CSV exports produced?**  
    `export_symbol_csvs()` groups normalized rows by symbol, sorts each group by date, and writes it without a pandas index. It returns the number of files written, which becomes `symbols_exported` in the validation report.

65. **How are CSV file names made safer?**  
    Before creating a filename, `export_symbol_csvs()` retains only alphanumeric characters and `-`, `_`, or `.` from the symbol. Empty sanitized names are skipped. The CSV remains a convenient one-symbol export rather than a replacement for the complete database.

66. **What does the SQLite database contain?**  
    `write_database()` creates or replaces a `daily_prices` table from the cleaned OHLCV DataFrame and a `sectors` table from the optional mapping DataFrame. It also creates a symbol/date index and a `stock_latest` view.

67. **What is the `daily_prices` table’s logical schema?**  
    It contains the normalized observation columns: `symbol`, `date`, `open`, `high`, `low`, `close`, and `volume`. Pandas `to_sql()` creates the physical SQLite table from the DataFrame; the code does not declare a separate hand-written schema with explicit constraints.

68. **What is the `sectors` table’s logical schema?**  
    It stores the normalized mapping as `symbol` and `sector`. The table is written even when the optional sector file is absent, in which case the input frame has those two columns and no mapping rows.

69. **What is the `stock_latest` SQLite view?**  
    It selects all columns from `daily_prices` for rows whose date matches the maximum date for that symbol. In effect, it exposes each symbol’s latest stored observation and can simplify queries for current-in-dataset values.

70. **Why add an index on `(symbol, date)`?**  
    The index `idx_daily_prices_symbol_date` is aligned with common access patterns: filtering a stock’s time series and ordering or finding dates within that stock. It can help SQL queries and joins without changing the table’s contents.

71. **How does `write_database()` try to protect an existing database from partial writes?**  
    It writes the replacement tables into a sibling file whose suffix ends in `.tmp`, uses a SQLite transaction, closes the connection, and then replaces the destination with the completed temporary file. A `finally` block removes a leftover temporary file.

72. **What does “atomic” database replacement mean in this code?**  
    The intent is to keep the destination database from being replaced until the new database is fully written. `temporary.replace(destination)` performs the final filesystem replacement. Actual replacement guarantees can depend on filesystem behavior, especially if source and destination are on different volumes; here they are in the same output directory.

73. **How could an analyst query a symbol’s time series in SQLite?**  
    A simple query can select `date`, `open`, `high`, `low`, `close`, and `volume` from `daily_prices` for a chosen `symbol`, ordered by `date`. The `(symbol, date)` index is designed to support this common query shape.

74. **How could an analyst join prices to sectors in SQL?**  
    Join `daily_prices` to `sectors` on `symbol`, then filter or group by `sector`. For example, daily rows can be counted by sector, but that is a row-level count; for average annual returns, use the per-symbol return calculation before grouping to match `sector_performance()`.

75. **How could `stock_latest` and `sectors` be joined?**  
    Join `stock_latest` to `sectors` using their `symbol` columns. This yields latest available daily observations with optional sector labels, useful for descriptive snapshots. It does not calculate returns or imply all symbols have mappings.

76. **Does this project generate a Power BI report file?**  
    No. The README says Power BI can connect to SQLite with an installed SQLite connector or import the per-symbol CSVs, but the project does not generate a `.pbix`. Report authoring is a separate task in Power BI Desktop.

77. **How is dashboard data cached?**  
    `load_project_data()` is decorated with `@st.cache_data`. Its cache key includes the source path and source modification time plus the sector file modification time, so changing those tracked file attributes causes Streamlit to reload and process the data.

78. **Why are modification times passed to the cached function?**  
    They act as cache-key inputs even though the function discards them internally. This gives Streamlit a way to distinguish data-file versions and avoid reusing a result after the source or sector file has changed.

79. **What is a limitation of the current cache key?**  
    It uses file paths and modification times, not a content hash. If a file is replaced while preserving its timestamp, Streamlit may not detect the content change from those arguments alone. The code also caches a function that runs the export-and-database pipeline, so it is designed around the app’s current load flow.

80. **How does the dashboard handle a missing dataset?**  
    It shows instructions for placing YAML in the raw-data folder or setting `STOCK_DATA_PATH`, optionally adding `sectors.csv`, and refreshing the page. It then calls `st.stop()` so charts are not rendered from invented or empty values.

81. **How does the app handle load and parse errors?**  
    The loading block catches common filesystem, value, pandas parser/empty-data, and YAML errors, displays the error with `st.error()`, and stops execution. This gives the user an actionable failure point rather than a later chart exception.

82. **What does the dashboard display about validation?**  
    It shows the symbol count, latest available date, and accepted observation count. If rows were rejected or duplicate observations removed, an expandable report shows those totals and the reason-count dictionary.

83. **Which key performance indicators appear at the top?**  
    The app displays stocks analyzed, green stocks, red stocks, average latest close, and average latest volume. It separately captions neutral-stock count when that count is nonzero.

84. **How are yearly top gainers and losers visualized?**  
    `app.py` selects the ten largest or smallest `annual_return_pct` values and renders horizontal Plotly bar charts with green and red color scales. Their ranking uses the first-to-last return for each symbol in the loaded data window.

85. **How is volatility visualized?**  
    The dashboard selects the ten highest `volatility_pct` values and displays a horizontal bar chart with an orange scale. This is annualized historical sample volatility derived from daily closing-price returns, not a forecast of future risk.

86. **How are cumulative-return lines selected?**  
    The app takes the five symbols with the largest first-to-last annual returns and plots their `cumulative_return` series over date. This chart selection is based on the same loaded-period summary; it does not select five stocks independently of the data window.

87. **How are monthly leader charts arranged?**  
    The app sorts the available month values, lays them out two columns at a time, and combines each month’s gainers and losers into a grouped Plotly bar chart. `monthly_leaders()` supplies up to five records for each side.

88. **What does the stock summary table show?**  
    In an expander, the app presents the per-symbol summary DataFrame and formats first/last close, annual return, volatility, and average volume for readability. Its source is `metrics["stocks"]`, not a separate data feed.

89. **How does the correlation visual communicate values?**  
    It uses a Plotly `Heatmap` with symbols on both axes, a diverging `RdBu` scale bounded from -1 to 1, and hover text showing the pair and correlation. A message is shown instead if fewer than two stocks are represented.

90. **How is UI presentation kept separate from analytics?**  
    Reusable calculations live in `stock_analysis.analytics`: `calculate_metrics()`, `sector_performance()`, and `monthly_leaders()`. The Streamlit module calls these functions and focuses on layout, labels, chart construction, and user-facing messages.

91. **What tests are included?**  
    `tests/test_stock_analysis.py` covers nested YAML context, ZIP ingestion, invalid and duplicate rows, incomplete OHLCV input, return/volatility/monthly leader calculations, sector aggregation, CSV exports, and SQLite table/view outputs.

92. **How do the tests verify validation behavior?**  
    `test_invalid_and_duplicate_rows_are_reported()` checks that an invalid date is rejected and the last duplicate observation survives. `test_incomplete_price_rows_are_reported_not_silently_dropped()` checks that a missing volume is rejected and counted under `invalid_price_or_volume`.

93. **How are metric calculations tested without real market data?**  
    The helper `_sample_data()` builds a small synthetic DataFrame for `AAA` and `BBB`. Tests assert example returns, positive volatility, green/red counts, and monthly leaders. These are unit-test fixtures, not claims about the project’s supplied market performance.

94. **How can the test suite be run?**  
    From the project root, run `python -m pytest`, as documented in the README. Focused test execution can also target `tests/test_stock_analysis.py` when iterating on ingestion, analytics, or persistence changes.

95. **What data-integrity issue does deduplication solve?**  
    Multiple valid rows for one symbol and date would otherwise distort return sequences and create ambiguity in latest-date queries. Keeping the last valid duplicate and reporting how many were removed gives deterministic downstream data while preserving a visible signal that the source had duplicates.

96. **What integrity limitations should be disclosed?**  
    The loader checks required fields, parseability, positive OHLC prices, nonnegative volume, and high/low consistency, but it does not verify an exchange’s official calendar, source provenance, currency, corporate actions, or whether the symbol is a real listed security. Data correctness still depends on the source provider.

97. **How does the code treat adjusted closing prices?**  
    `adjusted_close` and `adj_close` are recognized as aliases for the canonical `close` field. The model stores and analyzes one close series; it does not keep both raw close and adjusted close separately or document the source’s adjustment methodology.

98. **What assumptions or limitations affect return interpretation?**  
    Metrics use the supplied closing-price sequence, with no explicit transaction costs, dividends, split handling beyond any adjustment already present in the input, or benchmark comparison. The “annual return” is the available-period first-to-last percentage, while volatility assumes 252 trading days.

99. **What are the main operational limitations?**  
    A valid source is required; very large ZIPs are bounded by the implemented member-count and uncompressed-size limits; outputs are local CSV/SQLite/JSON files; and Power BI integration is via import or connector rather than a generated report. The README recommends Python 3.10 or later.

100. **How would you responsibly summarize this project in an interview?**  
     It is a modular Python pipeline and Streamlit dashboard for user-supplied daily stock data: YAML/ZIP ingestion, normalization and validation, pandas-based return and volatility analysis, optional sector aggregation, CSV and SQLite delivery, and tested core functions. Be clear about the first-to-last return definition, the lack of included market results, source-data limitations, and that it is not investment advice.
