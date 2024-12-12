import streamlit as st



st.set_page_config(
    page_title = "PISI3 - Grupo 09",
    layout = "centered",
    menu_items = {
        'About': '''Dashboard das análises de dados do grupo 09 da cadeira de PISI3.'''
    }
)

st.markdown('''
            Dataset utilizado: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/data)
            ''')
st.header("Os bancos do dataset")
st.code("""
    df_categorias = pd.read_parquet(categoria_nome)
    df_clientes = pd.read_parquet(clientes)
    df_geoloc = pd.read_parquet(geoloc)
    df_pedidos = pd.read_parquet(pedidos)
    df_itens = pd.read_parquet(itens)
    df_pagamentos = pd.read_parquet(pagamentos)
    df_produtos = pd.read_parquet(produtos)
    df_reviews = pd.read_parquet(reviews)
    df_vendedores = pd.read_parquet(vendedores)
        """)

st.header("Transformações")
st.code("""
df_pedidos['order_estimated_delivery_date'] = pd.to_datetime(df_pedidos['order_estimated_delivery_date'])
df_pedidos['order_delivered_customer_date'] = pd.to_datetime(df_pedidos['order_delivered_customer_date'])
df_pedidos['order_purchase_timestamp'] = pd.to_datetime(df_pedidos['order_purchase_timestamp'])
df_pedidos['on_time'] = (df_pedidos['order_delivered_customer_date'] <= df_pedidos['order_estimated_delivery_date']).astype(int)
        """)