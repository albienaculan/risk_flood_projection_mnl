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
from streamlit_folium import st_folium, folium_static
import calplot


ox.config(log_console=True, use_cache=True)
ox.__version__

"st.session_state object: ", st.session_state

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

    def getNearestEssentials(barangay, data):
        brgy_df = manila_total_population.loc[manila_total_population['Barangay'] == barangay]
        proj = pyproj.Transformer.from_crs(4326, 4326, always_xy=True)
        brgy_longitude = brgy_df["lon"] # note that this is the X coordinate
        brgy_latitude = brgy_df["lat"] # note that this is the Y coordinate
    
        x, y = proj.transform(brgy_longitude, brgy_latitude)
    
        brgy_point = Point(x, y)
    
        essential_places = ['marketplace_data', 'hospital_data', 'pharmacy_data', 'mall_data', 'supermarket_data']
    
        list_of_dataframes_of_essentials = []
        dictionary_of_essentials = {}
    
        for essential_place in essential_places:
            dat = data[essential_place]
            dat['distance_from_barangay'] = dat['geometry'].distance(brgy_point)
            minimum_distance = dat['distance_from_barangay'].min()
            answer = dat[dat["distance_from_barangay"] == minimum_distance]
            list_of_dataframes_of_essentials.append(answer)
            dictionary_of_essentials[essential_place.replace("_data","")] = answer['name'].item()
        
        dictionary_of_point = {}
        
        for i in range(len(list_of_dataframes_of_essentials)):
            x,y = list_of_dataframes_of_essentials[i]['lon'], list_of_dataframes_of_essentials[i]['lat']
            point = Point(x,y)
            dictionary_of_point["nearest_"+essential_places[i].replace("_data","")] = Point(x,y)
        
        return list_of_dataframes_of_essentials, dictionary_of_essentials, dictionary_of_point

    def shortest_path(origin, destination, network):
    
        if network == "drive":
            graph = ox.io.load_graphml(filepath=r'C:\Users\albie\OneDrive\Desktop\Flood_NOAH\MetroManila\Graph\Initial_Graph\MNL_street_graphs_drive.graphml')
        elif network == "bike":
            graph = ox.io.load_graphml(filepath=r'C:\Users\albie\OneDrive\Desktop\Flood_NOAH\MetroManila\Graph\Initial_Graph\MNL_street_graphs_bike.graphml')
        elif network == "walk":
            graph = ox.io.load_graphml(filepath=r'C:\Users\albie\OneDrive\Desktop\Flood_NOAH\MetroManila\Graph\Initial_Graph\MNL_street_graphs_walk.graphml')

        graph_proj = ox.project_graph(graph, to_crs="4326")
        
        # Get the edges as GeoDataFrame
        edges = ox.graph_to_gdfs(graph_proj, nodes=False)
        
        # Get CRS info UTM
        CRS = edges.crs

        # Reproject all data
        origin_proj = origin.to_crs(crs=CRS)
        destination_proj = destination.to_crs(crs=CRS)
        
        # routes of shortest path
        routes = gpd.GeoDataFrame()
        
        # Get nodes from the graph
        nodes = ox.graph_to_gdfs(graph_proj, edges=False)
    
        # Iterate over origins and destinations
        for oidx, orig in origin_proj.iterrows():
            # Find closest node from the graph → point = (latitude, longitude)
            closest_origin_node = ox.nearest_nodes(G=graph_proj, Y = orig.geometry.centroid.y, X = orig.geometry.centroid.x)
            # Iterate over targets
            for tidx, target in destination_proj.iterrows():
                # Find closest node from the graph → point = (latitude, longitude)
                closest_target_node = ox.nearest_nodes(graph_proj, Y = target.geometry.centroid.y, X = target.geometry.centroid.x)
                # Check if origin and target nodes are the same → if they are → skip
                if closest_origin_node == closest_target_node:
                    print("Same origin and destination node. Skipping ..")
                    continue
                    
                # Find the shortest path between the points
                route = nx.shortest_path(graph_proj, source=closest_origin_node, target=closest_target_node, weight="length")
                # Extract the nodes of the route
                route_nodes = nodes.loc[route]
                # Create a LineString out of the route
                path = LineString(list(route_nodes.geometry.values))
                # Append the result into the GeoDataFrame
                routes = routes.append([[path]], ignore_index=True)
                
        # Add a column name
        routes.columns = ["geometry"]
        
        # Set coordinate reference system
        routes.crs = nodes.crs
        
        # Set geometry
        routes = routes.set_geometry("geometry")
        
        return routes
    
    def plotEssentials(barangay, data, network):
        destinations, dictionary_of_essentials, dictionary_of_point = getNearestEssentials(barangay, data)
        
        origin = manila_total_population[manila_total_population["Barangay"] == barangay]
        origin.rename(columns={"Geometry": "geometry"}, inplace=True)
        origin.set_geometry("geometry", inplace=True)
        
        m = folium.Map(location=[origin.centroid.y, origin.centroid.x], zoom_start = 15)
    #     m.fit_bounds(m.get_bounds(), padding=(30, 30))
        amenity_color = {"marketplace": "yellow", "hospital": "red", "pharmacy": "blue", "mall": "purple", "supermarket":"green"}
        folium.Marker(location=[origin.centroid.y, origin.centroid.x]).add_to(m)
        
        for i in range(len(destinations)):
            linestring = shortest_path(origin, destinations[i], network).set_crs("4326")
            folium.Choropleth(linestring, line_weight=3, line_color=amenity_color[list(dictionary_of_essentials.keys())[i]]).add_to(m)
            folium.Marker(location=[destinations[i].centroid.y, destinations[i].centroid.x], popup=destinations[i]['name']).add_to(m)
            folium.Icon(color=amenity_color[list(dictionary_of_essentials.keys())[i]], icon='')
        return m

    place_query = {'city':'Manila','country':'Philippines'}
    amenity_MNL = ox.geometries.geometries_from_place(
        place_query, tags={"amenity": True})

    amenity_MNL = amenity_MNL.to_crs("epsg:4326")

    shop_MNL = ox.geometries.geometries_from_place(
        place_query, tags={"shop": True})

    shop_MNL = shop_MNL.to_crs("epsg:4326")

    def create_lat_long_column(data):
        data['lon'] = data.centroid.x
        data['lat'] = data.centroid.y
        
    create_lat_long_column(amenity_MNL), create_lat_long_column(shop_MNL)

    # palengke, mall, hospital, grocery, pharmacy

    essential_list = ["marketplace", "hospital", "pharmacy"]
    shop_list = ["mall", "supermarket"]

    essential_dict = {}
    shop_dict = {}

    for essential in essential_list:
        data = amenity_MNL[amenity_MNL["amenity"] == essential]
        essential_dict[essential + "_data"] = data[data["name"].notnull()]
        
    for shop in shop_list:
        data = shop_MNL[shop_MNL["shop"] == shop]
        shop_dict[shop + "_data"] = data[data["name"].notnull()]
        
    data = {**essential_dict, **shop_dict} #merge two data

    for key in list(data.keys()):
        data[key].set_geometry("geometry", inplace=True)

    barangay = st.text_input("Enter the barangay here: ", key="barangay")
    

    m1 = plotEssentials(barangay, data, "drive")
    
    if 'barangay' not in st.session_state:
        st.session_state.m1


    folium_static(m1)
    
        
        
        