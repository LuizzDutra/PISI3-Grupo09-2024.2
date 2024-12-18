import streamlit as st
import pandas as pd
from arquivos import df_pedidos, df_clientes, df_itens, df_produtos, df_geoloc, df
import plotly.express as px

st.header("Análise dos prazos\n")


def contagem_prazos():
    # Group by 'on_time' and count the number of orders
    on_time_counts = df_pedidos.groupby('on_time')['order_id'].count().reset_index()
    on_time_counts.rename(columns={'order_id': 'order_count'}, inplace=True)


    # Create the plot
    #st.dataframe(on_time_counts)
    fig = px.bar(on_time_counts, x='on_time', y='order_count',
                labels={'on_time': 'Entrega no Prazo', 'order_count': 'Número de Pedidos'},
                text='order_count',
                title='Número de Pedidos Entregues no Prazo vs. Fora do Prazo')
                
    #fig.update_xaxes(tickvals=[0, 1], ticktext=['Fora do Prazo', 'No Prazo'])
    fig.update_layout(xaxis=dict(tickmode='array',
                            tickvals=[0, 1],
                            ticktext=['Atrasado', 'No Prazo']))
    st.plotly_chart(fig)
    st.markdown('''
                O gráfico apresenta uma comparação entre o número de pedidos entregues no prazo e os pedidos atrasados. O eixo X representa as categorias de entrega (Atrasado e No Prazo), enquanto o eixo Y exibe o número total de pedidos.
                ---
                **Insights Observados**

                1.   Dos 117.329 pedidos totais, aproximadamente 90% (105.998 pedidos) foram entregues no prazo. Isso sugere que a logística de entrega é, em grande parte, eficiente.
                2.   Pedidos Atrasados Representam 10% do Total e apesar de ser uma fração menor (11.331 pedidos), os atrasos ainda impactam um volume relevante de clientes. De fato, essa proporção pode ser suficiente para prejudicar a satisfação geral e a reputação do serviço.
                3.   Em contraste, os pedidos "Cancelados" e "Indisponíveis" apresentam avaliações mais baixas (próximas a 1-2), evidenciando insatisfação.

                4.   O volume de pedidos atrasados pode ser analisado em conjunto com outras variáveis, como:
                - Estado do Cliente: Identificar regiões com maior incidência de atrasos.
                Categorias de Produto: Produtos específicos podem ter maior probabilidade de atrasos.
                - Tempo de Processamento: Identificar gargalos na cadeia logística.

                5.   Focar na redução da taxa de pedidos atrasados por meio do uso de modelos preditivos para antecipar atrasos e tomar ações corretivas.
                ''')

def atraso_medio():
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
    # Plot the results

    fig5 = px.bar(state_delays, x='customer_state', y='delivery_delay',
                    labels={'customer_state': 'Estado', 'delivery_delay': 'Atraso Médio (dias)'},
                    title='Atraso Médio de Entrega por Estado')
    
    st.plotly_chart(fig5)

    st.markdown('''>O gráfico acima mostra o atraso médio dos pedidos em função do estado do cliente, podemos ver que o Amapá possui o maior atraso médio, de 106 dias, no entanto apenas 3 pedidos de  68, que foram pro Amapá atrasaram.''')

def atrasos_estados():
    # Merge the dataframes
    merged_df = pd.merge(df_pedidos, df_clientes[['customer_id', 'customer_state']], on='customer_id', how='left')

    # Group by customer state and on_time, then count the orders
    state_ontime_counts = merged_df.groupby(['customer_state', 'on_time'])['order_id'].count().reset_index()
    state_ontime_counts.rename(columns={'order_id': 'order_count'}, inplace=True)
    fig2 = px.bar(state_ontime_counts, x='customer_state', y='order_count', color='on_time',
                labels={'customer_state': 'Estado do Cliente', 'order_count': 'Número de Pedidos', 'on_time': 'Entrega no Prazo'},
                title='Número de Pedidos Entregues no Prazo vs. Fora do Prazo por Estado',
                    color_continuous_scale=["#f77678", "#768ff7"])
    st.plotly_chart(fig2)
    st.markdown('''
                >Com este gráfico tem o intuito de tentar visualizar se algum estado em particular possui algum problema com prazos de entrega, entretanto, os estados parecem ter uma proporção similar entre eles.''')

def atraso_categorias():
    merged_df = pd.merge(df_pedidos[['order_id','customer_id', 'on_time']], df_clientes[['customer_id']], on='customer_id', how='left')
    temp_df = pd.merge(df_itens[['order_id', 'product_id']], df_produtos[['product_id', 'product_category_name']], on='product_id', how='left')
    merged_df = pd.merge(merged_df, temp_df[['order_id', 'product_id', 'product_category_name']], on='order_id', how='left').drop(columns=['customer_id', 'product_id'])
    #st.dataframe(merged_df)
    category_delay_counts = merged_df.groupby(['product_category_name', 'on_time'])['order_id'].count().reset_index()
    category_delay_counts.rename(columns={'order_id': 'order_count'}, inplace=True)
    fig3 = px.bar(category_delay_counts, x='order_count', y="product_category_name", color='on_time',
                labels={'product_category_name': 'Categoria do Produto', 'order_count': 'Número de Pedidos', 'on_time': 'Entrega no Prazo'},
                title='Atraso na Entrega por Categoria de Produto',
                color_continuous_scale=["#f77678", "#768ff7"])
    st.plotly_chart(fig3)
    st.markdown('''
                >Este gráfico possue as entregas separadas por categoria e uma divisão com cor referente ao prazo.
                O motivo é a observação de uma possível categoria problemática nas entregas, mas não há uma categoria de produto
                com problemas de atraso aparentes.
                ''')

def count_atrasos_dias():
    # Create a boolean mask for delayed orders
    delayed_orders_mask = df_pedidos['order_delivered_customer_date'] > df_pedidos['order_estimated_delivery_date']
    # Filter the dataframe to include only delayed orders
    delayed_orders_df = df_pedidos.copy()[delayed_orders_mask]
    # Calculate the delay in days
    delayed_orders_df['delay_days'] = (delayed_orders_df['order_delivered_customer_date'] - delayed_orders_df['order_estimated_delivery_date']).dt.days

    # Create the plot
    fig4 = px.histogram(delayed_orders_df, x='delay_days', nbins=30,
                    labels={'delay_days': 'Atraso em Dias', 'y':''},
                    title='Dias de Atraso nos Pedidos').update_layout(yaxis_title='')

    st.plotly_chart(fig4)

    st.markdown('''>O histograma acima nos mostra que a maioria dos pedidos que atrasaram, sofreram atrasos entre 1 (0 não entra na análise, nesse caso o pedido foi entregue dentro do prazo estimado) a 9 dias. ''')

def entrega_top_10():
    top_10_categorias = df['product_category_name'].value_counts().head(10)

    # Extract the day of the week from 'Data de Entrega'
    df['Dia da Semana Entrega'] = df['order_delivered_customer_date'].dt.dayofweek

    # Create the boxplot using plotly
    fig = px.box(df.loc[df['product_category_name'].isin(top_10_categorias.index)], 
                x='Dia da Semana Entrega', 
                y='product_category_name',
                orientation='h',
                title='Tempo de Entrega por Categoria de Produto (Top 10)',
                labels={'Dia da Semana Entrega': 'Dia da Semana de Entrega (0=Segunda, 6=Domingo)',
                        'product_category_name': 'Categoria do Produto'})

    st.plotly_chart(fig)
    st.markdown('''
                O gráfico de barras horizontal mostra o tempo médio de entrega das principais categorias de produtos ao longo da semana. O eixo X representa os dias da semana (0 = Segunda-feira, 6 = Domingo), enquanto o eixo Y indica as categorias de produtos.
                ---
                **Insights Observados**

                1.   A maioria das categorias possui tempo médio de entrega concentrado entre 3 e 4 dias úteis, com algumas pequenas variações.
                2.   Categorias como "utilidades_domesticas", "automotivo" e "moveis_decoracao" têm tempos de entrega mais longos, estendendo-se até a metade da semana (próximos a 4 dias). Isso pode ser explicado por fatores como: Volume ou peso do produto ou menor frequência de pedidos, resultando em menos rotas otimizadas.
                3.   "informatica_acessorios", "telefonia", "beleza_saude" e "esporte_lazer" apresentam os menores tempos médios de entrega, sendo majoritariamente concluídos em 3 dias úteis. Isso pode indicar processos logísticos mais eficientes ou menor complexidade na distribuição desses produtos.

                4.   A dispersão do tempo de entrega é relativamente uniforme entre as categorias, com poucas variações extremas, sugerindo que o sistema logístico é padronizado, mas ainda há espaço para otimização.
                ''')

@st.cache_data
def mostrar_analise_prazos():
    
    contagem_prazos()
    atrasos_estados()
    atraso_categorias()
    count_atrasos_dias()
    entrega_top_10()
    #atraso_medio()

    
mostrar_analise_prazos()
