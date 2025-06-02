
import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="Glass Factory OMS - Phase 5", layout="wide")

DB_FILE = "orders.db"

# Initialize DB
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prefix TEXT,
            customer TEXT,
            phone TEXT,
            address TEXT,
            category TEXT,
            product_desc TEXT,
            dimensions TEXT,
            quantity INTEGER,
            price REAL,
            supplier TEXT,
            status TEXT,
            delivery_date TEXT,
            deposit REAL
        )
    """)
    conn.commit()
    conn.close()

def add_order(data):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO orders (
            prefix, customer, phone, address, category, product_desc,
            dimensions, quantity, price, supplier, status, delivery_date, deposit
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

def view_orders():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM orders", conn)
    conn.close()
    return df

init_db()

st.title("📋 Εργοστάσιο Υαλοπινάκων – Φάση 5")

st.subheader("➕ Δημιουργία Νέας Παραγγελίας")
with st.form("order_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        prefix = st.selectbox("Τύπος Παραγγελίας", ["M", "T", "Π", "K", "A"])
        customer = st.text_input("Όνομα Πελάτη")
        phone = st.text_input("Τηλέφωνο")
        address = st.text_input("Διεύθυνση")
        category = st.selectbox("Κατηγορία Προϊόντος", ["Glass", "Aluminium", "PVC", "Door"])
        supplier = st.text_input("Προμηθευτής")
    with col2:
        product_desc = st.text_area("Περιγραφή Προϊόντος")
        dimensions = st.text_input("Διαστάσεις")
        quantity = st.number_input("Ποσότητα", min_value=1)
        price = st.number_input("Τιμή (€)", min_value=0.0)
        status = st.selectbox("Κατάσταση", ["Νέα", "Σε εξέλιξη", "Ολοκληρωμένη"])
        delivery_date = st.date_input("Ημερομηνία Παράδοσης")
        deposit = st.number_input("Προκαταβολή (€)", min_value=0.0)

    submitted = st.form_submit_button("Καταχώρηση")
    if submitted:
        add_order((
            prefix, customer, phone, address, category, product_desc,
            dimensions, quantity, price, supplier, status,
            str(delivery_date), deposit
        ))
        st.success("✅ Παραγγελία καταχωρήθηκε.")

st.subheader("📄 Προβολή Παραγγελιών")
orders_df = view_orders()
st.dataframe(orders_df)
