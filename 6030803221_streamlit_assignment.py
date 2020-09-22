
#Streamlit Assignment
#6030803221 Kullaporn Kanoktipstaporn

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk
import folium as fo
from streamlit_folium import folium_static
import geopandas as gp

#ตั้งชื่อหัวข้อและคำอธิบายเพิ่มเติม
st.title("Streamlit Assignment by 6030803221_Kullaporn")
st.markdown(
"""
A demo of streamlit app. Use the slider
to choose a specific date and time. 
""")
#---------------------------------------------------------------------------------------------

#Select the date from imported data @github
clex_date = st.selectbox(
    'Date :' , ['20190101','20190102','20190103','20190104','20190105'])
if clex_date=='20190101':
    DATA_URL = ("https://raw.githubusercontent.com/Kullaporn/Updated_Streamlit/master/20190101.csv")
elif clex_date=='20190102':
    DATA_URL = ("https://raw.githubusercontent.com/Kullaporn/Updated_Streamlit/master/20190102.csv")
elif clex_date=='20190103':
    DATA_URL = ("https://raw.githubusercontent.com/Kullaporn/Updated_Streamlit/master/20190103.csv")
elif clex_date=='20190104':
    DATA_URL = ("https://raw.githubusercontent.com/Kullaporn/Updated_Streamlit/master/20190104.csv")
elif clex_date=='20190105':
    DATA_URL = ("https://raw.githubusercontent.com/Kullaporn/Updated_Streamlit/master/20190105.csv")
#----------------------------------------------------------------------------------------------------------------------------

#Import data
DATE_TIME = "timestart"
@st.cache(allow_output_mutation=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    data[DATE_TIME] = pd.to_datetime(data[DATE_TIME],format='%d/%m/%Y %H:%M')
    return data
data = load_data(100000)
#-----------------------------------------------------------------------------------------------------------------------------

#create slide bar for showing data
hour = st.slider("The choosen time to look", 0, 23, step=3)

data = data[data[DATE_TIME].dt.hour == hour]
#-----------------------------------------------------------------------------------------------------------------------------

# set geometry
crs = "EPSG:4326"
geometry = gp.points_from_xy(data.lonstartl,data.latstartl)
geo_df  = gp.GeoDataFrame(data,crs=crs,geometry=geometry)

#--------------------------------------------------------------------------------------------------

#Geo data
st.subheader("Geo data between %i:00 and %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data["latstartl"]), np.average(data["lonstartl"]))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data,
            get_position=["lonstartl", "latstartl"],
            radius=100,
            elevation_scale=4,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
        ),
    ],
))
#------------------------------------------------------------------------------------------------------------------------------

#Breakdown histogram
st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data[DATE_TIME].dt.hour >= hour) & (data[DATE_TIME].dt.hour < (hour + 1))
]
hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "pickups": hist})

st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
    ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("pickups:Q"),
        tooltip=['minute', 'pickups']
    ), use_container_width=True)
#------------------------------------------------------------------------------------------------------------------------------

#checkbox for showing raw data
if st.checkbox("Show raw data", False):
    st.subheader("Raw data by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))

#---------------------------------------------------------------------------------------------------------------------

#Create map
longitude = 100.523186
latitude = 13.736717

station_map = fo.Map(
	location = [latitude, longitude], 
	zoom_start = 10)

latitudes = list(data.latstartl)
longitudes = list(data.lonstartl)
date_time = list(data.timestart)
labels = list(data.no)

for lat, lon, t, label in zip(latitudes, longitudes, date_time, labels):
    if data.timestart[label].hour==hour and data.timestart[label].year!=2018:
        fo.Marker(
            location = [lat, lon], 
	    popup = [label,lat,lon,t],
	    icon = fo.Icon(color='blue')
	).add_to(station_map)

folium_static(station_map)
    
