import os
import mysql.connector

# Database Connection Details (should match Project-01.py)
DB_HOST = "127.0.0.1"
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = "client_query_db"

def init_db_standalone():
    conn = None
    try:
        # First connect to MySQL server without a database to create it
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()

        # Create Database if it doesn't exist
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cur.execute(f"USE {DB_NAME}")
        print(f"Database '{DB_NAME}' is ready.")

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                username VARCHAR(255) NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL,
                UNIQUE(username, role)
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                query_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                mail_id VARCHAR(255) NOT NULL,
                mobile_number VARCHAR(20) NOT NULL,
                query_heading VARCHAR(255) NOT NULL,
                query_description TEXT NOT NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'Open',
                query_created_time DATETIME NOT NULL,
                query_closed_time DATETIME
            )
        """)

        conn.commit()
        print("Database schema initialized successfully.")
    except mysql.connector.Error as err:
        print(f"Error initializing database schema: {err}")
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    init_db_standalone()
