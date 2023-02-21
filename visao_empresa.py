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

st.sidebar.markdown('# Marktplace - Visão Empresa')

st.sidebar.markdown('# Cury Company')

st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown('''--- ''')


filtro_data = st.sidebar.slider('Selecione o período',
    value=pd.datetime(2022, 4, 13),
    min_value = pd.datetime(2022,2 , 11),
    max_value = pd.datetime(2022,4,6),
    format = ('DD/MM/YYYY'))

filtro_trafego = st.sidebar.multiselect('Selecione o tipo de Tráfego', ['Low', 'Medium','High', 'Jam'] ,
                                        default = ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown('''--- ''')

#-------------------
# FILTROS SIDEBAR
#-------------------

dataset = dataset.loc[dataset['Order_Date'] < filtro_data, : ]
dataset = dataset.loc[dataset['Road_traffic_density'].isin(filtro_trafego)]

#-------------------
# LAYOUT STREAMLIT
#-------------------

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])


with tab1:
    with st.container():
        st.markdown('# Número de pedidos por dia')
        df1 = dataset.loc[: , ['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
        fig = px.bar(df1, x='Order_Date', y='ID')
        st.plotly_chart(fig)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:    
            st.markdown('#### Distribuição dos pedidos por tipo de tráfego')
            df1 = dataset.loc[:, ['ID', 'Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index()

            df1['%']= df1['ID'] / df1['ID'].sum()

            fig = px.pie(df1, values='%', names='Road_traffic_density')
            st.plotly_chart(fig, use_container_width = True)
        with col2:
            st.markdown('#### Distribuição dos pedidos por cidade e tipo de tráfego')
            df1 = dataset.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()


            fig = px.scatter(df1, x='City', y='Road_traffic_density', size='ID', color = 'City')
            st.plotly_chart(fig, use_container_width = False)
            
with tab2:
    with st.container():
        st.markdown('# Distribuição de pedidos por semana')
        dataset['week'] = dataset['Order_Date'].dt.strftime('%U')
        df1 = dataset.loc[:, ['ID', 'week']].groupby(['week']).count().reset_index()
        fig = px.line(df1, x='week', y='ID')
        st.plotly_chart(fig)

    with st.container():
        st.markdown('# Distruição de pedidos por pessoa por semana')
        df1 = dataset.loc[:, ['ID', 'week']].groupby(['week']).count().reset_index()
        df2 = dataset.loc[:,['Delivery_person_ID','week']].groupby(['week']).nunique().reset_index()

        df_aux = pd.merge(df1, df2, how='inner')
        df_aux['%'] = df_aux['ID'] / df_aux['Delivery_person_ID']
        fig = px.line(df_aux, x='week', y='%')
        st.plotly_chart(fig)

with tab3:
    with st.container():
        st.markdown('# Distribuição geográfica dos pedidos')
        cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude','Road_traffic_density', 'City']
        df1 = dataset.loc[:, cols].groupby(['City','Road_traffic_density']).mean().reset_index()
        map = folium.Map()

        for index, location in df1.iterrows():
            folium.Marker([location['Restaurant_latitude'], 
                        location['Restaurant_longitude']],
                        popup=location[['City','Road_traffic_density']]).add_to(map)

        folium_static(map, width=1024, height=600)