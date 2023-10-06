import obspy 
from config import SQES_Config as config_
from obspy import read, read_inventory, UTCDateTime
from obspy.signal import PPSD
from obspy.imaging.cm import pqlx
from obspy.clients.fdsn import Client
import datetime
import pandas as pd
import os
import calendar
import numpy as np
import streamlit as st

class sqes_visualization():
    
    url_ = st.secrets.FDSNclient.url
    usr_ = st.secrets.FDSNclient.username
    pass_ = st.secrets.FDSNclient.password
    client = Client(url_,user=usr_,password=pass_)

    def get_station_metadata(station_code):
        if not os.path.exists(f"{config_.station_metadata_path}/{station_code}.xml"):
            sqes_visualization.client.get_stations(
                network="IA",
                station=str(station_code),
                loc="*",
                level="response",
                filename=f"{config_.station_metadata_path}/{station_code}.xml"
            )
        else:
            print(f"{config_.station_metadata_path}/{station_code}.xml exist!")
            
    def get_station_waveform(station_code, starttime, endtime=None):
        t1 = UTCDateTime(starttime.isoformat())
        t2 = None
        fname = None
        
        if not endtime is None:
            t2 = UTCDateTime(endtime.isoformat())
            fname = f"{station_code}-{starttime.strftime(config_.timecode)}-{endtime.strftime(config_.timecode)}"
        else:
            endtime = starttime + datetime.timedelta(days=1)
            t2 = UTCDateTime(endtime.isoformat())
        
        fname = f"{station_code}-{starttime.strftime(config_.timecode)}-{endtime.strftime(config_.timecode)}"

        if not os.path.exists(f"{config_.station_waveform_path}/{fname}.mseed"):
            st = sqes_visualization.client.get_waveforms(
                network="IA",
                station=str(station_code),
                location="*",
                channel="???",
                starttime=t1,
                endtime=t2,
            )
            st.write(f"{config_.station_waveform_path}/{fname}.mseed", format="MSEED") 
            st.plot(outfile=f"{config_.station_waveform_image_path}/{fname}.png")
        else:
            print(f"{config_.station_waveform_image_path}/{fname}.mseed exist!")

    def get_event(date):
        df = pd.DataFrame(columns=['eventid','lat','lon','depth','mag','origin_time','evaluation_status','area'])
        
        if datetime.datetime.now() >= datetime.datetime.combine(datetime.date(date.year,date.month,calendar.monthrange(date.year,date.month)[1]),datetime.time(23,59,59,999999)):
            t1 = UTCDateTime(datetime.datetime.combine(datetime.date(date.year,date.month,1),datetime.time(0,0,0,00000)))
            t2 = UTCDateTime(datetime.datetime.combine(datetime.date(date.year,date.month,calendar.monthrange(date.year,date.month)[1]),datetime.time(23,59,59,999999)))
            fname=f"{config_.event_metadata_path}/{t1.strftime(config_.event_timecode)}.csv"
        else:
            t1 = UTCDateTime(datetime.datetime.combine(datetime.date(date.year,date.month,1),datetime.time(0,0,0,00000)))
            t2 = UTCDateTime(datetime.datetime.now())
            fname=f"{config_.event_metadata_path}/{t1.strftime(config_.event_timecode)}_uncomplete.csv" 
            
        catalog = sqes_visualization.client.get_events(t1,t2)
    
        for event in catalog:
            event_dict = {
                "eventid" : event.resource_id.id.split('/')[-1],
                "lat" : event.origins[0].latitude,
                "lon" : event.origins[0].longitude,
                "depth" : event.origins[0].depth / 1000,
                "mag" : event.magnitudes[0].mag if len(event.magnitudes) > 0 else np.nan,
                "origin_time" : event.origins[0].time.strftime(config_.datetime_convert_rules),
                "evaluation_status" : event.origins[0].evaluation_status,
                "area" : event.event_descriptions[0].text
            }
            
            df = pd.concat([df, pd.DataFrame([event_dict])], ignore_index=True)
        
        df.to_csv(fname, index=False)
    
    def run_ppsd(station_waveform, station_metadata,filename):
        st = read(station_waveform)
        inv = read_inventory(station_metadata)
        
        # PSD processing
        ppsd = PPSD(st[0].stats,metadata=inv,ppsd_length=600,period_limits=(0.02,100))
        ppsd.add(st)
        ppsd.plot(f"{config_.station_psd_image_path}/{filename}.png",cmap=pqlx)
        