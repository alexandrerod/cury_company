import pandas as pd
import plotly.express as px
import numpy as np
import inflection
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import streamlit as st

st.set_page_config(page_title="Home", page_icon="📊", layout="wide")
#-----------
# FUNÇÕES
#-----------
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')
def restaurant_map(df):
    cols = ['restaurant_id', 'restaurant_name', 'country_code', 'city',
    'longitude', 'latitude', 'cuisines',
    'average_cost_for_two','aggregate_rating','rating_color','currency']
    df1 = df.loc[filter,cols].reset_index(drop=True)

    map = folium.Map(zoom_start=4)
    cluster_marker = MarkerCluster().add_to(map)

    for index, location in df1.iterrows():
        text = f'''
        <b>{location['restaurant_name']}</b><br>
        Price:{location['average_cost_for_two']}({location['currency']}) para dois <br>
        Type: {location['cuisines']}<br>
        Aggregate Rating: {location['aggregate_rating']}/5.0
        '''
        folium.Marker((location['latitude'], 
        location['longitude']),
        popup=folium.Popup(text, min_width=200,max_width=300),
        icon=folium.Icon(color = location['rating_color'], 
        icon='remove-sign')).add_to(cluster_marker)


    folium_static(map, width=800, height=600)
    return
def clean_code(df):
    df = df.dropna()
    df = df.drop_duplicates(subset='Restaurant ID', keep='last')

    # PREENCHENDO O NOME DOS PAÍSES
    COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America",
    }
    def country_name(country_id):
        return COUNTRIES[country_id]

    df['Country Code'] = df['Country Code'].apply(country_name)

    # CRIAÇÃO DO TIPO DE CATEGORIA DA COMIDA
    def create_price_tye(price_range):
        if price_range == 1:
            return "cheap"
        elif price_range == 2:
            return "normal"
        elif price_range == 3:
            return "expensive"
        else:
            return "gourmet"

    df['Price range'] = df['Price range'].apply(create_price_tye)

    # ATRIBUINDO NOME PARA AS CORES
    COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
    }
    def color_name(color_code):
        return COLORS[color_code]
    df['Rating color'] = df['Rating color'].apply(color_name)

    # RENOMEANDO AS COLUNAS DO DATAFRAME
    def rename_columns(dataframe):
        df = dataframe.copy()
        title = lambda x: inflection.titleize(x)
        snakecase = lambda x: inflection.underscore(x)
        spaces = lambda x: x.replace(" ", "")
        cols_old = list(df.columns)
        cols_old = list(map(title, cols_old))
        cols_old = list(map(spaces, cols_old))
        cols_new = list(map(snakecase, cols_old))
        df.columns = cols_new
        return df
    df = rename_columns(df)

    #CATEGORIZANDO OS RESTAURANTES SOMENTE POR UM TIPO DE CULINÁRIA

    df["cuisines"] = df.loc[:, "cuisines"].apply(lambda x: x.split(",")[0])
    return df


#-----------
# CARREGANDO E LIMPANDO OS DADOS
#-----------
df = pd.read_csv('zomato.csv')
df = clean_code(df)


#-----------
# SIDEBAR
#-----------

st.sidebar.markdown('# Filtros')




country_filter = st.sidebar.multiselect('Escolha os paises que deseja visualizar as informações',
                                df['country_code'].unique(),
                                default=['Brazil', 'England', 'Qatar', 'South Africa', 'Canada', 'Australia'])


filter =df['country_code'].isin(country_filter)

st.sidebar.markdown('---------')
st.sidebar.markdown('### Dados Tratados')
st.sidebar.download_button(label='Download',
                           data=convert_df(df),file_name='zomato_clean.csv')

st.markdown('# Fome Zero')
st.markdown('## O melhor lugar para encontrar o seu mais novo restaurante favorito!')
st.markdown('### Temos as seguintes marcas dentro da nossa plataforma')

with st.container():
    col1,col2,col3,col4,col5 = st.columns(5,gap='small')
    with col1:
        df1 = df['restaurant_id'].nunique()
        col1.metric(f"{'Restaurantes Cadastrados':10}",df1)
    with col2:
        df1 = df['country_code'].nunique()
        col2.metric('Paises cadastrados',df1)
    with col3:
        df1 = df['city'].nunique()
        col3.metric('Cidades Cadastradas',df1)
    with col4:
        df1 = df['votes'].sum()
        col4.metric('Avaliações feitas na plataforma',df1)

    with col5:
        df1 = df['cuisines'].nunique()
        col5.metric('Tipos de culinaria oferecidas',df1)

with st.container():

    restaurant_map(df)
