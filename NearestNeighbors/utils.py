from concrete import fhe
from config import circuit_filepath, number_of_neighbors
from shapely.geometry import Point
import geopandas as gpd
import streamlit as st
import folium
from streamlit_folium import st_folium

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


def transform_point(longitude, latitude):
    """Transform coordinates into an integer to be processed by the FHE circuit

    Args:
        longitude (float): longitude of the point
        latitude (float): latitude of the point

    Returns:
        int, int: integers to be processed by the FHE circuit
    """
    gdf = gpd.GeoDataFrame({'geometry': [Point(longitude, latitude)]}, crs='EPSG:4326')
    gdf = gdf.to_crs('EPSG:2154')
    x, y = gdf.geometry.iloc[0].x, gdf.geometry.iloc[0].y
    x = int(x) % 10000
    y = int(y) % 10000

    return x, y


def process_result(rest, result):
    """Add the nearest restaurants in the map and in the client view

    Args:
        rest (geopandas.DataFrame): list of restaurants
        result (list[(int, int)]): list of the nearest neighbors returned by the algorithm
    """
    add_to_client_side(f"The {number_of_neighbors} closest restaurant to your location are:")
    for index, res in enumerate(result):
        mask1 = rest['geometry'].to_crs("epsg:2154").apply(lambda geom: int(geom.x) % 10000 == res[0])
        mask2 = rest['geometry'].to_crs("epsg:2154").apply(lambda geom: int(geom.y) % 10000 == res[1])
        final_mask = mask1 & mask2
        result_df = rest[final_mask]
        restaurant_info = f"{result_df.name.iloc[0]}, {result_df.cuisine.iloc[0]}"
        add_marker(result_df.geometry, restaurant_info)
        add_to_client_side(f"{index+1}. {restaurant_info}.")


def add_marker(coordinates, name):
    """Add a marker with coordinates and a name to the Streamlit session.

    Args:
        coordinates (Point): The coordinates of the marker 
        name (str): The name or label for the marker
    """
    data = {'coordinates': coordinates, 'name': name}
    st.session_state['markers'].append(data)

def display_map(restaurants, returned_objects=None):
    """Display the map with nodes and optional markers and paths.

    Args:
        nodes (geopandas.DataFrame): A dataframe containing the nodes to display
        returned_objects (List[str], optional): Objects to be returned when interacting with the map. Defaults to None.

    Returns:
        Streamlit.FoliumMap: An interactive map displaying nodes and markers
    """
    m = restaurants.explore(
        scheme="naturalbreaks",
        tooltip="name",
        popup=["name"],
        name="Quadratic-Paris",
        color="red",  
        marker_kwds=dict(radius=5, fill=True, name='node_id'),  
    )

    if 'position' in st.session_state:
        position = st.session_state['position']
        folium.Marker([position.y, position.x], popup='Starting point', tooltip='Starting point').add_to(m)
        
    if 'markers' in st.session_state:
        for mrk in st.session_state['markers']:
            folium.Marker([mrk['coordinates'].y, mrk['coordinates'].x], popup=mrk['name'], tooltip=mrk['name'],
                                      icon=folium.Icon(color='black',icon_color='#FFFF00')).add_to(m)

        
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

