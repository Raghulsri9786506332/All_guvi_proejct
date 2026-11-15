import os
import mysql.connector

try:
    conn = mysql.connector.connect(
        host="127.0.0.1",
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database="client_query_db",
    )
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS queries;")
    cur.execute("DROP TABLE IF EXISTS users;")
    conn.commit()
    print("Tables dropped successfully.")
except Exception as e:
    print(f"Error dropping tables: {e}")
