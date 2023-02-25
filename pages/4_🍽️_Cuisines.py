import pandas as pd
import plotly.express as px
import numpy as np
import inflection
import folium
from folium.plugins import MarkerCluster

import streamlit as st

st.set_page_config(page_title="Cuisines", page_icon="🍽️", layout="wide")
#-----------
# FUNÇÕES
#-----------
def worst_cuisines(df):
    df1 = df.loc[:, ['aggregate_rating','cuisines']].groupby(['cuisines']).mean().sort_values(['aggregate_rating'] ,ascending=[True]).reset_index()
    fig = px.bar(df1.head(restaurant_filter), x='cuisines', y='aggregate_rating', labels={'cuisines': 'Culinárias', 'aggregate_rating': 'Média da nota média'}
                                    , width=600, title=f'Top {restaurant_filter} Piores tipos de culinárias', text_auto=True) 

    fig.update_layout(
        title={
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    return fig
def best_cuisines(df):
    df1 = df.loc[:, ['aggregate_rating','cuisines']].groupby(['cuisines']).mean().sort_values(['aggregate_rating'] ,ascending=[False]).reset_index()
    fig = px.bar(df1.head(restaurant_filter) ,x='cuisines', y='aggregate_rating', labels={'cuisines': 'Culinárias', 'aggregate_rating': 'Média da nota média'}
                                    , width=600, title=f'Top {restaurant_filter} Melhores tipos de culinárias', text_auto=True) 



    fig.update_layout(
        title={
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    return fig
def metric_cuisines(index,df):
    '''
    Parametros de entrada:
        - index: Varia com a quantidade de colunas, começando sempre com 0
        - df: Dataframe
    '''
 
    df_aux = df.loc[filter2, ['aggregate_rating','restaurant_id','restaurant_name', 'cuisines']].groupby(['cuisines', 'restaurant_id','restaurant_name']).max().sort_values(['aggregate_rating', 'restaurant_id'] ,ascending=[False,True]).reset_index()
    metrica = df_aux.loc[index,['cuisines','restaurant_name', 'aggregate_rating']]
 
    
    return metrica
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

restaurant_filter = st.sidebar.slider('Selecione a quantidade de restaurantes que você deseja visualziar',
                                      value=10,
                                      min_value=1,
                                      max_value=20)

cuisines_filter = st.sidebar.multiselect('Escolha os tipos de culinaria',
                                        df['cuisines'].unique(),
                                        default=['Home-made', 'BBQ','Brazilian', 'Japanese','Arabian', 'American','Italian'])


#-----------
# FILTER
#-----------
filter = df['country_code'].isin(country_filter)
df = df.loc[filter,:]
filter2 = (df['cuisines'].isin(cuisines_filter)) & (df['country_code'].isin(country_filter))

#-----------
# STREAMLIT LAYOUT
#-----------

st.markdown('# :knife_fork_plate: Visão Tipos de Cusinhas')


with st.container():
    st.markdown('## Melhores restaurantes dos principais tipos Culinários')
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:

        metrica = metric_cuisines(0,df)
        col1.metric(f'{metrica["restaurant_name"]}', value=f'{metrica["aggregate_rating"]}/5.0')
    with col2:
        metrica = metric_cuisines(1,df)
        col2.metric(f'{metrica["restaurant_name"]}', value=f'{metrica["aggregate_rating"]}/5.0')
    with col3:
        metrica= metric_cuisines(2,df)
        col3.metric(f'{metrica["restaurant_name"]}', value=f'{metrica["aggregate_rating"]}/5.0')
    with col4:
        metrica = metric_cuisines(3,df)
        col4.metric(f'{metrica["restaurant_name"]}', value=f'{metrica["aggregate_rating"]}/5.0')
       
    with col5:
        metrica = metric_cuisines(4,df)
        col5.metric(f'{metrica["restaurant_name"]}', value=f'{metrica["aggregate_rating"]}/5.0')
       

with st.container():

    st.markdown(f'# Top {restaurant_filter} Restaurantes')
    colunas=['restaurant_id', 'restaurant_name', 'country_code','city','cuisines', 'average_cost_for_two', 'aggregate_rating', 'votes']

    df1 = df.loc[df['cuisines'].isin(cuisines_filter),colunas].sort_values(['aggregate_rating','restaurant_id'], ascending=[False,True])
    st.dataframe(df1.head(restaurant_filter))
   
with st.container():
    
    col1, col2 = st.columns(2, gap='medium')
    
    with col1:

        fig= best_cuisines(df)
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:

        fig = worst_cuisines(df)
        st.plotly_chart(fig, use_container_width=True)
      