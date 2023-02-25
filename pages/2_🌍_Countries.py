import pandas as pd
import plotly.express as px
import numpy as np
import inflection
import folium
from folium.plugins import MarkerCluster

import streamlit as st

st.set_page_config(page_title="Countries", page_icon="🌍", layout="wide")

#-----------
# FUNÇÕES
#-----------
def avg_price_for_two(df):
    df1 = df.loc[:,['average_cost_for_two', 'country_code']].groupby(['country_code']).mean().reset_index()
    df_aux = df1.iloc[0:5,:]

    fig = px.bar(df_aux, x='country_code', y= 'average_cost_for_two', labels={'country_code': 'Paises', 'average_cost_for_two': 'Preço do prato para duas pessoas'}
                                                        , title='Média de Preço de um prato para duas pessoas por País', text_auto=True, width=200)
    fig.update_layout(
        title={
            'y':0.9,
            'x':0.5,
            'font_size':14,
            'xanchor': 'center',
            'yanchor': 'top'})
    return fig
def votes_per_country(df):
    df1 = df.loc[:,['votes','country_code']].groupby(['country_code']).mean().sort_values('votes', ascending=False).reset_index()

    df_aux = df1.iloc[0:5,:]

    fig = px.bar(df_aux, x='country_code', y= 'votes', labels={'country_code': 'Paises', 'votes': 'Quantidade de Avaliações'}
                                                        , title='Média de Avaliações feitas por País', text_auto=True, width=200)
    fig.update_layout(
        title={
            'y':0.9,
            'x':0.5,
            'font_size':14,
            'xanchor': 'center',
            'yanchor': 'top'})
    return fig
def cities_per_contry(df):
    df1 = df.loc[:, ['city','country_code']].groupby(['country_code']).count().sort_values('city',ascending=False).reset_index()
    df1 = df1.iloc[0:6,:]


    fig = px.bar(df1, x='country_code', y='city', title='Quantidade de Cidades Registradas por país',
                labels={'city': 'Quantidade de Cidades', 'country_code': 'Paises'},text_auto=True)
    fig.update_layout(
    title={
        'y':0.9,
        'x':0.5,
        'font_size':14,
        'xanchor': 'center',
        'yanchor': 'top'})
    return fig
def restaurants_per_country(df):
    df1 = df.loc[:, ['restaurant_id', 'country_code']].groupby(['country_code']).nunique().sort_values('restaurant_id', ascending=False).reset_index()

    df_bar = df1.iloc[0:6,:]
    fig = px.bar(df_bar, x='country_code', y='restaurant_id'
                                        ,title='Quantidade de Restaurantes Registrados por País'
                                        , labels=dict(restaurant_id='Quantidade de Resturantes', country_code='Paises'),text_auto=True)

    fig.update_layout(
        title={
            'y':0.9,
            'x':0.5,
            'font_size':14,
            'xanchor': 'center',
            'yanchor': 'top'})
    return fig
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



#-----------
# FILTER
#-----------
filter = df['country_code'].isin(country_filter)
df = df.loc[filter,:]

#-----------
# STREAMLIT LAYOUT
#-----------

st.markdown('# :earth_americas: Visão Paises')


with st.container():
    fig = restaurants_per_country(df)
    st.plotly_chart(fig)

with st.container():

    fig = cities_per_contry(df)
    st.plotly_chart(fig)

with st.container():
    col1, col2 = st.columns(2, gap='medium')
    
    with col1:

        fig = votes_per_country(df)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = avg_price_for_two(df)
        st.plotly_chart(fig, use_container_width=True)
