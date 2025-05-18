
# -*- coding: utf-8 -*-
"""
Created on Sun May  4 18:56:05 2025
Extract precipitation data from weatherbit

DSI-3260 File transfer protocol available through ftp://ftp.ncdc.noaa.gov/pub/data/15min_precip-3260/, 
documentation isfound within the server

The data set is retrieved through this public link https://www.ncei.noaa.gov/pub/data/hpd/auto/v2/beta/15min/ along
with documentation information https://www.ncei.noaa.gov/pub/data/hpd/auto/v2/beta/15min/readme.csv.txt

@author: ruchuan2
"""


import pandas as pd
import requests
import pytz
from io import StringIO
from timezonefinder import TimezoneFinder
from itertools import chain
import folium
url = "https://www.ncei.noaa.gov/pub/data/hpd/auto/v2/beta/15min/all_csv/"
response = requests.get(url)

weather_station = pd.read_csv(
    "C:/Users/ruchuan2/Box/latency_arbitrage/weather_station.xls")

stations = weather_station['StnID']
lons = weather_station['xlon']
lats = weather_station['ylat']

weather_data = []

for i in range(len(stations)):

    url = f"https://www.ncei.noaa.gov/pub/data/hpd/auto/v2/beta/15min/all_csv/{stations[i]}.15m.csv"

    response = requests.get(url)
    df = pd.read_csv(StringIO(response.text))

    # extract Val column

    df = df.filter(regex=r'(Val|DATE|STATION)')
    df.columns = list(
        chain(*[['STATION', 'DATE'], df.columns[2:].str.replace("Val", "").tolist()]))
    dates = pd.bdate_range('2018-08-01', '2019-12-31').strftime("%Y-%m-%d")
    df['DATE'] = df['DATE'].astype('str')
    df = df.loc[df['DATE'].isin(dates)]

    # melt the datset

    df = pd.melt(df, id_vars=['STATION', 'DATE'], value_vars=df.columns[2:],
                 var_name='timestamp', value_name='precipitation')

    # make timestamps

    df['timestamp'] = df['timestamp'].str.slice(
        0, 2) + ":" + df['timestamp'].str.slice(2, 4)
    df['timestamp'] = df['DATE'] + " " + df['timestamp']

    # identify the timezone
    time_zone = TimezoneFinder()
    localtime = time_zone.timezone_at(lng=lons[i], lat=lats[i])

    # local timestamps
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=False)
    df['timestamp'] = df['timestamp'].dt.tz_localize(localtime)
    df['timestamp'] = df['timestamp'].dt.tz_convert('America/New_York')

    # using dt.time function will solve all of your headaches
    market_open = pd.to_datetime('09:30').time()
    market_close = pd.to_datetime('16:00').time()

    df = df.loc[(df['timestamp'].dt.time >= market_open) & (
        df['timestamp'].dt.time <= market_close)].reset_index(drop=True)
    del df['DATE']

    # precipataion is hundreds of inch

    df['precipitation'] = df['precipitation']/100

    weather_data.append(df)

weather_data = pd.concat(weather_data)
weather_data.to_pickle(
    "C:/Users/ruchuan2/Box/latency_arbitrage/weather_data.pkl")

# mapping the weather stations

weather_data = pd.read_pickle(
    "C:/Users/ruchuan2/Box/latency_arbitrage/weather_data.pkl")

m = folium.Map(location=[41.0, -82.5], zoom_start=6, tiles="OpenStreetMap")

# Add markers
for name, lat, lon in stations:
    folium.Marker(
        location=[lat, lon],
        popup=name,
        tooltip=name,
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

# Save or display the map
m.save("weather_stations_map.html")
m  # Display in a Jupyter notebook
