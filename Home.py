import streamlit as st
from config import SQES_Config as config_
config_.page_config("Home")

# "sl station_state object:", st.session_state

st.title("Interactive Web App (dev)")

col1, col2 = st.columns(2,gap="medium")

with col1:
    st.image("assets/bmkg_puslitbang.png")

with col2:
    st.header("Introduction")
    st.markdown('''
        1. SQES Visualization Dashboard ---
            SQES Data Analysis Dashboard based on Streamlit | 
            Original SQES Website: <http://182.16.248.172/sensorbmkg>
        
        2. Realtime Earthquake ---
            Realtime Earthquake data plot based on InaTEWS BMKG
            Original InaTEWS BMKG Website: <https://inatews.bmkg.go.id/>
            
        This Web App is still in development More features will be added in the future. Click on the sidebar to see the other pages.\n
        
    ''')
st.divider()
st.markdown('''
    Putu Hendra Widyadharma - Pusat Penelitian dan Pengembangan @ 2023
''')

config_.page_footer()