import streamlit as st
import joblib
import pandas as pd
import numpy as np
import pathlib
#from utils import download_file_from_google_drive
import os
import pydrive
from pydrive.auth import GoogleAuth
import gdown

@st.cache_data
def carregar_dados():
    return pd.read_parquet('dataframe/df_parquete.parquet')

@st.cache_data
def carregar_modelo():
    with st.spinner():
        if not pathlib.Path('model/random_forest_model.pkl').exists():
            with st.spinner('Baixando modelo Random Forest'):
                os.makedirs('model', exist_ok=True)
                #modelo
                gdown.download(id='12R0mWOM-ZyhYv2Ne65bE2PhahWPTcdzm', fuzzy=True, output='model/random_forest_model.pkl')
                #encoders
                gdown.download(id='1FpX7eR7xEBkUtXYp-lWpDNRc0Z3t3iTI', fuzzy=True, output='encoders/label_encoder_estado_cliente.pkl')
                gdown.download(id='1_1rdn7N4-Rd6OxUTqvSJhfuLGmQqtBMc', fuzzy=True, output='encoders/label_encoder_estado_vendedor.pkl')
                gdown.download(id='1pjBvDzYHHnpUq7902ctUles0PRdfhtb4', fuzzy=True, output='encoders/label_encoder_nome_categoria_produto.pkl')
        return joblib.load('model/random_forest_model.pkl')

model = carregar_modelo()
table = carregar_dados()
columns = table.columns.tolist()
columns_with_enconders = {}


for col in columns:
    if (table[col].dtype == 'object') and col != 'alvo':
        columns_with_enconders[col] = joblib.load(f'encoders/label_encoder_{col}.pkl')

input_data = []


def transform_input(user_input):
    pass

def view_modelo():
    st.title("Aplicativo de Predição")
    user = input_fields()
    if st.button(label="Enviar"):
        input_data.clear()
        for k,v in user.items():
            if(table[k].dtype == 'object'):
                coded = columns_with_enconders[k].transform([v])[0]
                input_data.append(coded)
            elif table[k].dtype == 'datetime64[ns]':
                print(type(v))
                input_data.append(pd.Timestamp(v).timestamp())
            else:
                input_data.append(v)  
        input = np.array(input_data).reshape(1,-1)
        prediction = model.predict(input)
        st.write(f"A classe prevista é: {prediction[0]}")

def input_fields():
    inputs = {}
    for column in columns:
        if column != "alvo":
            if table[column].dtype == 'object':
                # Para colunas categóricas
                categorias = table[column].unique().tolist()
                inputs[column] = st.selectbox(label=column, options=categorias, key=column)
            elif table[column].dtype == 'datetime64[ns]':
                # Para colunas de data
                inputs[column] = st.date_input(label=column, key=column)
            else:
                # Para colunas numéricas
                inputs[column] = st.number_input(label=column, key=column)
    return inputs

view_modelo()