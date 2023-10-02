import numpy as np
from concrete import fhe
import config 
import network

_, point_coordinates = network.get()

N_PTS = point_coordinates.shape[0]


points = fhe.LookupTable(point_coordinates.flatten())


def get_point(index):
    return (points[2*index], points[2*index + 1])


def all_distances(x, y):
    xs = np.arange(0, 2 * N_PTS, 2)
    ys = np.arange(1, 2 * N_PTS, 2)
    a = abs(points[xs] - x)
    b = abs(points[ys] - y)
    return a + b



# TLUs
relu = fhe.univariate(lambda x: x if x > 0 else 0)
is_positive = fhe.univariate(lambda x: 1 if x > 0 else 0)
arg_selection = fhe.univariate(lambda x: (x-1)//2 if x % 2 else 0)  # relu packed with a flag (alternating between 0 and relu)



def swap(this_idx, this_dist, that_idx, that_dist):
    """
    Swaps this and that if this > that. 
    We must pass both the index and the distance for both this and that.

    Returns:
      idxmin, min, idxmax, max of this and that based on distance
    """
    diff = this_dist - that_dist
    idx = arg_selection(2 * (this_idx - that_idx) + is_positive(diff))
    dist = relu(diff)

    idx_min = this_idx - idx
    idx_max = that_idx + idx 
    dist_min = this_dist - dist
    dist_max = that_dist + dist
    return fhe.array([idx_min, dist_min, idx_max, dist_max])


@fhe.compiler({"x": "encrypted", "y": "encrypted"})
def knn(x, y):
    dist = all_distances(x, y)
    idx = list(range(N_PTS))
    for k in range(2):
        for i in range(k+1, N_PTS):
             idx[k], dist[k], idx[i], dist[i] = swap(idx[k], dist[k], idx[i], dist[i])
    return fhe.array([get_point(idx[j]) for j in range(2)])


inputset = [
            (1550, 4289),
            (1908, 3972),
            (1705, 4253),
            (1980, 4071)
            ]

 
circuit = knn.compile(inputset)

circuit.server.save(config.circuit_filepath)