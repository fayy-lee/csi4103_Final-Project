"""Compare clustering quality across four synthetic cluster shapes."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import RANDOM_STATE
from evaluation import calculate_ari, calculate_silhouette
from generate_data import (
    FIGURES_DIR,
    PROJECT_ROOT,
    generate_anisotropic_blobs,
    generate_concentric_circles,
    generate_gaussian_blobs,
    generate_two_moons,
)
from hierarchical import fit_hierarchical
from kmeans import fit_kmeans


def main():
    generators = {
        "Gaussian blobs": generate_gaussian_blobs,
        "Anisotropic blobs": generate_anisotropic_blobs,
        "Two moons": generate_two_moons,
        "Concentric circles": generate_concentric_circles,
    }
    linkages = ("single", "ward", "average")
    fig, axes = plt.subplots(
        len(generators),
        2 + len(linkages),
        figsize=(14, 9),
        sharex="row",
        sharey="row",
        constrained_layout=True,
    )
    rows = []

    for row_index, (shape, generate) in enumerate(generators.items()):
        X, y = generate(n_samples=1000, random_state=RANDOM_STATE)
        n_clusters = len(np.unique(y))

        predictions = {
            "K-Means": fit_kmeans(
                X, n_clusters=n_clusters, random_state=RANDOM_STATE
            ).labels_,
        }
        for linkage in linkages:
            predictions[f"Hierarchical ({linkage})"] = fit_hierarchical(
                X, n_clusters=n_clusters, linkage=linkage
            ).labels_

        for method, labels in predictions.items():
            rows.append({
                "shape": shape,
                "method": method,
                "ari": calculate_ari(y, labels),
                "silhouette": calculate_silhouette(X, labels),
            })

        panels = {"True labels": y, **predictions}
        for ax, (title, labels) in zip(axes[row_index], panels.items()):
            ax.scatter(
                X[:, 0],
                X[:, 1],
                c=labels,
                cmap="tab10",
                vmin=0,
                vmax=9,
                s=6,
                linewidths=0,
            )
            ax.set_aspect("equal", adjustable="box")
            ax.set_xticks([])
            ax.set_yticks([])
            if row_index == 0:
                ax.set_title(title)

        axes[row_index, 0].set_ylabel(shape)

    tables_dir = PROJECT_ROOT / "results" / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    scores = pd.DataFrame(rows)
    scores.to_csv(tables_dir / "cluster_shape_results.csv", index=False)
    fig.savefig(FIGURES_DIR / "cluster_shape_comparison.png", dpi=200)
    plt.close(fig)

    print(scores.round(4).to_string(index=False))


if __name__ == "__main__":
    main()