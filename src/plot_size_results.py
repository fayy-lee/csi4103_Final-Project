
"""
plot_size_results.py

Generates visualizations for the dataset size experiment:
    1. Runtime vs. dataset size (log-log scale)
    2. Clustering quality vs. dataset size
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent

RESULTS_FILE = (
    PROJECT_ROOT / "results" / "tables" / "dataset_size_results.csv"
)

FIGURES_DIR = PROJECT_ROOT / "results" / "figures"

# Load Results
def load_results():

    if not RESULTS_FILE.exists():
        raise FileNotFoundError(
            f"Results file not found: {RESULTS_FILE}"
        )

    return pd.read_csv(RESULTS_FILE)

# Runtime vs. Dataset Size
def plot_runtime(results):

    plt.figure(figsize=(9, 6))

    for algorithm in results["algorithm"].unique():

        algorithm_data = results[
            results["algorithm"] == algorithm
        ].sort_values("n_samples")

        plt.plot(
            algorithm_data["n_samples"],
            algorithm_data["runtime_seconds"],
            marker="o",
            linewidth=2,
            label=algorithm
        )

    plt.xscale("log")
    plt.yscale("log")

    plt.xlabel("Number of Samples (n)")
    plt.ylabel("Runtime (seconds)")
    plt.title("Runtime vs. Dataset Size")

    plt.grid(True, which="both", linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()

    output_path = FIGURES_DIR / "runtime_vs_size.png"

    plt.savefig(output_path, dpi=300)
    plt.show()

    print(f"Saved: {output_path}")

# Clustering Quality vs. Dataset Size
def plot_quality(results):

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    metrics = [
        ("ari", "Adjusted Rand Index (ARI)"),
        ("silhouette_score", "Silhouette Score")
    ]

    for ax, (metric, title) in zip(axes, metrics):

        for algorithm in results["algorithm"].unique():

            algorithm_data = results[
                results["algorithm"] == algorithm
            ].sort_values("n_samples")

            ax.plot(
                algorithm_data["n_samples"],
                algorithm_data[metric],
                marker="o",
                linewidth=2,
                label=algorithm
            )

        ax.set_xscale("log")
        ax.set_xlabel("Number of Samples (n)")
        ax.set_ylabel("Score")
        ax.set_title(title)
        ax.set_ylim(-0.1, 1.05)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend()

    fig.suptitle("Clustering Quality vs. Dataset Size")
    fig.tight_layout()

    output_path = FIGURES_DIR / "quality_vs_size.png"

    plt.savefig(output_path, dpi=300)
    plt.show()

    print(f"Saved: {output_path}")

# Main
if __name__ == "__main__":

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    results = load_results()

    plot_runtime(results)
    plot_quality(results)
