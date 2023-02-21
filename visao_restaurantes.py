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
    col1, col2, col3 = st.columns(3, gap='small')
    with col1:
        df1 = dataset['Delivery_person_ID'].nunique()
        col1.metric('Entregadores uni.', df1)
    with col2:
        df1 = dataset.loc[:, ['Time_taken(min)', 'Festival']].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']})
        df1.columns = ['avg_time', 'std_time']
        df1 = df1.reset_index()
        yes_festival = df1.loc[df1['Festival'] == 'Yes', 'avg_time']
        col2.metric('Tempo médio - Festival',np.round(yes_festival),2)
    with col3:
        df1 = dataset.loc[:, ['Time_taken(min)', 'Festival']].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']})
        df1.columns = ['avg_time', 'std_time']
        df1 = df1.reset_index()
        yes_festival = df1.loc[df1['Festival'] == 'No', 'avg_time']
        col3.metric('Tempo médio sem Festival',np.round(yes_festival),2)

with st.container():
    st.markdown('### Distribuição de entrega por cidade')
    df1 = dataset.loc[:, ['Time_taken(min)', 'City']].groupby(['City']).agg({'Time_taken(min)': ['mean', 'std']})
    df1.columns = ['avg_time_delivery', 'std_time_delivery']
    df1 = df1.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Control',
        x=df1['City'],
        y=df1['avg_time_delivery'],
        error_y = dict(type='data', array=df1['std_time_delivery']
                    )

    )
                )

    fig.update_layout(barmode='group')

    st.plotly_chart(fig, use_container_width=True)
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        cols = ['Restaurant_latitude','Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude', 'City']
        df1 = dataset.loc[:, cols]
        df1['distance(km)'] = df1.loc[:, cols].apply(lambda x: np.round(haversine(
                                            (x['Restaurant_latitude'], x['Restaurant_longitude'])
                                            ,(x['Delivery_location_latitude'], x['Delivery_location_longitude'])
                                            ),2), axis=1
                                            )
        avg_distance = df1.loc[:, ['distance(km)', 'City']].groupby(['City']).mean().reset_index()
        fig = px.pie(avg_distance, values='distance(km)', names='City', width=350)
        col1.plotly_chart(fig, use_container_with=True,)


    with col2:
        df1 = dataset.loc[: , ['Time_taken(min)', 'City','Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})

        df1.columns = ['avg_time', 'std_time']
        df1 = df1.reset_index()

        fig = px.sunburst(df1, path=['City', 'Road_traffic_density'], values='avg_time',
                        color='std_time', width=400,color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df1['std_time']))


        col2.plotly_chart(fig, use_container_with=False)
with st.container():
    st.markdown('### Tempo médio e desvio padrão por cidade e tipo de pedido')

    df1 = dataset.loc[: , ['Time_taken(min)', 'City','Type_of_order']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})

    df1.columns = ['avg_time', 'std_time']
    df1 = df1.reset_index()
    st.dataframe(df1)