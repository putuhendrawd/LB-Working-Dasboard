import streamlit as st
from streamlit_folium import st_folium as sl_folium
import folium
import streamlit.components.v1 as components
import pandas as pd
import geopandas as gpd
from config import SQES_Config as config_
import datetime
from PIL import Image
import os
from src.sqes_visualization import sqes_visualization

config_.page_config("SQES Visualization")  
 
# "sl station_state object:", st.session_state

### init
if 'df_caller' not in st.session_state:
    st.session_state.df_caller = False
    st.session_state.gdf = None
    st.session_state.df_event_caller = False
    st.session_state.df_event = None
    st.session_state.gdf_event = None
    st.session_state.gdf_station_filter = st.session_state.gdf
    st.session_state.csv_metadata = None
    st.session_state.data_quality_dominant_options = None
    st.session_state.data_quality_dominant_multiselect = None
    st.session_state.site_quality_options = None
    st.session_state.site_quality_multiselect = None
    st.session_state.station_options = None
    st.session_state.datetime_input_start = None
    st.session_state.datetime_input_end = None

if 'df_visit_status' not in st.session_state:
    st.session_state.df_visit_status = pd.read_csv(config_.visit_data, delimiter=";")
    st.session_state.visit_status_options = ['Visited', 'Not Visited', 'All']
    st.session_state.visit_status_selectbox = 'All'

## callbacks
### upload callbacks
def upload_cb():
    st.session_state.df_caller = True
    st.session_state.csv_metadata = st.session_state.upload_metadata
    read_data(st.session_state.upload_metadata,";")

def datetime_maker_cb(date,time):
    dt = datetime.datetime.combine(date,time)   
    return dt

### read data
@st.cache_data
def read_data(df,sep=","):
    st.session_state.df = pd.read_csv(df, delimiter=sep)
    # st.session_state.df.replace(np.nan,'---',inplace=True)
    st.session_state.data_quality_dominant_options = st.session_state.df.data_quality_dominant.unique().tolist()
    st.session_state.site_quality_options = st.session_state.df.site_quality.unique().tolist()
    st.session_state.station_options = st.session_state.df.kode_sensor.tolist()
    gdf_maker(st.session_state.df)
    st.session_state.filtered_df = st.session_state.df.copy()

def gdf_maker(df):
    st.session_state.gdf = gpd.GeoDataFrame(df, 
                                            geometry=gpd.points_from_xy(df.lon_sensor, df.lat_sensor),crs="EPSG:4326")

def gdf_event_maker(df):
    st.session_state.gdf_event = gpd.GeoDataFrame(df, 
                                            geometry=gpd.points_from_xy(df.lon, df.lat),crs="EPSG:4326")

def gdf_station_filter():
    st.session_state.gdf_station_filter = st.session_state.gdf[st.session_state.gdf['kode_sensor'] == str(st.session_state.select_station_waveform) ]

def filter_df():
    if len(st.session_state.site_quality_multiselect) == 0:
        sqv_ = st.session_state.site_quality_options
    else:
        sqv_ = st.session_state.site_quality_multiselect
    if len(st.session_state.data_quality_dominant_multiselect) == 0:
        dqdv_ = st.session_state.data_quality_dominant_options
    else:
        dqdv_ = st.session_state.data_quality_dominant_multiselect
    
    if ~((len(st.session_state.data_quality_dominant_multiselect) == 0) and (len(st.session_state.site_quality_multiselect) == 0)):
        filtered_df = st.session_state.filtered_df
        filtered_df = filtered_df[(filtered_df['site_quality'].isin(sqv_)) & (filtered_df['data_quality_dominant'].isin(dqdv_))]
        st.session_state.filtered_df = filtered_df
    else:
        reset_filter_df()

    if ~(st.session_state.visit_status_selectbox == 'All'):
        if st.session_state.visit_status_selectbox == 'Visited':
            filtered_df = st.session_state.filtered_df
            filtered_df = filtered_df[filtered_df['kode_sensor'].isin(st.session_state.df_visit_status.Stasiun)]
            st.session_state.filtered_df = filtered_df
        else:
            filtered_df = st.session_state.filtered_df
            filtered_df = filtered_df[~filtered_df['kode_sensor'].isin(st.session_state.df_visit_status.Stasiun)]
            st.session_state.filtered_df = filtered_df 
    
    gdf_maker(st.session_state.filtered_df)
             
def reset_filter_df():
    st.session_state.filtered_df = st.session_state.df
    gdf_maker(st.session_state.filtered_df)

def datetime_convert(str):
    return(datetime.datetime.strptime(str, config_.datetime_convert_rules))

def datetime_convert(str):
    return(datetime.datetime.strptime(str, config_.datetime_convert_rules))

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

### map init
map_center = [-2.3723687086440504, 115.75584725102497]
zoom_start = 4.5
m = folium.Map(location=map_center, zoom_start=zoom_start)
m_waveform = folium.Map(location=map_center, zoom_start=zoom_start)

if st.session_state.gdf is not None:
    
    popup = folium.GeoJsonPopup(
        fields=st.session_state.df.columns.tolist(),
        localize=True,
        labels=True
    )
    
    tooltip = folium.GeoJsonTooltip(
        fields=["kode_sensor", "lokasi_sensor" ,"site_quality", "data_quality_dominant"],
        aliases=["Stasiun", "Detail", "Site Quality", "Dominant Data Quality"],
        localize=True,
        sticky=False,
        labels=True,
        max_width=800,
    )
    
    g = folium.GeoJson(
        st.session_state.gdf,
        tooltip=tooltip,
        popup=popup
        # marker=folium.Marker(icon=folium.plugins.BeautifyIcon(icon_shape="circle-dot", color="red"))
    ).add_to(m)
    
# main

tab1, tab2, tab3 = st.tabs(["Data Visualization and Filtering", "Station Details", "Earthquake Waveform"])
with tab1:
    side, main = st.columns([0.3,0.7],gap="medium")
    # SIDEBAR
    with side:
        st.subheader("Controls")
        if st.session_state.df_caller:
            st.info(f"Data {st.session_state.csv_metadata.name} Loaded")
            st.subheader("Filters")
            st.session_state.site_quality_multiselect = st.multiselect("Site Quality Value", st.session_state.site_quality_options)
            st.session_state.data_quality_dominant_multiselect = st.multiselect("Data Quality Dominant Value", st.session_state.data_quality_dominant_options)
            st.session_state.visit_status_selectbox = st.selectbox("Visit Status Value", st.session_state.visit_status_options, index=2)
            run, reset = st.columns(2)
            run.button("Run",on_click=filter_df, use_container_width=True)
            reset.button("Reset", on_click=reset_filter_df, use_container_width=True)
        else:
            st.info("Upload Here!")
            st.file_uploader("Choose a file",type="csv",label_visibility="collapsed", on_change=upload_cb, key="upload_metadata")
    
    # MAIN WINDOW   
    with main:
        # css='''
        # <style>
        #     section.main>div {
        #         padding-bottom: 0rem;
        #         overflow: off;
        #     }
        #     [data-testid="column"] {
        #         overflow: auto;
        #         height: 100vh;
        #     }
        # </style>
        # '''
        # st.markdown(css, unsafe_allow_html=True)
        
        if st.session_state.df_caller:
            st.subheader("Map")
            map_render = sl_folium(
                m,
                center=map_center,
                zoom=zoom_start,
                key="new",
                height=500,
                width=900,
            ) 
            st.subheader("Data")

            st.text(f"data length: {len(st.session_state.filtered_df)} rows")
            st.dataframe(st.session_state.filtered_df, hide_index=True, width=900, height=500)
            csv = convert_df(st.session_state.filtered_df)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name='filter_df.csv',
                mime='text/csv',
            )
        else:
            st.subheader("Data")
            st.warning("No data loaded, click on the sample dataset button to load a sample dataset, or upload a file.")
with tab2:
        col1, col2 = st.columns([0.3,0.7])
        if st.session_state.df_caller:
            with col1:
                st.subheader("Station Detail")
                st.selectbox("Select station", st.session_state.station_options, key='select_station')
                col11, col12 = st.columns(2)
                col11.date_input("Select Start Date", datetime.datetime.now()+datetime.timedelta(days=-2), key="date_input_start")
                col12.time_input("Specify Start Time", datetime.time(0,0,0,0), key="time_input_start")
                col11.date_input("Select End Date", datetime.datetime.now()+datetime.timedelta(days=-1), key="date_input_end")           
                col12.time_input("Specify End Time", datetime.time(23,59,59,0), key="time_input_end")
                st.session_state.datetime_input_start = datetime_maker_cb(st.session_state.date_input_start, st.session_state.time_input_start)
                st.session_state.datetime_input_end = datetime_maker_cb(st.session_state.date_input_end, st.session_state.time_input_end)
                st.button("Retrieve Data", key='retrieve_data')
            
            with col2:
                st.subheader("Waveform Data")
                if st.session_state.retrieve_data:
                    fname = f"{st.session_state.select_station}-{st.session_state.datetime_input_start.strftime(config_.timecode)}-{st.session_state.datetime_input_end.strftime(config_.timecode)}"
                    if not os.path.exists(f"{config_.station_waveform_image_path}/{fname}.png"):
                        with st.spinner("downloading data"):
                            sqes_visualization.get_station_waveform(st.session_state.select_station,st.session_state.datetime_input_start,st.session_state.datetime_input_end)
                            sqes_visualization.get_station_metadata(st.session_state.select_station)
                        image = Image.open(f"{config_.station_waveform_image_path}/{fname}.png")             
                        st.image(image)
                    else:
                        image = Image.open(f"{config_.station_waveform_image_path}/{fname}.png")
                        st.image(image)
                
                else:
                    st.warning("Retrieve data first!")
                st.subheader("PSD Data")
                if st.session_state.retrieve_data:
                    fname = f"{st.session_state.select_station}-{st.session_state.datetime_input_start.strftime(config_.timecode)}-{st.session_state.datetime_input_end.strftime(config_.timecode)}"
                    if not os.path.exists(f"{config_.station_psd_image_path}/{fname}.png"):
                        with st.spinner("downloading data"):
                            sqes_visualization.run_ppsd(f"{config_.station_waveform_path}/{fname}.mseed",f"{config_.station_metadata_path}/{st.session_state.select_station}.xml",fname)
                        image = Image.open(f"{config_.station_psd_image_path}/{fname}.png")             
                        st.image(image)
                    else:
                        image = Image.open(f"{config_.station_psd_image_path}/{fname}.png")
                        st.image(image)
                
                else:
                    st.warning("Retrieve data first!")
                st.subheader("HVSR Data")
                st.warning("Under Development")
        else:
            st.warning("Please upload data first!")
        
with tab3:
        if st.session_state.df_caller:
            show_waveform = False
            ev_date = st.date_input("Select Earthquake Data Range (only year and month input valid)", value="today",min_value=datetime.datetime(2009,1,1,0,0,0,0),max_value=datetime.datetime.now()-datetime.timedelta(days=-1))
            st.toggle("Show Datatable", key='show_datatable')
            if not os.path.exists(f"{config_.event_metadata_path}/{ev_date.strftime(config_.event_timecode)}.csv"):
                if not st.session_state.df_event_caller:
                    with st.spinner("downloading data"):
                        sqes_visualization.get_event(ev_date)
                try:
                    df_event = pd.read_csv(f"{config_.event_metadata_path}/{ev_date.strftime(config_.event_timecode)}.csv")
                except:
                    df_event = pd.read_csv(f"{config_.event_metadata_path}/{ev_date.strftime(config_.event_timecode)}_uncomplete.csv")
                gdf_event_maker(df_event)
                st.session_state.df_event_caller = True
            else:
                df_event = pd.read_csv(f"{config_.event_metadata_path}/{ev_date.strftime(config_.event_timecode)}.csv")
                gdf_event_maker(df_event)
            
            if st.session_state.gdf_event is not None:
                popup_ev = folium.GeoJsonPopup(
                    fields=df_event.columns.tolist(),
                    localize=True,
                    labels=True
                )
                
                tooltip_ev = folium.GeoJsonTooltip(
                    fields=["eventid", "depth", "mag"],
                    aliases=["Event ID", "Depth", "Magnitude"],
                    localize=True,
                    sticky=False,
                    labels=True,
                    max_width=800,
                )
                
                g_ev = folium.GeoJson(
                    st.session_state.gdf_event,
                    tooltip=tooltip_ev,
                    popup=popup_ev,
                    marker=folium.Circle(radius=10000, fill_color="red", fill_opacity=0.4, color="black", weight=1)
                ).add_to(m_waveform)
                
                if st.session_state.gdf_station_filter is not None:
                    s = folium.GeoJson(
                        st.session_state.gdf_station_filter,
                        tooltip=tooltip,
                        popup=popup
                    ).add_to(m_waveform)
            
            col1, col2 = st.columns([0.7,0.3])
            with col1:
                if st.session_state.show_datatable:
                    st.dataframe(df_event)
                    
                map_render = sl_folium(
                    m_waveform,
                    center=map_center,
                    zoom=zoom_start,
                    key="new",
                    height=500,
                    width=900,
                ) 
            with col2:
                st.subheader("Select Station")
                st.selectbox("Select station", st.session_state.station_options, key='select_station_waveform',on_change=gdf_station_filter, label_visibility="collapsed")
                st.subheader("Selected Events")
                try:
                    map_render["last_active_drawing"]["properties"]
                    waveform_time_start = datetime_convert(map_render["last_active_drawing"]["properties"]["origin_time"])
                    waveform_time_end = waveform_time_start+datetime.timedelta(minutes=5)
                except:
                    None
                st.button("Retrieve Data", key='retrieve_station_waveform_by_event')
            
            if st.session_state.retrieve_station_waveform_by_event:
                st.subheader(f"{st.session_state.select_station_waveform} Waveform on {map_render['last_active_drawing']['properties']['eventid']}")
                fname = f"{st.session_state.select_station_waveform}-{waveform_time_start.strftime(config_.timecode)}-{waveform_time_end.strftime(config_.timecode)}"
                if not os.path.exists(f"{config_.station_waveform_image_path}/{fname}.png"):
                    with st.spinner("downloading data"):
                        sqes_visualization.get_station_waveform(st.session_state.select_station_waveform,waveform_time_start,waveform_time_end)
                    image = Image.open(f"{config_.station_waveform_image_path}/{fname}.png")             
                    st.image(image)
                else:
                    image = Image.open(f"{config_.station_waveform_image_path}/{fname}.png")
                    st.image(image)
        else:
            st.warning("Please upload data first!")
    
config_.page_footer()