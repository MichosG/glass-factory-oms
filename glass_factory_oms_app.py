
import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import os

DB_FILE = "orders.db"

ORDER_PREFIXES = {
    "M": "Transportation",
    "T": "Installation",
    "Π": "Pick-up",
    "Κ": "Retail",
    "A": "Special Client"
}

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            prefix TEXT,
            customer TEXT,
            address TEXT,
            phone TEXT,
            description TEXT,
            price REAL,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def generate_order_id(prefix):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM orders WHERE prefix = ?", (prefix,))
    count = cur.fetchone()[0] + 1
    conn.close()
    return f"{prefix}-{str(count).zfill(4)}"

def insert_order(order_id, prefix, customer, address, phone, description, price):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orders (order_id, prefix, customer, address, phone, description, price, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (order_id, prefix, customer, address, phone, description, price, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def fetch_orders():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM orders ORDER BY id DESC", conn)
    conn.close()
    return df

st.set_page_config(page_title="Glass Factory - Phase 1", layout="wide")
st.title("📦 Glass Factory OMS — Phase 1")

init_db()

st.subheader("➕ Create New Order")
with st.form("order_form"):
    prefix = st.selectbox("Order Type", options=list(ORDER_PREFIXES.keys()), format_func=lambda x: f"{x} - {ORDER_PREFIXES[x]}")
    customer = st.text_input("Customer Name")
    address = st.text_area("Address")
    phone = st.text_input("Phone Number")
    description = st.text_area("Order Description")
    price = st.number_input("Total Price (€)", min_value=0.0, step=1.0)

    submitted = st.form_submit_button("Submit Order")
    if submitted:
        order_id = generate_order_id(prefix)
        insert_order(order_id, prefix, customer, address, phone, description, price)
        st.success(f"Order {order_id} created successfully!")

st.subheader("📋 All Orders")
orders_df = fetch_orders()
st.dataframe(orders_df)

csv = orders_df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Orders CSV", data=csv, file_name="orders_phase1.csv", mime="text/csv")
