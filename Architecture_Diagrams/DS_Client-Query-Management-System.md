# Client Query Management System — Architecture

```mermaid
flowchart TD
    Browser[User browser]
    UI[Streamlit UI<br/>Project-01.py]
    Session[Streamlit session state<br/>login, username, role]
    Auth[Authentication and registration<br/>authenticate_user / register_user]
    Client[Client workflow<br/>submit_query / fetch_queries]
    Support[Support workflow<br/>fetch_queries / close_query]
    Connector[MySQL Connector<br/>parameterized SQL]
    Engine[SQLAlchemy engine<br/>Pandas query reads]
    DB[(MySQL<br/>client_query_db)]
    Users[(users table)]
    Queries[(queries table)]
    Init[init_schema.py<br/>create database and tables]
    Seed[seed_users.py<br/>insert demo accounts]
    CSV[synthetic_client_queries CSV]
    Loader[load_csv_to_mysql.py<br/>Pandas + SQLAlchemy]
    Check[check_schema.py]
    Drop[drop_tables.py<br/>destructive utility]

    Browser --> UI
    UI <--> Session
    UI --> Auth
    UI --> Client
    UI --> Support
    Auth --> Connector
    Client --> Connector
    Support --> Connector
    Client --> Engine
    Support --> Engine
    Connector --> DB
    Engine --> DB
    DB --- Users
    DB --- Queries
    Init --> DB
    Seed --> DB
    CSV --> Loader --> DB
    Check --> DB
    Drop -. deletes tables .-> DB
```

## Request flow

1. A user opens the Streamlit app in a browser and logs in or registers.
2. The app checks or writes account data in the MySQL `users` table.
3. A client submits a query; the app inserts it into `queries` with `Open` status.
4. Clients see query rows filtered using their username/email. Support users can search and filter the full list and close an open query.
5. The CSV loader is an optional separate path for importing sample query rows.

## Notes

- The application has two database access styles: MySQL Connector for writes and SQLAlchemy/Pandas for reads.
- The current schema does not define a foreign key linking a query to a user, and the app does not use a SQL `JOIN`.
- The app uses role selection at registration and SHA-256 password hashing. These are demo limitations, not production security recommendations.
- `drop_tables.py` removes both application tables and should be treated as destructive.
