# load_csv_to_mysql.py

## Purpose

This script reads `synthetic_client_queries (1).csv`, adjusts several CSV column names to match the database schema, and appends the data to the MySQL `queries` table.

## Function

### `load_data()`

Reads the CSV with Pandas, renames `client_email`, `client_mobile`, `date_raised`, and `date_closed` to the corresponding database column names, and removes `query_id` so MySQL can assign IDs. It then uses SQLAlchemy and Pandas to append the rows to `queries`.

The script prints progress and reports errors raised during database insertion. The CSV file must be in the current working folder when the script is run.

Run:

```powershell
python load_csv_to_mysql.py
```

## Important notes

- Create the database and `queries` table first with `init_schema.py`.
- The script uses append mode. Running it again can insert the same sample records again.
- Check that the local database settings in the script are correct.
- Dates and column names in the CSV must remain compatible with the table schema.
