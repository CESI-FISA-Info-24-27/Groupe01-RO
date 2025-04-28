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


def test_spatial_complexity():
    results = []
    #tailles = [i for i in range(100, 1000, 100)]
    tailles = [10000]
    #densites = [round(i, 1) for i in np.arange(0.1, 1, 0.1)]
    densites = [0.01, 0.001, 0.0001]

    for n in tailles:
        for d in densites:
            g = Graph()
            print(f"Generating graph for n verses={n}, density={d}")

            start = time()
            tracemalloc.start()
            g.generate_geo_graph(n=n, density=d)
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            end = time()

            results.append({
                'n': n,
                'densité': d,
                'mémoire_utilisée_kB': current / 1024,
                'pic_mémoire_kB': peak / 1024,
                'temps_s': round(end - start, 2)
            })

            results_df = pd.DataFrame(results)

    # Créer plusieurs graphiques dans une seule figure
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Graphique du temps d'exécution avec ligne et points
    sns.lineplot(x='n', y='temps_s', hue='densité', palette='viridis', data=results_df, ax=axes[0], marker='o', linewidth=2)
    axes[0].set_title("Temps de construction des graphes")
    axes[0].set_xlabel("Taille du graphe (n)")
    axes[0].set_ylabel("Temps de construction (s)")
    axes[0].grid(True)

    # Graphique de la mémoire utilisée avec ligne et points
    sns.lineplot(x='n', y='mémoire_utilisée_kB', hue='densité', palette='viridis', data=results_df, ax=axes[1], marker='o', linewidth=2)
    axes[1].set_title("Mémoire utilisée")
    axes[1].set_xlabel("Taille du graphe (n)")
    axes[1].set_ylabel("Mémoire utilisée (kB)")
    axes[1].grid(True)

    plt.tight_layout()  # Ajuster les espacements
    plt.show()


test_spatial_complexity()

