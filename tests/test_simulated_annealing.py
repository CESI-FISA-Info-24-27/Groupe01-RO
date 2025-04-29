import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import cProfile
import pstats
import io
from time import time
import random

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from graph import Graph
from algorithms import Algorithms


def profile_simulated_annealing(n, density, initial_temp, min_temp, cooling_rate, max_iter, num_vehicles):
    g = Graph()
    g.generate_geo_graph(n=n, density=density)

    pr = cProfile.Profile()
    pr.enable()

    start = time()
    try:
        _, elapsed_time = Algorithms.simulated_annealing(
            graph=g,
            initial_temp=initial_temp,
            min_temp=min_temp,
            cooling_rate=cooling_rate,
            max_iterations=max_iter,
            num_vehicles=num_vehicles
        )
    except Exception as e:
        print(f"❌ Erreur: {e}")
        elapsed_time = None

    pr.disable()

    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumtime')
    ps.print_stats(25)  # Top 25 fonctions les plus coûteuses

    return elapsed_time, s.getvalue()


def run_profiling_all():
    tailles = [100, 200, 300]  # Pour des tests rapides
    densites = [0.3, 0.5, 0.7]
    initial_temp = 1200
    min_temp = 0.1
    cooling_rate = 0.95
    max_iterations = 150
    num_vehicles = 5

    output_dir = Path(__file__).resolve().parent.parent / "data" / "profiling"
    output_dir.mkdir(parents=True, exist_ok=True)

    results = []

    for n in tailles:
        for d in densites:
            print(f"▶ Profiling SA for n={n}, density={d}")
            elapsed_time, profile_text = profile_simulated_annealing(
                n, d, initial_temp, min_temp, cooling_rate, max_iterations, num_vehicles
            )

            results.append({
                "size": n,
                "density": d,
                "exec_time_sec": elapsed_time
            })

            profile_file = output_dir / f"profile_sa_n{n}_d{str(d).replace('.', '_')}.txt"
            with open(profile_file, "w") as f:
                f.write(profile_text)
            print(f"✔ Profil saved to {profile_file}")

    # Résumé CSV et graphique
    df = pd.DataFrame(results)
    df.dropna(inplace=True)
    print("\n=== Résultats de profiling Simulated Annealing ===\n")
    print(df.to_string(index=False))

    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x='size', y='exec_time_sec', hue='density', marker='o', palette='magma')
    plt.title("Temps d'exécution de Simulated Annealing")
    plt.xlabel("Nombre de sommets (n)")
    plt.ylabel("Temps (secondes)")
    plt.grid(True)
    plt.tight_layout()

    output_dir = Path(__file__).resolve().parent.parent / "data" / "test"
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_path = output_dir / "performance_profiling.png"
    plt.savefig(plot_path)
    print(f"📊 Plot saved to {plot_path}")


if __name__ == "__main__":
    run_profiling_all()