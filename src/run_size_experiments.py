"""
run_size_experiments.py

Runs only the dataset-size experiment (Part 1) and writes
results/tables/dataset_size_results.csv. The same experiment is also run by
run_experiments.py, which additionally runs the dataset-characteristics
comparison.
"""

from run_experiments import run_size_experiment, save_size_results

if __name__ == "__main__":
    save_size_results(run_size_experiment())
