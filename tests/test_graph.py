import sys
from pathlib import Path
import tracemalloc
import pandas as pd
import numpy as np
from time import time
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from graph import Graph


def test_spatial_complexity(display = False):
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
                'used_memory_kB': current / 1024,
            })

            results_df = pd.DataFrame(results)

    # === Affichage console pour CI ===
    print("\n=== Résultats de la mesure de complexité spatiale ===\n")
    print(results_df.to_string(index=False))

    if(display) :
        # Create a graph showing memory usage according to graph's size and density evolution
        plt.figure(figsize=(10, 6))
        sns.lineplot(
            data=results_df,
            x='size',
            y='used_memory_kB',
            hue='density',
            marker='o',
            palette='viridis'
        )
        plt.title("Memory used according to the graph size")
        plt.xlabel("Number of vertices (n)")
        plt.ylabel("Memory used (kB)")
        plt.grid(True)
        plt.tight_layout()
        plt.show()

test_spatial_complexity()

