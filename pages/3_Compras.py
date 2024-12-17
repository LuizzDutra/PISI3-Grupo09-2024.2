import streamlit as st
import pandas as pd
from arquivos import df_produtos, df_itens, df_pedidos, df
import plotly.express as px

st.header("Análise das informações de compras\n")

def valor_compras_estado():
    compras_por_estado = df.groupby('customer_state')['price'].sum().reset_index()

    # Crie o gráfico de barras com Plotly Express
    fig = px.bar(compras_por_estado,
                x='customer_state',
                y='price',
                labels={'customer_state': 'Estado', 'price': 'Valor Total de Compras'},
                title='Valor Total de Compras por Estado')
    st.plotly_chart(fig)
    st.markdown('''
            O gráfico de barras apresenta o valor total de compras realizadas em cada estado brasileiro. O eixo X mostra os estados, enquanto o eixo Y representa o valor total de compras em moeda local.
            ---
            **Insights Observados**

            1.   O estado de São Paulo (SP) se destaca como o líder absoluto em volume total de compras, ultrapassando 7 milhões. Esse fato pode ser explicado pela densidade populacional elevada, maior concentração de consumidores e infraestrutura robusta de comércio eletrônico.
            2.   Minas Gerais (MG) e Rio de Janeiro (RJ) também se destacam, com valores totais de compras na faixa de 2 a 3 milhões. Esses estados são importantes centros econômicos, com grande participação no mercado de e-commerce.
            3.   Os estados do Sudeste (SP, RJ, MG) concentram a maior parte das compras, evidenciando a desigualdade regional no comportamento de consumo.

            4.   A dispersão do tempo de entrega é relativamente uniforme entre as categEstados como AC (Acre), AM (Amazônas), AP (Amapá), RR (Roraima), RO (Rondônia), RN (Rio Grande do Norte) e TO (Tocantins) apresentam valores totais muito baixos. Isso pode estar relacionado a Baixa penetração do e-commerce nessas regiões ou poder aquisitivo reduzido.
            ''')

def tipo_pagamento():
    # Cálculo das porcentagens de cada tipo de pagamento
    payment_counts = df['payment_type'].value_counts()
    payment_percentages = payment_counts / payment_counts.sum() * 100

    fig = px.pie(df, 
             names='payment_type', 
             title='Distribuição dos Tipos de Pagamento',
             hole=0.3) # Adiciona um furo no centro para melhor visualização
    st.plotly_chart(fig)
    st.markdown('''O gráfico de pizza mostra a distribuição percentual dos métodos de pagamento utilizados em compras no e-commerce. Cada fatia representa a participação de um tipo de pagamento específico.
---
**Insights Observados**

1.   O Cartão de Crédito é o método mais utilizado, representando 73,7% das transações. Essa predominância reflete a preferência dos consumidores por parcelamentos e maior praticidade na aprovação das compras.
2.   O Boleto Bancário é o segundo método mais popular, com 19,5% das transações. Esse método atende principalmente consumidores que:
- Não possuem cartão de crédito.
- Preferem realizar pagamentos à vista.
- Buscam opções sem incidência de juros.
3.   Em regiões menos bancarizadas ou com menor acesso a crédito, o boleto bancário tende a ganhar mais destaque.

4.   A preferência pelo cartão de crédito pode ser mais significativa em consumidores de maior poder aquisitivo ou habituados a compras online recorrentes.
''')


def top_categorias():
    # Top 10 categorias de produtos mais comprados
    top_10_categorias = df['product_category_name'].value_counts().head(10)

    # Gráfico de barras das top 10 categorias com Plotly Express
    fig = px.bar(y=top_10_categorias.index, 
                x=top_10_categorias.values,
                labels={'y':'product_category_name', 'x':'Número de Pedidos'},
                title='Top 10 Categorias de Produtos Mais Vendidos')

    fig.update_layout(yaxis_title='Categoria do Produto', xaxis_title='Número de Pedidos', yaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig)
    st.markdown('''
                O gráfico de barras apresenta as 10 categorias de produtos com maior número de pedidos em um e-commerce. O eixo X mostra as categorias de produtos, enquanto o eixo Y representa o número total de pedidos por categoria.
                ---
                **Insights Observados**

                1.   A categoria "cama_mesa_banho" lidera com cerca de 12.000 pedidos, indicando uma alta demanda por produtos dessa linha, possivelmente relacionada à sazonalidade ou promoções.
                2.   "beleza_saude" ocupa a segunda posição com 10.000 pedidos, sugerindo uma forte procura por produtos de autocuidado e saúde, um segmento geralmente resiliente e crescente no mercado.
                3.   Categorias como "esporte_lazer" e "moveis_decoracao" apresentam números próximos de 9.000 pedidos, refletindo uma competição equilibrada entre elas. Isso pode indicar que consumidores investem tanto em bem-estar físico (esporte e lazer) quanto em conforto doméstico (móveis e decoração).

                4.   As categorias "cama_mesa_banho", "moveis_decoracao" e "utilidades_domesticas" indicam um forte comportamento de consumo voltado para o lar, sugerindo um aumento de demanda por melhorias no ambiente doméstico.


                5.   A relevância da categoria "beleza_saude" aponta para uma preocupação crescente com bem-estar e autocuidado
                ''')

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
                O gráfico mostra a tendência das vendas ao longo do tempo em uma visão mensal. O eixo X representa os meses, enquanto o eixo Y mostra o total de vendas em valores monetários (soma dos preços). Cada ponto no gráfico indica o volume total de vendas no mês correspondente.
---
**Insights Observados**

1.   Meses com picos de vendas podem estar correlacionados a atrasos nas entregas devido a demandas mais altas. Essa informação pode ser cruzada com dados de tempo de entrega e avaliações dos clientes para construir modelos preditivos.
2.   Tendências de crescimento ou declínio sustentadas ao longo do tempo podem ser indicativos da saúde do negócio. De fato, um aumento consistente sugere um mercado em expansão, enquanto quedas contínuas exigem estratégias de recuperação.
3.   É possível detectar sazonalidades, como aumentos de vendas em Black Friday, Natal ou outras datas comemorativas que influenciam o comportamento de compra.
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
    valor_compras_estado()
    tipo_pagamento()
    top_categorias()

mostrar_trend_compras()
