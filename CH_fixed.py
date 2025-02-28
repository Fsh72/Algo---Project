
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
    """Processes a node, creates shortcuts, and optionally updates the graphs.

    Args:
        graph (nx.Graph): The graph to process the node in.
        node (str): The node to process.
        update_graph (bool): Whether to update the shortcut graph.
        shortcut_graph (nx.Graph): The shortcut graph to update.
        criterion (str): The criterion to order nodes by.

    Returns:
        Tuple[int, int]: The node's rank and the number of shortcuts added.
    """
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

# Define and process the graph
graph = nx.Graph()
edges = [
    ("A", "B", 4), ("B", "C", 2), ("B", "G", 1), ("C", "D", 1),
    ("D", "E", 3), ("D", "I", 1), ("E", "J", 3), ("F", "G", 1),
    ("G", "H", 2), ("G", "L", 1), ("I", "J", 1), ("I", "N", 3),
    ("J", "O", 3), ("K", "L", 1), ("K", "P", 1), ("L", "M", 3),
    ("M", "N", 3), ("N", "O", 3), ("P", "Q", 1), ("Q", "R", 3),
    ("Q", "V", 1), ("R", "S", 3), ("S", "T", 3), ("T", "Y", 3),
    ("U", "V", 3), ("V", "W", 2), ("W", "X", 2), ("X", "Y", 2)
]

for u, v, weight in edges:
    graph.add_edge(u, v, weight=weight)

criteria = ["edge_difference", "shortcuts_added", "edges_removed"]
online_options = [True, False]

for criterion in criteria:
    for online in online_options:
        print(f"Criterion: {criterion}")
        print(f"Online calculation: {online}")
        graph_copy = graph.copy()
        ch_graph, node_order, shortcuts_added = create_contraction_hierarchy(
            graph_copy, online=online, criterion=criterion
        )

       # print(f"Shortcuts added: {shortcuts_added}")
        print("Node Order:", node_order)

        source_node = "A"
        target_node = "Y"
        shortest_path, path_length = find_shortest_path_custom(
            ch_graph, source_node, target_node, node_order
        )

        print("Shortest Path:", shortest_path)
        print("Shortest Path Length:", path_length)
