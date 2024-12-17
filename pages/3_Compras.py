import streamlit as st
import pandas as pd
from arquivos import df_produtos, df_itens, df_pedidos
import plotly.express as px

st.header("Análise das informações de compras\n")

@st.cache_data
def mostrar_trend_compras():
    merged_df = pd.merge(df_itens, df_produtos, on='product_id', how='left')
    merged_df = pd.merge(merged_df, df_pedidos, on='order_id', how='left')

    product_popularity = merged_df.groupby('product_category_name')['order_id'].count().reset_index()
    product_popularity = product_popularity.rename(columns={'order_id': 'order_count'})
    fig1 = px.bar(product_popularity, x='order_count', y='product_category_name', title='Popularidade das categorias de produto')

    fig1.update_layout(xaxis_title='Quantidade de Pedidos',yaxis_title='Categoria de Produto')

    st.plotly_chart(fig1)
    st.markdown('''
                >Com esse gráfico se obtem como categorias de produto mais compradas sendo:
                
                >cama_mesa_banho, beleza_saude e esporte_lazer.
                ''')
    


    average_price_by_category = merged_df.groupby('product_category_name')['price'].mean().reset_index()
    fig2 = px.bar(average_price_by_category, x='price', y='product_category_name', title='Preço médio por categoria de produto')

    fig2.update_layout(xaxis_title='Preço', yaxis_title='Categoria de Produto' )
    st.plotly_chart(fig2)
    st.markdown('''
                >Com esse gráfico é possível observar que a categoria com valor de compra mais elevado é a de computadores(pcs).
                
                >Mas é necessário se atentar que é uma das categorias menos compradas, com 203 compras no dataset.
                ''')

    #merged_df['purchase_month'] = merged_df['order_purchase_timestamp'].dt.to_period('M')
    monthly_purchases = merged_df.groupby(merged_df['order_purchase_timestamp'].dt.to_period('M'))['order_id'].count().reset_index()
    monthly_purchases = monthly_purchases.rename(columns={'order_id':'order_count'})
    monthly_purchases['order_purchase_timestamp'] = monthly_purchases['order_purchase_timestamp'].dt.to_timestamp()
    fig3 = px.line(monthly_purchases, x='order_purchase_timestamp', y='order_count', title='Quantidade de compras por mês')

    fig3.update_layout(xaxis_title='Mês da Compra',yaxis_title='Quantidade de Pedidos')

    st.plotly_chart(fig3)
    st.markdown('''
                >É possível observar que entre os mêses 3 e 8 se tem maiores quantidades de pedidos no dataset.
                ''')

    price_bins = [0, 50, 100, 200, float('inf')]
    price_labels = ['0-50', '51-100', '101-200', '200+']
    merged_df['price_category'] = pd.cut(merged_df['price'], bins=price_bins, labels=price_labels, right=False)
    price_category_purchases = merged_df.groupby('price_category', observed=True)['order_id'].count().reset_index()
    price_category_purchases = price_category_purchases.rename(columns={'order_id':'order_count'})
    fig4 = px.bar(price_category_purchases, x='price_category', y='order_count', title='Valor de compra por categoria')

    fig4.update_layout(xaxis_title='Categoria de Preço',yaxis_title='Quantidade de Pedidos')

    st.plotly_chart(fig4)
    st.markdown('''
                No gráfico é possível observar uma relação inversamente proporcional esperada entre valor de compra e número de pedidos.
                ''')

mostrar_trend_compras()