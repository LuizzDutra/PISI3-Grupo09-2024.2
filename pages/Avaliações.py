import streamlit as st
import pandas as pd
from arquivos import df_reviews, df_pedidos, df_clientes
import plotly.express as px

st.header("Avaliações")
@st.cache_data
def analise_avaliacoes():
    with st.echo():
        review_counts = df_reviews.groupby('review_score')['review_score'].count().reset_index(name='count')
        fig1 = px.bar(review_counts, x='review_score', y='count',
                    labels={'review_score': 'Nota da Avaliação', 'count': 'Número de Avaliações'},
                    title='Distribuição das Avaliações dos Clientes')
    
    st.markdown('''>Aqui agrupamos as avaliações dos clientes por nota, contamos quantas avaliações há para cada nota e criamos um gráfico de barras para visualizar essa distribuição. O gráfico tem eixos rotulados com "Nota da Avaliação" e "Número de Avaliações", com um título indicando que o gráfico mostra a distribuição das avaliações dos clientes.''')
    
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
    
    st.markdown(''''>Aqui realizamos uma análise de pedidos, avaliando a quantidade de pedidos por estado e a distribuição das avaliações dos clientes (por nota) em relação ao total de pedidos em cada estado. O gráfico gerado mostra a porcentagem de cada nota de avaliação em cada estado, com cores representando as diferentes notas.''')
        
    fig2 = px.bar(merged_counts, x='customer_state', y='percentage', color='review_score',
                    labels={'customer_state': 'Estado do Cliente', 'percentage': 'Porcentagem de Avaliações', 'review_score': 'Nota da Avaliação'},
                    title='Porcentagem de Notas de Avaliação por Estado',
                    color_continuous_scale=["#ff1600", "#76f786"])
    st.plotly_chart(fig2)

analise_avaliacoes()