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
    st.markdown('''>Agrupamos os dados da coluna on_time e usamos o count para adquirir a contagem de pedidos fora e dentro do prazo.''')
    st.plotly_chart(fig1)
    st.markdown('''
                >Observa-se que a maioria dos pedidos são entregues no prazo.
                >Mas ainda cerca de 10% chegam atrasados.
                ''')

    with st.echo():
        # Merge the dataframes
        merged_df = pd.merge(df_pedidos, df_clientes, on='customer_id', how='left')

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


    with st.echo():
        temp_df = pd.merge(df_itens, df_produtos, on='product_id', how='left')
        merged_df = pd.merge(merged_df, temp_df, on='order_id', how='left')

        category_delay_counts = merged_df.groupby(['product_category_name', 'on_time'])['order_id'].count().reset_index()
        category_delay_counts.rename(columns={'order_id': 'order_count'}, inplace=True)
        fig3 = px.bar(category_delay_counts, x='order_count', y="product_category_name", color='on_time',
                    labels={'product_category_name': 'Categoria do Produto', 'order_count': 'Número de Pedidos', 'on_time': 'Entrega no Prazo'},
                    title='Atraso na Entrega por Categoria de Produto',
                    color_continuous_scale=["#f77678", "#768ff7"])
    st.markdown('''
                >Aqui é reutilizada a "merged_df" do código anterior além de ser feito um merge com df_itens e df_produtos.
                Assim sendo possível relacionar a coluna on_time com a categoria do produto através do groupby.
                Após isso é feita a contagem de produtos por categoria, classificados entre dentro e fora do prazo.''')
    st.plotly_chart(fig3)
    st.markdown('''
                >Este gráfico possue as entregas separadas por categoria e uma divisão com cor referente ao prazo.
                O motivo é a observação de uma possível categoria problemática nas entregas, mas não há uma categoria de produto
                com problemas de atraso aparentes.
                ''')
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







def mostrar_trend_compras():
    with st.echo():
        merged_df = pd.merge(df_itens, df_produtos, on='product_id', how='left')
        merged_df = pd.merge(merged_df, df_pedidos, on='order_id', how='left')

        product_popularity = merged_df.groupby('product_category_name')['order_id'].count().reset_index()
        product_popularity = product_popularity.rename(columns={'order_id': 'order_count'})
        fig1 = px.bar(product_popularity, x='order_count', y='product_category_name', title='Popularidade das categorias de produto')

        fig1.update_layout(xaxis_title='Quantidade de Pedidos',yaxis_title='Categoria de Produto')

    st.markdown('''
                >Primeiramente é feito o merge entre itens produtos e pedidos, para serem utilizadas as colunas de
                categoria de item e preço que seram relevantes no uso do merged_df.
                Após isso é realizado um groupby na categoria e feito uma agregação de count, para alcançar a quantidade de compras
                de determinada categoria.
                ''')
    st.plotly_chart(fig1)
    st.markdown('''
                >Com esse gráfico se obtem como categorias de produto mais compradas sendo:
                
                >cama_mesa_banho, beleza_saude e esporte_lazer.
                ''')

    


    with st.echo():
        average_price_by_category = merged_df.groupby('product_category_name')['price'].mean().reset_index()
        fig2 = px.bar(average_price_by_category, x='price', y='product_category_name', title='Preço médio por categoria de produto')
    
        fig2.update_layout(xaxis_title='Preço', yaxis_title='Categoria de Produto' )

    st.markdown('''
                >Neste código é realizado o cálculo das médias de preço por categoria de produto.
                ''')
    st.plotly_chart(fig2)
    st.markdown('''
                >Com esse gráfico é possível observar que a categoria com valor de compra mais elevado é a de computadores(pcs).
                
                >Mas é necessário se atentar que é uma das categorias menos compradas, com 203 compras no dataset.
                ''')

    with st.echo():
        merged_df['purchase_month'] = merged_df['order_purchase_timestamp'].dt.month
        monthly_purchases = merged_df.groupby('purchase_month')['order_id'].count().reset_index()
        monthly_purchases = monthly_purchases.rename(columns={'order_id':'order_count'})
        fig3 = px.line(monthly_purchases, x='purchase_month', y='order_count', title='Quantidade de compras por mês')

        fig3.update_layout(xaxis_title='Mês da Compra',yaxis_title='Quantidade de Pedidos')

    st.markdown('''
                >Aqui é criada uma coluna no merged_df denominada de purchase_month com o intuito de realizar a contagem de compras
                por mês.
                ''')
    st.plotly_chart(fig3)
    st.markdown('''
                >É possível observar que entre os mêses 3 e 8 se tem maiores quantidades de pedidos no dataset.
                ''')


    with st.echo():
        price_bins = [0, 50, 100, 200, float('inf')]
        price_labels = ['0-50', '51-100', '101-200', '200+']
        merged_df['price_category'] = pd.cut(merged_df['price'], bins=price_bins, labels=price_labels, right=False)
        price_category_purchases = merged_df.groupby('price_category', observed=True)['order_id'].count().reset_index()
        price_category_purchases = price_category_purchases.rename(columns={'order_id':'order_count'})
        fig4 = px.bar(price_category_purchases, x='price_category', y='order_count', title='Valor de compra por categoria')

        fig4.update_layout(xaxis_title='Categoria de Preço',yaxis_title='Quantidade de Pedidos')

    st.markdown('''
                >Neste código é realizada a separação de compras em categorias de preço através do cut.
                Após isso é feita a contagem das compras através do agrupamento das categorias.
                ''')
    st.plotly_chart(fig4)
    st.markdown('''
                No gráfico é possível observar uma relação inversamente proporcional esperada entre valor de compra e número de pedidos.
                ''')

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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Main", "Transformar","Concentração", "Prazos", "Compras", "Avaliações"])

with tab1:
    st.markdown('''
                Dataset utilizado: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce/data)
                ''')
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
    

with tab2:
    st.header("Transformação de dados")
    transformar_dados()
with tab3:
    st.header("Concentração de vendedores e clientes nos estados")
    mostrar_relacao_estados()
with tab4:
    st.header("Análise dos prazos\n")
    mostrar_analise_prazos()
with tab5:
    st.header("Análise das informações de compras\n")
    mostrar_trend_compras()
with tab6:
    st.header("Avaliações")
    analise_avaliacoes()
