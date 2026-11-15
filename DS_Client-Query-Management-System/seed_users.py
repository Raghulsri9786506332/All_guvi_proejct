import os
import mysql.connector
import hashlib

# Database Connection Details (should match Project-01.py)
DB_HOST = "127.0.0.1"
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = "client_query_db"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def seed_demo_users_standalone():
    conn = None
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cur = conn.cursor()

        demo_users = [
            ("client1@gmail.com", hash_password("client123"), "Client"),
            ("support1", hash_password("support123"), "Support"),
        ]

        for username, hpw, role in demo_users:
            try:
                cur.execute(
                    "INSERT INTO users (username, hashed_password, role) VALUES (%s, %s, %s)",
                    (username, hpw, role)
                )
                print(f"User '{username}' ({role}) seeded successfully.")
            except mysql.connector.IntegrityError:
                print(f"User '{username}' ({role}) already exists, skipping.")
            except Exception as e:
                print(f"Error seeding user '{username}': {e}")

        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error seeding demo users: {err}")
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    seed_demo_users_standalone()