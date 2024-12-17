import pandas as pd
path = "data/"
pedidos = path + "olist_orders_dataset.parquet"
produtos = path + "olist_products_dataset.parquet"
vendedores = path + "olist_sellers_dataset.parquet"
itens = path + "olist_order_items_dataset.parquet"
reviews = path + "olist_order_reviews_dataset.parquet"
geoloc = path + "olist_geolocation_dataset.parquet"
clientes = path + "olist_customers_dataset.parquet"
pagamentos = path + "olist_order_payments_dataset.parquet"
categoria_nome = path + "product_category_name_translation.parquet"

df_categorias = pd.read_parquet(categoria_nome)
df_clientes = pd.read_parquet(clientes)
df_geoloc = pd.read_parquet(geoloc)
df_pedidos = pd.read_parquet(pedidos)
df_itens = pd.read_parquet(itens)
df_pagamentos = pd.read_parquet(pagamentos)
df_produtos = pd.read_parquet(produtos)
df_reviews = pd.read_parquet(reviews)
df_vendedores = pd.read_parquet(vendedores)

df_pedidos['order_estimated_delivery_date'] = pd.to_datetime(df_pedidos['order_estimated_delivery_date'])
df_pedidos['order_delivered_customer_date'] = pd.to_datetime(df_pedidos['order_delivered_customer_date'])
df_pedidos['order_purchase_timestamp'] = pd.to_datetime(df_pedidos['order_purchase_timestamp'])
df_pedidos['on_time'] = (df_pedidos['order_delivered_customer_date'] <= df_pedidos['order_estimated_delivery_date']).astype(int)

df = df_pedidos.merge(df_itens, on='order_id', how='inner')
df = df.merge(df_pagamentos, on='order_id', how='inner', validate='m:m')
df = df.merge(df_reviews, on='order_id', how='inner')
df = df.merge(df_produtos, on='product_id', how='inner')
df = df.merge(df_clientes, on='customer_id', how='inner')
df = df.merge(df_vendedores, on='seller_id', how='inner')