# Contains a set of useful functions
import pandas as pd
from concrete import fhe
from config import circuit_filepath, keys_filepath
import streamlit as st
import folium
from streamlit_folium import st_folium

def set_up_server():
    """Load a server instance from a specified circuit file

    Raises:
        OSError: If there is an issue loading the FHE server.

    Returns:
       concrete.fhe.compilation.server.Server: A server instance loaded from the circuit file.
    """
    try:
        server = fhe.Server.load(circuit_filepath)
    except OSError as e:
        raise OSError(f"Something went wrong with the circuit. Make sure that the circuit \
            exists in {circuit_filepath}.If not run python generate_circuit.py.") from e

    return server

def set_up_client(serialized_client_specs):
    """Generate a client instance from a specified circuit file

    Args:
        serialized_client_specs (bytes): A serialized client specs

    Returns:
        concrete.fhe.compilation.client.Client: A client instance created from the client specs
    """
    
    client_specs = fhe.ClientSpecs.deserialize(serialized_client_specs)
    client = fhe.Client(client_specs)

    return client

def display_encrypted(encrypted_object):
    """Display a truncated representation of an encrypted object as a hexadecimal string

    Args:
        encrypted_object (bytes): A serialized encrypted object to display

    Returns:
        str: A truncated hexadecimal representation of the encrypted object
    """
    encoded_text = encrypted_object.hex()
    res = '...' + encoded_text[-10:]
    return res

def compute_shortest_path(nodes_nb, client, server):
    """Calculate the shortest path between two nodes

    Args:
        nodes_nb (int): The number of nodes in the network
        client (concrete.fhe.compilation.client.Client): A client instance
        server (concrete.fhe.compilation.server.Server): A server instance

    Returns:
        List[bytes]: A list of encrypted values representing the path
    """
    deserialized_origin = fhe.Value.deserialize(st.session_state['encrypted_origin'])
    deserialized_destination = fhe.Value.deserialize(st.session_state['encrypted_destination'])
    deserialized_evaluation_keys = fhe.EvaluationKeys.deserialize(st.session_state['evaluation_key'])
    client.keys.load_if_exists_generate_and_save_otherwise(keys_filepath)
    origin = st.session_state['origin_node']
    destination = st.session_state['destination_node']
    encrypted_path = [st.session_state['encrypted_origin'], ]
    o, d = deserialized_origin, deserialized_destination
    for _ in range(nodes_nb):
        if origin == destination:
            break
        o = server.run(o, d, evaluation_keys=deserialized_evaluation_keys)
        origin = client.decrypt(o)
        encrypted_path.append(o.serialize())
    return encrypted_path

    
def generate_path(shortest_path, roads):
    """Generate a path from a list of nodes using road data.

    Args:
        shortest_path (List[int]): A list of nodes representing the shortest path.
        roads (geopandas.DataFrame): A DataFrame containing the ways between the nodes.

    Returns:
       pandas.DataFrame: A DataFrame representing the road segments that form the shortest path.
    """
    pairs_list = []
    for i in range(len(shortest_path) - 1):
        current_element = shortest_path[i]
        next_element = shortest_path[i + 1]
        result = roads.groupby('way_id').filter(lambda x: set([current_element, next_element]).issubset(x['node_id']))
        pairs_list.append(result)
    final_result = pd.concat(pairs_list)
    return final_result




def decrypt_shortest_path(client):
    """Decrypt and store the shortest path in the session state

    Args:
        client (concrete.fhe.compilation.client.Client): A client instance
    """
    client.keys.load_if_exists_generate_and_save_otherwise(keys_filepath)
    path = []
    for enc_value in st.session_state['encrypted_shortest_path']:
        deserialized_result = fhe.Value.deserialize(enc_value)
        path.append(client.decrypt(deserialized_result))
    st.session_state['decrypted_result'] = path

def init_session():
    """Initialize the Streamlit session and layout configuration.

    Returns:
        Streamlit.columns: A tuple of Streamlit columns for layout customization.
    """
    st.set_page_config(layout="wide")
    
    if 'markers' not in st.session_state:
        st.session_state['markers'] = []
    if 'server_side' not in st.session_state:
            st.session_state['server_side'] = []    
    if 'client_side' not in st.session_state:
            st.session_state['client_side'] = []

    c1, c2, c3 = st.columns([1, 3, 1])

    return c1, c2, c3

def add_marker(coordinates, name):
    """Add a marker with coordinates and a name to the Streamlit session.

    Args:
        coordinates (Point): The coordinates of the marker 
        name (str): The name or label for the marker
    """
    data = {'coordinates': coordinates, 'name': name}
    st.session_state['markers'].append(data)


def display_map(nodes, returned_objects=None, path=None):
    """Display the map with nodes and optional markers and paths.

    Args:
        nodes (geopandas.DataFrame): A dataframe containing the nodes to display
        returned_objects (List[str], optional): Objects to be returned when interacting with the map. Defaults to None.
        path (pandas.DataFrame, optional): A DataFrame representing the road segments that form the shortest path. Defaults to None.

    Returns:
        Streamlit.FoliumMap: An interactive map displaying nodes, markers, and paths
    """
    m = nodes.explore(
        color="red",  
        marker_kwds=dict(radius=5, fill=True, name='node_id'),  
        tooltip="node_id",  
        tooltip_kwds=dict(labels=False), 
        zoom_control=False,
    )

    if 'markers' in st.session_state:
        for mrk in st.session_state['markers']:
            folium.Marker([mrk['coordinates'].y, mrk['coordinates'].x], popup=mrk['name'], tooltip=mrk['name']).add_to(m)

    if path is not None:
        path.explore(
                m=m,  
                color="green",
                style_kwds = {"weight":5},
                tooltip="name",
                popup=["name"],
                name="Quadratic-Paris", 
            )
        
    return st_folium(m, width=725, key="origin", returned_objects=returned_objects)


def add_to_server_side(message):
    """Add a message to the server side of the view

    Args:
        message (str): The message to be added to the server side
    """
    st.session_state['server_side'].append(message)

def add_to_client_side(message):
    """Add a message to the client side of the view

    Args:
        message (str): The message to be added to the client side
    """
    st.session_state['client_side'].append(message)

def display_server_side():
    """Display the messages stored in the server-side view.
    """
    st.write("**Server-side**")
    for message in st.session_state['server_side']:
        st.write(message)

def display_client_side():
    """Display the messages stored in the client-side view.
    """
    st.write("**Client-side**")
    for message in st.session_state['client_side']:
        st.write(message)

def restart_session():
    """Clear the session state to restart
    """
    if st.button('Restart'):
        for key in st.session_state.items():
            if key[0] != 'evaluation_key':
                del st.session_state[key[0]]
        st.rerun() 
