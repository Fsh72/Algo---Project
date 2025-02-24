import osmnx as ox
import networkx as nx
import heapq
import time
import tracemalloc
import random


### Step 1: Compute Node Ordering - Edge Difference ###
def compute_edge_difference_ranking(G):
    """Computes node ranking based on Edge Difference (ED)."""
    node_ranks = {}
    pq = []

    for node in G.nodes():
        edges_before = len(list(G.edges(node)))
        neighbors = list(G.neighbors(node))
        potential_shortcuts = (len(neighbors) * (len(neighbors) - 1)) // 2
        edge_difference = potential_shortcuts - edges_before

        heapq.heappush(pq, (edge_difference, node))

    rank = 0
    while pq:
        _, node = heapq.heappop(pq)
        node_ranks[node] = rank
        rank += 1

    return node_ranks


### Step 2: Compute Node Ordering - Rank-by-Degree ###
def compute_degree_ranking(G):
    """Computes node ranking based on node degree."""
    degree_order = sorted(G.nodes(), key=lambda node: G.degree(node))
    return {node: rank for rank, node in enumerate(degree_order)}


### Step 3: Contract Graph ###
def contract_graph(G, node_order):
    """Contracts the graph based on node ordering while preserving node attributes."""
    G_contracted = G.copy()
    overlay_graph = nx.Graph()
    shortcut_count = {}
    node_levels = {}

    for node in node_order:
        if node not in G_contracted:
            continue
        contract_node(G_contracted, node, overlay_graph, shortcut_count, node_levels)

    for u, v, data in overlay_graph.edges(data=True):
        if not G_contracted.has_edge(u, v):
            G_contracted.add_edge(u, v, **data)

    for node in G_contracted.nodes():
        if node in G.nodes():
            G_contracted.nodes[node]["x"] = G.nodes[node].get("x", None)
            G_contracted.nodes[node]["y"] = G.nodes[node].get("y", None)
            G_contracted.nodes[node]["level"] = node_levels.get(node, 0)

    return G_contracted, len(shortcut_count)


### Step 4: Contract Node Function ###
def contract_node(G, node, overlay_graph, shortcut_count, node_levels, max_hops=5):
    """Contracts a node by removing it and adding shortcut edges where necessary."""
    if node not in G:
        return

    neighbors = list(G.neighbors(node))
    edge_weights = {neighbor: G[node][neighbor].get("length", 1) for neighbor in neighbors}

    if len(neighbors) < 2:
        return

    for i in range(len(neighbors)):
        for j in range(i + 1, len(neighbors)):
            u, v = neighbors[i], neighbors[j]

            if overlay_graph.has_edge(u, v) or G.has_edge(u, v):
                continue

            shortcut_weight = edge_weights[u] + edge_weights[v]

            witness_length = nx.single_source_dijkstra_path_length(
                G, source=u, cutoff=max_hops, weight="length"
            ).get(v, float("inf"))

            if witness_length <= shortcut_weight:
                continue

            overlay_graph.add_edge(u, v, length=shortcut_weight)
            shortcut_count[(u, v)] = shortcut_count.get((u, v), 0) + 1

    node_levels[node] = len(G)
    G.remove_node(node)


### Step 5: CH-Bidirectional Dijkstra for Shortest Paths ###
def ch_shortest_path(G, source, target):
    """Finds the shortest path using CH-Bidirectional Dijkstra."""
    if source not in G or target not in G:
        return float("inf")

    forward_queue = [(0, source)]
    reverse_queue = [(0, target)]
    forward_dist = {source: 0}
    reverse_dist = {target: 0}
    forward_visited = {}
    reverse_visited = {}

    best_path = float("inf")

    while forward_queue or reverse_queue:
        if forward_queue:
            f_dist, f_node = heapq.heappop(forward_queue)
            forward_visited[f_node] = f_dist
            if f_node in reverse_visited:
                best_path = min(best_path, f_dist + reverse_visited[f_node])

            for neighbor in G.neighbors(f_node):
                weight = G[f_node][neighbor].get("length", 1)
                new_dist = f_dist + weight
                if neighbor not in forward_dist or new_dist < forward_dist[neighbor]:
                    forward_dist[neighbor] = new_dist
                    heapq.heappush(forward_queue, (new_dist, neighbor))

        if reverse_queue:
            r_dist, r_node = heapq.heappop(reverse_queue)
            reverse_visited[r_node] = r_dist
            if r_node in forward_visited:
                best_path = min(best_path, r_dist + forward_visited[r_node])

            for neighbor in G.neighbors(r_node):
                weight = G[r_node][neighbor].get("length", 1)
                new_dist = r_dist + weight
                if neighbor not in reverse_dist or new_dist < reverse_dist[neighbor]:
                    reverse_dist[neighbor] = new_dist
                    heapq.heappush(reverse_queue, (new_dist, neighbor))

    return best_path


### Step 6: Run Query Experiments ###
def query_performance(G_ch):
    """Measures CH query time with multiple random queries."""
    nodes = list(G_ch.nodes())
    num_queries = 50
    total_time = 0

    for _ in range(num_queries):
        source, target = random.sample(nodes, 2)
        start_time = time.time()
        ch_shortest_path(G_ch, source, target)
        total_time += time.time() - start_time

    avg_time = total_time / num_queries
    return avg_time


### Step 7: Compare Orderings ###
def compare_orderings(G):
    """Compares Edge-Difference and Rank-by-Degree CH performance."""

    results = {}

    for method, ordering_func in {
        "Edge Difference": compute_edge_difference_ranking,
        "Rank by Degree": compute_degree_ranking,
    }.items():
        print(f"\nProcessing CH using {method} ordering...")

        tracemalloc.start()
        start_time = time.time()

        node_order = ordering_func(G)
        G_ch, num_shortcuts = contract_graph(G, node_order)

        time_taken = time.time() - start_time
        mem_usage = tracemalloc.get_traced_memory()[1] / (1024 * 1024)
        tracemalloc.stop()

        query_time = query_performance(G_ch)

        results[method] = {
            "Nodes": len(G_ch.nodes()),
            "Edges": len(G_ch.edges()),
            "Shortcuts": num_shortcuts,
            "Time (s)": time_taken,
            "Memory (MB)": mem_usage,
            "Avg Query Time (ms)": query_time * 1000,
        }

    return results


### Step 8: Run Experiment ###
def run_experiment():
    """Runs CH on a real road network and compares methods."""
    print("Loading real-world road network...")
    place_name = "New York, USA"
    G = ox.graph_from_place(place_name, network_type='drive')
    G = nx.Graph(G)

    print(f"Original graph: {len(G.nodes())} nodes, {len(G.edges())} edges")

    results = compare_orderings(G)

    print("\nComparison Results:")
    for method, data in results.items():
        print(f"\n{method} Ordering:")
        for metric, value in data.items():
            print(f"  {metric}: {value}")

    print("\nSaving contracted graph...")
    G_ch, _ = contract_graph(G, compute_edge_difference_ranking(G))
    ox.save_graphml(nx.MultiDiGraph(G_ch), filepath="NewYork_CH.graphml")
    print("Graph saved as NewYork_CH.graphml")


if __name__ == "__main__":
    run_experiment()
