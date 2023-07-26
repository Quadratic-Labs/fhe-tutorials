from concrete import fhe
import numpy


# TLUs
relu = fhe.univariate(lambda x: x if x > 0 else 0)
is_positive = fhe.univariate(lambda x: 1 if x > 0 else 0)
arg_selection = fhe.univariate(lambda x: (x-1)//2 if x % 2 else 0)

# Database of Points of Interests
points_array = numpy.array([
    [2, 3], [1, 5], [3, 2], [5, 2], [1, 1],
    [9, 4], [13, 2], [14, 13], [9, 8], [8, 0],
    [2, 10], [3, 8], [8, 12], [4, 10], [7, 7],
])
N_PTS = points_array.shape[0]
points = fhe.LookupTable(points_array.flatten())


def get_point(index: int):
    return (points[2*index], points[2*index + 1])


def all_distances(x: int, y: int):
    """
    Computes distances to all points of interests (POI).

    Arguments:
        x, y: coordinates of center
    
    Returns:
        array of distances (int) to POI.
    """
    xs = numpy.arange(0, 2 * N_PTS, 2)
    ys = numpy.arange(1, 2 * N_PTS, 2)
    a = abs(points[xs] - x)
    b = abs(points[ys] - y)
    return a + b


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
    dist = [distance((x, y), get_point(i)) for i in range(N_PTS)]
    idx = list(range(N_PTS))
    for k in range(2):
        for i in range(k+1, N_PTS):
             idx[k], dist[k], idx[i], dist[i] = swap(idx[k], dist[k], idx[i], dist[i])
    return fhe.array([get_point(idx[j]) for j in range(2)])


inputset = [(4, 3), (0, 0), (7, 3), (4, 7)]

circuit = knn.compile(inputset)
circuit.client.keys.generate()


def nearest(x, y):
    """
    Privately get nearest points of interest (POI).
    
    Arguments:
        x, y: coordinates of the center

    Returns:
        Kx2 array of coordinates of neareast POI.
    """
    ex, ey = circuit.encrypt(x, y)
    res = circuit.run(ex, ey)
    return circuit.decrypt(res)