
"""
evaluation.py

Evaluation metrics for comparing K-Means and
Hierarchical Clustering.

Metrics:
    - Runtime
    - Silhouette Score
    - Adjusted Rand Index (ARI)
"""

from sklearn.metrics import (
    adjusted_rand_score,
    silhouette_score
)

# Evaluation Metrics
def calculate_silhouette(X, predicted_labels):
    """
    Calculate the Silhouette Score.

    Measures how well-separated the predicted clusters are.

    Range:
        -1 to 1

    Higher values generally indicate better-defined clusters.
    """

    n_clusters = len(set(predicted_labels))

    if n_clusters < 2 or n_clusters >= len(X):
        return float("nan")

    return silhouette_score(X, predicted_labels)


def calculate_ari(true_labels, predicted_labels):
    """
    Calculate the Adjusted Rand Index.

    Compares predicted cluster assignments against
    the ground-truth labels.

    Range:
        -1 to 1

    1.0 indicates perfect agreement.
    0.0 indicates agreement similar to random assignment.
    """

    return adjusted_rand_score(
        true_labels,
        predicted_labels
    )

# Combined Evaluation
def evaluate_clustering(
    X,
    true_labels,
    predicted_labels,
    runtime_seconds
):
    """
    Calculate all evaluation metrics for a clustering result.

    Returns:
        Dictionary containing runtime, silhouette score,
        and adjusted rand index.
    """

    return {
        "runtime": runtime_seconds,
        "silhouette_score": calculate_silhouette(
            X,
            predicted_labels
        ),
        "ari": calculate_ari(
            true_labels,
            predicted_labels
        ),
        "n_clusters": len(set(predicted_labels))
    }

# Example Usage
if __name__ == "__main__":

    from time import perf_counter

    from generate_data import generate_gaussian_blobs
    from kmeans import fit_kmeans

    # Generate dataset
    X, y = generate_gaussian_blobs()

    # Measure K-Means runtime
    start_time = perf_counter()

    model = fit_kmeans(
        X,
        n_clusters=len(set(y))
    )

    runtime = perf_counter() - start_time

    # Evaluate clustering
    results = evaluate_clustering(
        X,
        y,
        model.labels_,
        runtime
    )

    print("K-Means Evaluation")
    print("-------------------------")
    print(f"Runtime: {results['runtime']:.6f} seconds")
    print(f"Silhouette Score: {results['silhouette_score']:.4f}")
    print(f"Adjusted Rand Index: {results['ari']:.4f}")
    print(f"Number of clusters: {results['n_clusters']}")
