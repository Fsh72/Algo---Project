
import networkx as nx
from typing import Tuple, List, Dict
from Final.bidirectional_dijkstra_fixed import bidirectional_dijkstra
import time

# node ordering of Barak's code

def save_node_ordering(contraction_order, suffix):
    """Saves the CH node ordering to a file with a unique suffix."""
    filename = f"CH_node_ordering_{suffix}.txt"
    with open(filename, "w") as file:
        for node in contraction_order:
            file.write(f"{node}\n")
    print(f"Node ordering saved to {filename}")


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
    """
    Creates the Contraction Hierarchy (CH) for the given graph.
    Saves the node ordering separately for each method (online/offline, criterion).
    """
    temp_graph = graph.copy()
    shortcut_graph = graph.copy()
    shortcuts_added = 0
    contraction_order = []

    ordering_name = f"{'online' if online else 'offline'}_{criterion}"

    if online:
        # Online: Iteratively update ranks while contracting nodes
        remaining_nodes = set(temp_graph.nodes())
        while remaining_nodes:
            node_ranks = {node: process_node(temp_graph, node, criterion=criterion)[0] for node in remaining_nodes}
            selected_node = min(node_ranks, key=node_ranks.get)
            contraction_order.append(selected_node)
            shortcuts_added += process_node(temp_graph, selected_node, update_graph=True, shortcut_graph=shortcut_graph, criterion=criterion)[1]
            remaining_nodes.remove(selected_node)
    else:
        # Offline: Compute all ranks beforehand, then contract nodes sequentially
        precomputed_ranks = {node: process_node(graph, node, criterion=criterion)[0] for node in graph.nodes()}
        contraction_order = sorted(precomputed_ranks, key=precomputed_ranks.get)

        for node in contraction_order:
            shortcuts_added += process_node(temp_graph, node, update_graph=True, shortcut_graph=shortcut_graph, criterion=criterion)[1]

    # ✅ Save the node ordering for both online and offline methods
    save_node_ordering(contraction_order, ordering_name)

    return nx.compose(shortcut_graph, graph), contraction_order, shortcuts_added


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
