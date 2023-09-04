import folium
import streamlit as st
from streamlit_folium import st_folium
from shapely.geometry import Point
import geopandas
import config 
from generate_circuit import circuit, N_NODES
from utils import shortest_path, generate_path
from network import get_frames

st.set_page_config(layout="wide")
ways = geopandas.read_file(config.roads_filepath)
nodes, _, rel = get_frames(ways)


m = nodes.explore(
    color="red",  
    marker_kwds=dict(radius=5, fill=True, name='node_id'),  
    tooltip="node_id",  
    tooltip_kwds=dict(labels=False), 
    zoom_control=False,
)


c1, c2 = st.columns([1, 3])

if 'origin' not in st.session_state :
    with c1:
        st.write("Select the origin on the map")

    with c2:
        st_data_origin = st_folium(m, width=725, key="origin", returned_objects=["last_object_clicked"])
           
    if st_data_origin["last_object_clicked"]:
        origin = Point(st_data_origin["last_object_clicked"]["lng"], st_data_origin["last_object_clicked"]["lat"])
        origin_node = nodes[nodes['geometry'] == origin]['node_id'].values[0]
        st.session_state['origin'] = origin
        st.write(f"Selected node is node number: {origin_node}")  
        st.experimental_rerun()

if 'origin' in st.session_state and 'destination' not in st.session_state:
    origin = st.session_state['origin']
    folium.Marker([origin.y, origin.x], popup="Origin", tooltip="Origin").add_to(m)    
    origin_node = nodes[nodes['geometry'] == origin]['node_id'].values[0]
    with c1:
        st.write(f"Selected origin is node number: {origin_node}")   
        st.write("Select the destination on the map")         
    with c2:
        st_data_destination = st_folium(m, width=725, key="destination", returned_objects=["last_object_clicked"])
        
    if st_data_destination["last_object_clicked"]:
        destination = Point(st_data_destination["last_object_clicked"]["lng"], st_data_destination["last_object_clicked"]["lat"])
        st.session_state['destination'] = destination
        st.write(st_data_destination["last_object_clicked"])
        st.experimental_rerun()

if 'origin' in st.session_state and 'destination' in st.session_state and 'shortest_path' not in st.session_state :
    origin = st.session_state['origin']
    folium.Marker([origin.y, origin.x], popup="Origin", tooltip="Origin").add_to(m)
    destination = st.session_state['destination']
    folium.Marker([destination.y, destination.x], popup="Destination", tooltip="Destination").add_to(m)
    origin_node = nodes[nodes['geometry'] == origin]['node_id'].values[0]
    destination_node = nodes[nodes['geometry'] == destination]['node_id'].values[0]
    with c1:
        st.write(f"Selected origin is node number: {origin_node}")   
        st.write("")
        st.write(f"Selected destination is node number: {destination_node}")   
        if st.button('Compute shortest path'):
            with st.spinner('Computing the shortest path'):
                shortest_path_list = shortest_path(circuit, N_NODES, origin_node, destination_node)
                shortest_path_list[0] = int(shortest_path_list[0])
                st.session_state['shortest_path'] = shortest_path_list
            st.experimental_rerun()
    with c2:
        st_data_final = st_folium(m, width=725, key="destination", returned_objects=[])



if 'origin' in st.session_state and 'destination' in st.session_state and 'shortest_path' in st.session_state :

    shortest_path_list = st.session_state['shortest_path']
    final_result = generate_path(shortest_path_list, rel)

    final_result.explore(
        m=m,  
        color="green",
        style_kwds = {"weight":5},
        tooltip="name",
        popup=["name"],
        name="Quadratic-Paris", 
    )

    origin = st.session_state['origin']
    folium.Marker([origin.y, origin.x], popup="Origin", tooltip="Origin").add_to(m)  
    
    destination = st.session_state['destination']
    folium.Marker([destination.y, destination.x], popup="Destination", tooltip="Destination").add_to(m)  
    
    with c1:
        st.write(shortest_path_list)
        if st.button('Restart'):
            del st.session_state['origin']
            del st.session_state['destination']
            del st.session_state['shortest_path']
            st.experimental_rerun() 
    with c2:
        st_data_short_path = st_folium(m, width=725, key="destination", returned_objects=[])


# TODO printer les indices des noeuds chiffrés si possible (i.e. envoyer ce qu'on envoie au serveur)
# TODO enlever les bouttons delete origin et delete destination et mettre plutôt un truc sequentiel 