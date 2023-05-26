from concrete import fhe


def take_min(x, y):
    return (x + y - abs(x - y)) // 2


def shortest_path_from_first(weights):
    """
    Find shortest path on an encrypted weighted graph from origin.

    The origin is taken as the first vertex of the graph. This can always be
    done by eventually permuting the vertices.

    Parameters:
        weights (numpy.ndarray): NxN weight matrix

    Returns:
        fhe.array: previous vertex on shortest path from origin.
    """
    inf = 9  # TODO: infinity in Zama
    N = weights.shape[0]
    distances = [inf] * N
    distances[0] = 0
    previous = [0] * N

    for _ in range(1, N):
        for v in range(N):
            for u in range(N):
                candidate = distances[u] + weights[u, v]
                cond = (candidate < distances[v])
                distances[v] = take_min(candidate, distances[v])
                previous[v] = u * cond + previous[v] * (1 - cond)
    return fhe.array(previous)


def select_path(paths, origin, destination):
    """
    Select path from encrypted origin and destination.

    Selection is done anonymously via dot-products. Selectors must therefore
    be arrays of same length as the corresponding axis in paths.
    For example, to select the first element out of three, one would use 
    [1, 0, 0] as selector.

    Parameters:
        paths (numpy.ndarray): (origin x destination x path) array
        origin (numpy.ndarray): array selector on origin
        destination (numpy.ndarray): array selector on destination
    """
    res = [0] * paths.shape[2]
    for z in range(paths.shape[2]):
        for y in range(paths.shape[1]):
            for x in range(paths.shape[0]):
                res[z] += paths[x, y, z] * origin[x] * destination[y]
    return fhe.array(res)
