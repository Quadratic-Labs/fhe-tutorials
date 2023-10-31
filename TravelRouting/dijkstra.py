import heapq

import numpy


class Dijkstra:
    """
    Dijkstra's algorithm for finding shortest_paths on a weighted graph
    """
    def __init__(self, weights):
        weights = numpy.array(weights)
        if weights.shape[0] != weights.shape[1]:
            raise ValueError("Graph weights must be a square-matrix")
        self.weights = weights
        self.n_vertices = weights.shape[0]

    def shortest_from_origin(self, origin):
        """
        Find shortest distances and paths from an origin to all vertices.

        Parameters:
            origin (int): index of the origin vertex.

        Returns:
            distances (numpy.ndarray): shortest distance from origin.
            previous_nodes (list): previous vertex on the shortest path.
        """
        distances = numpy.full((self.n_vertices,), numpy.inf)
        distances[origin] = 0
        previous_nodes = [None] * self.n_vertices
        priority_queue = [(0, origin)]

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)
            if current_distance > distances[current_node]:
                continue
            for neighbor in range(self.n_vertices):
                alt_distance = current_distance + self.weights[current_node, neighbor]
                if alt_distance < distances[neighbor]:
                    distances[neighbor] = alt_distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(priority_queue, (alt_distance, neighbor))

        return distances, previous_nodes

    def _get_path_from_previous_nodes(self, destination, previous_nodes):
        path = []
        current_node = destination
        while current_node is not None:
            path.append(current_node)
            current_node = previous_nodes[current_node]
        return path[::-1]

    def get_all_shortest_paths(self, as_array=True):
        """
        Find all shortest paths.

        Parameters:
            as_array (bool): Should return a numpy array. Default to True.

        Returns:
            shortest_paths (list or numpy.ndarray): i,j,k -> k-th node on the
                shortest path from i to j.
        """
        shortest_paths = []
        max_length = 0
        for start in range(self.n_vertices):
            paths_from_start = []
            _, previous_nodes = self.shortest_from_origin(start)
            for end in range(self.n_vertices):
                path = self._get_path_from_previous_nodes(end, previous_nodes)
                paths_from_start.append(path)
                max_length = max(max_length, len(path))
            shortest_paths.append(paths_from_start)
        if as_array:
            res = numpy.zeros((self.n_vertices, self.n_vertices, max_length)).astype(int)
            for start in range(self.n_vertices):
                res[start, :, :] = start
                for end in range(self.n_vertices):
                    length = len(shortest_paths[start][end])
                    res[start, end, :length] = shortest_paths[start][end]
            shortest_paths = res
        return shortest_paths
