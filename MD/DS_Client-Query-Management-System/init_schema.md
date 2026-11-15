# init_schema.py

## Purpose

This standalone setup script connects to MySQL, creates the `client_query_db` database if needed, selects it, and creates the `users` and `queries` tables if they do not already exist.

## Function

### `init_db_standalone()`

Connects to the MySQL server, prepares the database and tables, and commits the changes. It prints a success message when setup completes and reports MySQL errors. It closes the connection in the `finally` block when a connection was opened.

The script calls this function when run directly:

```powershell
python init_schema.py
```

Set the connection settings in this file to match the local MySQL server before running it. Do not put production credentials in shared source code.

## Tables created

- `users`: auto-increment ID, username, password hash, and role. A username and role pair must be unique.
- `queries`: auto-increment query ID, contact details, heading, description, status, creation time, and optional closing time.
