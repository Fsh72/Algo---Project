
import heapq


def bidirectional_dijkstra(graph, source, target, node_order_map):
    """Bidirectional Dijkstra's algorithm for contraction hierarchies."""

    # Initialize priority queues and distance dictionaries
    forward_queue = [(0, source)]
    backward_queue = [(0, target)]
    forward_dist = {source: 0}
    backward_dist = {target: 0}
    forward_pred = {source: None}
    backward_pred = {target: None}
    best_meeting_node = None
    best_path_length = float("inf")

    while forward_queue or backward_queue:
        # Forward search
        if forward_queue:
            forward_cost, forward_node = heapq.heappop(forward_queue)
            if forward_node in backward_dist:
                total_cost = forward_cost + backward_dist[forward_node]
                if total_cost < best_path_length:
                    best_path_length = total_cost
                    best_meeting_node = forward_node

            for neighbor, edge_data in graph[forward_node].items():
                cost = forward_cost + edge_data["weight"]
                if neighbor not in forward_dist or cost < forward_dist[neighbor]:
                    forward_dist[neighbor] = cost
                    forward_pred[neighbor] = forward_node
                    heapq.heappush(forward_queue, (cost, neighbor))

        # Backward search
        if backward_queue:
            backward_cost, backward_node = heapq.heappop(backward_queue)
            if backward_node in forward_dist:
                total_cost = backward_cost + forward_dist[backward_node]
                if total_cost < best_path_length:
                    best_path_length = total_cost
                    best_meeting_node = backward_node

            for neighbor, edge_data in graph[backward_node].items():
                cost = backward_cost + edge_data["weight"]
                if neighbor not in backward_dist or cost < backward_dist[neighbor]:
                    backward_dist[neighbor] = cost
                    backward_pred[neighbor] = backward_node
                    heapq.heappush(backward_queue, (cost, neighbor))

    # Reconstruct the shortest path
    if best_meeting_node is None:
        return None, float("inf")

    path = []
    node = best_meeting_node
    while node is not None:
        path.append(node)
        node = forward_pred[node]
    path.reverse()

    node = backward_pred[best_meeting_node]
    while node is not None:
        path.append(node)
        node = backward_pred[node]

    return path, best_path_length
