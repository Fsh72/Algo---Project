import osmnx as ox
import networkx as nx
import heapq
import copy
import time
import psutil

class ContractionHierarchies:
    def __init__(self, graph, order_strategy="default"):
        self.original_graph = graph  # Keep the original graph
        self.contracted_graph = copy.deepcopy(graph)  # Copy for modifications
        self.rank = {}  # Node ranking for contraction
        self.shortcuts = {}  # Store shortcut edges
        self.order = []  # Contraction order
        self.order_strategy = order_strategy  # "default" or "degree"

    def compute_node_order(self):
        """Compute contraction order based on the selected strategy."""
        if self.order_strategy == "default":
            # Default heuristic: Lower degree nodes contracted first
            self.order = sorted(self.contracted_graph.nodes(), key=lambda n: self.contracted_graph.degree(n))
        elif self.order_strategy == "degree":
            # Degree-based ordering: Higher degree nodes are contracted first
            self.order = sorted(self.contracted_graph.nodes(), key=lambda n: -self.contracted_graph.degree(n))

        self.rank = {node: i for i, node in enumerate(self.order)}

    def contract_node(self, node):
        """Contract a node and add necessary shortcuts."""
        neighbors = list(self.contracted_graph.neighbors(node))
        for i in range(len(neighbors)):
            for j in range(i + 1, len(neighbors)):
                u, v = neighbors[i], neighbors[j]
                if not self.contracted_graph.has_edge(u, v):
                    weight_u = float(self.contracted_graph[node][u].get("length", 1.0))
                    weight_v = float(self.contracted_graph[node][v].get("length", 1.0))
                    shortcut_weight = weight_u + weight_v

                    self.contracted_graph.add_edge(u, v, length=shortcut_weight)
                    self.shortcuts[(u, v)] = shortcut_weight

    def preprocess(self):
        """Preprocess the graph to build contraction hierarchies."""
        self.compute_node_order()
        for node in self.order:
            self.contract_node(node)

    def bidirectional_dijkstra(self, source, target):
        """Bidirectional search for shortest path using CH."""
        if source not in self.contracted_graph or target not in self.contracted_graph:
            raise ValueError(f"One or both nodes {source}, {target} are missing in the graph.")

        if source == target:
            return 0

        forward_pq = []
        backward_pq = []

        forward_dist = {node: float("inf") for node in self.contracted_graph.nodes()}
        backward_dist = {node: float("inf") for node in self.contracted_graph.nodes()}

        forward_dist[source] = 0
        backward_dist[target] = 0

        heapq.heappush(forward_pq, (0, source))
        heapq.heappush(backward_pq, (0, target))

        visited_forward = set()
        visited_backward = set()

        best_meeting_node = None
        best_path = float("inf")

        while forward_pq or backward_pq:
            # Forward search step
            if forward_pq:
                forward_cost, forward_node = heapq.heappop(forward_pq)
                if forward_node in visited_forward:
                    continue
                visited_forward.add(forward_node)

                if forward_node in visited_backward:
                    total_cost = forward_dist[forward_node] + backward_dist[forward_node]
                    if total_cost < best_path:
                        best_meeting_node = forward_node
                        best_path = total_cost

                for neighbor in self.contracted_graph.neighbors(forward_node):
                    weight = float(self.contracted_graph[forward_node][neighbor].get("length", 1.0))
                    new_dist = forward_dist[forward_node] + weight
                    if new_dist < forward_dist[neighbor]:
                        forward_dist[neighbor] = new_dist
                        heapq.heappush(forward_pq, (new_dist, neighbor))

            # Backward search step
            if backward_pq:
                backward_cost, backward_node = heapq.heappop(backward_pq)
                if backward_node in visited_backward:
                    continue
                visited_backward.add(backward_node)

                if backward_node in visited_forward:
                    total_cost = forward_dist[backward_node] + backward_dist[backward_node]
                    if total_cost < best_path:
                        best_meeting_node = backward_node
                        best_path = total_cost

                for neighbor in self.contracted_graph.neighbors(backward_node):
                    weight = float(self.contracted_graph[backward_node][neighbor].get("length", 1.0))
                    new_dist = backward_dist[backward_node] + weight
                    if new_dist < backward_dist[neighbor]:
                        backward_dist[neighbor] = new_dist
                        heapq.heappush(backward_pq, (new_dist, neighbor))

        return best_path if best_path < float("inf") else None

def memory_usage():
    """Returns current memory usage in MB."""
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)  # Convert bytes to MB


# Load a real-world road network using osmnx
city_name = "Falcon, Colorado, USA"
print(f"Loading road network for {city_name}...")
G = ox.graph_from_place(city_name, network_type="drive")

# Convert to an undirected graph
G = G.to_undirected()

# Ensure all edges have a "length" attribute
for u, v, data in G.edges(data=True):
    if "length" not in data:
        G[u][v]["length"] = 1.0  # Assign a default value if missing

# Select random nodes for source and target
nodes = list(G.nodes())
source, target = nodes[0], nodes[-1]  # Choosing first and last nodes for testing

# Compare different node ordering strategies
for strategy in ["default", "degree"]:
    print(f"\nTesting Contraction Hierarchies with {strategy} node ordering...")

    # Measure initial memory usage
    initial_memory = memory_usage()

    # Run Contraction Hierarchies
    ch = ContractionHierarchies(G, order_strategy=strategy)

    # Preprocessing (this step is slow)
    start_preprocess = time.time()
    ch.preprocess()
    end_preprocess = time.time()

    # Measure memory after preprocessing
    preprocess_memory = memory_usage()

    print(f"Preprocessing Time ({strategy}): {end_preprocess - start_preprocess:.2f} seconds")
    print(f"Memory Usage after Preprocessing ({strategy}): {preprocess_memory - initial_memory:.2f} MB")

    # Query shortest path using CH with bidirectional Dijkstra
    start_query = time.time()
    shortest_path_length = ch.bidirectional_dijkstra(source, target)
    end_query = time.time()

    # Measure memory after query
    query_memory = memory_usage()

    print(f"Shortest Path ({strategy}) from {source} to {target}: {shortest_path_length} meters")
    print(f"Query Time ({strategy}): {end_query - start_query:.4f} seconds")
    print(f"Memory Usage after Query ({strategy}): {query_memory - preprocess_memory:.2f} MB")
