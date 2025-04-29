import sys
from pathlib import Path
import tracemalloc
import pandas as pd
import numpy as np
from time import time
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from src.graph import Graph


def test_spatial_complexity():
    results = []
    tailles = [i for i in range(100, 1000, 100)]
    densites = [0.001, 0.01, 0.05, 0.1, 0.15, 0.20, 0.25, 0.3]

    for n in tailles:
        for d in densites:
            g = Graph()
            print(f"Generating graph for n vertices={n}, density={d}")

            tracemalloc.start()
            g.generate_geo_graph(n=n, density=d)
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            results.append({
                'size': n,
                'density': d,
                'used_memory_MB': current / 1024**2,
            })

            print("Success")

    
    results_df = pd.DataFrame(results)

    # === Affichage console pour CI ===
    print("\n=== Résultats de la mesure de complexité spatiale ===\n")
    print(results_df.to_string(index=False))

    # Créer le dossier si nécessaire
    output_dir = Path(__file__).resolve().parent.parent / "data" / "test"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Créer le graphique
    plt.figure(figsize=(10, 6))
    sns.lineplot(
        data=results_df,
        x='size',
        y='used_memory_MB',
        hue='density',
        marker='o',
        palette='viridis'
    )
    plt.title("Memory used according to the graph size")
    plt.xlabel("Number of vertices (n)")
    plt.ylabel("Memory used (MB)")
    plt.grid(True)
    plt.tight_layout()

    # Enregistrer le fichier image
    plot_path = output_dir / "spatial_complexity.png"
    plt.savefig(plot_path)
    print(f"Plot saved to {plot_path}")


print("Starting space complexity test")

