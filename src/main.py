from graph import Graph
import time
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

# Récupérer les chemins depuis le fichier .env
geonames_path = os.getenv("GEONAMES_PATH")
shapefile_path = os.getenv("SHAPEFILE_PATH")
output_path = os.getenv("OUTPUT_PATH")
serialized_graph_path = os.getenv("SERIALIZE_GRAPH_PATH")

def main():
    print("Write your code here")

if __name__ == "__main__":
    main()