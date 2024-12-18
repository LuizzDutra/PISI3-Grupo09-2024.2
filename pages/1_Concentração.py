import streamlit as st
import pandas as pd
from arquivos import df_clientes, df_vendedores, df
import plotly.express as px

st.header("Concentração de vendedores e clientes nos estados")



def mostrar_relacao_estados():
    clientes_por_estado = df_clientes.groupby('customer_state')['customer_unique_id'].nunique()
    fig1 = px.bar(clientes_por_estado, x=clientes_por_estado.index, y=clientes_por_estado.values,
                labels={'customer_state': 'Estado', 'y': 'Número de Clientes Únicos'},
                title='Quantidade de Clientes Únicos por Estado')
    
    vendedores_por_estado = df_vendedores.groupby('seller_state')['seller_id'].nunique()
    fig2 = px.bar(vendedores_por_estado, x=vendedores_por_estado.index, y=vendedores_por_estado.values,
                labels={'seller_state': 'Estado', 'y': 'Número de Vendedores Únicos'},
                title='Quantidade de Vendedores Únicos por Estado')

    st.plotly_chart(fig1)
    st.markdown('''>É possível observar uma maior concentração de clientes na região sudeste do Brasil, principalmente no estado de São Paulo.''')

    st.plotly_chart(fig2)
    st.markdown('''
                >Também se observa uma concentração de vendedores no estado de São Paulo e uma menor concentração no sudeste do país.
                >É possível perceber a ausência de vendedores em alguns estados, como Roraima e Tocantins.''')
    
@st.cache_data
def mostrar_concentracao():
    mostrar_relacao_estados()
    #top_categorias()

mostrar_concentracao()