
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import os

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
        return pd.read_csv(ORDERS_FILE, parse_dates=["Deadline", "Order Date"])
    else:
        return pd.DataFrame(columns=[
            'Order ID', 'Customer', 'Phone', 'Address', 'Product Type', 'Glass Type',
            'Processing', 'Dimensions', 'Quantity', 'Price (€)', 'Status',
            'Deadline', 'Order Date'
        ])

def save_orders(df):
    df.to_csv(ORDERS_FILE, index=False)

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
    st.title("📦 Glass Factory Order Management System")

    if "orders" not in st.session_state:
        st.session_state.orders = load_orders()

    if user_role in ["admin", "sales"]:
        st.subheader("➕ Create New Order")
        with st.form("new_order_form"):
            customer = st.text_input("Customer Name")
            phone = st.text_input("Phone Number")
            address = st.text_area("Address")
            product = st.selectbox("Product Type", ["Tempered", "Laminated", "Float"])
            glass_type = st.selectbox("Glass Thickness", [
                "4mm", "5mm", "6mm", "8mm", "10mm", "12mm",
                "3+3mm laminated", "4+4mm laminated", "5+5mm laminated", "6+6mm laminated"
            ])
            processing = st.multiselect("Processing Required", ["Only Cut", "Ronde", "Holes"])
            dims = st.text_input("Dimensions (e.g. 100x200)")
            qty = st.number_input("Quantity", min_value=1, value=1)
            price = st.number_input("Total Price (€)", min_value=0.0, step=1.0)
            deadline = st.date_input("Deadline", value=datetime.today())
            submitted = st.form_submit_button("Add Order")
            if submitted:
                new_order = {
                    "Order ID": len(st.session_state.orders) + 1,
                    "Customer": customer,
                    "Phone": phone,
                    "Address": address,
                    "Product Type": product,
                    "Glass Type": glass_type,
                    "Processing": ", ".join(processing),
                    "Dimensions": dims,
                    "Quantity": qty,
                    "Price (€)": price,
                    "Status": "New",
                    "Deadline": pd.to_datetime(deadline),
                    "Order Date": pd.to_datetime(datetime.today())
                }
                st.session_state.orders = pd.concat(
                    [st.session_state.orders, pd.DataFrame([new_order])],
                    ignore_index=True
                )
                save_orders(st.session_state.orders)
                st.success("Order added successfully.")

    st.subheader("📋 Order List")
    st.dataframe(st.session_state.orders)

    csv = st.session_state.orders.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download Orders as CSV", data=csv, file_name="orders.csv", mime="text/csv")

    if user_role in ["admin", "manager"]:
        st.subheader("📊 Analytics Dashboard")
        if not st.session_state.orders.empty:
            fig = px.histogram(st.session_state.orders, x="Product Type", title="Orders by Product Type")
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.line(
                st.session_state.orders.sort_values("Order Date"),
                x="Order Date",
                y="Quantity",
                title="Quantity Ordered Over Time"
            )
            st.plotly_chart(fig2, use_container_width=True)

# Entry point
user = authenticate_user()
if user:
    main_app(user)
