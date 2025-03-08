import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, davies_bouldin_score
from scipy.sparse import hstack
import plotly.express as px
from arquivos import df
import json
import requests

# Título da Aplicação
st.header("Machine Learning - K-Means Clustering")

df.fillna({'review_comment_message': '', 'payment_value': 0}, inplace=True)

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
#nltk.download('all', quiet=True)

def preprocess_text(text):
    text = re.sub(r'\W+', ' ', text) 
    text = text.lower()
    words = nltk.word_tokenize(text)  
    stop_words = set(stopwords.words('portuguese'))
    lemmatizer = nltk.WordNetLemmatizer()
    return ' '.join([lemmatizer.lemmatize(word) for word in words if word not in stop_words])

df['review_comment_message'] = df['review_comment_message'].fillna('')
df['comentarios_limpos'] = df['review_comment_message'].apply(preprocess_text)

tfidf = TfidfVectorizer(max_features=1000)
X_text = tfidf.fit_transform(df['comentarios_limpos'])

df['total_gasto'] = df['payment_value']

scaler = StandardScaler()
X_numeric = scaler.fit_transform(df[['total_gasto']])

if 'customer_state' not in df.columns:
    st.error("Erro: A coluna 'customer_state' não existe no DataFrame.")
    st.stop()

onehot = OneHotEncoder(handle_unknown='ignore')
X_region = onehot.fit_transform(df[['customer_state']])

X_combined = hstack([X_numeric, X_region, X_text])

def plot_elbow_method(X):
    distortions = []
    k_values = range(2, 10)

    for k in k_values:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X)
        distortions.append(kmeans.inertia_)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(k_values, distortions, 'bo-')
    ax.set_xlabel('Número de Clusters (k)')
    ax.set_ylabel('Inércia')
    ax.set_title('Método do Cotovelo')
    ax.grid()

    return fig

st.title("Análise de Clusters com K-Means")

st.subheader("Método do Cotovelo")
fig_elbow = plot_elbow_method(X_combined)
st.pyplot(fig_elbow)


kmeans = KMeans(n_clusters=6, random_state=42, n_init=10)

df['cluster_kmeans'] = kmeans.fit_predict(X_combined)

st.subheader("Distribuição dos Clusters")
analysis = df.groupby(['customer_state', 'cluster_kmeans']).agg(
    {'total_gasto': ['mean', 'sum'], 'comentarios_limpos': 'count'}
).reset_index()

st.write(analysis)

scatter_data = df.groupby(['customer_state', 'cluster_kmeans']).size().reset_index(name='count')

fig, ax = plt.subplots(figsize=(12, 8))
sns.scatterplot(
    data=scatter_data,
    x='customer_state',
    y='count',
    hue='cluster_kmeans',
    size='count',
    sizes=(50, 500),
    palette='coolwarm',
    ax=ax
)

ax.set_title('Frequência de Clusters por Estado')
ax.set_xlabel('Estado')
ax.set_ylabel('Frequência')
plt.xticks(rotation=45)
plt.tight_layout()

st.pyplot(fig)

@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    response =  requests.get(url)
    return response.json()

geojson_brasil = load_geojson()

state_name_to_geojson = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia",
    "CE": "Ceará", "DF": "Distrito Federal", "ES": "Espírito Santo", "GO": "Goiás",
    "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
    "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco", "PI": "Piauí",
    "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul",
    "RO": "Rondônia", "RR": "Roraima", "SC": "Santa Catarina", "SP": "São Paulo",
    "SE": "Sergipe", "TO": "Tocantins"
}
map_data_comentarios = df.groupby("customer_state")["review_comment_message"].count().reset_index()
map_data_comentarios["estado_nome"] = map_data_comentarios["customer_state"].map(state_name_to_geojson)

map_data_comentarios["tooltip"] = map_data_comentarios.apply(
    lambda row: f"<b>{row['estado_nome']}</b><br>Comentários: {row['review_comment_message']}", axis=1
)

st.markdown("<h2 style='text-align: left; font-size: 36px;'>Mapa de Comentários por Estado</h2>", unsafe_allow_html=True)

fig_comentarios = px.choropleth(
    map_data_comentarios,
    geojson=geojson_brasil,
    locations="estado_nome",
    featureidkey="properties.name",
    color="review_comment_message",
    color_continuous_scale="Reds",  
    title="Quantidade de Comentários por Estado",
    hover_data={"estado_nome": False, "review_comment_message": False, "tooltip": True}  
)

fig_comentarios.update_geos(
    fitbounds="locations",  
    visible=False,  
    projection_type="mercator" 
)

fig_comentarios.update_layout(
    height=800,  
    width=1200,  
    margin={"r": 0, "t": 50, "l": 0, "b": 0},  
    font=dict(size=16), 
    title_font=dict(size=28)  
)

st.plotly_chart(fig_comentarios, use_container_width=True)