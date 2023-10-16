import streamlit as st
from shapely.geometry import Point
import geopandas
import config 
from utils import generate_path, set_up_server, set_up_client, display_encrypted, add_marker,\
                  display_map, init_session, add_to_server_side, add_to_client_side, display_client_side,\
                  display_server_side, restart_session, compute_shortest_path, decrypt_shortest_path
from network import get_frames

ways = geopandas.read_file(config.roads_filepath)
nodes, _, rel = get_frames(ways)

server = set_up_server()
client = set_up_client(server.client_specs.serialize())

c1, c2, c3 = init_session()

with c1:
    display_client_side()

with c3:
    display_server_side()

# keys generation view
if 'evaluation_key' not in st.session_state:
    with c1:
        if st.button('Generate keys'):
            with st.spinner('Generating keys'):
                client.keys.load_if_exists_generate_and_save_otherwise(config.keys_filepath)
                st.session_state['evaluation_key'] = client.evaluation_keys.serialize()
                add_to_client_side("Encryption/decryption keys and evaluation keys are generated.")
                add_to_client_side("The evaluation key is sent to the server.")
                add_to_server_side(f"Evaluation key: {display_encrypted(st.session_state['evaluation_key'])}")
            st.rerun()
else:
    # Origin selection view
    if 'origin' not in st.session_state :
        with c1:
            st.write("Select the origin on the map")
        with c2:
            st_data_origin = display_map(nodes, returned_objects=["last_object_clicked"])
            
        if st_data_origin["last_object_clicked"]:
            origin = Point(st_data_origin["last_object_clicked"]["lng"], st_data_origin["last_object_clicked"]["lat"])
            add_marker(origin, 'origin')
            origin_node = nodes[nodes['geometry'] == origin]['node_id'].values[0]
            st.session_state['origin'] = origin
            st.session_state['origin_node'] = origin_node
            add_to_client_side(f"Selected origin is node number: {origin_node}")  
            st.rerun()

    # Destination selection view
    if 'origin' in st.session_state and 'destination' not in st.session_state:
        origin_node = st.session_state['origin_node']
        with c1:
            st.write("Select the destination on the map")         
        with c2:
            st_data_destination = display_map(nodes, returned_objects=["last_object_clicked"])

        if st_data_destination["last_object_clicked"]:
            destination = Point(st_data_destination["last_object_clicked"]["lng"], st_data_destination["last_object_clicked"]["lat"])
            add_marker(destination, 'destination')
            destination_node = nodes[nodes['geometry'] == destination]['node_id'].values[0]
            st.session_state['destination'] = destination
            st.session_state['destination_node'] = destination_node
            add_to_client_side(f"Selected destination is node number: {destination_node}")
            st.rerun()

    # Origin/Destination encryption view
    if 'destination' in st.session_state and 'encrypted_origin' not in st.session_state :
        origin_node = st.session_state['origin_node']
        destination_node = st.session_state['destination_node']
        with c1:
            if st.button('Encrypt and send inputs'):
                with st.spinner('Encrypting inputs'):
                    client.keys.load(config.keys_filepath)
                    origin, destination = client.encrypt(origin_node, destination_node)
                    st.session_state['encrypted_origin'] = origin.serialize()
                    st.session_state['encrypted_destination'] = destination.serialize()
                    add_to_server_side(f"Received origin: {display_encrypted(st.session_state['encrypted_origin'])}")
                    add_to_server_side(f"Received destination: {display_encrypted(st.session_state['encrypted_destination'])}")
                st.rerun()
        with c2:
            st_data_final = display_map(nodes)

    # Shortest path computation view
    if 'encrypted_origin' in st.session_state and 'encrypted_shortest_path' not in st.session_state:
        origin_node = st.session_state['origin_node']
        destination_node = st.session_state['destination_node']
        with c2:
            st_data_final = display_map(nodes)
        with c3:
            if st.button('Compute and send shortest path'):
                with st.spinner('Computing'):
                    encrypted_path = compute_shortest_path(nodes.shape[0], client, server)
                    st.session_state['encrypted_shortest_path'] = encrypted_path
                    add_to_client_side("Received path is:")
                    add_to_client_side(f"{display_encrypted(st.session_state['encrypted_shortest_path'][0])}")
                    add_to_client_side("...")
                    add_to_client_side(f"{display_encrypted(st.session_state['encrypted_shortest_path'][-1])}")
                st.rerun()
                
    # Result decryption view
    if 'encrypted_shortest_path' in st.session_state and 'decrypted_result' not in st.session_state :
        with c1:
            if st.button('Decrypt and show shortest path'):
                with st.spinner('Computing'):
                    decrypt_shortest_path(client)
                st.rerun()
        with c2:
            st_data_final = display_map(nodes)
            
    # Display result view
    if 'decrypted_result' in st.session_state :
        with c1:
            st.write(f"Decrypted result is: {st.session_state['decrypted_result']}")
            restart_session()
        with c2:
            shortest_path_list = st.session_state['decrypted_result']
            final_result = generate_path(shortest_path_list, rel)
            display_map(nodes, path=final_result)
