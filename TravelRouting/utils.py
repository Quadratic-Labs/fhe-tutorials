import pandas as pd
from concrete import fhe
from config import circuit_filepath

def set_up_server():
    # Setting up a server
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

def shortest_path(circuit, N_NODES, origin, destination):
    path = [origin, ]
    o, d = circuit.encrypt(origin, destination)
    for _ in range(N_NODES - 1):
        # Careful: breaking early could lead to information leak
        if origin == destination:
            break
        o = circuit.run(o, d)
        origin = circuit.decrypt(o)
        path.append(origin)
    return path

def generate_path(shortest_path_list, rel):
    pairs_list = []
    for i in range(len(shortest_path_list) - 1):
        current_element = shortest_path_list[i]
        next_element = shortest_path_list[i + 1]
        result = rel.groupby('way_id').filter(lambda x: set([current_element, next_element]).issubset(x['node_id']))
        pairs_list.append(result)
    final_result = pd.concat(pairs_list)
    return final_result