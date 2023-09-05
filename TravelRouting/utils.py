import pandas as pd
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