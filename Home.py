import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Home',
)

st.header('Marktplace - Visão Restaurantes')

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown('''--- ''')

st.write('# Curry Company Growth Dashboard')

st.markdown(
'''
Growth Dashboard foi contruído para acompanhar as métricas de crescimento dos Restaurantes e Entregadores.
## Como utilizar este Dashboard?

- Visão Empresa:
    - Visão Gerencial: Métricas gerais de comportamento.
    - Visão Tática: Indicadores semanais e diários de crescimento.
    - Visão Geográfica - Insights gerais de geolocalização.
- Visão Entregadores:
    - Acompanhamento dos indicadores semanais de crescimento.
- Visão Resturantes:
    - Indicadores semanais de crescimento dos Restaurantes.

### Ask for Help:
    - Time da Datascience

''')