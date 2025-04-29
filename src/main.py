# Add the path to the src folder
import sys
import os
sys.path.append(os.path.abspath("../src"))

# All necessary imports
from dotenv import load_dotenv
import random
from graph import Graph
from algorithms import Algorithms
from utils import *
import networkx as nx

# Load environment variables
load_dotenv()

# Retrieve paths from the .env file
geonames_path = os.getenv("GEONAMES_PATH")
shapefile_path = os.getenv("SHAPEFILE_PATH")
output_path = os.getenv("OUTPUT_PATH")
serialized_graph_path = os.getenv("SERIALIZE_GRAPH_PATH")

def main():
    # Setup for GIF
    # clear_folder("./data/results/gif")

    # Graph generation
    graph = Graph()
    
    graph.generate_geo_graph(100, 0.5)
    graph.save_graph_svg("./data/results/initial_graph.svg")
    
    # Algorithms.simulated_annealing(graph, 1000, 0.1, 0.9, 50, 5)
    
    #print("Vehicle paths: " + str(graph.get_all_tsp_paths()))
    # graph.save_graph_svg("./data/results/final_graph.svg", True, graph.get_all_tsp_paths())

    # Create GIF
    # png_folder = "./data/results/gif" 
    # output_gif = "./data/results/sa_gif.gif"
    # create_gif_from_png_folder(png_folder, output_gif, duration=300)

    Algorithms.simulated_annealing(
        graph=graph,
        initial_temp=1000,
        min_temp=0.1,
        cooling_rate=0.95,
        max_iterations=500,
        num_vehicles=3,
    )

    graph.save_graph_svg("./data/results/final_graph.svg", True, graph.get_all_tsp_paths())
if __name__ == "__main__":
    main()