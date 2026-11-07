
"""
hierarchical.py

Implementation of Agglomerative Hierarchical Clustering
using Ward and Single Linkage methods.
"""

from sklearn.cluster import AgglomerativeClustering

# Hierarchical Clustering
def fit_hierarchical(
    X,
    n_clusters,
    linkage="ward"
):
    """
    Fit an Agglomerative Hierarchical Clustering model.

    Parameters:
        X: Feature matrix containing the data points.
        n_clusters: Number of clusters to identify.
        linkage: Linkage method ('ward' or 'single').

    Returns:
        Fitted AgglomerativeClustering model.
    """

    if linkage not in ["ward", "single"]:
        raise ValueError(
            "Linkage must be either 'ward' or 'single'."
        )

    model = AgglomerativeClustering(
        n_clusters=n_clusters,
        linkage=linkage
    )

    model.fit(X)

    return model

# Example Usage
if __name__ == "__main__":

    from generate_data import generate_gaussian_blobs

    X, y = generate_gaussian_blobs()

    n_clusters = len(set(y))

    # Ward linkage
    ward_model = fit_hierarchical(
        X,
        n_clusters=n_clusters,
        linkage="ward"
    )

    # Single linkage
    single_model = fit_hierarchical(
        X,
        n_clusters=n_clusters,
        linkage="single"
    )

    print("Hierarchical Clustering Results")
    print("--------------------------------")

    print("\nWard Linkage:")
    print(f"Number of clusters: {n_clusters}")
    print(f"Number of data points: {len(ward_model.labels_)}")

    print("\nSingle Linkage:")
    print(f"Number of clusters: {n_clusters}")
    print(f"Number of data points: {len(single_model.labels_)}")
