import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import heapq
import math
import os
import json


def haversine_distance(lat1, long1, lat2, long2):
    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(long1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(long2)

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    R = 6371  # Radius of the Earth in kilometers
    distance = R * c

    return distance
    # return dlon + dlat


def bfs(G, start_node, end_node):
    visited = set()
    queue = deque([start_node])

    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)

            if node == end_node:
                return visited, True

            # Add connected Nodes to queue
            connected_edges = G.edges(node, data=True)
            for u, v, data in connected_edges:
                if v not in visited:
                    queue.append(v)

    return visited, False


def a_star(G, start, end):
    visited = set()
    min_heap = []
    distance = haversine_distance(G.nodes[start]['x'], G.nodes[start]['y'], G.nodes[end]['x'], G.nodes[end]['y'])

    heapq.heappush(min_heap, (distance, start))

    while min_heap:
        _, node = heapq.heappop(min_heap)
        if node not in visited:
            visited.add(node)

            if node == end:
                # Found End
                return visited, True

            # Add connected Nodes to queue
            connected_edges = G.edges(node, data=True)
            for u, v, data in connected_edges:
                if v not in visited:
                    distance = haversine_distance(G.nodes[node]['x'], G.nodes[node]['y'], G.nodes[end]['x'], G.nodes[end]['y'])
                    heapq.heappush(min_heap, (distance, v))

    # Did Not Find End
    return visited, False


def load_city_graph(city_name):
    G = None
    path = f'{city_name}/{city_name}.graphml'
    if os.path.exists(path):
        print(f'Loading {city_name} From XML')
        G = ox.load_graphml(path)
        print(f'{len(G.nodes)} Total Nodes')
    else:
        print('File not Found')
        return

    with open(f'{city_name}/locations.json', 'r') as file:
        locations = json.load(file)

    return G, locations


def save_results(G, visited, start, end, start_location, end_location, fName):
    point_color = '#b407f2'
    text_color = 'red'
    subgraph = G.subgraph(visited)

    edge_colors = ['blue' if edge in subgraph.edges else 'gray' for edge in G.edges]

    fig, ax = ox.plot_graph(G,
                            figsize=(14, 14),  # Size of the plot
                            bgcolor='white',  # Background color
                            node_size=2,  # Size of the nodes
                            node_color='black',  # Color of the nodes
                            edge_color=edge_colors,  # Color of the edges
                            edge_linewidth=1,  # Width of the edges
                            show=False,  # Display the plot
                            save=True)

    # Plot Start and End in purple
    for node_index in range(len([start, end])):
        node = [start, end][node_index]
        label = [start_location, end_location][node_index]

        x, y = G.nodes[node]['x'], G.nodes[node]['y']
        ax.scatter(x, y, color=point_color, s=5, zorder=5)
        plt.annotate(label, (x, y), textcoords='offset points', xytext=(0, 10), ha='center', color=text_color, fontsize=8)

    plt.text(0.95, 0.05, f'{len(G.nodes)} Total Nodes\n{len(visited)} Visited Nodes', fontsize=14, ha='right', va='bottom', transform=plt.gcf().transFigure, color=text_color)

    # Save Figure to file
    plt.title(fName.replace('/', ': ')[:-4], fontsize=20, color=text_color)
    plt.savefig(fName, dpi=1000, bbox_inches='tight')
    plt.close()
    return


def main():
    city_name = 'Manhattan'
    algorithm = 'AStar'

    start_location = 'Central Park'
    end_location = 'Apollo Theater'

    G, locations = load_city_graph(city_name)

    times_square = locations[start_location]
    empire_state = locations[end_location]

    start = ox.nearest_nodes(G, X=times_square['longitude'], Y=times_square['latitude'])
    end = ox.nearest_nodes(G, X=empire_state['longitude'], Y=empire_state['latitude'])

    if algorithm == 'BFS':
        visited, end_reached = bfs(G, start, end)
    elif algorithm == 'AStar':
        visited, end_reached = a_star(G, start, end)
    else:
        print('Not Implemented')
        return

    if end_reached:
        print('Reached The End Node')
    else:
        print('Did Not Reach End Node')
    print(f'{len(visited)} Total Nodes Visited')

    fName = f'{city_name}/{algorithm} {start_location} To {end_location} Plot.png'
    save_results(G, visited, start, end, start_location, end_location, fName)
    print('Finished')
    return


if __name__ == "__main__":
    main()
