
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

All numbers below come from the CSV files in `results/tables/`. See
`report/main.pdf` for the full write-up.

### Dataset Size

K-Means runtime is essentially flat from 500 to 20,000 points (~0.1 s, dominated
by the fixed cost of its 10 restarts). Hierarchical runtime grows roughly as
n² (fitted exponents 1.9 to 2.1): at 5,000 points K-Means takes 0.13 s versus
0.70 s (Ward) and 0.80 s (Average). Below ~1,000 points the hierarchical
methods are actually faster. All methods reach ARI = 1 on these easy blobs, so
size affects cost, not quality. Hierarchical clustering is capped at 5,000
points (its distance matrix is ~100 MB there, ~1.6 GB at 20,000).

### Cluster Shape

Single linkage recovers two moons and concentric circles perfectly (ARI = 1.00).
K-Means, Ward and Average score between -0.001 and 0.36 on these shapes. On
convex blobs all methods are perfect. Ward and Average edge out K-Means on
varying-size blobs; Single linkage fails on overlapping and varying-size blobs.

### Cluster Separation

Three Gaussian clusters, centre distance d = 6, spread sigma from 0.5 to 5
(separation ratio d/sigma from 12 down to 1.2), 10 random datasets per level.
An **oracle** (assign each point to its nearest true centre) shows the best ARI
any method could reach at each overlap.

| Method | Starts to fail (ARI < 0.9 x oracle) |
|---|---|
| Single | d/sigma = 6 (collapses to ARI ~ 0, peeling off outliers) |
| Average | d/sigma = 4 |
| Ward | d/sigma = 3 |
| K-Means | never: it tracks the oracle at every level |

K-Means' low ARI at heavy overlap is the data's ambiguity, not an algorithm
failure. (This setup matches K-Means' own assumptions, so it is its home turf.)

### Overall Findings

No algorithm wins everywhere. K-Means is the efficient, robust default for
compact clusters; Ward behaves like a slightly worse K-Means; Single linkage is
the only method that follows non-convex shapes but is brittle to noise and
overlap. The Silhouette Score can disagree with ARI (it rewards round, compact
clusters), so it should not be used alone to compare different algorithms.

## Technologies

- **Python:** Experiment implementation
- **NumPy:** Numerical operations and dataset generation
- **Pandas:** Experimental results and data management
- **Scikit-learn:** Clustering algorithms, synthetic datasets, and evaluation metrics
- **Matplotlib:** Data visualizations
- **SciPy:** Scientific computing
- **python-pptx:** Builds the presentation slides
- **LaTeX:** Project report preparation

## Repository Structure

```text
csi4103_Final-Project/
├── data/
│   └── README.md                     (all data is synthetic, generated on the fly)
├── report/
│   ├── main.tex                      LaTeX report
│   ├── references.bib
│   ├── main.pdf                      compiled report
│   └── generated/                    LaTeX tables generated from results/tables/
├── results/
│   ├── figures/
│   │   ├── dataset_overview.png
│   │   ├── runtime_vs_size.png
│   │   ├── quality_vs_size.png
│   │   ├── cluster_shape_comparison.png
│   │   ├── separation_comparison.png
│   │   └── separation_examples.png
│   └── tables/
│       ├── clustering_results.csv    dataset characteristics
│       ├── dataset_size_results.csv
│       ├── cluster_shape_results.csv
│       ├── separation_results.csv    raw: one row per (sigma, seed, method)
│       ├── separation_summary.csv    mean / std per (sigma, method)
│       └── separation_thresholds.csv failure point of each method
├── slides/
│   ├── build_slides.py               builds the deck from results/
│   └── K-Means_vs_Hierarchical.pptx
└── src/
    ├── common.py                     shared run_experiment() harness, fixed seed
    ├── generate_data.py              all synthetic dataset generators
    ├── kmeans.py
    ├── hierarchical.py
    ├── evaluation.py                 runtime, silhouette, ARI
    ├── run_experiments.py            dataset characteristics + dataset size
    ├── run_size_experiments.py       dataset size only
    ├── plot_size_results.py
    ├── run_shape_experiments.py
    ├── run_separation_experiments.py
    ├── plot_separation_results.py
    └── make_report_tables.py         CSV -> LaTeX tables for the report
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

Dataset characteristics (and dataset size):

```bash
python src/run_experiments.py
```

Dataset size only:

```bash
python src/run_size_experiments.py
```

Cluster shape:

```bash
python src/run_shape_experiments.py
```

This generates `results/figures/cluster_shape_comparison.png` (ground truth vs.
K-Means vs. Single, Ward and Average linkage) and
`results/tables/cluster_shape_results.csv` (ARI and silhouette per shape and method).

Cluster separation:

```bash
python src/run_separation_experiments.py
```

This writes `results/tables/separation_results.csv` and
`results/figures/separation_examples.png`. It runs 4 methods x 10 separation
levels x 10 seeds and takes about a minute.

### 6. Generate Visualizations

```bash
python src/plot_size_results.py
python src/plot_separation_results.py
```

`plot_separation_results.py` also writes `separation_summary.csv` and
`separation_thresholds.csv` (where each method starts to fail).

### 7. Build the Report and Slides

```bash
python src/make_report_tables.py          # CSV -> report/generated/*.tex
cd report && latexmk -pdf main.tex        # -> report/main.pdf
cd .. && python slides/build_slides.py    # -> slides/K-Means_vs_Hierarchical.pptx
```

Note: the plotting scripts call `plt.show()`, which opens a window. On a
machine without a display, run them with `MPLBACKEND=Agg`.

Runtimes depend on your machine, so re-running will change the runtime columns
slightly; ARI and silhouette are reproducible (fixed seeds).

## Authors

- Elizabeth Lam
- Iaroslav (Yaro) Volkov
- Fay Lee

University of Ottawa  
CSI 4103/5138 – Great Algorithms  
Fall 2026
