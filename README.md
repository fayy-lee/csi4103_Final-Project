
# K-Means vs. Hierarchical Clustering

An empirical comparison of computational efficiency and clustering quality.

## Project Overview

This project investigates how dataset characteristics influence the performance of K-Means and Hierarchical Clustering algorithms.

We examine three primary factors:

- **Dataset size:** How does computational runtime and clustering quality change as the number of samples increases?
- **Cluster shape:** How well do the algorithms handle compact, irregular, and non-convex clusters?
- **Cluster separation:** How does the degree of overlap between clusters affect clustering performance?

Our objective is to identify the conditions under which each algorithm performs best and understand the trade-offs between computational efficiency and clustering quality.

## Research Hypothesis

We hypothesize that K-Means will generally be more computationally efficient on large datasets with well-separated, approximately spherical clusters.

Hierarchical Clustering may achieve better clustering results on irregularly shaped datasets, depending on the linkage strategy. However, its computational and memory requirements may limit its scalability as dataset size increases.

## Algorithms

We compare the following configurations:

- **K-Means:** Partitions data into a predefined number of clusters using cluster centroids.
- **Hierarchical (Ward):** Agglomerative clustering that minimizes the increase in within-cluster variance.
- **Hierarchical (Single):** Agglomerative clustering based on the minimum distance between points in different clusters.
- **Hierarchical (Average):** Agglomerative clustering based on the average distance between points in different clusters.

## Experimental Methodology

Synthetic datasets are generated using Scikit-learn to investigate different clustering characteristics.

### 1. Dataset Size

Gaussian blob datasets are generated with increasing sample sizes:

- 500
- 1,000
- 2,500
- 5,000
- 10,000
- 20,000

All algorithms are evaluated where computationally feasible. Hierarchical clustering is capped at smaller dataset sizes due to its memory requirements.

Runtime and clustering quality are compared against the number of samples using logarithmic visualizations.

### 2. Cluster Shape

We investigate how different cluster structures influence algorithm performance, including:

- **Gaussian blobs:** Regular, compact clusters used as a baseline.
- **Two moons:** Irregular, non-convex cluster shapes.
- **Concentric circles:** Nested, non-convex clusters.
- **Anisotropic blobs:** Elongated clusters with different orientations.
- **Overlapping blobs:** Clusters with substantial overlap.
- **Varying-size blobs:** Clusters with different sizes and densities.

Each algorithm is evaluated on the same datasets. Visualizations compare the ground-truth labels with the predicted cluster assignments.

### 3. Cluster Separation

We investigate how changing cluster separation and within-cluster variation affects clustering quality.

Synthetic Gaussian blobs are generated with varying cluster standard deviations and/or distances between cluster centers, ranging from well-separated to heavily overlapping clusters.

We examine how ARI and Silhouette Scores change as separation decreases, identifying the conditions under which each algorithm begins to struggle.

### Evaluation Metrics

Algorithms are evaluated using:

- **Runtime:** Time required to fit the clustering algorithm.
- **Silhouette Score:** Measures cluster cohesion and separation.
- **Adjusted Rand Index (ARI):** Measures agreement between predicted clusters and known ground-truth labels.
- **Visualizations:** Compare ground-truth and predicted cluster assignments, as well as performance trends across experimental conditions.

Experiments use fixed random seeds to support reproducibility. Runtime measurements use repeated executions, with appropriate size limits for computationally expensive algorithms.

## Results and Findings

The experiments evaluate algorithm performance across dataset size, cluster shape, and cluster separation.

### Dataset Size

The scalability experiment examines how runtime and clustering quality change as the number of samples increases.

Preliminary findings suggest that K-Means maintains relatively low runtime as dataset size increases, while hierarchical clustering experiences greater computational costs.

### Cluster Shape

The shape experiments investigate the limitations of centroid-based and hierarchical approaches.

Initial results suggest that Single linkage can identify non-convex structures such as two moons and concentric circles, where K-Means and Ward linkage struggle.

Ward linkage performs competitively on compact and varying-size datasets, while Single linkage may be less effective on overlapping or differently sized clusters.

### Cluster Separation

The separation experiments investigate how clustering quality changes as clusters become less distinct.

ARI and Silhouette Score trends are used to identify when each algorithm begins to misclassify points or produce less well-defined clusters.

### Overall Findings

The combined experiments highlight the trade-offs between computational efficiency and clustering quality.

Rather than identifying one universally superior algorithm, the project investigates which approaches are most suitable under different data conditions.

## Technologies

- **Python:** Experiment implementation
- **NumPy:** Numerical operations and dataset generation
- **Pandas:** Experimental results and data management
- **Scikit-learn:** Clustering algorithms, synthetic datasets, and evaluation metrics
- **Matplotlib:** Data visualizations
- **SciPy:** Scientific computing
- **LaTeX:** Project report preparation

## Repository Structure

```text
csi4103_Final-Project/
├── data/
│   └── README.md
├── notebooks/
├── report/
│   ├── main.tex
│   └── references.bib
├── results/
│   ├── figures/
│   │   ├── dataset_overview.png
│   │   ├── runtime_vs_size.png
│   │   ├── quality_vs_size.png
│   │   ├── cluster_shape_comparison.png
│   │   └── separation_comparison.png
│   └── tables/
│       ├── clustering_results.csv
│       ├── dataset_size_results.csv
│       └── separation_results.csv
└── src/
    ├── common.py
    ├── generate_data.py
    ├── kmeans.py
    ├── hierarchical.py
    ├── evaluation.py
    ├── run_experiments.py
    ├── plot_size_results.py
    ├── run_shape_experiments.py
    ├── plot_shape_results.py
    ├── run_separation_experiments.py
    └── plot_separation_results.py
```

## Running the Experiments

### 1. Clone the Repository

```bash
git clone https://github.com/fayy-lee/csi4103_Final-Project.git
cd csi4103_Final-Project
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv .venv
```

Windows Git Bash:

```bash
source .venv/Scripts/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Generate Synthetic Datasets

```bash
python src/generate_data.py
```

### 5. Run the Experiments

Dataset characteristics:

```bash
python src/run_experiments.py
```

Dataset size:

```bash
python src/run_size_experiments.py
```

Cluster shape:

```bash
python src/run_shape_experiments.py
```

Cluster separation:

```bash
python src/run_separation_experiments.py
```

### 6. Generate Visualizations

```bash
python src/plot_size_results.py
python src/plot_shape_results.py
python src/plot_separation_results.py
```

Experimental tables and figures are generated in the `results/` directory.

## Authors

- Elizabeth Lam
- Iaroslav (Yaro) Volkov
- Fay Lee

University of Ottawa  
CSI 4103/5138 – Great Algorithms  
Fall 2026
