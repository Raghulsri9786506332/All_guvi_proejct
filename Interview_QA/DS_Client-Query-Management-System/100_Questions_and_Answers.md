# Client Query Management System: 100 Interview Questions and Answers

These questions are based on the Streamlit application in `Project-01.py` and its MySQL setup, seed, and CSV-import scripts. Answers describe the current implementation; suggested improvements are identified as such.

1. **Q: What problem does this application solve?**  
   **A:** It provides a small client-support workflow: clients register or log in, submit queries, and view queries associated with their email; support users can search, filter, and close open queries. Streamlit supplies the interface and MySQL persists users and queries.

2. **Q: What are the main architectural components?**  
   **A:** `Project-01.py` contains both the UI and database operations. MySQL Connector handles inserts and updates, SQLAlchemy plus Pandas reads query results into a DataFrame, and standalone scripts initialize the schema, seed accounts, inspect/drop tables, and load a CSV. There is no separate API service or custom class layer.

3. **Q: How is the application organized in code?**  
   **A:** It is a single Streamlit script organized into functions such as `get_connection`, `authenticate_user`, `submit_query`, and `fetch_queries`, followed by top-level UI code. The utility scripts handle setup tasks separately; this is a function-oriented design, not an object-oriented domain model.

4. **Q: What happens when a user opens the app?**  
   **A:** Streamlit executes `Project-01.py` from the top. The app configures a wide page, displays the title, initializes missing login keys in `st.session_state`, then shows either the Login/Register tabs or the page for the stored role.

5. **Q: Why does Streamlit rerun the script after interaction?**  
   **A:** Reruns are Streamlit’s normal execution model: a widget interaction causes the script to execute again from the top. The app therefore keeps login state in `st.session_state` and uses forms for grouped input rather than relying on ordinary local variables to persist.

6. **Q: How does this app use `st.session_state`?**  
   **A:** It initializes `logged_in`, `username`, and `role` if absent, sets them after successful login, and clears them on logout. These values let the rerun choose the authenticated UI branch and determine which dashboard to display.

7. **Q: What is the effect of `st.rerun()` after login?**  
   **A:** The login branch sets the three session-state values, reports success, and calls `st.rerun()`. The next execution takes the authenticated branch immediately instead of waiting for another widget interaction.

8. **Q: What does the logout button do, and what does it not do?**  
   **A:** It resets `logged_in` to `False`, clears the username and role, and reruns the script to show the login page. It does not revoke a server-side token or invalidate an independent session record; the app’s login state is Streamlit session state.

9. **Q: Why are forms used for login and query submission?**  
   **A:** `st.form` groups related fields and submits them together. The database action runs only after `st.form_submit_button` returns true, avoiding a database write on every field edit during the form interaction.

10. **Q: What is the distinction between the Client and Support screens?**  
    **A:** The logged-in `role` selects the screen. A Client gets the query form and a table filtered to their username; a Support user gets status and text filters, all matching queries, and a control to close an open query.

11. **Q: Which functions own the database connections?**  
    **A:** `get_connection()` returns a MySQL Connector connection for the configured database, while `get_engine()` constructs a SQLAlchemy engine used by `fetch_queries()`. Most write functions open their own connector connection and close it after the operation.

12. **Q: Why does the project use both MySQL Connector and SQLAlchemy?**  
    **A:** The direct connector is used for explicit cursor operations such as `INSERT` and `UPDATE`; SQLAlchemy is used with `pd.read_sql_query` to load results into Pandas. The split supports the code’s current needs, although standardizing on one access layer could make transaction and connection handling easier to maintain.

13. **Q: What is the purpose of `get_connection()`?**  
    **A:** It centralizes the host, user, password, and database settings for direct MySQL connections. Functions such as `register_user` and `close_query` call it rather than repeating connection arguments at each call site.

14. **Q: What is the purpose of `get_engine()`?**  
    **A:** It builds a SQLAlchemy engine URL for `client_query_db` using the MySQL Connector driver. `fetch_queries()` passes that engine and its SQL string and parameters to Pandas for reading.

15. **Q: Does the main app create its tables automatically?**  
    **A:** `init_db()` contains `CREATE TABLE IF NOT EXISTS` statements, but the normal top-level UI flow does not call it. The standalone `init_schema.py` creates the database and tables, so setup must be run separately before using the app.

16. **Q: What does `init_schema.py` do that `init_db()` does not?**  
    **A:** The standalone script first connects without selecting the application database, creates `client_query_db` if needed, selects it, and creates the `users` and `queries` tables. The app’s `init_db()` only creates tables through a connection that already expects that database to exist.

17. **Q: What is the responsibility of `seed_users.py`?**  
    **A:** It inserts a demo Client and a demo Support account using password hashes and catches duplicate-key errors so an existing demo account is skipped. It is an optional setup script; the app’s own `seed_demo_users()` function is defined but is not called in the normal UI flow.

18. **Q: What does `check_schema.py` help verify?**  
    **A:** It runs `SHOW CREATE TABLE queries` and prints MySQL’s actual definition of the `queries` table. This is useful for comparing the live schema with the declarations in `init_schema.py`.

19. **Q: Why is `drop_tables.py` potentially dangerous?**  
    **A:** It executes `DROP TABLE IF EXISTS` for both `queries` and `users` and commits. This removes stored application data, so it should only be used for intentional cleanup or a disposable development database.

20. **Q: How does the app register a user?**  
    **A:** `register_user(username, password, role)` hashes the supplied password, inserts username/hash/role into `users`, commits, and returns a `(success, message)` tuple. A MySQL integrity error is reported as an existing username for that role.

21. **Q: How does login authentication work?**  
    **A:** `authenticate_user` hashes the entered password and queries `users` for a row matching username, hash, and role. It returns `True` if `fetchone()` finds a row and `False` otherwise; the UI sets session state only on success.

22. **Q: Why is role included in the authentication query?**  
    **A:** The SQL condition is `username = %s AND hashed_password = %s AND role = %s`. The role selector is therefore part of the credential match, and the same username under a different role would not satisfy that login attempt.

23. **Q: How are roles represented in the database and UI?**  
    **A:** `users.role` is a `VARCHAR(50)` and the UI presents the literal choices `Client` and `Support` during login and registration. The code uses role equality to choose a UI branch; it does not implement a general permissions or role-policy framework.

24. **Q: Can an arbitrary role be registered through the current UI?**  
    **A:** The UI’s select box limits the submitted values to Client and Support. However, the `register_user` function itself accepts a role argument without validating it, so a separate caller could pass another value unless validation is added there or enforced in the database.

25. **Q: Is registration restricted to client accounts?**  
    **A:** No. The Register tab exposes the same `Client`/`Support` role selector, so a user can register a Support account through the UI. A production design should restrict privileged account creation to a controlled process.

26. **Q: What database constraints protect the `users` table?**  
    **A:** `id` is an auto-increment primary key; username, password hash, and role are non-null; and `UNIQUE(username, role)` prevents duplicate usernames within the same role. The schema does not enforce uniqueness of username across different roles.

27. **Q: What fields are stored in the `queries` table?**  
    **A:** It has auto-increment `query_id`, `mail_id`, `mobile_number`, `query_heading`, `query_description`, `status`, `query_created_time`, and nullable `query_closed_time`. Text, contact data, current status, and lifecycle timestamps are kept in one table.

28. **Q: What constraints and defaults are defined for queries?**  
    **A:** The query ID is the primary key; email, mobile, heading, description, status, and creation time are non-null. `status` defaults to `Open`, while `query_closed_time` can be `NULL`; there are no foreign keys or status check constraints in the declared schema.

29. **Q: Why is `query_id` auto-incremented?**  
    **A:** It supplies a stable database-generated identifier for each query. `close_query(query_id)` uses that identifier to target a record, and the CSV loader drops imported `query_id` values so MySQL can generate IDs.

30. **Q: How is a new query inserted?**  
    **A:** `submit_query` creates a timestamp, then inserts the contact fields and text with status `'Open'` and closing time `NULL`. It uses `%s` placeholders for the supplied values and commits the transaction.

31. **Q: How does `submit_query` create the timestamp?**  
    **A:** It calls `datetime.now().strftime("%Y-%m-%d %H:%M:%S")` and passes that string as `query_created_time`. This uses the application machine’s local clock rather than an explicitly configured UTC/database timestamp.

32. **Q: What validations happen before a client submission?**  
    **A:** The UI checks that email, mobile, heading, and description are all truthy, and otherwise displays “Please fill all fields.” It does not currently validate email format, phone-number format, length limits, or trimmed whitespace.

33. **Q: How does a client see their own queries in the current flow?**  
    **A:** The UI calls `fetch_queries(mail_id=st.session_state.username)`, and `fetch_queries` adds `AND mail_id = %s`. The form defaults the email field to the username, but the table filter itself is based on the logged-in username.

34. **Q: Is the query author linked to the logged-in account in the schema?**  
    **A:** No. The `queries` table stores `mail_id` as text and has no user ID foreign key. The app associates rows with a user by matching email text, which is simple but can become fragile if usernames or emails change.

35. **Q: How can Support users filter query status?**  
    **A:** The select box offers `All`, `Open`, and `Closed`. `fetch_queries` omits a status condition for `All`; otherwise it appends `AND status = %s` and binds the selected status.

36. **Q: How does the text search work?**  
    **A:** If `search_text` is nonempty, `fetch_queries` adds a condition matching `query_heading LIKE %s OR query_description LIKE %s`. It binds the same pattern, such as `%refund%`, for both fields.

37. **Q: How are multiple optional filters combined?**  
    **A:** The query starts with `SELECT * FROM queries WHERE 1=1`, then appends conditions for status, search text, and email only when supplied. Because each condition is joined with `AND`, active filters narrow the result together.

38. **Q: Why does `fetch_queries` start with `WHERE 1=1`?**  
    **A:** It makes every optional condition easy to append with `AND` without checking whether a `WHERE` clause already exists. It is a common dynamic-query construction pattern; it is not itself a security control.

39. **Q: How are SQL values parameterized in the app?**  
    **A:** Connector statements use `%s` placeholders and tuples, for example the `INSERT` in `submit_query`; `fetch_queries` binds its `params` tuple to the read. This keeps values separate from SQL text instead of concatenating user-provided values into the statement.

40. **Q: Does parameterization make every part of dynamic SQL safe automatically?**  
    **A:** No. The code safely binds values such as status, search patterns, email, and IDs, while the SQL structure is assembled from fixed fragments. If future code makes table or column names user-selectable, those identifiers need allow-list validation because placeholders generally bind values, not SQL identifiers.

41. **Q: What does the `LIKE` pattern mean in this search?**  
    **A:** Wrapping the entered text in `%` on both sides searches for that substring anywhere in the heading or description. It does not escape `%` or `_`, so those characters typed by a user retain SQL `LIKE` wildcard meaning.

42. **Q: In what order are query results returned?**  
    **A:** `fetch_queries` appends `ORDER BY query_created_time DESC`, so the newest creation timestamp appears first. No explicit secondary sort is provided for equal timestamps.

43. **Q: How are query rows displayed?**  
    **A:** The result of `pd.read_sql_query` is a Pandas DataFrame, which the UI displays with `st.dataframe(..., use_container_width=True)`. The support UI derives an `open_df` from that displayed result for the close selector.

44. **Q: How does the application close a query?**  
    **A:** `close_query` updates status to `Closed` and sets `query_closed_time` to the current formatted timestamp, with a `WHERE` clause requiring both the specified `query_id` and current status `Open`. It commits the update.

45. **Q: Why does `close_query` include `status = 'Open'` in its condition?**  
    **A:** It prevents the update from changing already-closed records and makes the transition one-way through this function. The UI also only offers IDs from rows currently marked Open, but the database condition is an additional guard against stale UI state.

46. **Q: Does the app report whether a close operation actually changed a row?**  
    **A:** No. `close_query` commits but does not inspect `cursor.rowcount` or return a result. The UI then displays success based on the button click, even if a concurrent update meant no row matched.

47. **Q: How are database changes made durable?**  
    **A:** The write functions call `conn.commit()` after inserts or updates. Without that commit, MySQL’s transaction behavior could leave changes uncommitted; explicit transaction context management would make success/failure handling clearer.

48. **Q: How are database connections closed?**  
    **A:** Most functions close the connector connection after their work; `register_user` uses `finally` so it closes on both success and integrity error. Other functions such as `authenticate_user`, `submit_query`, and `close_query` do not consistently use `try/finally`, so an exception can bypass their close call.

49. **Q: What error handling exists for registration?**  
    **A:** `register_user` catches `mysql.connector.IntegrityError`, returns a user-facing duplicate message, and closes the connection in `finally`. Other connector failures are not caught in this function and can propagate to Streamlit.

50. **Q: What error handling exists for authentication?**  
    **A:** The current function performs the query and returns whether a row exists, but it does not catch connection or SQL errors. An unavailable database therefore does not become the ordinary “invalid username” result; it can surface as an application error.

51. **Q: What error handling exists for the CSV loader?**  
    **A:** `load_data()` reads the CSV before its `try` block, then catches exceptions around engine creation and `to_sql`, printing an error and a password reminder. A missing CSV or parsing failure can occur before that handler.

52. **Q: What error handling exists in the standalone schema setup?**  
    **A:** `init_schema.py` catches `mysql.connector.Error`, prints a diagnostic, and closes the connection in `finally` if it is connected. It is a command-line setup script rather than an error page integrated into the Streamlit UI.

53. **Q: What is the password-hashing implementation?**  
    **A:** `hash_password(password)` encodes the string as UTF-8 and returns `hashlib.sha256(...).hexdigest()`. Registration stores that digest, and authentication hashes the entered password and compares the resulting text in SQL.

54. **Q: Why is plain SHA-256 not a good production password-storage algorithm?**  
    **A:** It is fast and unsalted in this implementation, so a leaked hash database is easier to attack with precomputed or high-speed guessing. A password-specific, salted, deliberately slow algorithm such as Argon2id or bcrypt is a realistic improvement.

55. **Q: Does this implementation use a per-user salt?**  
    **A:** No. `hash_password` takes only the password and returns its deterministic SHA-256 digest; the schema stores no separate salt. The same password therefore produces the same digest for different users.

56. **Q: How are database credentials configured?**  
    **A:** The scripts declare database host, username, password, and database name as constants in source. This is convenient for a local exercise but risky for shared or deployed code; environment variables or Streamlit secrets should be used, with secrets excluded from version control.

57. **Q: How is access control enforced in the UI?**  
    **A:** The UI branches on the session-state role: only the Client branch calls the client page and only the Support branch displays the support dashboard. Query visibility for a client also uses `mail_id=st.session_state.username`.

58. **Q: Is the UI role check equivalent to a robust authorization boundary?**  
    **A:** Not by itself. The application is a single Streamlit script and relies on session state and UI branching; there is no separate service-layer authorization policy, role-permission matrix, or audit trail. Production access control should be verified at every data operation.

59. **Q: Can a client choose a different email in the submission form?**  
    **A:** Yes. The email field defaults to the session username but is still editable, and the submit function stores the value supplied by the form. The client’s listing remains filtered by the logged-in username, so a submitted query with a different email may not appear in that client’s own list.

60. **Q: What is one security concern in query ownership?**  
    **A:** Ownership is represented by a client-supplied email string, not a server-enforced user ID relationship. A better design would derive ownership from the authenticated identity on the server and store a foreign key to `users.id`, rather than trusting an editable field.

61. **Q: What does the login screen reveal about demo accounts?**  
    **A:** It displays demo usernames and passwords in an informational message, and the setup guide describes the demo accounts created by `seed_users.py`. That is acceptable only for a controlled demonstration; those credentials must be removed or changed before exposure to real users.

62. **Q: What does the CSV loader read?**  
    **A:** `load_data()` reads `synthetic_client_queries (1).csv` using `pd.read_csv`. The script expects that relative path to exist in the current working directory, so it depends on how and from where it is launched.

63. **Q: How are CSV columns mapped to database fields?**  
    **A:** The loader renames `client_email` to `mail_id`, `client_mobile` to `mobile_number`, `date_raised` to `query_created_time`, and `date_closed` to `query_closed_time`. Other columns such as `query_heading`, `query_description`, and `status` retain their names.

64. **Q: Why does the CSV loader remove `query_id`?**  
    **A:** The database assigns `query_id` using `AUTO_INCREMENT`, so the loader drops the CSV identifier before appending rows. This avoids trying to preserve potentially conflicting source IDs.

65. **Q: How are CSV rows inserted?**  
    **A:** The script builds a SQLAlchemy engine and calls `df.to_sql(name="queries", con=engine, if_exists="append", index=False)`. It appends records to the existing table and does not include the DataFrame index.

66. **Q: What can happen if the CSV loader is run more than once?**  
    **A:** Because it uses `if_exists="append"` and does not deduplicate rows, repeating the import can insert the same records again with new auto-increment IDs. An idempotent import could track a source key or stage and validate rows before merging.

67. **Q: Does `to_sql` validate the CSV against the application schema?**  
    **A:** The script renames a few columns and drops `query_id`, but it does not explicitly validate required fields, status values, data types, or date parsing before insertion. MySQL’s existing table constraints and SQLAlchemy conversion may reject incompatible data, but error messages are only printed.

68. **Q: What is a possible CSV date-format issue?**  
    **A:** The sample contains date-only values such as `2025-02-26`, while the schema declares `DATETIME`. The loader does not explicitly parse or normalize these columns, so a production-quality importer should define expected formats, convert them deliberately, and report invalid rows.

69. **Q: Does the CSV import script initialize the database schema?**  
    **A:** No. It assumes the database and `queries` table already exist. The setup guide runs `init_schema.py` first; the loader’s comment about creating a table if missing is not guaranteed to match the declared application schema if `to_sql` creates one from inferred DataFrame types.

70. **Q: What does the sample CSV reveal about the source data?**  
    **A:** Its columns include `query_id`, `client_email`, `client_mobile`, `query_heading`, `query_description`, `status`, `date_raised`, and `date_closed`. The loader adapts these source names to the application’s `queries` schema, except for fields already named the same.

71. **Q: Are there automated tests in the project?**  
    **A:** The inspected project contains the app, setup and utility scripts, a sample CSV, and documentation, but no test suite. Important behavior such as authentication, filtering, status updates, schema compatibility, and import repeatability therefore needs explicit automated coverage.

72. **Q: How would you unit-test `hash_password`?**  
    **A:** Test that the result matches SHA-256’s expected hexadecimal output for a known UTF-8 string, and that repeated calls for the same input are equal. A future salted password hasher would instead need tests for verification and distinct per-user salts.

73. **Q: How would you test `fetch_queries` without a live MySQL database?**  
    **A:** Refactor query construction into a small pure helper returning SQL and parameters, then test combinations such as status only, search only, email only, and all filters together. Database integration tests can separately exercise the actual parameter binding and result DataFrame.

74. **Q: How would you integration-test query submission and closure?**  
    **A:** Use an isolated test database, insert a query through `submit_query`, verify it is Open with a null close time, close it, then verify Closed status and a populated close time. Also assert that trying to close it again does not change it.

75. **Q: How would you test the client query-visibility rule?**  
    **A:** Create rows for two different email values and verify the client call `fetch_queries(mail_id=...)` returns only the matching one. Add a UI-level test or refactored authorization test ensuring the filter uses the authenticated username rather than editable submission input.

76. **Q: How would you test `register_user` duplicate behavior?**  
    **A:** Register a user, repeat the same username and role, and assert the second call returns `False` with the duplicate message. Also test that the same username with a different role is allowed by the current `UNIQUE(username, role)` constraint, if that behavior is intended.

77. **Q: What testing challenge comes from the current structure?**  
    **A:** Database calls, query construction, hashing, and UI logic are coupled within one script, and there are no injected connection dependencies or test fixtures. Extracting a data-access module and pure validation/query-building functions would make focused tests easier.

78. **Q: What happens if the MySQL server is unavailable during a page rerun?**  
    **A:** The current read and authentication paths do not consistently catch connector or SQLAlchemy exceptions, so the rerun can fail rather than showing a graceful database-unavailable message. A connection layer should classify failures, log details safely, and present a simple user-facing message.

79. **Q: How might query volume affect performance?**  
    **A:** `fetch_queries` selects all columns and has no pagination or result limit, and Support can request all matching rows. With a large table, loading every result into Pandas and rendering it can become slow; server-side pagination and indexes would help.

80. **Q: Which database indexes might help the current access patterns?**  
    **A:** An index on `queries.mail_id` could help client listings, and indexes on status or creation time may help common support filters and ordering. The substring search with leading `%` generally cannot use a normal B-tree index effectively, so larger-scale text search may need a different strategy.

81. **Q: Are there foreign keys between users and queries?**  
    **A:** No. `queries.mail_id` is plain text, and the schema does not declare any foreign key to `users`. Adding a `user_id` foreign key could enforce referential integrity and avoid inconsistencies when user identifiers change.

82. **Q: Does the schema constrain valid query statuses?**  
    **A:** No check constraint or status lookup table is defined. The UI and write function currently use `Open` and `Closed`, but the database itself could accept other strings through imports or alternate scripts.

83. **Q: How could status consistency be improved?**  
    **A:** Add a database constraint or a controlled status table, validate imported values, and centralize allowed transitions. That would keep application code, CSV data, and database records aligned even when writes do not come through the Streamlit UI.

84. **Q: What limitation comes from storing the whole query in one table?**  
    **A:** The table captures a query’s current status and timestamps but has no message thread, assignment, category, priority, or status-history table. Supporting back-and-forth support conversations or auditability would require additional related records.

85. **Q: Does the current schema retain a history of status changes?**  
    **A:** No. `close_query` overwrites the status and sets one closing timestamp; there is no event or history table recording who changed the status or when other transitions occurred.

86. **Q: Is there an assignment workflow for Support users?**  
    **A:** No. The support dashboard shows filtered queries and allows closing them, but the schema and UI do not assign a query to a particular support user or track ownership.

87. **Q: How are query form and database field names connected?**  
    **A:** The UI captures `mail_id`, `mobile_number`, `query_heading`, and `query_description`, then passes them in that order to `submit_query`. That function maps those values into matching column names in the `queries` insert statement.

88. **Q: What is the role of Pandas in this project?**  
    **A:** Pandas receives database reads as a DataFrame through `pd.read_sql_query`, enabling straightforward display and filtering of open rows in the dashboard. It also reads the CSV and provides `to_sql` for bulk append in the loader.

89. **Q: How does the support close selector avoid offering closed rows?**  
    **A:** The UI derives `open_df` from the already-filtered DataFrame using `df["status"] == "Open"` and populates the selector from its `query_id` values. If there are no open rows, it displays an informational message instead.

90. **Q: What behavior occurs when search or status filters return no rows?**  
    **A:** The DataFrame is still displayed, and `open_df` becomes an empty DataFrame when no results exist. The close section then shows “No open queries available to close”; the UI does not currently offer a separate no-search-results explanation.

91. **Q: Why should database operations use context managers or centralized cleanup?**  
    **A:** It ensures connections and cursors are released even when an exception occurs. Only some paths, such as `register_user` and schema initialization, guarantee cleanup in a `finally` block; adopting context managers consistently would reduce leaked connections.

92. **Q: How could transaction handling be improved?**  
    **A:** Wrap each write in a clear transaction boundary, commit only after the operation succeeds, and roll back on failure. Returning a structured result and checking `rowcount` for `close_query` would let the UI distinguish success, stale state, and database errors.

93. **Q: How could credentials be removed from source code safely?**  
    **A:** Read connection settings from environment variables or Streamlit’s secrets configuration, document required keys without committing their values, and use a least-privilege database account. Deployment secrets should be rotated if they have ever been shared.

94. **Q: What validation would you add to registration?**  
    **A:** Trim and require a username, enforce password length and complexity policy appropriate to the product, validate role choices inside `register_user`, and provide user-friendly field errors. The current UI submits values with no such checks beyond role options.

95. **Q: What validation would you add to query submission?**  
    **A:** Normalize whitespace, validate email and phone formats, enforce sensible maximum lengths, and prevent a blank description after trimming. The database already has non-null constraints and fixed-width limits for some fields, but front-end validation would give clearer feedback.

96. **Q: What is one improvement to the app’s deployment readiness?**  
    **A:** Move credentials out of source, replace SHA-256 password hashing, prevent public Support self-registration, add robust exception handling and audit logging, and verify authorization in the data layer. The current app is better suited to a local demonstration than an internet-facing service.

97. **Q: How could the code be separated for easier maintenance?**  
    **A:** Keep Streamlit rendering in a UI module, put SQL and transaction logic in a repository/data-access module, and place input validation and authentication policy in service functions. Such a refactor would preserve the current behavior while making each layer independently testable.

98. **Q: What is a realistic improvement to CSV import reliability?**  
    **A:** Resolve the CSV path relative to the script, validate required columns and types, explicitly parse dates and allowed statuses, and load into a staging table before inserting. Record import outcomes or source identifiers so reruns do not silently duplicate records.

99. **Q: What project limitations should an interview candidate state honestly?**  
    **A:** It is a compact Streamlit/MySQL demo with a single-file UI, no automated tests, editable client email, no query-to-user foreign key, simple unsalted SHA-256 hashes, credentials in source, unbounded support reads, and limited exception handling. It also has no JOIN-based workflow, custom classes, assignment, or status history.

100. **Q: How would you summarize the most valuable next steps?**  
     **A:** First make the basics safer and verifiable: move secrets to configuration, use a password-specific hash, restrict Support account creation, and enforce query ownership in server-side data operations. Then add focused tests, schema constraints/indexes, pagination, robust transactions, and a repeatable validated CSV import.
