import folium
import streamlit as st
from streamlit_folium import st_folium
from shapely.geometry import Point
import geopandas
import config 
from concrete import fhe
from utils import generate_path, set_up_server, set_up_client, display_encrypted
from network import get_frames

st.set_page_config(layout="wide")
ways = geopandas.read_file(config.roads_filepath)
nodes, _, rel = get_frames(ways)

server = set_up_server()
client = set_up_client(server.client_specs.serialize())

m = nodes.explore(
    color="red",  
    marker_kwds=dict(radius=5, fill=True, name='node_id'),  
    tooltip="node_id",  
    tooltip_kwds=dict(labels=False), 
    zoom_control=False,
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
            st.rerun()
else:
    with c1:
        st.write("Encryption/decryption keys and evaluation keys are generated.")
        st.write("The evaluation key is sent to the server.")
    with c3:
        st.write(f"Evaluation key: {display_encrypted(st.session_state['evaluation_key'])}")

            
    if 'origin' not in st.session_state :
        with c1:
            st.write("Select the origin on the map")

        with c2:
            st_data_origin = st_folium(m, width=725, key="origin", returned_objects=["last_object_clicked"])

        with c3:
            st.write("")
            
        if st_data_origin["last_object_clicked"]:
            origin = Point(st_data_origin["last_object_clicked"]["lng"], st_data_origin["last_object_clicked"]["lat"])
            origin_node = nodes[nodes['geometry'] == origin]['node_id'].values[0]
            st.session_state['origin'] = origin
            st.session_state['origin_node'] = origin_node
            st.write(f"Selected node is node number: {origin_node}")  
            st.rerun()

    if 'origin' in st.session_state and 'destination' not in st.session_state:
        origin = st.session_state['origin']
        folium.Marker([origin.y, origin.x], popup="Origin", tooltip="Origin").add_to(m)    
        origin_node = st.session_state['origin_node']
        with c1:
            st.write(f"Selected origin is node number: {origin_node}")   
            st.write("Select the destination on the map")         
        with c2:
            st_data_destination = st_folium(m, width=725, key="destination", returned_objects=["last_object_clicked"])
        with c3:
            st.write("")
            st.write("")

        if st_data_destination["last_object_clicked"]:
            destination = Point(st_data_destination["last_object_clicked"]["lng"], st_data_destination["last_object_clicked"]["lat"])
            st.session_state['destination'] = destination
            st.session_state['destination_node'] = nodes[nodes['geometry'] == destination]['node_id'].values[0]
            st.write(st_data_destination["last_object_clicked"])
            st.rerun()

    if 'origin' in st.session_state and 'destination' in st.session_state and 'encrypted_origin' not in st.session_state :
        origin = st.session_state['origin']
        folium.Marker([origin.y, origin.x], popup="Origin", tooltip="Origin").add_to(m)
        destination = st.session_state['destination']
        folium.Marker([destination.y, destination.x], popup="Destination", tooltip="Destination").add_to(m)
        # breakpoint()
        origin_node = st.session_state['origin_node']
        destination_node = st.session_state['destination_node']
        with c1:
            st.write(f"Selected origin is node number: {origin_node}")   
            st.write(f"Selected destination is node number: {destination_node}")   
            if st.button('Encrypt and send inputs'):
                with st.spinner('Encrypting inputs'):
                    client.keys.load(config.keys_filepath)
                    origin, destination = client.encrypt(origin_node, destination_node)
                    st.session_state['encrypted_origin'] = origin.serialize()
                    st.session_state['encrypted_destination'] = destination.serialize()
                st.rerun()
        with c2:
            st_data_final = st_folium(m, width=725, key="destination", returned_objects=[])
        with c3:
            st.write("")
            st.write("")

    if 'encrypted_origin' in st.session_state and 'encrypted_shortest_path' not in st.session_state:
        origin = st.session_state['origin']
        folium.Marker([origin.y, origin.x], popup="Origin", tooltip="Origin").add_to(m)
        destination = st.session_state['destination']
        folium.Marker([destination.y, destination.x], popup="Destination", tooltip="Destination").add_to(m)
        
        origin_node = st.session_state['origin_node']
        destination_node = st.session_state['destination_node']
        with c1:
            st.write(f"Selected origin is node number: {origin_node}")   
            st.write(f"Selected destination is node number: {destination_node}")
        with c2:
            origin = st.session_state['origin']
            folium.Marker([origin.y, origin.x], popup="Origin", tooltip="Origin").add_to(m)  
            destination = st.session_state['destination']
            folium.Marker([destination.y, destination.x], popup="Destination", tooltip="Destination").add_to(m)
            st_data_final = st_folium(m, width=725, key="destination", returned_objects=[])
        with c3:
            st.write("")    
            st.write("")    
            st.write(f"Received origin: {display_encrypted(st.session_state['encrypted_origin'])}")
            st.write(f"Received destination: {display_encrypted(st.session_state['encrypted_destination'])}")
            if st.button('Compute shortest path'):
                with st.spinner('Computing'):
                    deserialized_origin = fhe.Value.deserialize(st.session_state['encrypted_origin'])
                    deserialized_destination = fhe.Value.deserialize(st.session_state['encrypted_destination'])
                    deserialized_evaluation_keys = fhe.EvaluationKeys.deserialize(st.session_state['evaluation_key'])
                    client.keys.load_if_exists_generate_and_save_otherwise(config.keys_filepath)
                    origin = st.session_state['origin_node']
                    destination = st.session_state['destination_node']
                    path = [origin, ]
                    encrypted_path = [st.session_state['encrypted_origin'], ]
                    o, d = deserialized_origin, deserialized_destination
                    for _ in range(nodes.shape[0] - 1):
                        # Careful: breaking early could lead to information leak
                        if origin == destination:
                            break
                        o = server.run(o, d, evaluation_keys=client.evaluation_keys)
                        origin = client.decrypt(o)
                        encrypted_path.append(o.serialize())
                        path.append(origin)
                        
                    st.session_state['encrypted_shortest_path'] = encrypted_path
                    st.session_state['decrypted_shortest_path'] = path
                st.rerun()

    if 'encrypted_shortest_path' in st.session_state and 'decrypted_result' not in st.session_state :  
        origin = st.session_state['origin']
        folium.Marker([origin.y, origin.x], popup="Origin", tooltip="Origin").add_to(m)
        destination = st.session_state['destination']
        folium.Marker([destination.y, destination.x], popup="Destination", tooltip="Destination").add_to(m)
        
        origin_node = st.session_state['origin_node']
        destination_node = st.session_state['destination_node']
        with c1:
            st.write(f"Selected origin is node number: {origin_node}")   
            st.write(f"Selected destination is node number: {destination_node}") 
            st.write("Received path is:")
            st.write(f"{display_encrypted(st.session_state['encrypted_shortest_path'][0])}")
            st.write("...")
            st.write(f"{display_encrypted(st.session_state['encrypted_shortest_path'][-1])}")
            
            if st.button('Decrypt and show shortest path'):
                with st.spinner('Computing'):
                    client.keys.load_if_exists_generate_and_save_otherwise(config.keys_filepath)
                    path = []
                    for enc_value in st.session_state['encrypted_shortest_path']:
                        deserialized_result = fhe.Value.deserialize(enc_value)
                        path.append(client.decrypt(deserialized_result))
                    st.session_state['decrypted_result'] = path
                st.rerun()
        with c2:
            
            origin = st.session_state['origin']
            folium.Marker([origin.y, origin.x], popup="Origin", tooltip="Origin").add_to(m)  
            
            destination = st.session_state['destination']
            folium.Marker([destination.y, destination.x], popup="Destination", tooltip="Destination").add_to(m)
            st_data_final = st_folium(m, width=725, key="destination", returned_objects=[])
        with c3:
            st.write("")    
            st.write("")    
            st.write(f"Received origin: {display_encrypted(st.session_state['encrypted_origin'])}")
            st.write(f"Received destination: {display_encrypted(st.session_state['encrypted_destination'])}")
    if 'decrypted_result' in st.session_state :
        origin = st.session_state['origin']
        folium.Marker([origin.y, origin.x], popup="Origin", tooltip="Origin").add_to(m)
        destination = st.session_state['destination']
        folium.Marker([destination.y, destination.x], popup="Destination", tooltip="Destination").add_to(m)
        
        origin_node = st.session_state['origin_node']
        destination_node = st.session_state['destination_node']
        with c1:
            st.write(f"Selected origin is node number: {origin_node}")   
            st.write(f"Selected destination is node number: {destination_node}") 
            st.write("Received path is:")
            st.write(f"{display_encrypted(st.session_state['encrypted_shortest_path'][0])}")
            st.write("...")
            st.write(f"{display_encrypted(st.session_state['encrypted_shortest_path'][-1])}")
            st.write(f"Decrypted result is: {st.session_state['decrypted_result']}")
            if st.button('Restart'):
                for key in st.session_state.keys():
                    if key != 'evaluation_key':
                        del st.session_state[key]
                st.rerun() 
        with c2:
            origin = st.session_state['origin']
            folium.Marker([origin.y, origin.x], popup="Origin", tooltip="Origin").add_to(m)  
            destination = st.session_state['destination']
            folium.Marker([destination.y, destination.x], popup="Destination", tooltip="Destination").add_to(m)
            shortest_path_list = st.session_state['decrypted_result']
            final_result = generate_path(shortest_path_list, rel)
            final_result.explore(
                m=m,  
                color="green",
                style_kwds = {"weight":5},
                tooltip="name",
                popup=["name"],
                name="Quadratic-Paris", 
            )
            st_data_final = st_folium(m, width=725, key="destination", returned_objects=[])
        with c3:
            st.write("")    
            st.write("")    
            st.write(f"Received origin: {display_encrypted(st.session_state['encrypted_origin'])}")
            st.write(f"Received destination: {display_encrypted(st.session_state['encrypted_destination'])}")
