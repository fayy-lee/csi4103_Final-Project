# K-Means vs. Hierarchical Clustering

An empirical comparison of computational efficiency
and clustering quality.

## Project Overview

This project investigates how dataset characteristics
influence the performance of K-Means and Hierarchical
Clustering algorithms.

We examine three primary factors:

- Dataset size
- Cluster shape
- Cluster separation

Our objective is to identify the conditions under which
each algorithm performs best.

## Research Hypothesis

We hypothesize that K-Means will perform better in terms
of computational efficiency on large datasets with
well-separated clusters, while Hierarchical Clustering
may achieve better clustering results on irregularly
shaped datasets.

## Experimental Methodology

We will generate synthetic datasets and evaluate both
algorithms using:

- Runtime analysis
- Silhouette Score
- Adjusted Rand Index (ARI)
- Data visualizations

## Technologies

- Python
- NumPy
- Pandas
- Scikit-learn
- Matplotlib
- SciPy
- LaTeX

## Repository Structure

- `src/`: Algorithm implementations and experiments
- `data/`: Synthetic datasets
- `results/`: Experimental outputs and visualizations
- `notebooks/`: Exploratory analysis
- `report/`: Final LaTeX report

## Authors

- Elizabeth Lam
- Fay Lee
- Yaro Volkov

University of Ottawa  
CSI4103/5138 - Great Algorithms  
Fall 2026