
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Simulated user roles
roles = {
    "admin": "admin123",
    "sales": "sales123",
    "production": "prod123",
    "manager": "mgr123"
}

st.set_page_config(page_title="Glass Factory OMS", layout="wide")

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

    # Load or create mock data
    if "orders" not in st.session_state:
        st.session_state.orders = pd.DataFrame({
            'Order ID': [1, 2, 3, 4, 5],
            'Customer': ['Alpha Glass', 'Beta Build', 'ClearView Ltd', 'Zenith Glazing', 'Vista Panels'],
            'Product Type': ['Tempered', 'Laminated', 'Tempered', 'Float', 'Laminated'],
            'Dimensions': ['100x200', '120x240', '90x180', '100x100', '150x250'],
            'Quantity': [10, 20, 15, 5, 12],
            'Status': ['Completed', 'In Production', 'New', 'Delivered', 'New'],
            'Deadline': pd.to_datetime(['2025-05-20', '2025-06-05', '2025-06-10', '2025-05-28', '2025-06-15']),
            'Order Date': pd.to_datetime(['2025-05-01', '2025-05-15', '2025-05-25', '2025-05-10', '2025-05-30'])
        })

    if user_role in ["admin", "sales"]:
        st.subheader("➕ Create New Order")
        with st.form("new_order_form"):
            customer = st.text_input("Customer Name")
            product = st.selectbox("Product Type", ["Tempered", "Laminated", "Float"])
            dims = st.text_input("Dimensions (e.g. 100x200)")
            qty = st.number_input("Quantity", min_value=1, value=1)
            deadline = st.date_input("Deadline", value=datetime.today())
            submitted = st.form_submit_button("Add Order")
            if submitted:
                new_order = {
                    "Order ID": len(st.session_state.orders) + 1,
                    "Customer": customer,
                    "Product Type": product,
                    "Dimensions": dims,
                    "Quantity": qty,
                    "Status": "New",
                    "Deadline": pd.to_datetime(deadline),
                    "Order Date": pd.to_datetime(datetime.today())
                }
                st.session_state.orders = pd.concat([st.session_state.orders, pd.DataFrame([new_order])], ignore_index=True)
                st.success("Order added successfully.")

    st.subheader("📋 Order List")
    st.dataframe(st.session_state.orders)

    if user_role in ["admin", "manager"]:
        st.subheader("📊 Analytics Dashboard")
        fig = px.histogram(st.session_state.orders, x="Product Type", title="Orders by Product Type")
        st.plotly_chart(fig, use_container_width=True)

        fig2 = px.line(st.session_state.orders.sort_values("Order Date"), x="Order Date", y="Quantity", title="Quantity Ordered Over Time")
        st.plotly_chart(fig2, use_container_width=True)

# Entry point
user = authenticate_user()
if user:
    main_app(user)
