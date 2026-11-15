# Project-01.py

## Purpose

This is the main Streamlit application. It connects to MySQL, handles login and registration, lets clients submit and view queries, and gives support users a dashboard to search, filter, and close queries.

## Main parts

- **Database connection:** MySQL Connector is used for database commands. SQLAlchemy is used when reading query results into Pandas.
- **Tables:** `users` stores usernames, password hashes, and roles. `queries` stores contact information, query text, status, and dates.
- **Login and registration:** users choose a `Client` or `Support` role.
- **Client screen:** lets a client submit a query and view queries associated with their username.
- **Support screen:** shows queries, filters by status, searches text, and closes open queries.

## Functions

### `get_connection()`

Opens and returns a MySQL Connector connection using the database settings at the top of the file. Other functions use this connection to run SQL commands. The database settings must match the local MySQL setup.

### `get_engine()`

Creates and returns a SQLAlchemy engine for the MySQL database. `fetch_queries()` uses it to read query results into a Pandas DataFrame.

### `hash_password(password)`

Encodes the password as UTF-8 and returns its SHA-256 hash as text. The app compares hashes rather than storing the original password. SHA-256 by itself is not recommended for password storage; a password-specific algorithm such as bcrypt or Argon2 would be safer.

### `init_db()`

Creates the `users` and `queries` tables if they do not already exist, then commits the database changes. The standalone `init_schema.py` script provides a separate setup path that also creates the database.

### `seed_demo_users()`

Attempts to insert one demo client and one demo support user. It ignores a duplicate-user integrity error. This function is defined in the main app, but the normal UI flow does not call it; `seed_users.py` is the separate script for creating the demo users.

### `register_user(username, password, role)`

Hashes the password and inserts a new user. It returns a success value and a message. If the username and role already exist, it returns a message saying the user already exists.

### `authenticate_user(username, password, role)`

Hashes the supplied password and looks for a matching username, hash, and role in the `users` table. It returns `True` when a matching record exists and `False` otherwise.

### `submit_query(mail_id, mobile_number, query_heading, query_description)`

Inserts a new query into the `queries` table. The status starts as `Open`, the creation time is set to the current time, and the closing time is empty.

### `fetch_queries(status_filter=None, search_text=None, mail_id=None)`

Builds and runs a query to fetch records. It can filter by status, search the heading and description, and filter by email. It returns the results as a Pandas DataFrame, sorted with the newest query first.

### `close_query(query_id)`

Updates a query with the given ID, but only if its current status is `Open`. It changes the status to `Closed` and records the closing time.

## Important behavior and limitations

- The app uses parameterized values for database queries, which is safer than inserting user input directly into SQL.
- Client query visibility is filtered using the logged-in username as the email address. A production system should enforce and test authorization carefully on every request.
- The current source uses SHA-256 for password hashing and keeps database settings in the source file. Improve both before deployment.
- The app does not define custom classes; its application logic is organized mainly into functions.
- The Streamlit UI code runs at the top level and is rerun by Streamlit when a user interacts with the page.
