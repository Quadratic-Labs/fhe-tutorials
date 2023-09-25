# This script is used to generate the circuit archive.
# The circuit depends on the network, and must be recompiled for each different network.


import geopandas
from concrete import fhe

import config
import network
from dijkstra import Dijkstra


ways = geopandas.read_file(config.roads_filepath)
roads = network.get(ways)
weights = network.weighted_adjacency_matrix(roads)
router = Dijkstra(weights)

N_NODES = weights.shape[0]

# Matrix of origin x destination -> next node on shortest path
next_nodes = router.get_all_shortest_paths()[:, :, 1]
routes = fhe.LookupTable(next_nodes.flatten())


@fhe.compiler({"origin": "encrypted", "destination": "encrypted"})
def route(origin, destination):
    return routes[N_NODES * origin + destination]


circuit = route.compile([(0, N_NODES - 1), (N_NODES - 1, 0)])
circuit.server.save(config.circuit_filepath)