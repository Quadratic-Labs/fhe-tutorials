import numpy
from concrete import fhe

from dijkstra import Dijkstra


N_BITS = 6
inf = 2**N_BITS - 1  # infinity
# Origin x Destination -> Weight of edge (infinite if no edge)
weights = numpy.array([
    [  0,   1,   2, inf, inf, inf, inf, inf, inf, ],
    [  1,   0, inf,   1,   1, inf, inf, inf, inf, ],
    [  2, inf,   0, inf, inf,   1,   1, inf, inf, ],
    [inf,   1, inf,   0, inf,   1, inf, inf, inf, ],
    [inf,   1, inf, inf,   0,   1, inf,   1, inf, ],
    [inf, inf,   1,   1,   1,   0, inf, inf,   2, ],
    [inf, inf,   1, inf, inf, inf,   0, inf,   1, ],
    [inf, inf, inf, inf,   1, inf, inf,   0,   1, ],
    [inf, inf, inf, inf, inf,   2,   1,   1,   0, ],
])
N_NODES = weights.shape[0]
assert weights.shape[0] == weights.shape[1]
assert (weights == weights.T).all()
assert (weights.diagonal() == 0).all()


router = Dijkstra(weights)
# Matrix of origin x destination -> next node on shortest path
next_nodes = router.get_all_shortest_paths()[:, :, 1]
routes = fhe.LookupTable(next_nodes.flatten())


@fhe.compiler({"origin": "encrypted", "destination": "encrypted"})
def route(origin, destination):
    return routes[N_NODES * origin + destination]


circuit = route.compile([(0, N_NODES - 1), (N_NODES - 1, 0)])
circuit.client.keys.generate()

