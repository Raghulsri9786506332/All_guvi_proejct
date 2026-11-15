# drop_tables.py

## Purpose

This utility drops the `queries` and `users` tables from the project database.

## Functions

There are no functions defined in this file. It connects to MySQL, runs the two `DROP TABLE IF EXISTS` commands, and commits the changes when executed.

Run only when you intentionally want to delete both tables and their data:

```powershell
python drop_tables.py
```

**Warning:** This operation permanently deletes the table data. Back up anything important first.
