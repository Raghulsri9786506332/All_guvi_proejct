# synthetic_client_queries (1).csv

## Purpose

This is a synthetic sample dataset for loading example client queries into the database. It contains 5,200 rows.

## Columns

- `query_id`: sample query identifier from the CSV; the loader removes it so the database can generate an ID.
- `client_email`: client's email address; renamed to `mail_id`.
- `client_mobile`: client's mobile number; renamed to `mobile_number`.
- `query_heading`: short subject for the query.
- `query_description`: details of the client's issue or request.
- `status`: current state, such as open or closed.
- `date_raised`: date the query was submitted; renamed to `query_created_time`.
- `date_closed`: date the query was closed; renamed to `query_closed_time`.

The CSV is loaded by [load_csv_to_mysql.py](./load_csv_to_mysql.md). The names and date values should remain compatible with the database table.
