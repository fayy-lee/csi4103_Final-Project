
"""
run_experiments.py

Runs comparative experiments between K-Means
and Hierarchical Clustering.

Evaluates:
    - Runtime (average across repeated executions)
    - Silhouette Score
    - Adjusted Rand Index (ARI)

Results are saved as a CSV file.
"""

from pathlib import Path
from time import perf_counter

import pandas as pd

from generate_data import generate_all_datasets
from kmeans import fit_kmeans
from hierarchical import fit_hierarchical
from evaluation import evaluate_clustering

# Configuration
N_SAMPLES = 1000
N_REPEATS = 5
RANDOM_STATE = 42

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = PROJECT_ROOT / "results" / "tables"

# Algorithm Configurations
def get_algorithms():

    return {
        "K-Means": lambda X, k: fit_kmeans(
            X,
            n_clusters=k,
            random_state=RANDOM_STATE
        ),

        "Hierarchical (Ward)": lambda X, k: fit_hierarchical(
            X,
            n_clusters=k,
            linkage="ward"
        ),

        "Hierarchical (Single)": lambda X, k: fit_hierarchical(
            X,
            n_clusters=k,
            linkage="single"
        )
    }

# Run Experiments
def run_experiments():

    print("=" * 65)
    print("K-MEANS VS. HIERARCHICAL CLUSTERING")
    print("=" * 65)

    datasets = generate_all_datasets(
        n_samples=N_SAMPLES,
        random_state=RANDOM_STATE
    )

    algorithms = get_algorithms()

    all_results = []

    for dataset_name, (X, y) in datasets.items():

        n_clusters = len(set(y))

        print(f"\nDataset: {dataset_name}")
        print("-" * 50)

        for algorithm_name, algorithm in algorithms.items():

            runtimes = []
            predicted_labels = None

            # Repeat algorithm execution.
            for _ in range(N_REPEATS):

                start_time = perf_counter()

                model = algorithm(X, n_clusters)

                elapsed = perf_counter() - start_time

                runtimes.append(elapsed)
                predicted_labels = model.labels_

            average_runtime = sum(runtimes) / len(runtimes)

            # Calculate evaluation metrics separately
            # so they do not affect runtime measurements.
            metrics = evaluate_clustering(
                X,
                y,
                predicted_labels,
                average_runtime
            )

            result = {
                "dataset": dataset_name,
                "algorithm": algorithm_name,
                "n_samples": len(X),
                "n_clusters": n_clusters,
                "runtime_seconds": metrics["runtime"],
                "silhouette_score": metrics["silhouette_score"],
                "ari": metrics["ari"]
            }

            all_results.append(result)

            print(
                f"{algorithm_name:25} | "
                f"Runtime: {average_runtime:.6f}s | "
                f"Silhouette: {metrics['silhouette_score']:.4f} | "
                f"ARI: {metrics['ari']:.4f}"
            )

    return pd.DataFrame(all_results)

# Save Results
def save_results(results):

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    output_path = RESULTS_DIR / "clustering_results.csv"

    results.to_csv(output_path, index=False)

    print("\n" + "=" * 65)
    print("EXPERIMENTS COMPLETE")
    print("=" * 65)

    print(f"\nTotal experiments: {len(results)}")
    print(f"Results saved to: {output_path}")

# Main
if __name__ == "__main__":

    results = run_experiments()

    save_results(results)
