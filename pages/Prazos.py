import streamlit as st
import pandas as pd
from arquivos import df_pedidos, df_clientes, df_itens, df_produtos, df_geoloc
import plotly.express as px

st.header("Análise dos prazos\n")


def contagem_prazos():
    # Group by 'on_time' and count the number of orders
    with st.echo():
        on_time_counts = df_pedidos.groupby('on_time')['order_id'].count().reset_index()
        on_time_counts.rename(columns={'order_id': 'order_count'}, inplace=True)


        # Create the plot
        fig1 = px.bar(on_time_counts, x='on_time', y='order_count',
                    labels={'on_time': 'Entrega no Prazo', 'order_count': 'Número de Pedidos'},
                    title='Número de Pedidos Entregues no Prazo vs. Fora do Prazo')
        fig1.update_xaxes(tickvals=[0, 1], ticktext=['Fora do Prazo', 'No Prazo'])
    st.markdown('''>Agrupamos os dados da coluna on_time e usamos o count para adquirir a contagem de pedidos fora e dentro do prazo.''')
    st.plotly_chart(fig1)
    st.markdown('''
                >Observa-se que a maioria dos pedidos são entregues no prazo.
                >Mas ainda cerca de 10% chegam atrasados.
                ''')

def atraso_medio():
    with st.echo():
        # Merge the dataframes
        merged_df = pd.merge(df_pedidos, df_clientes, on='customer_id', how='left')
        merged_df = pd.merge(merged_df, df_geoloc, left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix', how='left')
        # Calculate delivery delay
        merged_df['delivery_delay'] = (merged_df['order_delivered_customer_date'] - merged_df['order_estimated_delivery_date']).dt.days

        # Filter for delayed orders
        delayed_orders = merged_df[merged_df['delivery_delay'] > 0]

        # Group by customer state and calculate the mean delay
        state_delays = delayed_orders.groupby('customer_state')['delivery_delay'].mean().reset_index()

        # Sort by mean delay in descending order
        state_delays = state_delays.sort_values('delivery_delay', ascending=False)

    st.markdown('''>Este código realiza uma análise dos atrasos nas entregas de pedidos, mesclando dados de pedidos, clientes e geolocalização. Ele calcula o atraso médio de entrega por estado, filtra os pedidos com atraso e agrupa os resultados por estado do cliente, ordenando os estados com maior atraso médio.''')    
        # Plot the results
    
    fig5 = px.bar(state_delays, x='customer_state', y='delivery_delay',
                    labels={'customer_state': 'Estado', 'delivery_delay': 'Atraso Médio (dias)'},
                    title='Atraso Médio de Entrega por Estado')
    
    st.plotly_chart(fig5)

    st.markdown('''>O gráfico acima mostra o atraso médio dos pedidos em função do estado do cliente, podemos ver que o Amapá possui o maior atraso médio, de 106 dias, no entanto apenas 3 pedidos de  68, que foram pro Amapá atrasaram.''')

def atrasos_estados():
    with st.echo():
        # Merge the dataframes
        merged_df = pd.merge(df_pedidos, df_clientes[['customer_id', 'customer_state']], on='customer_id', how='left')

        # Group by customer state and on_time, then count the orders
        state_ontime_counts = merged_df.groupby(['customer_state', 'on_time'])['order_id'].count().reset_index()
        state_ontime_counts.rename(columns={'order_id': 'order_count'}, inplace=True)
        fig2 = px.bar(state_ontime_counts, x='customer_state', y='order_count', color='on_time',
                    labels={'customer_state': 'Estado do Cliente', 'order_count': 'Número de Pedidos', 'on_time': 'Entrega no Prazo'},
                    title='Número de Pedidos Entregues no Prazo vs. Fora do Prazo por Estado',
                    color_continuous_scale=["#f77678", "#768ff7"])
    st.markdown('''
                >Primeiramente é feito um merge entre pedidos e clientes para se ter acesso a coluna customer_state.
                Após isso agrupamos com a coluna customer_state e on_time e é extraída a contagem''')
    st.plotly_chart(fig2)
    st.markdown('''
                >Com este gráfico tem o intuito de tentar visualizar se algum estado em particular possui algum problema com prazos de entrega, entretanto, os estados parecem ter uma proporção similar entre eles.''')

def atraso_categorias():
    with st.echo():
        merged_df = pd.merge(df_pedidos[['order_id','customer_id', 'on_time']], df_clientes[['customer_id']], on='customer_id', how='left')
        temp_df = pd.merge(df_itens[['order_id', 'product_id']], df_produtos[['product_id', 'product_category_name']], on='product_id', how='left')
        merged_df = pd.merge(merged_df, temp_df[['order_id', 'product_id', 'product_category_name']], on='order_id', how='left').drop(columns=['customer_id', 'product_id'])
        st.dataframe(merged_df)
        category_delay_counts = merged_df.groupby(['product_category_name', 'on_time'])['order_id'].count().reset_index()
        category_delay_counts.rename(columns={'order_id': 'order_count'}, inplace=True)
        fig3 = px.bar(category_delay_counts, x='order_count', y="product_category_name", color='on_time',
                    labels={'product_category_name': 'Categoria do Produto', 'order_count': 'Número de Pedidos', 'on_time': 'Entrega no Prazo'},
                    title='Atraso na Entrega por Categoria de Produto',
                    color_continuous_scale=["#f77678", "#768ff7"])
    st.markdown('''
                >Aqui é feito um merge com df_pedidos, df_clientes, df_itens e df_produtos.
                Assim sendo possível relacionar a coluna on_time com a categoria do produto através do groupby.
                Após isso é feita a contagem de produtos por categoria, classificados entre dentro e fora do prazo.''')
    st.plotly_chart(fig3)
    st.markdown('''
                >Este gráfico possue as entregas separadas por categoria e uma divisão com cor referente ao prazo.
                O motivo é a observação de uma possível categoria problemática nas entregas, mas não há uma categoria de produto
                com problemas de atraso aparentes.
                ''')

def count_atrasos_dias():
    with st.echo():
        # Create a boolean mask for delayed orders
        delayed_orders_mask = df_pedidos['order_delivered_customer_date'] > df_pedidos['order_estimated_delivery_date']
        # Filter the dataframe to include only delayed orders
        delayed_orders_df = df_pedidos.copy()[delayed_orders_mask]
        # Calculate the delay in days
        delayed_orders_df['delay_days'] = (delayed_orders_df['order_delivered_customer_date'] - delayed_orders_df['order_estimated_delivery_date']).dt.days

        # Create the plot
        fig4 = px.histogram(delayed_orders_df, x='delay_days', nbins=30,
                        labels={'delay_days': 'Atraso em Dias'},
                        title='Dias de Atraso nos Pedidos')
    
    st.markdown('''
                >Aqui criamos uma máscara para identificar pedidos entregues com atraso, filtramos esses pedidos em um novo DataFrame e calculamos o atraso em dias, armazenando o valor em uma nova coluna chamada delay_days''')

    st.plotly_chart(fig4)

    st.markdown('''>O histograma acima nos mostra que a maioria dos pedidos que atrasaram, sofreram atrasos entre 1 (0 não entra na análise, nesse caso o pedido foi entregue dentro do prazo estimado) a 9 dias. ''')

@st.cache_data
def mostrar_analise_prazos():
    
    contagem_prazos()
    atrasos_estados()
    atraso_categorias()
    count_atrasos_dias()
    #atraso_medio()

    
mostrar_analise_prazos()