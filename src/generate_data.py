
"""
generate_data.py

Generates synthetic datasets for comparing K-Means
and Hierarchical Clustering.

Each dataset contains:
    X: Feature matrix containing the data points.
    y: Ground-truth cluster labels.

All datasets use a fixed random seed to ensure
reproducibility across experiments.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from sklearn.datasets import make_blobs, make_circles, make_moons

# Configuration
RANDOM_STATE = 42
DEFAULT_SAMPLES = 1000

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR = PROJECT_ROOT / "results" / "figures"

# Dataset Generators
def generate_gaussian_blobs(
    n_samples=DEFAULT_SAMPLES,
    random_state=RANDOM_STATE
):
    """
    Generate well-separated Gaussian clusters.

    Purpose:
        Establish a baseline where both algorithms
        should perform reasonably well.
    """

    X, y = make_blobs(
        n_samples=n_samples,
        centers=3,
        cluster_std=0.7,
        random_state=random_state
    )

    return X, y


def generate_two_moons(
    n_samples=DEFAULT_SAMPLES,
    random_state=RANDOM_STATE
):
    """
    Generate two interleaving crescent-shaped clusters.

    Purpose:
        Test performance on non-spherical clusters.
    """

    X, y = make_moons(
        n_samples=n_samples,
        noise=0.08,
        random_state=random_state
    )

    return X, y


def generate_concentric_circles(
    n_samples=DEFAULT_SAMPLES,
    random_state=RANDOM_STATE
):
    """
    Generate two concentric circular clusters.

    Purpose:
        Test performance on non-convex cluster shapes.
    """

    X, y = make_circles(
        n_samples=n_samples,
        factor=0.4,
        noise=0.06,
        random_state=random_state
    )

    return X, y


def generate_overlapping_blobs(
    n_samples=DEFAULT_SAMPLES,
    random_state=RANDOM_STATE
):
    """
    Generate two partially overlapping Gaussian clusters.

    Purpose:
        Investigate how cluster separation influences
        clustering quality.
    """

    X, y = make_blobs(
        n_samples=n_samples,
        centers=[(-2, 0), (2, 0)],
        cluster_std=1.8,
        random_state=random_state
    )

    return X, y


def generate_varying_size_blobs(
    n_samples=DEFAULT_SAMPLES,
    random_state=RANDOM_STATE
):
    """
    Generate two clusters with different sizes and densities.

    Purpose:
        Investigate how unequal cluster sizes and
        densities influence algorithm performance.
    """

    smaller_cluster = int(n_samples * 0.25)
    larger_cluster = n_samples - smaller_cluster

    X, y = make_blobs(
        n_samples=[smaller_cluster, larger_cluster],
        centers=[(-3, 0), (3, 0)],
        cluster_std=[0.5, 1.5],
        random_state=random_state
    )

    return X, y

# Generate All Datasets
def generate_all_datasets(
    n_samples=DEFAULT_SAMPLES,
    random_state=RANDOM_STATE
):
    """
    Generate all five synthetic datasets.

    Returns:
        Dictionary mapping dataset names to (X, y) tuples.
    """

    return {
        "Gaussian Blobs": generate_gaussian_blobs(
            n_samples, random_state
        ),
        "Two Moons": generate_two_moons(
            n_samples, random_state
        ),
        "Concentric Circles": generate_concentric_circles(
            n_samples, random_state
        ),
        "Overlapping Blobs": generate_overlapping_blobs(
            n_samples, random_state
        ),
        "Varying-Size Blobs": generate_varying_size_blobs(
            n_samples, random_state
        )
    }

# Dataset Visualization
def plot_datasets(datasets, save=True):
    """
    Plot all generated datasets in a single figure.

    Each point is coloured according to its
    ground-truth cluster label.
    """

    n_datasets = len(datasets)

    fig, axes = plt.subplots(
        2, 3,
        figsize=(15, 9)
    )

    axes = axes.flatten()

    for ax, (name, (X, y)) in zip(axes, datasets.items()):

        ax.scatter(
            X[:, 0],
            X[:, 1],
            c=y,
            cmap="viridis",
            s=12,
            alpha=0.8
        )

        ax.set_title(name, fontsize=12)
        ax.set_xlabel("Feature 1")
        ax.set_ylabel("Feature 2")
        ax.grid(alpha=0.2)

    # Remove the unused sixth subplot.
    for ax in axes[n_datasets:]:
        ax.remove()

    fig.suptitle(
        "Synthetic Datasets for Clustering Experiments",
        fontsize=15,
        fontweight="bold"
    )

    plt.tight_layout()

    if save:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)

        output_path = FIGURES_DIR / "dataset_overview.png"

        plt.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight"
        )

        print(f"Figure saved to: {output_path}")

    plt.show()

# Main
if __name__ == "__main__":

    print("Generating synthetic datasets...\n")

    datasets = generate_all_datasets()

    for name, (X, y) in datasets.items():
        print(
            f"{name}: "
            f"{X.shape[0]} samples, "
            f"{X.shape[1]} features, "
            f"{len(np.unique(y))} clusters"
        )

    print("\nGenerating dataset visualizations...")

    plot_datasets(datasets)

    print("\nDataset generation complete!")
