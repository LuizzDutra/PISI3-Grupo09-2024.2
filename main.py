import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


st.set_page_config(
    page_title = "PISI3 - Grupo 09",
    layout = "centered",
    menu_items = {
        'About': '''Dashboard das análises de dados do grupo 09 da cadeira de PISI3.'''
    }
)

path = "data"

pedidos = path + "/olist_orders_dataset.csv"
produtos = path + "/olist_products_dataset.csv"
vendedores = path + "/olist_sellers_dataset.csv"
itens = path + "/olist_order_items_dataset.csv"
reviews = path + "/olist_order_reviews_dataset.csv"
geoloc = path + "/olist_geolocation_dataset.csv"
clientes = path + "/olist_customers_dataset.csv"
pagamentos = path + "/olist_order_payments_dataset.csv"
categoria_nome = path + "/product_category_name_translation.csv"

st.header("Os bancos do dataset")
with st.echo():
    df_categorias = pd.read_csv(categoria_nome)
    df_clientes = pd.read_csv(clientes)
    df_geoloc = pd.read_csv(geoloc)
    df_pedidos = pd.read_csv(pedidos)
    df_itens = pd.read_csv(itens)
    df_pagamentos = pd.read_csv(pagamentos)
    df_produtos = pd.read_csv(produtos)
    df_reviews = pd.read_csv(reviews)
    df_vendedores = pd.read_csv(vendedores)

def transformar_dados():
    with st.echo():
        df_pedidos['order_estimated_delivery_date'] = pd.to_datetime(df_pedidos['order_estimated_delivery_date'])
        df_pedidos['order_delivered_customer_date'] = pd.to_datetime(df_pedidos['order_delivered_customer_date'])
        df_pedidos['order_purchase_timestamp'] = pd.to_datetime(df_pedidos['order_purchase_timestamp'])
        df_pedidos['on_time'] = (df_pedidos['order_delivered_customer_date'] <= df_pedidos['order_estimated_delivery_date']).astype(int)

def mostrar_relacao_estados():
    with st.echo():
        clientes_por_estado = df_clientes.groupby('customer_state')['customer_unique_id'].nunique()
        fig1 = px.bar(clientes_por_estado, x=clientes_por_estado.index, y=clientes_por_estado.values,
                    labels={'x': 'Estado', 'y': 'Número de Clientes Únicos'},
                    title='Quantidade de Clientes Únicos por Estado')
        
        vendedores_por_estado = df_vendedores.groupby('seller_state')['seller_id'].nunique()
        fig2 = px.bar(vendedores_por_estado, x=vendedores_por_estado.index, y=vendedores_por_estado.values,
                    labels={'x': 'Estado', 'y': 'Número de Vendedores Únicos'},
                    title='Quantidade de Vendedores Únicos por Estado')
    st.markdown(">Neste código são agrupados, de acordo com os seus estados, os clientes e os vendedores.")

    st.plotly_chart(fig1)
    st.markdown('''>É possível observar uma maior concentração de clientes na região sudeste do Brasil, principalmente no estado de São Paulo.''')

    st.plotly_chart(fig2)
    st.markdown('''
                >Também se observa uma concentração de vendedores no estado de São Paulo e uma menor concentração no sudeste do país.
                >É possível perceber a ausência de vendedores em alguns estados, como Roraima e Tocantins.''')
    


def mostrar_analise_prazos():
    # Group by 'on_time' and count the number of orders
    with st.echo():
        on_time_counts = df_pedidos.groupby('on_time')['order_id'].count().reset_index()
        on_time_counts.rename(columns={'order_id': 'order_count'}, inplace=True)


        # Create the plot
        fig1 = px.bar(on_time_counts, x='on_time', y='order_count',
                    labels={'on_time': 'Entrega no Prazo', 'order_count': 'Número de Pedidos'},
                    title='Número de Pedidos Entregues no Prazo vs. Fora do Prazo')
        fig1.update_xaxes(tickvals=[0, 1], ticktext=['Fora do Prazo', 'No Prazo'])
    st.plotly_chart(fig1)

    with st.echo():
        # Merge the dataframes
        merged_df = pd.merge(df_pedidos, df_clientes, on='customer_id', how='left')

        # Group by customer state and on_time, then count the orders
        state_ontime_counts = merged_df.groupby(['customer_state', 'on_time'])['order_id'].count().reset_index()
        state_ontime_counts.rename(columns={'order_id': 'order_count'}, inplace=True)
        fig2 = px.bar(state_ontime_counts, x='customer_state', y='order_count', color='on_time',
                    labels={'customer_state': 'Estado do Cliente', 'order_count': 'Número de Pedidos', 'on_time': 'Entrega no Prazo'},
                    title='Número de Pedidos Entregues no Prazo vs. Fora do Prazo por Estado',
                    color_continuous_scale=["red", "blue"])
    st.plotly_chart(fig2)


    with st.echo():
        temp_df = pd.merge(df_itens, df_produtos, on='product_id', how='left')
        merged_df = pd.merge(merged_df, temp_df, on='order_id', how='left')

        category_delay_counts = merged_df.groupby(['product_category_name', 'on_time'])['order_id'].count().reset_index()
        category_delay_counts.rename(columns={'order_id': 'order_count'}, inplace=True)
        fig3 = px.bar(category_delay_counts, x='order_count', y="product_category_name", color='on_time',
                    labels={'product_category_name': 'Categoria do Produto', 'order_count': 'Número de Pedidos', 'on_time': 'Entrega no Prazo'},
                    title='Atraso na Entrega por Categoria de Produto',
                    color_continuous_scale=["red", "blue"])
    st.plotly_chart(fig3)



def mostrar_trend_compras():
    with st.echo():
        merged_df = pd.merge(df_itens, df_produtos, on='product_id', how='left')
        merged_df = pd.merge(merged_df, df_pedidos, on='order_id', how='left')

        # 2. Price Category (can be customized):
        price_bins = [0, 50, 100, 200, float('inf')]
        price_labels = ['0-50', '51-100', '101-200', '200+']
        merged_df['price_category'] = pd.cut(merged_df['price'], bins=price_bins, labels=price_labels, right=False)

        #1. Product Category Popularity:
        product_popularity = merged_df.groupby('product_category_name')['order_id'].count().reset_index()
        product_popularity = product_popularity.rename(columns={'order_id': 'order_count'})
        fig1 = px.bar(product_popularity, x='order_count', y='product_category_name', title='Popularidade das categorias de produto')
    st.plotly_chart(fig1)

    


    with st.echo():
        average_price_by_category = merged_df.groupby('product_category_name')['price'].mean().reset_index()
        fig2 = px.bar(average_price_by_category, x='price', y='product_category_name', title='Preço médio por categoria de produto')
    st.plotly_chart(fig2)

    with st.echo():
        merged_df['purchase_month'] = merged_df['order_purchase_timestamp'].dt.month
        monthly_purchases = merged_df.groupby('purchase_month')['order_id'].count().reset_index()
        monthly_purchases = monthly_purchases.rename(columns={'order_id':'order_count'})
        fig3 = px.line(monthly_purchases, x='purchase_month', y='order_count', title='Quantidade de compras por mês')
    st.plotly_chart(fig3)


    with st.echo():
        price_category_purchases = merged_df.groupby('price_category', observed=True)['order_id'].count().reset_index()
        price_category_purchases = price_category_purchases.rename(columns={'order_id':'order_count'})
        fig4 = px.bar(price_category_purchases, x='price_category', y='order_count', title='Valor de compra por categoria')
    st.plotly_chart(fig4)

def analise_avaliacoes():
    with st.echo():
        review_counts = df_reviews.groupby('review_score')['review_score'].count().reset_index(name='count')
        fig1 = px.bar(review_counts, x='review_score', y='count',
                    labels={'review_score': 'Nota da Avaliação', 'count': 'Número de Avaliações'},
                    title='Distribuição das Avaliações dos Clientes')
    st.plotly_chart(fig1)

    with st.echo():
        merged_df = pd.merge(df_pedidos, df_clientes, on='customer_id', how='left')
        merged_df = pd.merge(merged_df, df_reviews, on='order_id', how='left')

        total_orders_per_state = merged_df.groupby('customer_state')['order_id'].count().reset_index()
        total_orders_per_state.rename(columns={'order_id': 'total_orders'}, inplace=True)

        state_review_counts = merged_df.groupby(['customer_state', 'review_score'])['order_id'].count().reset_index()
        state_review_counts.rename(columns={'order_id': 'order_count'}, inplace=True)

        merged_counts = pd.merge(state_review_counts, total_orders_per_state, on='customer_state', how='left')
        merged_counts['percentage'] = (merged_counts['order_count'] / merged_counts['total_orders']) * 100

        fig2 = px.bar(merged_counts, x='customer_state', y='percentage', color='review_score',
                    labels={'customer_state': 'Estado do Cliente', 'percentage': 'Porcentagem de Avaliações', 'review_score': 'Nota da Avaliação'},
                    title='Porcentagem de Notas de Avaliação por Estado',
                    color_continuous_scale=["red", "#00FF00"])
    st.plotly_chart(fig2)

st.header("Transformação de dados")
transformar_dados()
st.header("Concentração de vendedores e clientes nos estados")
mostrar_relacao_estados()
st.header("Análise dos prazos\n")
mostrar_analise_prazos()
st.header("Análise da trend de compras\n")
mostrar_trend_compras()
st.header("Avaliações")
analise_avaliacoes()