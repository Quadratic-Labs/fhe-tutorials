from streamlit_folium import st_folium
import streamlit as st
import network
import config   
from utils import set_up_server, set_up_client, display_encrypted, transform_point
from shapely.geometry import Point

import folium
import streamlit as st
from streamlit_folium import st_folium
from shapely.geometry import Point
import geopandas
import config 
from concrete import fhe

st.set_page_config(layout="wide")
server = set_up_server()
client = set_up_client(server.client_specs.serialize())


restaurants, point_coordinates = network.get()

m = restaurants.explore(
    scheme="naturalbreaks",
    tooltip="name",
    popup=["name"],
    name="Quadratic-Paris",
    color="red",  
    marker_kwds=dict(radius=5, fill=True, name='node_id'),  
)
    


c1, c2, c3 = st.columns([1, 3, 1])

with c1:
    st.write("**Client-side**")

with c3:
    st.write("**Server-side**")


if 'evaluation_key' not in st.session_state:
    with c1:
        if st.button('Generate keys'):
            with st.spinner('Generating keys'):
                client.keys.load_if_exists_generate_and_save_otherwise(config.keys_filepath)
                st.session_state['evaluation_key'] = client.evaluation_keys.serialize()
            st.experimental_rerun()
else:
    with c1:
        st.write("Encryption/decryption keys and evaluation keys are generated.")
        st.write("The evaluation key is sent to the server.")
    with c3:
        st.write(f"Evaluation key: {display_encrypted(st.session_state['evaluation_key'])}")

    if 'position' not in st.session_state :
        with c1:
            st.write("Select your starting position on the map")

        with c2:
            map = st_folium(m, height=350, width=700)

        with c3:
            st.write("")
            
        if map.get("last_clicked"):
            position = Point(map.get("last_clicked")["lng"], map.get("last_clicked")["lat"])
            st.session_state['position'] = position
            st.write(f"Selected starting point is: {position}")  
            st.experimental_rerun()
            
    if 'position' in st.session_state and 'encrypted_position' not in st.session_state :
        
        position = st.session_state['position']
        folium.Marker([position.y, position.x], popup="Starting point", tooltip="Starting point").add_to(m)  
        
        with c1:
            st.write(f"Selected starting point is: ({position.x}, {position.y})")  
            
            if st.button('Encrypt and send inputs'):
                with st.spinner('Encrypting inputs'):
                    client.keys.load(config.keys_filepath)

                    x, y = transform_point(position.x, position.y)
                    encrypted_x, encrypted_y = client.encrypt(x, y)
                    encrypted_position = (encrypted_x.serialize(), encrypted_y.serialize())
                    st.session_state['encrypted_position'] = encrypted_position
                st.experimental_rerun()
        with c2:
            map = st_folium(m, height=350, width=700)

        with c3:
            st.write("")
            
    if 'encrypted_position' in st.session_state and 'encrypted_results' not in st.session_state:
        position = st.session_state['position']
        folium.Marker([position.y, position.x], popup="Starting point", tooltip="Starting point").add_to(m)  
        
        with c1:
            st.write(f"Selected starting point is: ({position.x}, {position.y})")
        with c2:
            map = st_folium(m, height=350, width=700)
        with c3:
            st.write("")    
            st.write("")
            encrypted_x = st.session_state['encrypted_position'][0]
            encrypted_y = st.session_state['encrypted_position'][1]
            
            st.write(f"Received starting point: ({display_encrypted(encrypted_x)},{display_encrypted(encrypted_y)})")
            if st.button(f'Find {config.number_of_neighbors} nearest neighbors'):
                with st.spinner('Computing'):
                    deserialized_x = fhe.Value.deserialize(encrypted_x)
                    deserialized_y = fhe.Value.deserialize(encrypted_y)
                    deserialized_evaluation_keys = fhe.EvaluationKeys.deserialize(st.session_state['evaluation_key'])
                    client.keys.load_if_exists_generate_and_save_otherwise(config.keys_filepath)

                    # TODO complete this part
                st.experimental_rerun()      
# map = st_folium(m, height=350, width=700)



# if map.get("last_clicked"):
#     st.write(map.get("last_clicked"))

