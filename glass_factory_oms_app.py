
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import os
from io import BytesIO

roles = {
    "admin": "admin123",
    "sales": "sales123",
    "production": "prod123",
    "manager": "mgr123"
}

st.set_page_config(page_title="Glass Factory OMS", layout="wide")
ORDERS_FILE = "orders_data.csv"

def load_orders():
    if os.path.exists(ORDERS_FILE):
        return pd.read_csv(ORDERS_FILE, parse_dates=["Order Date"])
    else:
        return pd.DataFrame(columns=[
            'Project Number', 'Order Date', 'Customer Name', 'Address', 'Phone',
            'Order Description', 'Ready', 'Price (€)', 'Remarks / Delivery Schedule',
            'Estimated Delivery', 'Deposit (€)', 'Suppliers', 'Entered By', 'Scan File Name'
        ])

def save_orders(df):
    df.to_csv(ORDERS_FILE, index=False)

def export_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Orders")
    return output.getvalue()

def authenticate_user():
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if username in roles and roles[username] == password:
        return username
    else:
        if username and password:
            st.sidebar.error("Invalid credentials")
        return None

def main_app(user_role):
    st.title("📦 Glass Factory Order Entry")

    if "orders" not in st.session_state:
        st.session_state.orders = load_orders()

    if user_role in ["admin", "sales"]:
        st.subheader("📝 Create New Order")
        with st.form("order_form"):
            project_number = st.text_input("ΑΡ. ΕΡΓΟΥ (Project Number)")
            customer = st.text_input("ΟΝΟΜΑ (Customer Name)")
            address = st.text_area("ΠΕΡΙΟΧΗ / ΔΙΕΥΘΥΝΣΗ (Address)")
            phone = st.text_input("ΤΗΛΕΦΩΝΑ (Phone Number)")
            order_desc = st.text_area("ΠΑΡΑΓΓΕΛΙΑ (Order Description)")
            ready = st.checkbox("ΕΤΟΙΜΟ (Ready?)")
            price = st.number_input("ΠΟΣΟ (Total Price €)", min_value=0.0, step=1.0)
            remarks = st.text_area("ΕΚΚΡΕΜΟΤΗΤΕΣ / ΗΜΕΡ ΤΟΠ / ΗΜΕΡ ΠΑΡ (Remarks)")
            estimated_delivery = st.text_input("ΕΝΔΕΙΚΤΙΚΟΣ ΧΡΟΝΟΣ ΠΑΡΑΔΟΣΗΣ")
            deposit = st.number_input("ΠΡΟΚΑΤΑΒΟΛΗ (Deposit €)", min_value=0.0, step=1.0)
            suppliers = st.text_input("ΠΡΟΜΗΘΕΥΤΕΣ (Suppliers)")
            uploaded_file = st.file_uploader("SCAN (Upload File)", type=["pdf", "jpg", "jpeg", "png"])

            submitted = st.form_submit_button("Add Order")
            if submitted:
                scan_filename = uploaded_file.name if uploaded_file else ""
                new_order = {
                    "Project Number": project_number,
                    "Order Date": datetime.today(),
                    "Customer Name": customer,
                    "Address": address,
                    "Phone": phone,
                    "Order Description": order_desc,
                    "Ready": "Yes" if ready else "No",
                    "Price (€)": price,
                    "Remarks / Delivery Schedule": remarks,
                    "Estimated Delivery": estimated_delivery,
                    "Deposit (€)": deposit,
                    "Suppliers": suppliers,
                    "Entered By": user_role,
                    "Scan File Name": scan_filename
                }
                st.session_state.orders = pd.concat(
                    [st.session_state.orders, pd.DataFrame([new_order])],
                    ignore_index=True
                )
                save_orders(st.session_state.orders)
                st.success("Order saved.")

    st.subheader("📋 Orders")
    st.dataframe(st.session_state.orders)

    csv = st.session_state.orders.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download CSV", data=csv, file_name="orders.csv", mime="text/csv")

    xlsx = export_excel(st.session_state.orders)
    st.download_button("📊 Download Excel", data=xlsx, file_name="orders.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    if user_role in ["admin", "manager"]:
        st.subheader("📈 Summary Analytics")
        if not st.session_state.orders.empty and "Customer Name" in st.session_state.orders.columns:
            fig = px.histogram(st.session_state.orders, x="Customer Name", title="Orders per Customer")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available yet to display charts.")

# Start the app
user = authenticate_user()
if user:
    main_app(user)
