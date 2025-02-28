
import networkx as nx
from typing import Tuple, List, Dict
from Final.bidirectional_dijkstra_fixed import bidirectional_dijkstra

def process_node(
    graph: nx.Graph,
    node: str,
    update_graph: bool = False,
    shortcut_graph: nx.Graph = None,
    criterion: str = "edge_difference",
) -> Tuple[int, int]:

    neighbors = list(graph.neighbors(node))
    shortcuts_added = 0
    added_shortcuts = set()  # Track added shortcuts

    for i in range(len(neighbors)):
        for j in range(i + 1, len(neighbors)):
            u = neighbors[i]
            v = neighbors[j]
            if graph.has_edge(u, node) and graph.has_edge(node, v):
                weight = graph[u][node]["weight"] + graph[node][v]["weight"]
                if (u, v) not in added_shortcuts and (v, u) not in added_shortcuts:
                    if not graph.has_edge(u, v) or graph[u][v]["weight"] > weight:
                        if update_graph:
                            print(f"Shortcut added: {u} --({weight})-- {v}")
                        shortcuts_added += 1
                        added_shortcuts.add((u, v))
                        if update_graph and shortcut_graph is not None:
                            shortcut_graph.add_edge(u, v, weight=weight)

    edges_removed = len(list(graph.edges(node)))  # Edges connected to the node
    if update_graph:
        graph.remove_node(node)

    rank = (
        shortcuts_added if criterion == "shortcuts_added"
        else edges_removed if criterion == "edges_removed"
        else shortcuts_added - edges_removed
    )
    return rank, shortcuts_added

def create_contraction_hierarchy(
    graph: nx.Graph, online: bool = False, criterion: str = "edge_difference"
) -> Tuple[nx.Graph, List[str], int]:
    """Creates a contraction hierarchy using edge difference ordering."""
    edge_differences: Dict[str, int] = {}
    nodes = list(graph.nodes())

    for node in nodes:
        edge_differences[node] = process_node(graph, node, criterion=criterion)[0]

    node_order = sorted(edge_differences, key=edge_differences.get)
    temp_graph = graph.copy()
    shortcut_graph = graph.copy()
    shortcuts_added = 0

    for node in node_order:
        shortcuts_added += process_node(
            temp_graph, node, update_graph=True, shortcut_graph=shortcut_graph, criterion=criterion
        )[1]

    return nx.compose(shortcut_graph, graph), node_order, shortcuts_added

def find_shortest_path_custom(
    graph: nx.Graph, source: str, target: str, node_order: List[str]
) -> Tuple[List[str], int]:
    """Finds the shortest path using the contraction hierarchy."""
    if source not in graph or target not in graph:
        raise ValueError("Source or target node not in graph")

    node_order_map = {node: order for order, node in enumerate(node_order)}
    try:
        path, length = bidirectional_dijkstra(graph, source, target, node_order_map)
    except Exception as e:
        print(f"Error finding shortest path: {e}")
        path, length = None, float('inf')

    return path, length

