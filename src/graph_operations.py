import random
import osmnx as ox

def generate_random_graph(graph, num_vertices, density, weight_range=(1, 10)):
    """
    Generates a random weighted graph with a specified number of vertices, density, and weight range.
    This function first ensures the graph is connected by generating a minimum spanning tree.
    Additional edges are then added based on the specified density.
    Args:
        graph (Graph): The graph object to populate with random edges. It must support methods
                       like `add_edge` and have an `adjacency_list` attribute.
        num_vertices (int): The number of vertices in the graph. Must be greater than or equal to 1.
        density (float): The density of the graph, a value between 0 and 1, where 0 means no edges
                         (except those ensuring connectivity) and 1 means a complete graph.
        weight_range (tuple, optional): A tuple specifying the range (inclusive) of edge weights.
                                        Defaults to (1, 10).
    Raises:
        ValueError: If `density` is not between 0 and 1.
        ValueError: If `num_vertices` is less than 1.
    Returns:
        None: The function modifies the provided `graph` object in place.
    """
    if density < 0 or density > 1:
        raise ValueError("Density must be between 0 and 1.")
    if num_vertices < 1:
        raise ValueError("The number of vertices must be greater than or equal to 1.")

    # Reset the graph
    graph.adjacency_list.clear()

    # Generate a minimum spanning tree to ensure connectivity
    vertices = list(range(num_vertices))
    random.shuffle(vertices)
    for i in range(1, num_vertices):
        u = vertices[i - 1]
        v = vertices[i]
        weight = random.randint(*weight_range)
        graph.add_edge(u, v, weight)

    # Add additional edges based on the density
    max_edges = num_vertices * (num_vertices - 1) // 2  # Maximum number of edges in a complete graph
    num_edges = int(density * max_edges)  # Number of edges to add
    existing_edges = set((min(u, v), max(u, v)) for u in graph.adjacency_list for v, _ in graph.adjacency_list[u])

    while len(existing_edges) < num_edges:
        u, v = random.sample(vertices, 2)
        if u != v:
            edge = (min(u, v), max(u, v))
            if edge not in existing_edges:
                weight = random.randint(*weight_range)
                graph.add_edge(u, v, weight)
                existing_edges.add(edge)

def load_graph_from_osm(graph, place_name):
    """
    Loads a road network graph from OpenStreetMap (OSM) for a specified location and adds it to the provided graph.
    This function downloads the road network for the given place name, filters it to include only major roads,
    and converts it into an adjacency list representation with renamed vertices. The edge weights are based on
    the road lengths in kilometers.
    Args:
        graph (Graph): The graph object where the OSM road network will be added. It must support the `add_edge` method.
        place_name (str): The name of the place to download the road network from OSM.
    Returns:
        None
    """
    # Download the road network graph with a filter for major roads
    custom_filter = (
        '["highway"~"motorway|trunk|primary|secondary|tertiary|motorway_link|trunk_link|primary_link|secondary_link"]'
    )
    osm_graph = ox.graph_from_place(place_name, network_type='drive', custom_filter=custom_filter)

    # Create a mapping between OSM node IDs and sequential integers
    node_mapping = {node: idx for idx, node in enumerate(sorted(osm_graph.nodes))}

    # Convert the OSM graph to an adjacency list with renamed vertices
    for u, v, data in osm_graph.edges(data=True):
        # Use the edge length in kilometers as the weight
        weight = round(data.get('length', 1) / 1000, 3)  # Convert from meters to kilometers and round to 3 decimal places
        graph.add_edge(node_mapping[u], node_mapping[v], weight)