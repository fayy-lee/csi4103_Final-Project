"""
run_separation_experiments.py

Part 3: cluster separation.

Three Gaussian clusters are generated with a fixed centre distance and an
increasing within-cluster standard deviation, so the separation ratio
(centre distance / std) falls from "well separated" to "heavily
overlapping". Every algorithm is run on the same datasets, and each setting
is repeated over several random seeds because ARI on overlapping data is
noisy from one draw to the next.

Outputs:
    results/tables/separation_results.csv   one row per (std, seed, algorithm)
    results/figures/separation_examples.png  example datasets and clusterings
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

import numpy as np

from common import RANDOM_STATE, run_experiment
from evaluation import calculate_ari, calculate_silhouette
from generate_data import (
    SEPARATION_CENTER_DISTANCE,
    SEPARATION_STDS,
    generate_separated_blobs,
    separation_centers,
)
from hierarchical import fit_hierarchical
from kmeans import fit_kmeans

# Configuration
N_SAMPLES = 1000
N_SEEDS = 10

ALGORITHMS = {
    "K-Means": "kmeans",
    "Hierarchical (Ward)": "ward",
    "Hierarchical (Average)": "average",
    "Hierarchical (Single)": "single",
}

# Reference line, not an algorithm: assign every point to its nearest TRUE
# centre. For equal-size, equal-variance spherical Gaussians this is the
# Bayes-optimal rule, so its ARI is the best score any method could reach.
# It shows how much of a low ARI is caused by overlap in the data itself
# rather than by the algorithm.
ORACLE_NAME = "Oracle (true centres)"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TABLES_DIR = PROJECT_ROOT / "results" / "tables"
FIGURES_DIR = PROJECT_ROOT / "results" / "figures"


def run_separation_experiment():
    """Run every algorithm on every separation level and seed."""

    rows = []

    for std in SEPARATION_STDS:
        ratio = SEPARATION_CENTER_DISTANCE / std
        print(f"\nstd = {std:<5} (separation ratio {ratio:.2f})")
        print("-" * 60)

        for seed_offset in range(N_SEEDS):
            seed = RANDOM_STATE + seed_offset
            dataset = generate_separated_blobs(
                cluster_std=std,
                n_samples=N_SAMPLES,
                random_state=seed,
            )

            X, y = dataset
            distances = np.linalg.norm(
                X[:, None, :] - separation_centers()[None, :, :], axis=2
            )
            oracle_labels = distances.argmin(axis=1)
            rows.append({
                "cluster_std": std,
                "separation_ratio": ratio,
                "seed": seed,
                "algorithm": ORACLE_NAME,
                "runtime_seconds": float("nan"),
                "silhouette_score": calculate_silhouette(X, oracle_labels),
                "ari": calculate_ari(y, oracle_labels),
            })

            for name, key in ALGORITHMS.items():
                metrics = run_experiment(dataset, key)
                rows.append({
                    "cluster_std": std,
                    "separation_ratio": ratio,
                    "seed": seed,
                    "algorithm": name,
                    "runtime_seconds": metrics["runtime_seconds"],
                    "silhouette_score": metrics["silhouette_score"],
                    "ari": metrics["ari"],
                })

        level = pd.DataFrame([r for r in rows if r["cluster_std"] == std])
        means = level.groupby("algorithm")[["ari", "silhouette_score"]].mean()
        for name in [ORACLE_NAME, *ALGORITHMS]:
            print(
                f"{name:25} | ARI: {means.loc[name, 'ari']:.4f} | "
                f"Silhouette: {means.loc[name, 'silhouette_score']:.4f}"
            )

    return pd.DataFrame(rows)


def plot_examples(stds=(0.5, 1.5, 2.5, 4.0)):
    """Scatter plots of the data and each algorithm at a few overlap levels."""

    panels = ["True labels"] + list(ALGORITHMS)
    fig, axes = plt.subplots(
        len(stds),
        len(panels),
        figsize=(14, 2.9 * len(stds)),
        sharex="row",
        sharey="row",
        constrained_layout=True,
    )

    for row, std in enumerate(stds):
        X, y = generate_separated_blobs(
            cluster_std=std, n_samples=N_SAMPLES, random_state=RANDOM_STATE
        )
        predictions = {"True labels": y}
        predictions["K-Means"] = fit_kmeans(
            X, n_clusters=3, random_state=RANDOM_STATE
        ).labels_
        for name, key in ALGORITHMS.items():
            if key != "kmeans":
                predictions[name] = fit_hierarchical(
                    X, n_clusters=3, linkage=key
                ).labels_

        for col, title in enumerate(panels):
            ax = axes[row, col]
            ax.scatter(
                X[:, 0], X[:, 1], c=predictions[title],
                cmap="tab10", vmin=0, vmax=9, s=6, linewidths=0,
            )
            ax.set_aspect("equal", adjustable="box")
            ax.set_xticks([])
            ax.set_yticks([])
            if row == 0:
                ax.set_title(title, fontsize=10)

        axes[row, 0].set_ylabel(
            f"std = {std}\nd/std = {SEPARATION_CENTER_DISTANCE / std:.1f}"
        )

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FIGURES_DIR / "separation_examples.png"
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
    print(f"Saved: {output_path}")


if __name__ == "__main__":

    print("=" * 65)
    print("CLUSTER SEPARATION EXPERIMENT")
    print("=" * 65)

    results = run_separation_experiment()

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = TABLES_DIR / "separation_results.csv"
    results.to_csv(output_path, index=False)

    print(f"\nTotal runs: {len(results)}")
    print(f"Saved: {output_path}")

    plot_examples()
