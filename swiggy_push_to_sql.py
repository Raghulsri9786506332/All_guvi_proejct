"""
NEW FILE: swiggy_push_to_sql.py
Pushes the 3,600-row Swiggy restaurant dataset into MySQL database (client_query_db).
"""
import os
import pandas as pd
import mysql.connector

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "raghul",
    "password": "Raghulsri9786@",
    "database": "client_query_db"
}

CSV_PATH = r"c:\Users\raghu\OneDrive\New folder\Guvi Auto code\swiggy_recommendation\swiggy_recommendation\data\swiggy.csv"

def push_to_sql():
    print(f"Reading dataset from: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(f"Total rows to push: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Create table if not exists
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS swiggy_restaurants (
        id INT PRIMARY KEY,
        name VARCHAR(255),
        city VARCHAR(100),
        rating FLOAT,
        rating_count VARCHAR(100),
        cost VARCHAR(50),
        cuisine VARCHAR(255),
        lic_no VARCHAR(100),
        link TEXT,
        address TEXT,
        menu TEXT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    cursor.execute(create_table_sql)

    # Clean existing data to avoid duplicates or primary key conflicts
    cursor.execute("TRUNCATE TABLE swiggy_restaurants;")
    conn.commit()

    # Insert rows in batches
    insert_sql = """
    INSERT INTO swiggy_restaurants 
    (id, name, city, rating, rating_count, cost, cuisine, lic_no, link, address, menu)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    batch = []
    batch_size = 500
    inserted_count = 0

    for _, row in df.iterrows():
        # Handle types & NaNs safely
        row_id = int(row.get("id", 0)) if pd.notnull(row.get("id")) else None
        name = str(row.get("name", "")) if pd.notnull(row.get("name")) else None
        city = str(row.get("city", "")) if pd.notnull(row.get("city")) else None
        
        try:
            rating = float(row.get("rating")) if pd.notnull(row.get("rating")) and str(row.get("rating")).replace(".", "").isdigit() else None
        except Exception:
            rating = None

        rating_count = str(row.get("rating_count", "")) if pd.notnull(row.get("rating_count")) else None
        cost = str(row.get("cost", "")) if pd.notnull(row.get("cost")) else None
        cuisine = str(row.get("cuisine", "")) if pd.notnull(row.get("cuisine")) else None
        lic_no = str(row.get("lic_no", "")) if pd.notnull(row.get("lic_no")) else None
        link = str(row.get("link", "")) if pd.notnull(row.get("link")) else None
        address = str(row.get("address", "")) if pd.notnull(row.get("address")) else None
        menu = str(row.get("menu", "")) if pd.notnull(row.get("menu")) else None

        batch.append((row_id, name, city, rating, rating_count, cost, cuisine, lic_no, link, address, menu))

        if len(batch) >= batch_size:
            cursor.executemany(insert_sql, batch)
            conn.commit()
            inserted_count += len(batch)
            print(f"  Pushed {inserted_count}/{len(df)} rows...")
            batch = []

    if batch:
        cursor.executemany(insert_sql, batch)
        conn.commit()
        inserted_count += len(batch)

    # Verify count in database
    cursor.execute("SELECT COUNT(*) FROM swiggy_restaurants;")
    db_count = cursor.fetchone()[0]
    print(f"\n✅ Verification: swiggy_restaurants table now contains {db_count} rows in MySQL (client_query_db)!")

    # Show sample 3 rows
    cursor.execute("SELECT id, name, city, rating, cost, cuisine FROM swiggy_restaurants LIMIT 3;")
    rows = cursor.fetchall()
    print("\nSample records from MySQL:")
    for r in rows:
        print(f"  ID {r[0]}: {r[1]} ({r[2]}) - Rating: {r[3]}, Cost: {r[4]}, Cuisine: {r[5]}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    push_to_sql()
