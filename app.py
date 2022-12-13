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


ox.config(log_console=True, use_cache=True)
ox.__version__


# st.set_page_config(page_title="Manila Risk Precipitation")

with st.container():
    st.subheader("Problem")

# next section

with st.container():
    # Data

    fp = "manila_data.shp"

    ph_gdf = gpd.read_file(fp)
    manila_total_population = gpd.GeoDataFrame(ph_gdf, geometry = gpd.points_from_xy(ph_gdf.lon, ph_gdf.lat), crs='4326')
    st.write(manila_total_population.head())
    # ph_gdf.set_geometry("Geometry", crs='4326', inplace=True)
    
    # Get Manila Boundaries of Districts:

    fp1 = "manila_district_data.shp"
    mnl_dstrct_gdf = gpd.read_file(fp1)
    manila_district_data = gpd.GeoDataFrame(mnl_dstrct_gdf, geometry = gpd.points_from_xy(mnl_dstrct_gdf.lon, mnl_dstrct_gdf.lat), crs='4326')
    st.write(manila_district_data)