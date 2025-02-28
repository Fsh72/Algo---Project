import heapq


def bidirectional_dijkstra(graph, source, target, node_order_map):


    # Initialize priority queues and distance dictionaries
    forward_queue = [(0, source)]
    backward_queue = [(0, target)]
    forward_dist = {source: 0}
    backward_dist = {target: 0}
    forward_pred = {source: None}
    backward_pred = {target: None}
    best_meeting_node = None
    best_path_length = float("inf")

    while forward_queue and backward_queue:
        # Get the minimum cost from both queues
        forward_min = forward_queue[0][0] if forward_queue else float('inf')
        backward_min = backward_queue[0][0] if backward_queue else float('inf')

        # **Improved stopping condition**
        if forward_min + backward_min >= best_path_length:
            break  # Stop early if no better path can be found

        # Expand the search frontier with lower priority
        if forward_queue and (not backward_queue or forward_min < backward_min):
            forward_cost, forward_node = heapq.heappop(forward_queue)

            if forward_node in backward_dist:
                total_cost = forward_cost + backward_dist[forward_node]
                if total_cost < best_path_length:
                    best_path_length = total_cost
                    best_meeting_node = forward_node

            for neighbor, edge_data in graph[forward_node].items():
                new_cost = forward_cost + edge_data["weight"]
                if neighbor not in forward_dist or new_cost < forward_dist[neighbor]:
                    forward_dist[neighbor] = new_cost
                    heapq.heappush(forward_queue, (new_cost, neighbor))

        else:
            backward_cost, backward_node = heapq.heappop(backward_queue)

            if backward_node in forward_dist:
                total_cost = backward_cost + forward_dist[backward_node]
                if total_cost < best_path_length:
                    best_path_length = total_cost
                    best_meeting_node = backward_node

            for neighbor, edge_data in graph[backward_node].items():
                new_cost = backward_cost + edge_data["weight"]
                if neighbor not in backward_dist or new_cost < backward_dist[neighbor]:
                    backward_dist[neighbor] = new_cost
                    heapq.heappush(backward_queue, (new_cost, neighbor))

    return best_meeting_node, best_path_length
