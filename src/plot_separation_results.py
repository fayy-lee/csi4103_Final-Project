"""
plot_separation_results.py

Plots ARI and Silhouette Score against cluster separation and reports the
point at which each algorithm starts to fail.

"Starts to fail" is the first separation level (moving from well separated
towards heavily overlapping) at which the mean ARI over all seeds drops
below FAILURE_ARI (absolute) or below RELATIVE_FAILURE x the ARI of the
oracle that knows the true cluster centres (relative).

Outputs:
    results/figures/separation_comparison.png
    results/tables/separation_summary.csv     mean/std per (level, algorithm)
    results/tables/separation_thresholds.csv  failure point per algorithm
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Configuration
FAILURE_ARI = 0.90
RELATIVE_FAILURE = 0.90  # fraction of the oracle ARI

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TABLES_DIR = PROJECT_ROOT / "results" / "tables"
FIGURES_DIR = PROJECT_ROOT / "results" / "figures"
RESULTS_FILE = TABLES_DIR / "separation_results.csv"

ORACLE_NAME = "Oracle (true centres)"

STYLES = {
    ORACLE_NAME: ("#7f7f7f", None, ":"),
    "K-Means": ("#1f77b4", "o", "-"),
    "Hierarchical (Ward)": ("#2ca02c", "s", "-"),
    "Hierarchical (Average)": ("#ff7f0e", "^", "--"),
    "Hierarchical (Single)": ("#d62728", "D", "--"),
}


def load_results():
    if not RESULTS_FILE.exists():
        raise FileNotFoundError(
            f"Results file not found: {RESULTS_FILE}\n"
            "Run `python src/run_separation_experiments.py` first."
        )
    return pd.read_csv(RESULTS_FILE)


def summarise(results):
    """Mean and standard deviation over seeds for every level/algorithm."""
    summary = (
        results
        .groupby(["algorithm", "cluster_std", "separation_ratio"])
        .agg(
            ari_mean=("ari", "mean"),
            ari_std=("ari", "std"),
            silhouette_mean=("silhouette_score", "mean"),
            silhouette_std=("silhouette_score", "std"),
            n_seeds=("seed", "nunique"),
        )
        .reset_index()
        .sort_values(["algorithm", "cluster_std"])
    )
    return summary


def failure_points(summary):
    """
    Failure point of every algorithm under two definitions, scanning from
    well separated towards heavily overlapping:

      absolute: first level where mean ARI < FAILURE_ARI
      relative: first level where mean ARI < RELATIVE_FAILURE * oracle ARI

    The relative definition separates "the algorithm got worse" from "the
    clusters genuinely overlap, so nobody can score highly".
    """
    oracle = (
        summary[summary["algorithm"] == ORACLE_NAME]
        .set_index("separation_ratio")["ari_mean"]
    )

    def first_failure(data, column_below):
        failed = data[column_below]
        return None if failed.empty else failed.iloc[0]

    rows = []
    for algorithm, data in summary.groupby("algorithm"):
        if algorithm == ORACLE_NAME:
            continue
        data = data.sort_values("separation_ratio", ascending=False).copy()
        data["oracle_ari"] = data["separation_ratio"].map(oracle)

        absolute = first_failure(data, data["ari_mean"] < FAILURE_ARI)
        relative = first_failure(
            data, data["ari_mean"] < RELATIVE_FAILURE * data["oracle_ari"]
        )

        row = {"algorithm": algorithm}
        for label, hit in (("abs", absolute), ("rel", relative)):
            row[f"{label}_fails_at_std"] = (
                None if hit is None else hit["cluster_std"]
            )
            row[f"{label}_fails_at_ratio"] = (
                None if hit is None else hit["separation_ratio"]
            )
            row[f"{label}_ari_at_failure"] = (
                None if hit is None else hit["ari_mean"]
            )
        rows.append(row)
    return pd.DataFrame(rows)


def plot_comparison(summary):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    panels = [
        ("ari", "Adjusted Rand Index (ARI)"),
        ("silhouette", "Silhouette Score"),
    ]

    for ax, (metric, title) in zip(axes, panels):
        for algorithm, data in summary.groupby("algorithm"):
            color, marker, linestyle = STYLES.get(
                algorithm, (None, "o", "-")
            )
            data = data.sort_values("separation_ratio")
            x = data["separation_ratio"]
            mean = data[f"{metric}_mean"]
            spread = data[f"{metric}_std"].fillna(0)

            ax.plot(
                x, mean, marker=marker, linestyle=linestyle,
                linewidth=2, color=color, label=algorithm,
            )
            if algorithm != ORACLE_NAME:
                ax.fill_between(
                    x, mean - spread, mean + spread, color=color, alpha=0.12
                )

        if metric == "ari":
            ax.axhline(
                FAILURE_ARI, color="grey", linestyle=":", linewidth=1.2,
                label=f"failure threshold (ARI = {FAILURE_ARI})",
            )

        ax.set_xscale("log")
        ticks = sorted(summary["separation_ratio"].unique())
        ax.set_xticks(ticks)
        ax.set_xticklabels([f"{t:g}" for t in ticks], fontsize=8)
        ax.minorticks_off()
        ax.set_xlabel(
            "Separation ratio  (centre distance / cluster std)\n"
            "<- heavily overlapping          well separated ->"
        )
        ax.set_ylabel("Score")
        ax.set_title(title)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(fontsize=8)

    axes[0].set_ylim(-0.05, 1.05)

    fig.suptitle(
        "Clustering Quality vs. Cluster Separation "
        "(mean +/- 1 std over seeds)"
    )
    fig.tight_layout()

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FIGURES_DIR / "separation_comparison.png"
    fig.savefig(output_path, dpi=300)
    plt.close(fig)
    print(f"Saved: {output_path}")


if __name__ == "__main__":

    results = load_results()
    summary = summarise(results)
    thresholds = failure_points(summary)

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(TABLES_DIR / "separation_summary.csv", index=False)
    thresholds.to_csv(TABLES_DIR / "separation_thresholds.csv", index=False)

    plot_comparison(summary)

    print(
        f"\nFailure points: abs = mean ARI < {FAILURE_ARI}, "
        f"rel = mean ARI < {RELATIVE_FAILURE} x oracle ARI"
    )
    print(thresholds.round(3).to_string(index=False))
