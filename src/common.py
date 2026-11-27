
from time import perf_counter
import numpy as np

from kmeans import fit_kmeans
from hierarchical import fit_hierarchical
from evaluation import calculate_silhouette, calculate_ari


RANDOM_STATE = 42


def run_experiment(dataset, algorithm):
    """
    Run one clustering experiment and return its runtime,
    silhouette score, and adjusted Rand index.

    Parameters:
        dataset: Tuple containing (X, true_labels)
        algorithm: "kmeans", "ward", "single", or "average"

    Returns:
        Dictionary containing runtime, silhouette, and ARI.
    """

    X, true_labels = dataset
    n_clusters = len(np.unique(true_labels))

    # Fit the selected clustering algorithm
    start_time = perf_counter()

    if algorithm == "kmeans":
        model = fit_kmeans(
            X,
            n_clusters=n_clusters,
            random_state=RANDOM_STATE
        )

    elif algorithm == "ward":
        model = fit_hierarchical(
            X,
            n_clusters=n_clusters,
            linkage="ward"
        )

    elif algorithm == "single":
        model = fit_hierarchical(
            X,
            n_clusters=n_clusters,
            linkage="single"
        )

    elif algorithm == "average":
        model = fit_hierarchical(
            X,
            n_clusters=n_clusters,
            linkage="average"
        )

    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    runtime = perf_counter() - start_time

    # Evaluate the resulting clusters
    predicted_labels = model.labels_

    silhouette = calculate_silhouette(X, predicted_labels)
    ari = calculate_ari(true_labels, predicted_labels)

    return {
        "runtime_seconds": runtime,
        "silhouette_score": silhouette,
        "ari": ari
    }
