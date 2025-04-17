from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from graph_operations import generate_random_graph, load_graph_from_osm

class Graph:
    """
    Graph class represents a weighted undirected graph and provides methods to manipulate and visualize it.
    Attributes:
        adjacency_list (defaultdict): A dictionary where keys are nodes and values are lists of tuples representing 
            neighbors and their respective edge weights.
        tsp_paths (dict): A dictionary to store Traveling Salesman Problem (TSP) paths for different vehicles.
    Methods:
        __init__():
            Initializes an empty graph with an adjacency list and a dictionary for TSP paths.
        add_edge(u, v, weight):
            Adds an undirected edge between nodes `u` and `v` with the specified `weight`.
        get_edge_weight(u, v):
            Retrieves the weight of the edge between nodes `u` and `v`. Returns 0 if no edge exists.
        get_neighbors(u):
            Returns a list of neighbors and their respective edge weights for the given node `u`.
        set_tsp_path(vehicle_id, path):
            Stores the TSP path for a specific vehicle identified by `vehicle_id`.
        get_tsp_path(vehicle_id):
            Retrieves the TSP path for the specified `vehicle_id`. Returns an empty list if no path is found.
        get_all_tsp_paths():
            Returns all stored TSP paths as a dictionary.
        draw_graph():
            Visualizes the graph using NetworkX and Matplotlib. Nodes are displayed with labels, and edges are labeled 
            with their weights.
    """
    def __init__(self):
        self.adjacency_list = defaultdict(list)
        self.tsp_paths = {}

    def add_edge(self, u, v, weight):
        """
        Adds an edge between two vertices in the graph with a specified weight.

        Parameters:
            u (hashable): The starting vertex of the edge.
            v (hashable): The ending vertex of the edge.
            weight (float): The weight or cost associated with the edge.

        Modifies:
            Updates the adjacency list to include the edge from `u` to `v` and 
            from `v` to `u` with the given weight.

        Example:
            graph.add_edge('A', 'B', 3.5)
        """
        self.adjacency_list[u].append((v, weight))
        self.adjacency_list[v].append((u, weight))

    def get_edge_weight(self, u, v):
        """
        Retrieves the weight of the edge between two vertices in the graph.

        Args:
            u (hashable): The starting vertex of the edge.
            v (hashable): The ending vertex of the edge.

        Returns:
            int or float: The weight of the edge if it exists, otherwise 0.
        """
        for neighbor, weight in self.adjacency_list[u]:
            if neighbor == v:
                return weight
        return 0

    def get_neighbors(self, u):
        """
        Retrieve the neighbors of a given node in the graph.

        Args:
            u (hashable): The node for which to retrieve the neighbors. 
                          It must be a valid key in the adjacency list.

        Returns:
            list: A list of nodes that are neighbors of the given node `u`.
        """
        return self.adjacency_list[u]

    def set_tsp_path(self, vehicle_id, path):
        """
        Sets the Traveling Salesperson Problem (TSP) path for a specific vehicle.

        Args:
            vehicle_id (int): The identifier of the vehicle for which the TSP path is being set.
            path (list): A list representing the TSP path, where each element is a node in the path.

        Returns:
            None
        """
        self.tsp_paths[vehicle_id] = path

    def get_tsp_path(self, vehicle_id):
        """
        Retrieve the Traveling Salesperson Problem (TSP) path for a specific vehicle.

        Args:
            vehicle_id (int): The unique identifier of the vehicle.

        Returns:
            list: A list representing the TSP path for the given vehicle. 
                  Returns an empty list if no path is found for the vehicle.
        """
        return self.tsp_paths.get(vehicle_id, [])

    def get_all_tsp_paths(self):
        """
        Retrieve all precomputed Traveling Salesman Problem (TSP) paths.

        Returns:
            list: A list containing all TSP paths.
        """
        return self.tsp_paths
    
    def draw_graph(self):
        """
        Draws the graph represented by the adjacency list of the current object.
        This method uses the NetworkX library to create a visual representation of the graph.
        Each node and edge is displayed, with edges labeled by their weights.
        The graph is laid out using the spring layout algorithm, which positions nodes
        to minimize edge crossings and create a visually appealing structure.
        Steps:
        - Creates a NetworkX graph from the adjacency list.
        - Adds edges with weights to the graph.
        - Computes positions for nodes using the spring layout.
        - Draws the graph with labeled nodes and edges.
        - Displays the graph using Matplotlib.
        Note:
            - The adjacency list should be a dictionary where keys are nodes and values
              are lists of tuples (neighbor, weight).
            - Requires the `networkx` and `matplotlib` libraries.
        Example:
            adjacency_list = {
                'A': [('B', 3), ('C', 1)],
                'B': [('A', 3), ('C', 7)],
                'C': [('A', 1), ('B', 7)]
            }
            graph = Graph(adjacency_list)
            graph.draw_graph()
        """
        g = nx.Graph()
        for u in self.adjacency_list:
            for v, weight in self.adjacency_list[u]:
                g.add_edge(u, v, weight=weight)

        pos = nx.spring_layout(g)  # Positionnement des nœuds
        edge_labels = nx.get_edge_attributes(g, 'weight')

        nx.draw(g, pos, with_labels=True, node_color='lightblue', node_size=500, font_size=10)
        nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
        plt.show()
