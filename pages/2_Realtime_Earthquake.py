import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium as sl_folium
from config import SQES_Config as config_
import datetime

config_.page_config("Realtime Earthquake")  

if not 'df_event' in locals():
    st.session_state.gdf_event = None

# @st.cache_data
def get_event_data() -> pd.DataFrame:
    return pd.read_xml(config_.dataset_url)

def gdf_event_maker(df):
    st.session_state.gdf_event = gpd.GeoDataFrame(df, 
                                            geometry=gpd.points_from_xy(df.bujur, df.lintang),crs="EPSG:4326")
    
def datetime_convert(str):
    return(datetime.datetime.strptime(str, config_.datetime_convert_rules))

### map init
df_event = get_event_data()
gdf_event_maker(df_event)
map_center = [-2.3723687086440504, 119.75584725102497]
zoom_start = 4.5
m = folium.Map(location=map_center, zoom_start=zoom_start)

popup = folium.GeoJsonPopup(
    fields = df_event.columns.tolist(),
    localize=True,
    labels=True
)

tooltip = folium.GeoJsonTooltip(
    fields=["eventid", "dalam", "mag"],
    aliases=["Event ID", "Depth", "Magnitude"],
    localize=True,
    sticky=False,
    labels=True,
    max_width=1000,
)

g = folium.GeoJson(
    st.session_state.gdf_event,
    tooltip=tooltip,
    popup=popup,
    marker=folium.Circle(radius=10000, fill_color="red", fill_opacity=0.4, color="black", weight=1)
).add_to(m)

st.subheader("Last 200 Earthquake From InaTEWS")
col1, col2 = st.columns([0.7,0.3])
with col1:
    map_render = sl_folium(
        m,
        center=map_center,
        zoom=zoom_start,
        key="new",
        height=600,
        width=1200,
    ) 
with col2:
    try:
        map_render["last_active_drawing"]["properties"]
        x = datetime_convert(map_render["last_active_drawing"]["properties"]["waktu"])
        x
    except:
        None
    
st.dataframe(df_event)

config_.page_footer()