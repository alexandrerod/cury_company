# Bibliotetecas para tratamento de dados
import pandas as pd
import numpy as np
from haversine import haversine
from streamlit_folium import folium_static
# bibliotecas para apresentação gráfica

import plotly.express as px
import plotly.graph_objects as go
import folium

import streamlit as st


#------------
# CARREGANDO OS DADOS
#-----------

df = pd.read_csv('FTC/proj01/train.csv')
dataset = df.copy()

#------------
# LIMPANDO OS DADOS
#-----------

#retirando NaN

filtro =( (dataset['Delivery_person_Age'] != 'NaN ')  & (dataset['multiple_deliveries'] != 'NaN ') 
& (dataset['Road_traffic_density'] != 'NaN ') & 
(dataset['Type_of_order'] != 'NaN ') & (dataset['City'] != 'NaN ')& (dataset['Festival'] != 'NaN ') )
dataset = dataset.loc[filtro, :]
# Convertendo tipo dos dados
dataset['Delivery_person_Age'] = dataset['Delivery_person_Age'].astype(int)
dataset['Delivery_person_Ratings'] = dataset['Delivery_person_Ratings'].astype(float)
dataset['multiple_deliveries'] = dataset['multiple_deliveries'].astype(int)

#transformação de data
dataset['Order_Date'] = pd.to_datetime(dataset['Order_Date'], format='%d-%m-%Y')

#transformando time_taken()
dataset['Time_taken(min)'] = dataset['Time_taken(min)'].apply(lambda x: x.split()[1])
dataset['Time_taken(min)'] = dataset['Time_taken(min)'].astype(int)

#retirando espaços
dataset['Festival'] = dataset['Festival'].str.strip()
dataset['ID'] = dataset['ID'].str.strip()
dataset['Weatherconditions'] = dataset['Weatherconditions'].str.strip()
dataset['Road_traffic_density'] = dataset['Road_traffic_density'].str.strip()
dataset['Type_of_order'] = dataset['Type_of_order'].str.strip()
dataset['Type_of_vehicle'] = dataset['Type_of_vehicle'].str.strip()
dataset['City'] = dataset['City'].str.strip()

#-------------------
# SIDEBAR STREAMLIT
#-------------------

st.sidebar.markdown('# Visão - Entregadores')
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('''-----------''')


filtro_data = st.sidebar.slider('Selecione o período',
                value=pd.datetime(2022, 4, 13),
                max_value=pd.datetime(2022,2 , 11),
                min_value=pd.datetime(2022,4,6), format='DD/MM/YY')

filtro_trafego = st.sidebar.multiselect('Selecione o tipo de Tráfego',
                                        ['Low', 'Medium','High', 'Jam'],
                                        default=['Low', 'Medium','High', 'Jam'])

filtro_cidade = st.sidebar.multiselect('Selecione sua cidade',['Urban', 'Semi-Urban', 'Metropolitian'] ,
                                     default= ['Urban', 'Semi-Urban', 'Metropolitian'])
st.markdown('''---------''')


#-------------------
# FILTRO SIDEBAR 
#-------------------

dataset = dataset.loc[dataset['Order_Date'] < filtro_data, :]
dataset = dataset.loc[dataset['Road_traffic_density'].isin(filtro_trafego), : ]
dataset = dataset.loc[dataset['City'].isin(filtro_cidade), :]
#-------------------
# LAYOUT STREAMLIT 
#-------------------

tab1 = st.tabs(['Visão Gerencial'])


with st.container():
    col1, col2, col3, col4 = st.columns(4, gap='small')
    with col1:
        age_max = dataset['Delivery_person_Age'].max()
        col1.metric('Maior idade',age_max)

    with col2:
        age_min = dataset['Delivery_person_Age'].min()
        col2.metric('Menor idade',age_min)
    with col3:
        worst_condition = dataset['Vehicle_condition'].min()
        col3.metric('Pior condição',worst_condition)
       

    with col4:
        best_condition = dataset['Vehicle_condition'].max()
        col4.metric('Melhor condição',best_condition)
with st.container():
    col1, col2 = st.columns(2, gap='small')
    with col1:
        st.markdown('### Média das avaliações Entregador')
        df1 = dataset.loc[:,['Delivery_person_Ratings', 'Delivery_person_ID']].groupby(['Delivery_person_ID']).mean().reset_index()
        st.dataframe(df1)

    with col2:
        st.markdown('### Média das avaliações - Tráfego')
        df1 = (dataset.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby([ 'Road_traffic_density'])
                                                                            .agg({'Delivery_person_Ratings': ['mean', 'std']}))
        df1.columns = ['avg_traffic', 'std_traffic']
        df1 = df1.reset_index()

        st.dataframe(df1)

        st.markdown('### Média das avaliações - Clima')
        df1 = dataset.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby(['Weatherconditions']).agg({'Delivery_person_Ratings': ['mean', 'std']})

        df1.columns = ['avg_conditions', 'std_conditions']

        df1 =df1.reset_index()
        st.dataframe(df1)
    with st.container():
        col1 , col2 = st.columns(2, gap='Medium')

        with col1:
            st.markdown('### Top 10 Entregadores mais Rápidos')
            df1 = dataset.loc[:, ['Time_taken(min)', 'Delivery_person_ID','City']].groupby(['Delivery_person_ID','City']).mean().sort_values('Time_taken(min)', ascending=True).reset_index().head(10)
            st.dataframe(df1)
            
        with col2:
            st.markdown('### Top 10 Entregadores mais Lentos')
            df1 = dataset.loc[:, ['Time_taken(min)', 'Delivery_person_ID','City']].groupby(['Delivery_person_ID','City']).mean().sort_values('Time_taken(min)', ascending=False).reset_index().head(10)
            st.dataframe(df1)
    

