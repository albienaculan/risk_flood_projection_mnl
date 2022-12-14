import streamlit as st
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from shapely import wkt
from shapely.geometry import Point, Polygon, LineString
import osmnx as ox
import shapely
import pyproj
import warnings
import folium
warnings.filterwarnings('ignore', category=DeprecationWarning)
import networkx as nx
my_google_elevation_api_key = 'AIzaSyAm9P27yqhOB4wedLCpHFiDq52-KaiTgUE' 
import networkx as nx
import numpy as np
import osmnx as ox
import geopandas as gpd
import pandas as pd
from streamlit_folium import st_folium
import calplot


ox.config(log_console=True, use_cache=True)
ox.__version__


# st.set_page_config(page_title="Manila Risk Precipitation")

with st.container():
    st.subheader("Precipitation for 2023")

    forecast = pd.read_csv('forecast_with_date.csv')
    forecast['date'] = pd.to_datetime(forecast['date'], yearfirst=True)
    forecast.set_index('date', inplace=True)

    col = 'Point.Forecast'
    fig,x = calplot.calplot(forecast[col], how='sum')
    st.pyplot(fig)
# next section

with st.container():
    # Data

    fp = "manila_data.shp"

    ph_gdf = gpd.read_file(fp)
    manila_total_population = gpd.GeoDataFrame(ph_gdf, geometry = gpd.points_from_xy(ph_gdf.lon, ph_gdf.lat), crs='4326')
    # st.write(manila_total_population.head())
    # ph_gdf.set_geometry("Geometry", crs='4326', inplace=True)
    
    # Get Manila Boundaries of Districts:

    fp1 = "manila_district_data.shp"
    mnl_dstrct_gdf = gpd.read_file(fp1)
    df = gpd.GeoDataFrame(mnl_dstrct_gdf, geometry = 'geometry', crs='4326')
    # st.write(manila_district_data)

    m = folium.Map(location=[14.5995, 120.9842], zoom_start=13, tiles='CartoDB positron')

    
    for _, r in df.iterrows():
        # Without simplifying the representation of each borough,
        # the map might not be displayed
        print(r)
        sim_geo = gpd.GeoSeries(r['geometry']).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j,
                           style_function=lambda x: {'fillColor': 'orange'})
        folium.Popup(r['District']).add_to(geo_j)
        geo_j.add_to(m)
        # geometry (active) column
    # df = gpd.GeoDataFrame(df, geometry = gpd.points_from_xy(mnl_dstrct_gdf.lon, mnl_dstrct_gdf.lat, crs="EPSG:4326"))
    df['centroid'] = df.centroid

    # st.write(df)
    for _, r in df.iterrows():
        lat = r['centroid'].y
        lon = r['centroid'].x
        folium.Marker(location=[lat, lon],
                  popup='District: {} <br> Total Labor Economic Damage: {}'.format(r['District'], r['Damage'])).add_to(m)
    
    st_data = st_folium(m, width=1000)
    
    
    