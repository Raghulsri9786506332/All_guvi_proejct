import os
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine

# Database credentials - Update these if they differ
DB_HOST = "127.0.0.1"
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = "client_query_db"

def load_data():
    csv_file = "synthetic_client_queries (1).csv"
    
    print(f"Reading {csv_file}...")
    df = pd.read_csv(csv_file)
    
    # Map CSV columns to match our database schema
    df = df.rename(columns={
        "client_email": "mail_id",
        "client_mobile": "mobile_number",
        "date_raised": "query_created_time",
        "date_closed": "query_closed_time"
    })
    
    # Drop query_id as it will be auto-incremented in the DB
    if "query_id" in df.columns:
        df = df.drop(columns=["query_id"])
        
    print("Connecting to MySQL...")
    try:
        # Create SQLAlchemy engine
        engine = create_engine(f"mysql+mysqlconnector://root:root@127.0.0.1/client_query_db")
        
        # Write records to the 'queries' table, appending to existing
        # If the table doesn't exist, it will create it
        print("Inserting records into the database...")
        df.to_sql(name="queries", con=engine, if_exists="append", index=False)
        print("Data loaded successfully!")
    except Exception as e:
        print(f"Error connecting or inserting into database: {e}")
        print("\nNote: Set MYSQL_USER and MYSQL_PASSWORD in your environment.")

if __name__ == "__main__":
    load_data()
