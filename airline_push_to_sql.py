"""
NEW FILE: airline_push_to_sql.py
Pushes the 23,616-row Airline Complaints dataset into MySQL database (client_query_db).
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

CSV_PATH = r"c:\Users\raghu\OneDrive\New folder\Guvi Auto code\airline-complaint-ai\data\raw\Airline_review.csv"

def push_to_sql():
    print(f"Reading dataset from: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(f"Total rows to push: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Create table if not exists
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS airline_reviews (
        id INT AUTO_INCREMENT PRIMARY KEY,
        airline_name VARCHAR(255),
        overall_rating FLOAT,
        review_title TEXT,
        review_date VARCHAR(100),
        verified VARCHAR(50),
        review LONGTEXT,
        aircraft VARCHAR(100),
        type_of_traveller VARCHAR(100),
        seat_type VARCHAR(100),
        route VARCHAR(255),
        date_flown VARCHAR(100),
        seat_comfort FLOAT,
        cabin_staff_service FLOAT,
        food_beverages FLOAT,
        ground_service FLOAT,
        inflight_entertainment FLOAT,
        wifi_connectivity FLOAT,
        value_for_money FLOAT,
        recommended VARCHAR(50)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """
    cursor.execute(create_table_sql)

    # Truncate existing data to start clean
    cursor.execute("TRUNCATE TABLE airline_reviews;")
    conn.commit()

    insert_sql = """
    INSERT INTO airline_reviews 
    (airline_name, overall_rating, review_title, review_date, verified, review,
     aircraft, type_of_traveller, seat_type, route, date_flown, seat_comfort,
     cabin_staff_service, food_beverages, ground_service, inflight_entertainment,
     wifi_connectivity, value_for_money, recommended)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    def parse_float(val):
        try:
            if pd.notnull(val):
                return float(val)
        except Exception:
            pass
        return None

    def parse_str(val, max_len=None):
        if pd.notnull(val):
            s = str(val).strip()
            return s[:max_len] if max_len else s
        return None

    batch = []
    batch_size = 1000
    inserted_count = 0

    for _, row in df.iterrows():
        batch.append((
            parse_str(row.get("Airline Name"), 255),
            parse_float(row.get("Overall_Rating")),
            parse_str(row.get("Review_Title")),
            parse_str(row.get("Review Date"), 100),
            parse_str(row.get("Verified"), 50),
            parse_str(row.get("Review")),
            parse_str(row.get("Aircraft"), 100),
            parse_str(row.get("Type Of Traveller"), 100),
            parse_str(row.get("Seat Type"), 100),
            parse_str(row.get("Route"), 255),
            parse_str(row.get("Date Flown"), 100),
            parse_float(row.get("Seat Comfort")),
            parse_float(row.get("Cabin Staff Service")),
            parse_float(row.get("Food & Beverages")),
            parse_float(row.get("Ground Service")),
            parse_float(row.get("Inflight Entertainment")),
            parse_float(row.get("Wifi & Connectivity")),
            parse_float(row.get("Value For Money")),
            parse_str(row.get("Recommended"), 50),
        ))

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
    cursor.execute("SELECT COUNT(*) FROM airline_reviews;")
    db_count = cursor.fetchone()[0]
    print(f"\n✅ Verification: airline_reviews table now contains {db_count} rows in MySQL (client_query_db)!")

    # Show sample 3 rows
    cursor.execute("SELECT id, airline_name, overall_rating, recommended, route FROM airline_reviews LIMIT 3;")
    rows = cursor.fetchall()
    print("\nSample records from MySQL:")
    for r in rows:
        print(f"  ID {r[0]}: {r[1]} - Rating: {r[2]}, Recommended: {r[3]}, Route: {r[4]}")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    push_to_sql()
