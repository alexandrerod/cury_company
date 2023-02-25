import pandas as pd
import plotly.express as px
import numpy as np
import inflection
import folium
from folium.plugins import MarkerCluster

import streamlit as st

st.set_page_config(page_title="Cities", page_icon="🏙️", layout="wide")
#-----------
# FUNÇÕES
#-----------

def top_restaurants_cuisines(df):
    df1 = df.loc[:,['cuisines', 'country_code','city']].groupby(['country_code','city']).nunique().sort_values(['cuisines','city'],ascending=[False,True]).reset_index()
    df_aux = df1.iloc[0:10,:]
    fig = px.bar(df_aux, x='city', y= 'cuisines',color='country_code', labels={'city': 'Cidades', 'cuisines': 'Quantidade de tipos de culinária únicos'}
                                                        , title='Top 10 Cidade com mais restaurantes com tipos de culinária distintos', text_auto=True, width=800)
    fig.update_layout(
        title={
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    return fig
def agg_lower_than_two(df):
    filtro = df['aggregate_rating'] < 2.5 
    df1 = (df.loc[filtro, ['city','country_code','restaurant_id']].groupby(['country_code','city'])
                                                                .count().sort_values(['restaurant_id','country_code'], ascending=[False,True])
                                                                .reset_index())
    df_aux = df1.iloc[0:7,:]

    fig = px.bar(df_aux, x='city', y= 'restaurant_id',color='country_code', labels={'city': 'Cidades', 'restaurant_id': 'Quantidade de restaurantes'}
                                                        , title='Top 7 Cidades com média de avaliação menor que 2.5', text_auto=True, width=400)
    fig.update_layout(
        title={
            'y':0.9,
            'x':0.5,
            'font_size':14,
            'xanchor': 'center',
            'yanchor': 'top'})
    return fig
def agg_higher_than_four(df):
    filtro = df['aggregate_rating'] > 4 
    df1 = df.loc[filtro, ['city','country_code','restaurant_id']].groupby(['country_code','city']).count().sort_values(['restaurant_id', 'country_code'], ascending=[False,True]).reset_index()
    df_aux = df1.iloc[0:7,:]

    fig = px.bar(df_aux, x='city', y= 'restaurant_id',color='country_code', labels={'city': 'Cidades', 'restaurant_id': 'Quantidade de restaurantes'}
                                                        , title='Top 7 Cidades com média de avaliação acima de 4', text_auto=True, width=400)
    fig.update_layout(
        title={
            'y':0.9,
            'x':0.4,
            'font_size':14,
            'xanchor': 'center',
            'yanchor': 'top'})
    return fig
def top_cities(df):
    df1 = (df.loc[:,['restaurant_id','country_code','city']].groupby(['country_code',
                        'city']).count().sort_values(['restaurant_id','city'], ascending=[False,True]).reset_index())
    df_aux = df1.iloc[0:10, : ]

    fig = px.bar(df_aux, x='city', y= 'restaurant_id',color='country_code', labels={'city': 'Cidades', 'restaurant_id': 'Quantidade de restaurantes'}
                                                        , title='Top 10 Cidades com mais restaurantes nda Base de Dados', text_auto=True, width=800)
    fig.update_layout(
        title={
            'y':0.9,
            'x':0.5,
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

st.markdown('# :cityscape: Visão Cidades')


with st.container():
        fig = top_cities(df)
        st.plotly_chart(fig, use_container_width=False)

with st.container():
    col1, col2 = st.columns(2, gap='medium')
    
    with col1:
        fig = agg_higher_than_four(df)

        st.plotly_chart(fig, use_container_width=False)
        

    
    with col2:

        fig = agg_lower_than_two(df)
        st.plotly_chart(fig, use_container_width=False)

with st.container():
    fig = top_restaurants_cuisines(df)

    st.plotly_chart(fig, use_container_width=False)
