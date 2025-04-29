import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import random
from geopy.distance import geodesic
import geopandas as gpd
from shapely.geometry import Point
from pyproj import Transformer
import pickle
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Récupérer les chemins depuis le fichier .env
geonames_path = os.getenv("GEONAMES_PATH")
shapefile_path = os.getenv("SHAPEFILE_PATH")

class Graph:
    def __init__(self):
        """
        Initializes a new instance of the graph class.

        Attributes:
            graph (networkx.Graph): An instance of a NetworkX graph used to represent the graph structure.
            tsp_paths (dict): A dictionary to store paths related to the Traveling Salesman Problem (TSP).
        """
        self.graph = nx.Graph()
        self.tsp_paths = {}
        
    def get_infos(self):
        """
        Returns detailed information about the graph.

        Returns:
            dict: A dictionary containing various properties of the graph.
        """
        infos = {
            "number_of_nodes": self.graph.number_of_nodes(),
            "number_of_edges": self.graph.number_of_edges(),
            "average_degree": sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes(),
            "density": nx.density(self.graph),
            "is_connected": nx.is_connected(self.graph) if nx.is_connected(self.graph) else False,
            "number_of_connected_components": nx.number_connected_components(self.graph),
            "average_clustering_coefficient": nx.average_clustering(self.graph),
        }

        return infos

    def add_edge(self, u, v, weight=1):
        """
        Adds an edge between two nodes in the graph with an optional weight.

        Parameters:
            u (hashable): The starting node of the edge.
            v (hashable): The ending node of the edge.
            weight (int, optional): The weight of the edge. Defaults to 1.

        Returns:
            None
        """
        self.graph.add_edge(u, v, weight=weight)

    def get_edge_weight(self, u, v):
        """
        Retrieve the weight of an edge between two nodes in the graph.

        Args:
            u (hashable): The starting node of the edge.
            v (hashable): The ending node of the edge.

        Returns:
            int or float: The weight of the edge if it exists, otherwise 0.
        """
        return self.graph[u][v]['weight'] if self.graph.has_edge(u, v) else 0
    
    def get_neighbors(self, u):
        """
        Retrieve the neighbors of a given node in the graph.

        Args:
            u: The node for which to find the neighbors.

        Returns:
            list: A list of neighboring nodes connected to the given node.
        """
        return list(self.graph.neighbors(u))

    def set_tsp_path(self, vehicle_id, path):
        """
        Sets the Traveling Salesman Problem (TSP) path for a specific vehicle.

        Args:
            vehicle_id (int): The identifier of the vehicle.
            path (list): The TSP path represented as a list of nodes or waypoints.

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
    
    def save(self, filepath):
        """
        Serializes the current graph object and saves it to the specified file.

        Args:
            filepath (str): The path to the file where the graph object will be saved.

        Raises:
            IOError: If there is an issue writing to the specified file.

        Example:
            graph.save("graph_data.pkl")
        """
        with open(filepath, 'wb') as f:
            pickle.dump(self, f)
        print(f"Graph serialized and saved to {filepath}")

    @staticmethod
    def load(filepath):
        """
        Deserializes and loads a graph object from a specified file.

        Args:
            filepath (str): The path to the file containing the serialized graph object.

        Returns:
            object: The deserialized graph object.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            IOError: If there is an error reading the file.
            pickle.UnpicklingError: If the file does not contain a valid serialized object.

        Example:
            graph = load('/path/to/graph.pkl')
        """
        with open(filepath, 'rb') as f:
            graph = pickle.load(f)
        print(f"Graph deserialized from {filepath}")
        return graph
    
    def calculate_distances(self, vehicle_paths):
        """
        Calculate the distance traveled by each vehicle and the total distance.

        Args:
            vehicle_paths (dict): A dictionary where keys are vehicle IDs and values are lists of nodes representing the paths.

        Returns:
            tuple: (distances_per_vehicle, total_distance)
                - distances_per_vehicle (dict): A dictionary with vehicle IDs as keys and their respective distances as values.
                - total_distance (float): The total distance traveled by all vehicles.
        """
        distances_per_vehicle = {}
        total_distance = 0

        for vehicle_id, path in vehicle_paths.items():
            distance = 0
            for i in range(len(path) - 1):
                distance += self.get_edge_weight(path[i], path[i + 1])
            distances_per_vehicle[vehicle_id] = distance
            total_distance += distance

        return distances_per_vehicle, total_distance

    def save_graph_svg(self, path, with_weights=True, vehicle_paths=None, max_labels=250):
        """
        Save the graph as an SVG file with optional geographic context and visual enhancements.

        Parameters:
            path (str): The file path where the SVG will be saved.
            with_weights (bool, optional): Whether to display edge weights on the graph. Defaults to True.
            vehicle_paths (dict, optional): A dictionary where keys are vehicle IDs and values are lists of nodes
                                            representing the paths of the vehicles. These paths will be highlighted.
            max_labels (int, optional): The maximum number of nodes for which labels and weights will be displayed.
                                        Defaults to 250.

        Output:
            - Saves the graph visualization as an SVG file at the specified `path`.
        """
        fig, ax = plt.subplots(figsize=(10, 10))

        # Load France shapefile if available
        if os.path.exists("./data/FR/ne_10m_admin_0_countries_fra/ne_10m_admin_0_countries_fra.shp"):
            france = gpd.read_file("./data/FR/ne_10m_admin_0_countries_fra/ne_10m_admin_0_countries_fra.shp")
            france = france.to_crs(epsg=3857)

            # Reproject node positions
            nodes = [{'city': name, 'geometry': Point(lon, lat)} for name, (lon, lat) in self.positions.items()]
            gdf_nodes = gpd.GeoDataFrame(nodes, crs="EPSG:4326").to_crs(epsg=3857)
            new_positions = {row['city']: (row.geometry.x, row.geometry.y) for _, row in gdf_nodes.iterrows()}

            # Plot France
            france.plot(ax=ax, color='whitesmoke', edgecolor='black')

            # Set geographic boundaries
            transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
            minx, miny = transformer.transform(-5.14, 41.33)
            maxx, maxy = transformer.transform(9.56, 51.09)
            ax.set_xlim(minx, maxx)
            ax.set_ylim(miny, maxy)
        else:
            new_positions = self.positions

        # Draw all edges in gray
        nx.draw_networkx_edges(self.graph, new_positions, edge_color='gray', ax=ax, width=0.5)

        # Draw all nodes
        nx.draw_networkx_nodes(self.graph, new_positions, node_color='orange', node_size=25, ax=ax)

        # Display node labels and edge weights if the number of nodes is small enough
        if len(self.graph.nodes) <= max_labels:
            nx.draw_networkx_labels(self.graph, new_positions, font_size=4, ax=ax)
            if with_weights:
                edge_labels = nx.get_edge_attributes(self.graph, 'weight')
                nx.draw_networkx_edge_labels(self.graph, new_positions, edge_labels=edge_labels, font_size=3, ax=ax)
        else:
            print(f"The number of cities ({len(self.graph.nodes)}) exceeds {max_labels}. Labels and weights will not be displayed.")

        # Highlight vehicle paths
        if vehicle_paths:
            colors = [
                'red', 'blue', 'green', 'purple', 'cyan', 'orange', 'pink', 'brown', 
                'yellow', 'lime', 'magenta', 'teal', 'gold', 'navy', 'maroon', 'olive', 
                'coral', 'turquoise', 'indigo', 'violet', 'crimson', 'chartreuse', 
                'darkorange', 'darkgreen', 'darkblue', 'darkred', 'darkcyan', 'darkmagenta'
            ]  # Add more colors if needed

            distances_per_vehicle, total_distance = self.calculate_distances(vehicle_paths)

            for vehicle_id, path_nodes in vehicle_paths.items():
                color = colors[vehicle_id % len(colors)]  # Cycle through colors if there are more vehicles than colors
                
                # Filter edges to include only existing edges in the graph
                edges = [
                    (path_nodes[i], path_nodes[i + 1])
                    for i in range(len(path_nodes) - 1)
                    if self.graph.has_edge(path_nodes[i], path_nodes[i + 1])
                ]
                
                # Draw the valid edges
                nx.draw_networkx_edges(self.graph, new_positions, edgelist=edges, edge_color=color, width=0.75, ax=ax)

                # Highlight the starting point of the vehicle
                start_node = path_nodes[0]
                nx.draw_networkx_nodes(self.graph, new_positions, nodelist=[start_node], node_color=color, node_size=50, ax=ax)

            # Draw the distance information in a box
            box_width = 0.20  # Narrower box
            box_height = 0.05 * (len(vehicle_paths) + 2)  # Adjust height based on the number of vehicles
            box_x = 0.01  # Move the box to the bottom-left corner
            box_y = 0.01

            # Add a rectangle for the box
            rect = plt.Rectangle((box_x, box_y), box_width, box_height, transform=ax.transAxes,
                                color='black', alpha=0.6, zorder=10, edgecolor='black')
            ax.add_patch(rect)

            # Add text and color rectangles for each vehicle's distance
            y_offset = box_y + box_height - 0.05
            for vehicle_id, distance in distances_per_vehicle.items():
                # Add a small rectangle with the vehicle's color
                rect_y_centered = y_offset - 0.015  # Center the rectangle vertically with the text
                ax.add_patch(plt.Rectangle((box_x + 0.01, rect_y_centered), 0.02, 0.03, transform=ax.transAxes,
                                            color=colors[vehicle_id % len(colors)], zorder=11))
                # Add the distance text in white
                ax.text(box_x + 0.04, y_offset, f"Vehicle {vehicle_id + 1}: {distance:.2f} km",
                        transform=ax.transAxes, fontsize=8, color='white', zorder=12)
                y_offset -= 0.05

            # Add total distance
            ax.text(box_x + 0.01, y_offset, f"Total: {total_distance:.2f} km",
                    transform=ax.transAxes, fontsize=9, color='white', zorder=12)

        plt.axis('off')
        plt.tight_layout()

        # Save the graph to the specified path
        plt.savefig(path, format='svg', bbox_inches='tight')
        plt.clf()

    def save_graph_png(self, path, with_weights=True, vehicle_paths=None, max_labels=250, dpi=300):
        """
        Save the graph as a PNG file with optional geographic context and visual enhancements.

        Parameters:
            path (str): The file path where the PNG will be saved.
            with_weights (bool, optional): Whether to display edge weights on the graph. Defaults to True.
            vehicle_paths (dict, optional): A dictionary where keys are vehicle IDs and values are lists of nodes
                                            representing the paths of the vehicles. These paths will be highlighted.
            max_labels (int, optional): The maximum number of nodes for which labels and weights will be displayed.
                                        Defaults to 250.
            dpi (int, optional): The resolution of the output image in dots per inch. Defaults to 300.

        Output:
            - Saves the graph visualization as a PNG file at the specified `path`.
        """
        fig, ax = plt.subplots(figsize=(10, 10))

        # Load France shapefile if available
        if os.path.exists("./data/FR/ne_10m_admin_0_countries_fra/ne_10m_admin_0_countries_fra.shp"):
            france = gpd.read_file("./data/FR/ne_10m_admin_0_countries_fra/ne_10m_admin_0_countries_fra.shp")
            france = france.to_crs(epsg=3857)

            # Reproject node positions
            nodes = [{'city': name, 'geometry': Point(lon, lat)} for name, (lon, lat) in self.positions.items()]
            gdf_nodes = gpd.GeoDataFrame(nodes, crs="EPSG:4326").to_crs(epsg=3857)
            new_positions = {row['city']: (row.geometry.x, row.geometry.y) for _, row in gdf_nodes.iterrows()}

            # Plot France
            france.plot(ax=ax, color='whitesmoke', edgecolor='black')

            # Set geographic boundaries
            transformer = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
            minx, miny = transformer.transform(-5.14, 41.33)
            maxx, maxy = transformer.transform(9.56, 51.09)
            ax.set_xlim(minx, maxx)
            ax.set_ylim(miny, maxy)
        else:
            new_positions = self.positions

        # Draw all edges in gray
        nx.draw_networkx_edges(self.graph, new_positions, edge_color='gray', ax=ax, width=0.5)

        # Draw all nodes
        nx.draw_networkx_nodes(self.graph, new_positions, node_color='orange', node_size=25, ax=ax)

        # Display node labels and edge weights if the number of nodes is small enough
        if len(self.graph.nodes) <= max_labels:
            nx.draw_networkx_labels(self.graph, new_positions, font_size=4, ax=ax)
            if with_weights:
                edge_labels = nx.get_edge_attributes(self.graph, 'weight')
                nx.draw_networkx_edge_labels(self.graph, new_positions, edge_labels=edge_labels, font_size=3, ax=ax)
        else:
            print(f"The number of cities ({len(self.graph.nodes)}) exceeds {max_labels}. Labels and weights will not be displayed.")

        # Highlight vehicle paths
        if vehicle_paths:
            colors = [
                'red', 'blue', 'green', 'purple', 'cyan', 'orange', 'pink', 'brown', 
                'yellow', 'lime', 'magenta', 'teal', 'gold', 'navy', 'maroon', 'olive', 
                'coral', 'turquoise', 'indigo', 'violet', 'crimson', 'chartreuse', 
                'darkorange', 'darkgreen', 'darkblue', 'darkred', 'darkcyan', 'darkmagenta'
            ]  # Add more colors if needed

            distances_per_vehicle, total_distance = self.calculate_distances(vehicle_paths)

            for vehicle_id, path_nodes in vehicle_paths.items():
                color = colors[vehicle_id % len(colors)]  # Cycle through colors if there are more vehicles than colors
                
                # Filter edges to include only existing edges in the graph
                edges = [
                    (path_nodes[i], path_nodes[i + 1])
                    for i in range(len(path_nodes) - 1)
                    if self.graph.has_edge(path_nodes[i], path_nodes[i + 1])
                ]
                
                # Draw the valid edges
                nx.draw_networkx_edges(self.graph, new_positions, edgelist=edges, edge_color=color, width=0.75, ax=ax)

                # Highlight the starting point of the vehicle
                start_node = path_nodes[0]
                nx.draw_networkx_nodes(self.graph, new_positions, nodelist=[start_node], node_color=color, node_size=50, ax=ax)

            # Draw the distance information in a box
            box_width = 0.20  # Narrower box
            box_height = 0.05 * (len(vehicle_paths) + 2)  # Adjust height based on the number of vehicles
            box_x = 0.01  # Move the box to the bottom-left corner
            box_y = 0.01

            # Add a rectangle for the box
            rect = plt.Rectangle((box_x, box_y), box_width, box_height, transform=ax.transAxes,
                                color='black', alpha=0.6, zorder=10, edgecolor='black')
            ax.add_patch(rect)

            # Add text and color rectangles for each vehicle's distance
            y_offset = box_y + box_height - 0.05
            for vehicle_id, distance in distances_per_vehicle.items():
                # Add a small rectangle with the vehicle's color
                rect_y_centered = y_offset - 0.015  # Center the rectangle vertically with the text
                ax.add_patch(plt.Rectangle((box_x + 0.01, rect_y_centered), 0.02, 0.03, transform=ax.transAxes,
                                            color=colors[vehicle_id % len(colors)], zorder=11))
                # Add the distance text in white
                ax.text(box_x + 0.04, y_offset, f"Vehicle {vehicle_id + 1}: {distance:.2f} km",
                        transform=ax.transAxes, fontsize=8, color='white', zorder=12)
                y_offset -= 0.05

            # Add total distance
            ax.text(box_x + 0.01, y_offset, f"Total: {total_distance:.2f} km",
                    transform=ax.transAxes, fontsize=9, color='white', zorder=12)

        plt.axis('off')
        plt.tight_layout()

        # Save the graph to the specified path as PNG with the specified DPI
        plt.savefig(path, format='png', bbox_inches='tight', dpi=dpi)
        plt.clf()

    def haversine_distance(coord1, coord2):
        """
        Calculate the Haversine distance between two geographical coordinates.

        The Haversine formula determines the great-circle distance between two points
        on a sphere given their latitude and longitude. This implementation uses the
        `geodesic` function from the `geopy` library to compute the distance in kilometers.

        Args:
            coord1 (tuple): A tuple representing the latitude and longitude of the first point (e.g., (lat1, lon1)).
            coord2 (tuple): A tuple representing the latitude and longitude of the second point (e.g., (lat2, lon2)).

        Returns:
            float: The distance between the two coordinates in kilometers.
        """
        return geodesic(coord1, coord2).kilometers

    def generate_geo_graph(self, n, density=0.1):
        """
        Generates a geographical graph based on a list of cities with their coordinates.
        This method reads a file containing geographical data, filters for populated places,
        selects a specified number of cities randomly, and creates a graph where nodes
        represent cities and edges represent geographical connections. The graph is 
        initialized as connected using a minimal spanning tree (MST) and additional edges 
        are added based on the specified density.
        Args:
            geonames_path (str): Path to the geonames file containing city data.
            n (int): Number of cities to include in the graph.
            density (float, optional): The density of the graph, determining the proportion 
                of possible edges to include. Defaults to 0.1.
        Raises:
            ValueError: If the file contains fewer valid cities than the requested number `n`.
        Attributes:
            graph (networkx.Graph): The generated graph with cities as nodes.
            positions (dict): A dictionary mapping city names to their geographical 
                coordinates (longitude, latitude).
        Notes:
            - The geonames file is expected to be a tab-separated file with specific columns.
            - Only cities with valid latitude and longitude values are considered.
            - The graph is initialized with a minimal spanning tree to ensure connectivity.
            - Additional edges are added randomly to achieve the desired density.
        """
        df = pd.read_csv(
            #geonames_path,
            "../data/FR/cities_of_france.txt", 
            sep='\t', 
            header=None,
            names=["geonameid", "name", "asciiname", "alternatenames", "latitude", "longitude", 
                "feature_class", "feature_code", "country_code", "cc2", "admin1_code", 
                "admin2_code", "admin3_code", "admin4_code", "population", "elevation", 
                "dem", "timezone", "modification_date"]
        )

        # Filter cities with valid coordinates
        df = df[df['feature_class'] == 'P']  # P = populated place
        df = df.dropna(subset=['latitude', 'longitude'])

        # Check if the file contains enough cities
        if len(df) < n:
            raise ValueError(f"The file contains only {len(df)} valid cities, but {n} are requested.")

        # Select n random cities
        df_sample = df.sample(n=n, random_state=42).reset_index(drop=True)
        self.graph = nx.Graph()
        self.positions = {}

        # Add nodes to the graph
        for idx, row in df_sample.iterrows():
            city = row['name']
            lat = row['latitude']
            lon = row['longitude']
            self.graph.add_node(city, pos=(lon, lat))  # Note: x = lon, y = lat
            self.positions[city] = (lon, lat)

        # Generate a minimal edge to make the graph connected (MST)
        cities = list(self.graph.nodes)
        if len(cities) > 1:  # Ensure there are at least 2 cities
            for i in range(len(cities) - 1):
                city1, city2 = cities[i], cities[i + 1]
                self._add_edge_with_geo_weight(city1, city2)

        # Add additional edges based on density
        max_edges = int(len(cities) * (len(cities) - 1) / 2 * density)
        added = set(self.graph.edges)
        while len(self.graph.edges) < max_edges:
            u, v = random.sample(cities, 2)
            if (u, v) not in added and (v, u) not in added:
                self._add_edge_with_geo_weight(u, v)
                added.add((u, v))

    def _add_edge_with_geo_weight(self, u, v):
        """
        Adds an edge between two nodes in the graph with a weight based on the 
        geodesic distance between their geographical positions.

        This method calculates the geodesic distance (in kilometers) between the 
        positions of nodes `u` and `v` using their latitude and longitude 
        coordinates. The calculated distance is rounded to two decimal places 
        and set as the weight of the edge.

        Args:
            u (hashable): The identifier of the first node.
            v (hashable): The identifier of the second node.

        Raises:
            KeyError: If either node `u` or `v` does not exist in the graph or 
                      if their 'pos' attribute is missing.
        """
        from geopy.distance import geodesic
        pos_u = self.graph.nodes[u]['pos']
        pos_v = self.graph.nodes[v]['pos']
        weight = geodesic((pos_u[1], pos_u[0]), (pos_v[1], pos_v[0])).kilometers
        self.graph.add_edge(u, v, weight=round(weight, 2))

    def plot_geo_graph(self, map_background=True):
        """
        Plots a geographic graph with optional map background.
        This method visualizes the graph using geographic positions for nodes.
        Optionally, it can display a map of France as the background.
        Parameters:
            map_background (bool): If True, displays a map of France as the background.
                                   Defaults to True.
        Returns:
            None
        """
        plt.figure(figsize=(10, 10))
        ax = plt.gca()

        # Optional: load the map of France as background
        if map_background:
            world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
            france = world[world.name == "France"]
            france.plot(ax=ax, color='lightgrey')

        # Draw edges and nodes with geographic positions
        nx.draw(self.graph, self.positions, with_labels=True, node_color='orange', edge_color='gray', ax=ax)

        plt.title("Geographic graph on map background")
        plt.show()
