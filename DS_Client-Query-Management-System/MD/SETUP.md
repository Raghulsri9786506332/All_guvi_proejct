# Setup and run guide

This guide describes how to run the project on a computer with Python and MySQL.

## 1. Install the Python packages

Open PowerShell in the project folder and install the packages used by the scripts:

```powershell
python -m pip install streamlit mysql-connector-python sqlalchemy pandas
```

## 2. Prepare MySQL

1. Start the MySQL server.
2. In PowerShell, set the MySQL credentials for the current terminal session (replace the values with your local account):

```powershell
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "your-local-mysql-password"
```

The database name used by the project is `client_query_db`. Do not put real passwords in source files or commit them.
3. From the project folder, create the database and tables:

```powershell
python init_schema.py
```

The schema script creates the database if needed and creates the `users` and `queries` tables.

## 3. Add demo users (optional)

To insert the demo client and support accounts, run:

```powershell
python seed_users.py
```

The demo credentials are listed in the app's login screen. Change or remove these accounts before using the app outside a local demo.

## 4. Start the Streamlit app

Run:

```powershell
python -m streamlit run Project-01.py
```

Streamlit prints a local address in the terminal. Open that address in a browser.

## 5. Load the sample CSV (optional)

The CSV loader expects `synthetic_client_queries (1).csv` in the current project folder and a `queries` table to already exist. Run:

```powershell
python load_csv_to_mysql.py
```

The loader appends rows. Running it repeatedly can add duplicate records. The script drops the CSV's `query_id` field so MySQL can generate IDs.

## Utility scripts

- `check_schema.py` prints the MySQL definition of the `queries` table.
- `drop_tables.py` permanently drops the `queries` and `users` tables. Do not run it unless you intend to delete that data.
