import network
from utils import set_up_server, set_up_client, display_encrypted, transform_point, process_result
from shapely.geometry import Point
import streamlit as st
from shapely.geometry import Point
import config 
from utils import set_up_server, set_up_client, display_encrypted, add_marker,\
                  display_map, init_session, add_to_server_side, add_to_client_side, display_client_side,\
                  display_server_side, restart_session
from concrete import fhe

server = set_up_server()
client = set_up_client(server.client_specs.serialize())
restaurants, point_coordinates = network.get()

c1, c2, c3 = init_session()

with c1:
    display_client_side()
with c2:
    st_map = display_map(restaurants)
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

    if 'position' not in st.session_state :
        with c1:
            st.write("Select your starting position on the st_map")

        if st_map.get("last_clicked"):
            position = Point(st_map.get("last_clicked")["lng"], st_map.get("last_clicked")["lat"])
            add_to_client_side(f"Selected starting point is: ({position.x}, {position.y})")  
            st.session_state['position'] = position
            st.rerun()
            
    if 'position' in st.session_state and 'encrypted_position' not in st.session_state :
        
        position = st.session_state['position']
        with c1:
            
            if st.button('Encrypt and send inputs'):
                with st.spinner('Encrypting inputs'):
                    client.keys.load(config.keys_filepath)

                    x, y = transform_point(position.x, position.y)
                    encrypted_x, encrypted_y = client.encrypt(x, y)
                    encrypted_position = (encrypted_x.serialize(), encrypted_y.serialize())
                    add_to_server_side(f"Received starting point: ({display_encrypted(encrypted_position[0])},{display_encrypted(encrypted_position[1])})")
                    st.session_state['encrypted_position'] = encrypted_position
                st.rerun()
            
    if 'encrypted_position' in st.session_state and 'encrypted_results' not in st.session_state:
        
        with c3:
            encrypted_x = st.session_state['encrypted_position'][0]
            encrypted_y = st.session_state['encrypted_position'][1]
            
            if st.button(f'Find {config.number_of_neighbors} nearest neighbors'):
                with st.spinner('Computing'):
                    deserialized_x = fhe.Value.deserialize(encrypted_x)
                    deserialized_y = fhe.Value.deserialize(encrypted_y)
                    deserialized_evaluation_keys = fhe.EvaluationKeys.deserialize(st.session_state['evaluation_key'])
                    client.keys.load_if_exists_generate_and_save_otherwise(config.keys_filepath)
                    res = server.run(deserialized_x, deserialized_y,  evaluation_keys=deserialized_evaluation_keys)
                    ser_res = fhe.Value.serialize(res)
                    add_to_server_side(f"The encrypted result {display_encrypted(ser_res)} is sent to the client.")
                    add_to_client_side(f"The received encrypted result is: {display_encrypted(ser_res)}.")
                    st.session_state['encrypted_results'] = ser_res
                st.rerun()
                
    if 'encrypted_results' in st.session_state and 'decrypted_result' not in st.session_state :
        res = st.session_state['encrypted_results']
        with c1:
            if st.button('Decrypt result'):
                with st.spinner('Computing'):
                    client.keys.load_if_exists_generate_and_save_otherwise(config.keys_filepath)
                    deser_res = fhe.Value.deserialize(res)
                    decrypted_result = client.decrypt(deser_res)
                    process_result(restaurants, decrypted_result)
                    st.session_state['decrypted_result'] = decrypted_result
                    st.rerun()
            
        
    if 'decrypted_result' in st.session_state:
        # for index, enc_res in enumerate(processed_result):
        #     # folium.Marker([enc_res.y, enc_res.x], popup=restaurants_list[index], tooltip=restaurants_list[index],
        #                 #   icon=folium.Icon(color='black',icon_color='#FFFF00')).add_to(m)
        #     add_marker(Point(enc_res.y, enc_res.x), restaurants_list[index])    
        # st.rerun()                    
        with c1:
            restart_session()
            
            
