
"""
kmeans.py

Implementation of K-Means clustering for the
comparative clustering experiments.
"""

from sklearn.cluster import KMeans

# K-Means Clustering
def fit_kmeans(
    X,
    n_clusters,
    random_state=42
):
    """
    Fit a K-Means clustering model.

    Parameters:
        X: Feature matrix containing the data points.
        n_clusters: Number of clusters to identify.
        random_state: Random seed for reproducibility.

    Returns:
        Fitted KMeans model.
    """

    model = KMeans(
        n_clusters=n_clusters,
        init="k-means++",
        n_init=10,
        max_iter=300,
        random_state=random_state,
        algorithm="lloyd"
    )

    model.fit(X)

    return model

# Example Usage
if __name__ == "__main__":

    from generate_data import generate_gaussian_blobs

    X, y = generate_gaussian_blobs()

    model = fit_kmeans(
        X,
        n_clusters=len(set(y))
    )

    print("K-Means Results")
    print("-------------------------")
    print(f"Number of clusters: {model.n_clusters}")
    print(f"Iterations: {model.n_iter_}")
    print(f"Inertia: {model.inertia_:.4f}")
    print(f"Number of data points: {len(model.labels_)}")
