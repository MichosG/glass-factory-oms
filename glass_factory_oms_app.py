
import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            contact TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            supplier_id INTEGER,
            material_received INTEGER,
            received_date TEXT,
            FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
        )
    """)
    conn.commit()
    conn.close()

def get_suppliers():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM suppliers", conn)
    conn.close()
    return df

def add_supplier(name, contact):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO suppliers (name, contact) VALUES (?, ?)", (name, contact))
        conn.commit()
    except:
        pass
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

def link_order_to_supplier(order_id, supplier_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO deliveries (order_id, supplier_id, material_received, received_date) VALUES (?, ?, 0, NULL)", (order_id, supplier_id))
    conn.commit()
    conn.close()

def update_delivery_status(delivery_id, status):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    date = datetime.now().isoformat() if status else None
    cur.execute("UPDATE deliveries SET material_received = ?, received_date = ? WHERE id = ?", (int(status), date, delivery_id))
    conn.commit()
    conn.close()

def fetch_orders():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM orders ORDER BY id DESC", conn)
    conn.close()
    return df

def fetch_supplier_deliveries():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("""
        SELECT d.id as delivery_id, o.order_id, s.name as supplier_name, s.contact, d.material_received, d.received_date
        FROM deliveries d
        JOIN suppliers s ON d.supplier_id = s.id
        JOIN orders o ON d.order_id = o.order_id
        ORDER BY d.id DESC
    """, conn)
    conn.close()
    return df

st.set_page_config(page_title="Glass Factory - Phase 2", layout="wide")
st.title("🏭 Glass Factory OMS — Phase 2: Supplier Tracking")

init_db()

tab1, tab2, tab3 = st.tabs(["➕ New Order", "📋 Orders", "🚚 Supplier Dashboard"])

with tab1:
    st.subheader("➕ Create New Order")
    with st.form("order_form"):
        prefix = st.selectbox("Order Type", options=list(ORDER_PREFIXES.keys()), format_func=lambda x: f"{x} - {ORDER_PREFIXES[x]}")
        customer = st.text_input("Customer Name")
        address = st.text_area("Address")
        phone = st.text_input("Phone Number")
        description = st.text_area("Order Description")
        price = st.number_input("Total Price (€)", min_value=0.0, step=1.0)
        suppliers_df = get_suppliers()
        supplier_names = suppliers_df["name"].tolist()
        selected_supplier = st.selectbox("Assign Supplier", options=supplier_names if supplier_names else ["(No suppliers)"])
        submitted = st.form_submit_button("Submit Order")
        if submitted:
            order_id = generate_order_id(prefix)
            insert_order(order_id, prefix, customer, address, phone, description, price)
            if selected_supplier != "(No suppliers)":
                supplier_id = suppliers_df[suppliers_df["name"] == selected_supplier]["id"].values[0]
                link_order_to_supplier(order_id, supplier_id)
            st.success(f"Order {order_id} created successfully!")

    st.divider()
    st.subheader("➕ Add New Supplier")
    with st.form("add_supplier"):
        supplier_name = st.text_input("Supplier Name")
        contact_info = st.text_input("Contact Info")
        add_btn = st.form_submit_button("Add Supplier")
        if add_btn and supplier_name:
            add_supplier(supplier_name, contact_info)
            st.success(f"Supplier {supplier_name} added.")

with tab2:
    st.subheader("📋 All Orders")
    orders_df = fetch_orders()
    st.dataframe(orders_df)
    csv = orders_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Orders CSV", data=csv, file_name="orders.csv", mime="text/csv")

with tab3:
    st.subheader("🚚 Supplier Deliveries")
    deliveries_df = fetch_supplier_deliveries()
    for _, row in deliveries_df.iterrows():
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        col1.markdown(f"**Order:** {row['order_id']}")
        col2.markdown(f"**Supplier:** {row['supplier_name']} ({row['contact']})")
        col3.markdown(f"**Received:** {'✅' if row['material_received'] else '❌'}")
        if not row['material_received']:
            if col4.button("Mark Received", key=f"rec_{row['delivery_id']}"):
                update_delivery_status(row['delivery_id'], True)
                st.experimental_rerun()
        else:
            col4.markdown(f"📅 {row['received_date']}")
