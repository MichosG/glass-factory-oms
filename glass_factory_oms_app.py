
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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT,
            product_type TEXT,
            details TEXT
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

def insert_product(order_id, product_type, details):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("INSERT INTO products (order_id, product_type, details) VALUES (?, ?, ?)", (order_id, product_type, details))
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

st.set_page_config(page_title="Εργοστάσιο Υαλοπινάκων - Φάση 3", layout="wide")
st.title("🏭 Εργοστάσιο Υαλοπινάκων — Φάση 3: Προϊόντα")

init_db()

tab1, tab2, tab3 = st.tabs(["➕ Νέα Παραγγελία", "📋 Παραγγελίες", "🚚 Παραδόσεις Προμηθευτών"])

with tab1:
    st.subheader("➕ Καταχώρηση Νέας Παραγγελίας")
    with st.form("order_form"):
        prefix = st.selectbox("Τύπος Παραγγελίας", options=list(ORDER_PREFIXES.keys()), format_func=lambda x: f"{x} - {ORDER_PREFIXES[x]}")
        customer = st.text_input("Ονοματεπώνυμο Πελάτη")
        address = st.text_area("Διεύθυνση")
        phone = st.text_input("Τηλέφωνο")
        description = st.text_area("Περιγραφή")
        price = st.number_input("Συνολικό Ποσό (€)", min_value=0.0, step=1.0)

        suppliers_df = get_suppliers()
        supplier_names = suppliers_df["name"].tolist()
        selected_supplier = st.selectbox("Επιλογή Προμηθευτή", options=supplier_names if supplier_names else ["(Δεν υπάρχουν προμηθευτές)"])

        st.markdown("### 🛒 Προϊόντα")
        product_entries = []
        for i in range(3):
            st.markdown(f"#### Προϊόν {i+1}")
            ptype = st.selectbox(f"Τύπος Προϊόντος {i+1}", ["", "Γυαλί", "Κούφωμα", "Πόρτα Laminated"], key=f"ptype_{i}")
            details = ""
            if ptype == "Γυαλί":
                gtype = st.selectbox("Τύπος Γυαλιού", ["Διάφανο", "Ματ"], key=f"gtype_{i}")
                thickness = st.selectbox("Πάχος (mm)", [4, 6, 8, 10, 12], key=f"thick_{i}")
                width = st.number_input("Πλάτος (cm)", key=f"gwidth_{i}")
                height = st.number_input("Ύψος (cm)", key=f"gheight_{i}")
                quantity = st.number_input("Ποσότητα", min_value=1, step=1, key=f"gqty_{i}")
                details = f"Τύπος: {gtype}, Πάχος: {thickness}mm, {width}x{height}cm, Τεμ: {quantity}"
            elif ptype == "Κούφωμα":
                material = st.selectbox("Υλικό", ["Αλουμίνιο", "PVC"], key=f"mat_{i}")
                width = st.number_input("Πλάτος (cm)", key=f"wwidth_{i}")
                height = st.number_input("Ύψος (cm)", key=f"wheight_{i}")
                color = st.text_input("Χρώμα", key=f"wcolor_{i}")
                energy = st.checkbox("Ενεργειακό Τζάμι", key=f"wenergy_{i}")
                model = st.text_input("Μοντέλο Elvial", key=f"wmodel_{i}")
                details = f"{material}, {width}x{height}cm, Χρώμα: {color}, Ενεργειακό: {energy}, Μοντέλο: {model}"
            elif ptype == "Πόρτα Laminated":
                width = st.number_input("Πλάτος (cm)", key=f"dwidth_{i}")
                height = st.number_input("Ύψος (cm)", key=f"dheight_{i}")
                open_dir = st.selectbox("Κατεύθυνση Ανοίγματος", ["Αριστερά", "Δεξιά", "Συρόμενη"], key=f"dir_{i}")
                color = st.text_input("Χρώμα", key=f"dcolor_{i}")
                frame = st.number_input("Πλάτος Κάσας (cm)", key=f"dframe_{i}")
                details = f"{width}x{height}cm, {open_dir}, Χρώμα: {color}, Κάσα: {frame}cm"
            product_entries.append((ptype, details))

        submitted = st.form_submit_button("Καταχώρηση")
        if submitted:
            order_id = generate_order_id(prefix)
            insert_order(order_id, prefix, customer, address, phone, description, price)
            if selected_supplier != "(Δεν υπάρχουν προμηθευτές)":
                supplier_id = suppliers_df[suppliers_df["name"] == selected_supplier]["id"].values[0]
                link_order_to_supplier(order_id, supplier_id)
            for ptype, det in product_entries:
                if ptype and det:
                    insert_product(order_id, ptype, det)
            st.success(f"Η παραγγελία {order_id} καταχωρήθηκε επιτυχώς!")

with tab2:
    st.subheader("📋 Όλες οι Παραγγελίες")
    orders_df = fetch_orders()
    st.dataframe(orders_df)
    csv = orders_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Λήψη CSV", data=csv, file_name="paraggelies.csv", mime="text/csv")

with tab3:
    st.subheader("🚚 Κατάσταση Προμηθευτών")
    deliveries_df = fetch_supplier_deliveries()
    for _, row in deliveries_df.iterrows():
        col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
        col1.markdown(f"**Παραγγελία:** {row['order_id']}")
        col2.markdown(f"**Προμηθευτής:** {row['supplier_name']} ({row['contact']})")
        col3.markdown(f"**Παραλήφθηκε:** {'✅' if row['material_received'] else '❌'}")
        if not row['material_received']:
            if col4.button("Επιβεβαίωση", key=f"rec_{row['delivery_id']}"):
                update_delivery_status(row['delivery_id'], True)
                st.experimental_rerun()
        else:
            col4.markdown(f"📅 {row['received_date']}")
