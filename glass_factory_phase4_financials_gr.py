
import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

DB_FILE = "orders.db"

ORDER_PREFIXES = {
    "M": "Μεταφορά",
    "T": "Τοποθέτηση",
    "Π": "Παραλαβή",
    "Κ": "Κατάστημα",
    "A": "Συνεργάτης"
}

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("ALTER TABLE orders ADD COLUMN advance REAL") if "advance" not in [col[1] for col in cur.execute("PRAGMA table_info(orders)")] else None
    cur.execute("ALTER TABLE orders ADD COLUMN balance REAL") if "balance" not in [col[1] for col in cur.execute("PRAGMA table_info(orders)")] else None
    conn.commit()
    conn.close()

def get_suppliers():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM suppliers", conn)
    conn.close()
    return df

def fetch_orders():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM orders ORDER BY id DESC", conn)
    conn.close()
    return df

st.set_page_config(page_title="Φάση 4 - Οικονομικά", layout="wide")
st.title("💶 Εργοστάσιο Υαλοπινάκων — Φάση 4: Οικονομικά")

init_db()

st.subheader("📋 Παραγγελίες με Οικονομικά Στοιχεία")
orders_df = fetch_orders()

if not orders_df.empty:
    orders_df["advance"] = orders_df["advance"].fillna(0.0)
    orders_df["balance"] = orders_df["balance"].fillna(orders_df["price"] - orders_df["advance"])
    st.dataframe(orders_df[["order_id", "customer", "price", "advance", "balance"]])

    csv = orders_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Εξαγωγή CSV", data=csv, file_name="paraggelies_oikonomika.csv", mime="text/csv")

    total_balance = orders_df["balance"].sum()
    st.markdown(f"### 💰 Συνολικό Υπόλοιπο: **{total_balance:.2f} €**")
else:
    st.info("Δεν υπάρχουν παραγγελίες.")
