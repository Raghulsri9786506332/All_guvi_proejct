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
    cur.execute("SHOW CREATE TABLE queries;")
    for row in cur.fetchall():
        print(row[1])
except Exception as e:
    print(e)
