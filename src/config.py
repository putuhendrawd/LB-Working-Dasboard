import streamlit as st

class SQES_Config():
    visit_data = "files/kunjungan_sqes.csv"
    station_metadata_path = "files/station_metadata"
    station_waveform_path = "files/station_waveform"
    station_waveform_image_path = "files/station_waveform_image"
    event_metadata_path = "files/event_metadata"
    station_psd_image_path = "files/station_psd_image"
    station_hvsr_image_path = "files/station_hvsr_image"
    timecode = "%d%m%y%H%M%S"
    event_timecode = "%B%Y"
    datetime_convert_rules="%Y/%m/%d %H:%M:%S.%f"
    dataset_url = st.secrets.earthquake_live_200event_url.url
    
    def page_config(title):
        st.set_page_config(
            page_title=title,
            page_icon="🧊",
            layout="wide",
            initial_sidebar_state="collapsed",
            menu_items={
                'About': "Interactive Web App Project @putuhendrawd"
            }
        )
    def page_footer():
        footer = """
        <style>
        footer{
            visibility:hidden;
        }
        footer:after{
            content:putu hendra widyadharma Puslitbang BMKG @ 2023 made with Streamlit;
            display:block;
            position:relative;
            color:tomato;
            padding:5px;
            top:3px;
        }
        </style>
        """
        st.markdown(footer, unsafe_allow_html=True)
        