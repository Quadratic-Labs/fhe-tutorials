import pandas as pd
from concrete import fhe
from config import circuit_filepath
from shapely.geometry import Point
import geopandas as gpd

def set_up_server():
    try:
        server = fhe.Server.load(circuit_filepath)
    except Exception:
        raise Exception(f"Something went wrong with the circuit. Make sure that the circuit exists in {circuit_filepath}. If not run python generate_circuit.py.") 

    return server

def set_up_client(serialized_client_specs):
    # Setting up client
    client_specs = fhe.ClientSpecs.deserialize(serialized_client_specs)
    client = fhe.Client(client_specs)

    return client

def display_encrypted(encrypted_object):
    encoded_text = encrypted_object.hex()
    res = '...' + encoded_text[-10:]
    return res


def transform_point(longitude, latitude):
    gdf = gpd.GeoDataFrame({'geometry': [Point(longitude, latitude)]}, crs='EPSG:4326')
    gdf = gdf.to_crs('EPSG:2154')
    x, y = gdf.geometry.iloc[0].x, gdf.geometry.iloc[0].y
    x = int(x) % 10000
    y = int(y) % 10000

    return x, y