# Add the path to the src folder
import sys
import os
sys.path.append(os.path.abspath("../src"))

# All necessary imports
from dotenv import load_dotenv
import random
from graph import Graph
from algorithms import Algorithms

# Load environment variables
load_dotenv()

# Retrieve paths from the .env file
geonames_path = os.getenv("GEONAMES_PATH")
shapefile_path = os.getenv("SHAPEFILE_PATH")
output_path = os.getenv("OUTPUT_PATH")
serialized_graph_path = os.getenv("SERIALIZE_GRAPH_PATH")

def main():
    # Graph generation
    graph = Graph()
    graph.generate_geo_graph(20, 0.1)

    graph.save_graph_svg("./data/results/initial_graph.svg")
    Algorithms.simulated_annealing_multi_vehicle(graph, 1000, 0.1, 0.9, 50, 3)
    graph.save_graph_svg("./data/results/final_graph.svg", graph.get_all_tsp_paths())
    # Display vehicle paths
    print("Vehicle paths: " + str(graph.get_all_tsp_paths()))
    
if __name__ == "__main__":
    main()