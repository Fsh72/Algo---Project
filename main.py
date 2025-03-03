import osmnx as ox
import networkx as nx
import time
import tracemalloc  # For detailed memory usage
import pandas as pd
from CH_fixed import create_contraction_hierarchy
from bidirectional_dijkstra_fixed import bidirectional_dijkstra
from bidirectional_dijkstra_fixed import bidirectional_dijkstra_classic

import random

def pick_random_node(G):
    """Picks a random node that has at least one connection."""
    node = random.choice(list(G.nodes))
    while G.degree(node) == 0:  # Ensure the node has at least one connection
        node = random.choice(list(G.nodes))
    return node

# ✅ Ensure Pandas Shows All Columns
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 1000)

# Start measuring overall memory usage
tracemalloc.start()

# Step 1: Download the road network of Falcon, Colorado
city_name = "Falcon, Colorado, USA"
print(f"Downloading graph for {city_name}...")
G = ox.graph_from_place(city_name, network_type="drive")

"""

# Save the graph after first download
ox.save_graphml(G, "Falcon.graphml")

# Next time, load the graph instead of downloading again
G = ox.load_graphml("Falcon.graphml")
"""

# Step 2: Add speed limits and travel times
G = ox.add_edge_speeds(G)
G = ox.add_edge_travel_times(G)

# Step 3: Project the graph to avoid sklearn dependency
G = ox.project_graph(G)

# Step 4: Convert MultiDiGraph to Graph (removes duplicate edges, keeps attributes)
G_undirected = nx.Graph(G)

# Select random source and target nodes
source = pick_random_node(G_undirected)
target = pick_random_node(G_undirected)

while source == target:
    target = pick_random_node(G_undirected)  # Ensure source and target are different
print(f"Randomly selected source: {source}, target: {target}")

# Step 5: Assign travel time as weight
for u, v, data in G_undirected.edges(data=True):
    data["weight"] = data.get("travel_time", data.get("length", 1) / 50.0)

# ✅ Define the 6 correct ordering criteria
ordering_methods = [
    ("edge_difference", True),
    ("edge_difference", False),
    ("shortcuts_added", True),
    ("shortcuts_added", False),
    ("edges_removed", True),
    ("edges_removed", False),
]

# ✅ Store results for comparison
results = []

for criterion, online in ordering_methods:
    ordering_name = f"{'Online' if online else 'Offline'} {criterion.replace('_', ' ').title()}"
    print(f"\n🔹 Running CH with Ordering: {ordering_name}...")

    # **Measure Preprocessing Time and Memory Usage**
    tracemalloc.reset_peak()
    start_preprocess = time.time()

    ch_graph, node_order, _ = create_contraction_hierarchy(G_undirected, online=online, criterion=criterion)

    end_preprocess = time.time()
    current_mem_pre, peak_mem_pre = tracemalloc.get_traced_memory()

    preprocessing_time = end_preprocess - start_preprocess
    preprocessing_memory = peak_mem_pre / 1024 / 1024

    print(f"✅ Preprocessing Completed: {preprocessing_time:.4f} sec, Memory: {preprocessing_memory:.2f} MB")

    # **Measure Query Time and Memory Usage for CH-Based BiDi Dijkstra**
    tracemalloc.reset_peak()
    start_query = time.time()

    node_order_map = {node: order for order, node in enumerate(node_order)}
    shortest_path_ch, path_length_ch = bidirectional_dijkstra(ch_graph, source, target, node_order_map)

    end_query = time.time()
    current_mem_query_ch, peak_mem_query_ch = tracemalloc.get_traced_memory()

    query_time_ch = end_query - start_query
    query_memory_ch = peak_mem_query_ch / 1024 / 1024

    print(f"✅ CH Query Completed: {query_time_ch:.4f} sec, Path Length: {path_length_ch:.2f}, Memory: {query_memory_ch:.2f} MB")

    # ✅ Store the results for CH Query
    results.append([ordering_name, preprocessing_time, preprocessing_memory, query_time_ch, path_length_ch, query_memory_ch])



# **Measure Query Time and Memory Usage for Classic BiDi Dijkstra**
tracemalloc.reset_peak()
start_query_classic = time.time()

shortest_path_orig, path_length_orig = bidirectional_dijkstra_classic(G_undirected, source, target)

end_query_classic = time.time()
current_mem_query_classic, peak_mem_query_classic = tracemalloc.get_traced_memory()

query_time_classic = end_query_classic - start_query_classic
query_memory_classic = peak_mem_query_classic / 1024 / 1024

print("\n🔹 Results for Classic Bidirectional Dijkstra:")
print(f"Query Time (s): {query_time_classic:.4f}")
print(f"Path Length: {path_length_orig:.2f}")
print(f"Query Memory (MB): {query_memory_classic:.2f}")

# ✅ Store Classic BiDi Dijkstra results in the DataFrame
results.append(["Classic Bidirectional Dijkstra", None, None, query_time_classic, path_length_orig, query_memory_classic])

# **Measure Total Memory Usage**
current_mem_total, peak_mem_total = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(f"\n**Total Peak Memory Usage:** {peak_mem_total / 1024 / 1024:.2f} MB")

# ✅ Display Results as a Table
df_results = pd.DataFrame(results, columns=["Ordering Method", "Preprocessing Time (s)", "Preprocessing Memory (MB)",
                                            "Query Time (s)", "Path Length", "Query Memory (MB)"])

# ✅ Print Full Table Without Truncation
print("\n🔹 CH Ordering Comparison Results:")
print(df_results)

