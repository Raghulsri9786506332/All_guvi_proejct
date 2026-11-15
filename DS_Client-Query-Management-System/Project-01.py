import streamlit as st
import mysql.connector
from sqlalchemy import create_engine
import hashlib
import os
import pandas as pd
from datetime import datetime
from urllib.parse import quote_plus

# -----------------------------
# Database Connection
# -----------------------------
DB_HOST = "127.0.0.1"
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
DB_NAME = "client_query_db"

def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def get_engine():
    pwd = quote_plus(DB_PASSWORD)
    return create_engine(f"mysql+mysqlconnector://{DB_USER}:{pwd}@{DB_HOST}/{DB_NAME}")


# -----------------------------
# Password Hashing
# -----------------------------
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# -----------------------------
# Initialize Tables
# -----------------------------
def init_db():
    conn = get_connection()
    cur = conn.cursor()

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
    conn.close()


# -----------------------------
# Seed Demo Users
# -----------------------------
def seed_demo_users():
    conn = get_connection()
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
        except mysql.connector.IntegrityError:
            pass

    conn.commit()
    conn.close()


# -----------------------------
# Register User
# -----------------------------
def register_user(username, password, role):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, hashed_password, role) VALUES (%s, %s, %s)",
            (username, hash_password(password), role)
        )
        conn.commit()
        return True, "User registered successfully."
    except mysql.connector.IntegrityError:
        return False, "Username already exists for this role."
    finally:
        conn.close()


# -----------------------------
# Authenticate User
# -----------------------------
def authenticate_user(username, password, role):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT username, role
        FROM users
        WHERE username = %s AND hashed_password = %s AND role = %s
    """, (username, hash_password(password), role))
    result = cur.fetchone()
    conn.close()

    if result:
        return True
    return False


# -----------------------------
# Submit Query
# -----------------------------
def submit_query(mail_id, mobile_number, query_heading, query_description):
    conn = get_connection()
    cur = conn.cursor()

    created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        INSERT INTO queries (
            mail_id,
            mobile_number,
            query_heading,
            query_description,
            status,
            query_created_time,
            query_closed_time
        )
        VALUES (%s, %s, %s, %s, 'Open', %s, NULL)
    """, (mail_id, mobile_number, query_heading, query_description, created_time))

    conn.commit()
    conn.close()


# -----------------------------
# Fetch Queries
# -----------------------------
def fetch_queries(status_filter=None, search_text=None, mail_id=None):
    query = "SELECT * FROM queries WHERE 1=1"
    params = []

    if status_filter and status_filter != "All":
        query += " AND status = %s"
        params.append(status_filter)

    if search_text:
        query += " AND (query_heading LIKE %s OR query_description LIKE %s)"
        like_text = f"%{search_text}%"
        params.extend([like_text, like_text])

    if mail_id:
        query += " AND mail_id = %s"
        params.append(mail_id)

    query += " ORDER BY query_created_time DESC"

    engine = get_engine()
    df = pd.read_sql_query(query, engine, params=tuple(params))
    return df


# -----------------------------
# Close Query
# -----------------------------
def close_query(query_id):
    conn = get_connection()
    cur = conn.cursor()

    closed_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        UPDATE queries
        SET status = 'Closed',
            query_closed_time = %s
        WHERE query_id = %s AND status = 'Open'
    """, (closed_time, query_id))

    conn.commit()
    conn.close()


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Client Query Management System", layout="wide")

init_db()
seed_demo_users()

st.title("Client Query Management System")

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# -----------------------------
# Login / Register Screen
# -----------------------------
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")

        with st.form("login_form"):
            username = st.text_input("Mail ID / Username")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["Client", "Support"])
            login_btn = st.form_submit_button("Login")

        if login_btn:
            if authenticate_user(username, password, role):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.role = role
                st.success(f"Login successful as {role}")
                st.rerun()
            else:
                st.error("Invalid username, password, or role.")

    with tab2:
        st.subheader("Register")

        with st.form("register_form"):
            new_username = st.text_input("Mail ID / Username")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["Client", "Support"])
            register_btn = st.form_submit_button("Register")

        if register_btn:
            success, message = register_user(new_username, new_password, new_role)
            if success:
                st.success(message)
            else:
                st.error(message)

    st.info("Demo users: client1@gmail.com / client123 and support1 / support123")


# -----------------------------
# After Login
# -----------------------------
else:
    st.sidebar.success(f"Logged in as: {st.session_state.username} ({st.session_state.role})")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

    # -------------------------
    # Client Page
    # -------------------------
    if st.session_state.role == "Client":
        st.header("Client Query Page")

        with st.form("query_form"):
            mail_id = st.text_input(
                "Email ID",
                value=st.session_state.username,
                help="Use the same email/username you used to login."
            )
            mobile_number = st.text_input("Mobile Number")
            query_heading = st.text_input("Query Heading")
            query_description = st.text_area("Query Description")
            submit_btn = st.form_submit_button("Submit Query")

        if submit_btn:
            if mail_id and mobile_number and query_heading and query_description:
                submit_query(mail_id, mobile_number, query_heading, query_description)
                st.success("Query submitted successfully.")
                st.rerun()
            else:
                st.error("Please fill all fields.")

        st.subheader("My Submitted Queries")
        my_queries = fetch_queries(mail_id=st.session_state.username)
        st.dataframe(my_queries, use_container_width=True)

    # -------------------------
    # Support Dashboard
    # -------------------------
    elif st.session_state.role == "Support":
        st.header("Support Dashboard")

        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Open", "Closed"])
        with col2:
            search_text = st.text_input("Search by Heading / Description")

        df = fetch_queries(status_filter=status_filter, search_text=search_text)

        st.subheader("All Queries")
        st.dataframe(df, use_container_width=True)

        open_df = df[df["status"] == "Open"] if not df.empty else pd.DataFrame()

        st.subheader("Close Open Query")
        if not open_df.empty:
            selected_query_id = st.selectbox("Select Query ID to Close", open_df["query_id"].tolist())

            if st.button("Close Selected Query"):
                close_query(selected_query_id)
                st.success(f"Query {selected_query_id} closed successfully.")
                st.rerun()
        else:
            st.info("No open queries available to close.")