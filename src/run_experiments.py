
"""
run_experiments.py

Runs comparative experiments between K-Means
and Hierarchical Clustering.

Experiments:
    1. Dataset characteristics:
       - Gaussian Blobs
       - Two Moons
       - Concentric Circles
       - Overlapping Blobs
       - Varying-Size Blobs

    2. Dataset size:
       - 500, 1,000, 2,500, 5,000, 10,000, 20,000 samples

Evaluates:
    - Runtime
    - Silhouette Score
    - Adjusted Rand Index (ARI)

Results are saved as separate CSV files.
"""

from pathlib import Path
from time import perf_counter
from statistics import median

import pandas as pd

from generate_data import (
    generate_all_datasets,
    generate_gaussian_blobs
)
from kmeans import fit_kmeans
from hierarchical import fit_hierarchical
from evaluation import evaluate_clustering
from common import run_experiment

# Configuration
N_SAMPLES = 1000
N_REPEATS = 5
RANDOM_STATE = 42

# Dataset size experiment
SIZE_VALUES = [500, 1000, 2500, 5000, 10000, 20000]
SIZE_REPEATS = 5

# Maximum size for hierarchical clustering
HIERARCHICAL_MAX_N = 5000

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

        "Hierarchical (Average)": lambda X, k: fit_hierarchical(
            X,
            n_clusters=k,
            linkage="average"
        ),

        "Hierarchical (Single)": lambda X, k: fit_hierarchical(
            X,
            n_clusters=k,
            linkage="single"
        )
    }

# Original Dataset Experiments
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

            # Evaluate clustering quality separately.
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

# Dataset Size Experiment
def run_size_experiment():

    print("\n" + "=" * 65)
    print("DATASET SIZE EXPERIMENT")
    print("=" * 65)

    algorithms = {
        "K-Means": "kmeans",
        "Hierarchical (Ward)": "ward",
        "Hierarchical (Average)": "average",
        "Hierarchical (Single)": "single"
    }

    all_results = []

    for n in SIZE_VALUES:

        print(f"\nDataset size: {n}")
        print("-" * 50)

        # Generate reproducible Gaussian blobs.
        dataset = generate_gaussian_blobs(
            n_samples=n,
            random_state=RANDOM_STATE
        )

        for algorithm_name, algorithm_key in algorithms.items():

            # Skip hierarchical clustering beyond the size limit.
            if algorithm_key != "kmeans" and n > HIERARCHICAL_MAX_N:

                print(
                    f"{algorithm_name:25} | "
                    "Skipped (size limit)"
                )
                continue

            runtimes = []
            silhouette_scores = []
            ari_scores = []

            # Repeat experiment.
            for _ in range(SIZE_REPEATS):

                metrics = run_experiment(
                    dataset,
                    algorithm_key
                )

                runtimes.append(metrics["runtime_seconds"])
                silhouette_scores.append(metrics["silhouette_score"])
                ari_scores.append(metrics["ari"])

            # Use median to reduce timing variability.
            result = {
                "algorithm": algorithm_name,
                "n_samples": n,
                "runtime_seconds": median(runtimes),
                "silhouette_score": median(silhouette_scores),
                "ari": median(ari_scores)
            }

            all_results.append(result)

            print(
                f"{algorithm_name:25} | "
                f"Runtime: {result['runtime_seconds']:.6f}s | "
                f"Silhouette: {result['silhouette_score']:.4f} | "
                f"ARI: {result['ari']:.4f}"
            )

    return pd.DataFrame(all_results)

# Save Original Results
def save_results(results):

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    output_path = RESULTS_DIR / "clustering_results.csv"

    results.to_csv(output_path, index=False)

    print("\n" + "=" * 65)
    print("ORIGINAL EXPERIMENTS COMPLETE")
    print("=" * 65)

    print(f"\nTotal experiments: {len(results)}")
    print(f"Results saved to: {output_path}")

# Save Dataset Size Results
def save_size_results(results):

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    output_path = RESULTS_DIR / "dataset_size_results.csv"

    results.to_csv(output_path, index=False)

    print("\n" + "=" * 65)
    print("DATASET SIZE EXPERIMENT COMPLETE")
    print("=" * 65)

    print(f"\nTotal experiments: {len(results)}")
    print(f"Results saved to: {output_path}")

# Main
if __name__ == "__main__":

    # Run original dataset experiments.
    results = run_experiments()
    save_results(results)

    # Run dataset size experiments.
    size_results = run_size_experiment()
    save_size_results(size_results)
