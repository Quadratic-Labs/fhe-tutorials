import geopandas
import networkx
import numpy


def get_frames(ways: geopandas.GeoDataFrame):
    edges = ways.explode(index_parts=False)[["id", "name", "geometry"]]
    edges.index.name = "way_id"
    edges = edges.reset_index()
    nodes = geopandas.GeoDataFrame({"geometry": edges.boundary.explode(index_parts=False).geometry.unique()})
    nodes.index.name = "node_id"
    nodes.reset_index(inplace=True)
    rel = edges.sjoin(nodes).to_crs("epsg:2154")
    return nodes, edges, rel


def get(ways: geopandas.GeoDataFrame) -> networkx.Graph:
    nodes, edges, rel = get_frames(ways)
    graph = networkx.Graph()
    for node in rel['node_id'].unique():
        graph.add_node(node, shape=nodes.loc[node, "geometry"])
    for idx in rel['way_id'].unique():
        node_id1, node_id2 = rel.loc[idx]['node_id']
        way = edges.loc[idx]
        way_length = rel.loc[idx]['geometry'].iloc[0].length
        graph.add_edge(
            node_id1, node_id2,
            weight=way.geometry.length,
            shape=way.geometry,
            id_=idx,
        )
    return graph


def weighted_adjacency_matrix(graph: networkx.Graph) -> numpy.ndarray:
    weights = numpy.full((graph.number_of_nodes(),)*2, numpy.inf)
    numpy.fill_diagonal(weights, 0., wrap=False)
    for i in graph:
        for j in graph[i]:
            weights[i, j] = graph[i][j]["weight"]
    return weights