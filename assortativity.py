import networkx as nx
import numpy as np


def get_feature_strength(graph: nx.DiGraph, node: int, feature: str) -> float:
    feature_strength: float = 0.0
    neighbours = list(graph.successors(node))+list(graph.predecessors(node))
    for neighbour in neighbours:
        if node != neighbour:
            feature_strength += (graph.nodes[neighbour][feature] - graph.nodes[node][feature])

    return feature_strength

def get_custom_weighted_type_strength(graph: nx.DiGraph, ij_type: str, feature_i: str, feature_j, W: float, target: bool) -> float:
    numerator: float = 0.0

    for node in graph.nodes:
        feature_strength: float = get_feature_strength(graph, node, feature_i)
        if ij_type == "j": feature_strength = get_feature_strength(graph, node, feature_j)

        if target:
            numerator += (graph.in_degree(node, weight="weight") * feature_strength)
        else:
            numerator += (graph.out_degree(node, weight="weight") * feature_strength)

    return numerator / W

def get_weighted_type_std(graph: nx.DiGraph, ij_type: str, feature_i: str, feature_j, weighted_type_strength: float, W: float, target: bool) -> float:
    numerator: float = 0.0

    for node in graph.nodes:
        feature_strength: float = get_feature_strength(graph, node, feature_i)
        if ij_type == "j": feature_strength = get_feature_strength(graph, node, feature_j)

        if target:
            total: float = graph.in_degree(node, weight="weight") * ((feature_strength - weighted_type_strength)**2)
            numerator += total
        else:
            total: float = graph.out_degree(node, weight="weight") * ((feature_strength - weighted_type_strength)**2)
            numerator += total

    return np.sqrt(numerator / W)


def get_W(graph: nx.DiGraph) -> float:
    return sum(graph[node_i][node_j]["weight"] for node_i, node_j in graph.edges)


def directed_weighted_assortativity(graph: nx.DiGraph, features: list[str]) -> list[float]:
    combinations = ((feature_i, feature_j) for feature_i in features for feature_j in features)
    rhos: list[float] = []

    W: float = get_W(graph)

    for i,j in combinations:
        numerator: float = 0.0
        weighted_i_strength: float = get_custom_weighted_type_strength(graph, "i", i, j, W, False)
        weighted_j_strength: float = get_custom_weighted_type_strength(graph, "j", i, j, W, True)
        source_i_std: float = get_weighted_type_std(graph, "i", i, j, weighted_i_strength, W, False)
        target_j_std: float = get_weighted_type_std(graph, "j", i, j, weighted_j_strength, W, True)

        for node_i, node_j in graph.edges:
            source_feature_strength = get_feature_strength(graph, node_i, i)
            target_feature_strength = get_feature_strength(graph, node_j, j)
            total = graph[node_i][node_j]["weight"] * ((source_feature_strength - weighted_i_strength) * (target_feature_strength - weighted_j_strength))
            numerator += total

        rhos.append(numerator / (W * source_i_std * target_j_std))


    return rhos


def gen_test_graph(size: int) -> nx.DiGraph:
    graph: nx.DiGraph = nx.complete_graph(size).to_directed()
    for node_i, node_j in graph.edges:
        graph[node_i][node_j]["weight"] = np.random.uniform()

    for node in graph.nodes:
        graph.nodes[node]["a"] = np.random.normal()
        graph.nodes[node]["b"] = np.random.uniform(0.01,0.3)
        graph.nodes[node]["c"] = np.random.uniform(0.01,0.3)
        graph.nodes[node]["d"] = np.random.uniform(0.01,0.3)

    return graph







