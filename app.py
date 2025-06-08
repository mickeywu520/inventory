import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# FastAPI Backend URL
FASTAPI_URL = "http://127.0.0.1:8000"

st.set_page_config(layout="wide")
st.title("進出貨管理系統")

# --- Helper Functions to interact with FastAPI ---
def get_products():
    response = requests.get(f"{FASTAPI_URL}/products/")
    if response.status_code == 200:
        return response.json()
    return []

def create_product(name, description):
    data = {"name": name, "description": description}
    response = requests.post(f"{FASTAPI_URL}/products/", json=data)
    return response.json()

def create_inbound_record(product_id, quantity, supplier):
    data = {"product_id": product_id, "quantity": quantity, "supplier": supplier}
    response = requests.post(f"{FASTAPI_URL}/inbound/", json=data)
    return response.json()

def get_inbound_records():
    response = requests.get(f"{FASTAPI_URL}/inbound/")
    if response.status_code == 200:
        return response.json()
    return []

def create_outbound_record(product_id, quantity, customer):
    data = {"product_id": product_id, "quantity": quantity, "customer": customer}
    response = requests.post(f"{FASTAPI_URL}/outbound/", json=data)
    return response.json()

def get_outbound_records():
    response = requests.get(f"{FASTAPI_URL}/outbound/")
    if response.status_code == 200:
        return response.json()
    return []

# --- Sidebar Navigation ---
st.sidebar.title("導覽")
page = st.sidebar.radio("選擇功能", ["產品管理", "進貨管理", "出貨管理", "查詢報表"])

# --- Page Content ---
if page == "產品管理":
    st.header("產品管理")

    st.subheader("新增產品")
    with st.form("new_product_form"):
        product_name = st.text_input("產品名稱", key="new_product_name")
        product_description = st.text_area("產品描述", key="new_product_description")
        submit_product = st.form_submit_button("新增產品")
        if submit_product:
            if product_name:
                new_product = create_product(product_name, product_description)
                if "id" in new_product:
                    st.success(f"產品 '{new_product['name']}' 新增成功！")
                else:
                    st.error(f"新增產品失敗: {new_product.get('detail', '未知錯誤')}")
            else:
                st.warning("產品名稱不能為空。")

    st.subheader("現有產品庫存")
    products = get_products()
    if products:
        df_products = pd.DataFrame(products)
        st.dataframe(df_products[["id", "name", "description", "current_stock"]])
    else:
        st.info("目前沒有產品。")

elif page == "進貨管理":
    st.header("進貨管理")

    st.subheader("新增進貨記錄")
    products = get_products()
    product_options = {p['name']: p['id'] for p in products}
    
    if not products:
        st.warning("請先在 '產品管理' 頁面新增產品。")
    else:
        with st.form("new_inbound_form"):
            selected_product_name = st.selectbox("選擇產品", list(product_options.keys()), key="inbound_product_select")
            inbound_product_id = product_options.get(selected_product_name)
            inbound_quantity = st.number_input("進貨數量", min_value=1, value=1, step=1, key="inbound_quantity")
            inbound_supplier = st.text_input("供應商", key="inbound_supplier")
            submit_inbound = st.form_submit_button("新增進貨")
            if submit_inbound:
                if inbound_product_id and inbound_quantity:
                    inbound_record = create_inbound_record(inbound_product_id, inbound_quantity, inbound_supplier)
                    if "id" in inbound_record:
                        st.success(f"產品 '{selected_product_name}' 進貨 {inbound_quantity} 單位成功！")
                        st.experimental_rerun() # Rerun to update product stock display
                    else:
                        st.error(f"新增進貨失敗: {inbound_record.get('detail', '未知錯誤')}")
                else:
                    st.warning("請選擇產品並輸入數量。")

    st.subheader("進貨記錄")
    inbound_records = get_inbound_records()
    if inbound_records:
        # Fetch product names for display
        product_id_to_name = {p['id']: p['name'] for p in products}
        for record in inbound_records:
            record['product_name'] = product_id_to_name.get(record['product_id'], '未知產品')
            record['inbound_date'] = datetime.fromisoformat(record['inbound_date']).strftime('%Y-%m-%d %H:%M:%S')
        df_inbound = pd.DataFrame(inbound_records)
        st.dataframe(df_inbound[["id", "product_name", "quantity", "supplier", "inbound_date"]])
    else:
        st.info("目前沒有進貨記錄。")

elif page == "出貨管理":
    st.header("出貨管理")

    st.subheader("新增出貨記錄")
    products = get_products()
    product_options = {p['name']: p['id'] for p in products}

    if not products:
        st.warning("請先在 '產品管理' 頁面新增產品。")
    else:
        with st.form("new_outbound_form"):
            selected_product_name = st.selectbox("選擇產品", list(product_options.keys()), key="outbound_product_select")
            outbound_product_id = product_options.get(selected_product_name)
            outbound_quantity = st.number_input("出貨數量", min_value=1, value=1, step=1, key="outbound_quantity")
            outbound_customer = st.text_input("客戶", key="outbound_customer")
            submit_outbound = st.form_submit_button("新增出貨")
            if submit_outbound:
                if outbound_product_id and outbound_quantity:
                    outbound_record = create_outbound_record(outbound_product_id, outbound_quantity, outbound_customer)
                    if "id" in outbound_record:
                        st.success(f"產品 '{selected_product_name}' 出貨 {outbound_quantity} 單位成功！")
                        st.experimental_rerun() # Rerun to update product stock display
                    else:
                        st.error(f"新增出貨失敗: {outbound_record.get('detail', '未知錯誤')}")
                else:
                    st.warning("請選擇產品並輸入數量。")

    st.subheader("出貨記錄")
    outbound_records = get_outbound_records()
    if outbound_records:
        # Fetch product names for display
        product_id_to_name = {p['id']: p['name'] for p in products}
        for record in outbound_records:
            record['product_name'] = product_id_to_name.get(record['product_id'], '未知產品')
            record['outbound_date'] = datetime.fromisoformat(record['outbound_date']).strftime('%Y-%m-%d %H:%M:%S')
        df_outbound = pd.DataFrame(outbound_records)
        st.dataframe(df_outbound[["id", "product_name", "quantity", "customer", "outbound_date"]])
    else:
        st.info("目前沒有出貨記錄。")

elif page == "查詢報表":
    st.header("查詢報表")

    st.subheader("所有產品庫存")
    products = get_products()
    if products:
        df_products = pd.DataFrame(products)
        st.dataframe(df_products[["id", "name", "description", "current_stock"]])
    else:
        st.info("目前沒有產品。")

    st.subheader("所有進貨記錄")
    inbound_records = get_inbound_records()
    if inbound_records:
        product_id_to_name = {p['id']: p['name'] for p in products}
        for record in inbound_records:
            record['product_name'] = product_id_to_name.get(record['product_id'], '未知產品')
            record['inbound_date'] = datetime.fromisoformat(record['inbound_date']).strftime('%Y-%m-%d %H:%M:%S')
        df_inbound = pd.DataFrame(inbound_records)
        st.dataframe(df_inbound[["id", "product_name", "quantity", "supplier", "inbound_date"]])
    else:
        st.info("目前沒有進貨記錄。")

    st.subheader("所有出貨記錄")
    outbound_records = get_outbound_records()
    if outbound_records:
        product_id_to_name = {p['id']: p['name'] for p in products}
        for record in outbound_records:
            record['product_name'] = product_id_to_name.get(record['product_id'], '未知產品')
            record['outbound_date'] = datetime.fromisoformat(record['outbound_date']).strftime('%Y-%m-%d %H:%M:%S')
        df_outbound = pd.DataFrame(outbound_records)
        st.dataframe(df_outbound[["id", "product_name", "quantity", "customer", "outbound_date"]])
    else:
        st.info("目前沒有出貨記錄。")
