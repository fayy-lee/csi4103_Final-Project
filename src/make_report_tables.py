"""
make_report_tables.py

Turns the CSV files in results/tables/ into LaTeX table bodies in
report/generated/, so every number in the report comes straight from the
experiments (nothing is copied by hand). Re-run after re-running any
experiment, then recompile the report.

Each generated file contains only a `tabular` environment; captions and
labels live in report/main.tex.
"""

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TABLES = PROJECT_ROOT / "results" / "tables"
OUT = PROJECT_ROOT / "report" / "generated"

SHORT = {
    "K-Means": "K-Means",
    "Hierarchical (Ward)": "Ward",
    "Hierarchical (Average)": "Average",
    "Hierarchical (Single)": "Single",
}
ORDER = list(SHORT)


def fmt(x, nd=3):
    if pd.isna(x):
        return "--"
    x = round(float(x), nd) + 0.0  # turns -0.0 into 0.0
    return f"{x:.{nd}f}".replace("-", "$-$")


def write(name, lines):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote report/generated/{name}")


def bold_best(values, nd=3, higher=True):
    """Format a row of numbers, bolding the best one(s)."""
    arr = np.array(values, dtype=float)
    best = np.nanmax(arr) if higher else np.nanmin(arr)
    cells = []
    for v in arr:
        s = fmt(v, nd)
        if not np.isnan(v) and np.isclose(v, best, atol=5e-4):
            s = r"\textbf{" + s + "}"
        cells.append(s)
    return cells


def table_characteristics():
    d = pd.read_csv(TABLES / "clustering_results.csv")
    lines = [
        r"\begin{tabular}{lrrrrrrrr}",
        r"\toprule",
        r"& \multicolumn{4}{c}{\textbf{ARI}} & "
        r"\multicolumn{4}{c}{\textbf{Silhouette}} \\",
        r"\cmidrule(lr){2-5}\cmidrule(lr){6-9}",
        r"\textbf{Dataset} & " + " & ".join(SHORT[a] for a in ORDER) + " & "
        + " & ".join(SHORT[a] for a in ORDER) + r" \\",
        r"\midrule",
    ]
    for name in d["dataset"].unique():
        g = d[d.dataset == name].set_index("algorithm").loc[ORDER]
        ari = bold_best(g["ari"].values)
        sil = bold_best(g["silhouette_score"].values)
        lines.append(f"{name} & " + " & ".join(ari + sil) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    write("characteristics.tex", lines)


def table_shape():
    d = pd.read_csv(TABLES / "cluster_shape_results.csv")
    d["method"] = d["method"].str.replace("Hierarchical (", "", regex=False)
    d["method"] = d["method"].str.rstrip(")").str.capitalize()
    d["method"] = d["method"].replace({"K-means": "K-Means"})
    cols = ["K-Means", "Ward", "Average", "Single"]
    lines = [
        r"\begin{tabular}{lrrrrrrrr}",
        r"\toprule",
        r"& \multicolumn{4}{c}{\textbf{ARI}} & "
        r"\multicolumn{4}{c}{\textbf{Silhouette}} \\",
        r"\cmidrule(lr){2-5}\cmidrule(lr){6-9}",
        r"\textbf{Shape} & " + " & ".join(cols) + " & "
        + " & ".join(cols) + r" \\",
        r"\midrule",
    ]
    for shape in d["shape"].unique():
        g = d[d["shape"] == shape].set_index("method").loc[cols]
        ari = bold_best(g["ari"].values)
        sil = bold_best(g["silhouette"].values)
        lines.append(f"{shape} & " + " & ".join(ari + sil) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    write("shape.tex", lines)


def table_size():
    d = pd.read_csv(TABLES / "dataset_size_results.csv")
    sizes = sorted(d["n_samples"].unique())

    # Runtime
    lines = [
        r"\begin{tabular}{rrrrr}",
        r"\toprule",
        r"\textbf{Samples} & " + " & ".join(
            r"\textbf{" + SHORT[a] + "}" for a in ORDER) + r" \\",
        r"\midrule",
    ]
    for n in sizes:
        g = d[d.n_samples == n].set_index("algorithm")
        vals = [g.runtime_seconds.get(a, np.nan) for a in ORDER]
        cells = bold_best(vals, nd=3, higher=False)
        lines.append(f"{n:,} & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    write("size_runtime.tex", lines)

    # Quality: identical across algorithms in this experiment; verify it.
    lines = [
        r"\begin{tabular}{rrr}",
        r"\toprule",
        r"\textbf{Samples} & \textbf{ARI (all methods)} & "
        r"\textbf{Silhouette (all methods)} \\",
        r"\midrule",
    ]
    for n in sizes:
        g = d[d.n_samples == n]
        assert g["ari"].round(4).nunique() == 1, f"ARI differs at n={n}"
        assert g["silhouette_score"].round(3).nunique() == 1, (
            f"Silhouette differs at n={n}"
        )
        lines.append(
            f"{n:,} & {g['ari'].iloc[0]:.3f} & "
            f"{g['silhouette_score'].iloc[0]:.3f} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    write("size_quality.tex", lines)

    # Empirical scaling exponent (slope of log runtime vs. log n).
    lines = [
        r"\begin{tabular}{lcr}",
        r"\toprule",
        r"\textbf{Method} & \textbf{Range of $n$} & "
        r"\textbf{Fitted exponent} \\",
        r"\midrule",
    ]
    for a in ORDER:
        g = d[d.algorithm == a].sort_values("n_samples")
        if a != "K-Means":
            g = g[g.n_samples >= 1000]
        slope = np.polyfit(
            np.log(g.n_samples), np.log(g.runtime_seconds), 1
        )[0]
        lo, hi = g.n_samples.min(), g.n_samples.max()
        lines.append(f"{SHORT[a]} & {lo:,}--{hi:,} & {fmt(slope, 2)} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    write("size_exponents.tex", lines)


def table_separation():
    s = pd.read_csv(TABLES / "separation_summary.csv")
    levels = sorted(s["cluster_std"].unique())

    for metric, fname in (("ari", "separation_ari.tex"),
                          ("silhouette", "separation_silhouette.tex")):
        lines = [
            r"\begin{tabular}{rrrrrr}",
            r"\toprule",
            r"\textbf{Std} & \textbf{$d/\sigma$} & "
            + " & ".join(r"\textbf{" + SHORT[a] + "}" for a in ORDER)
            + r" \\",
            r"\midrule",
        ]
        for std in levels:
            g = s[s.cluster_std == std].set_index("algorithm").loc[ORDER]
            ratio = g["separation_ratio"].iloc[0]
            cells = bold_best(g[f"{metric}_mean"].values)
            lines.append(f"{std:g} & {ratio:.1f} & " + " & ".join(cells)
                         + r" \\")
        lines += [r"\bottomrule", r"\end{tabular}"]
        write(fname, lines)

    t = pd.read_csv(TABLES / "separation_thresholds.csv").set_index(
        "algorithm"
    ).loc[ORDER]

    def cell(value, nd=1):
        return "never" if pd.isna(value) else f"{value:.{nd}f}"

    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"& \multicolumn{2}{c}{\textbf{Absolute (ARI $<0.9$)}} & "
        r"\multicolumn{2}{c}{\textbf{Relative (ARI $<0.9\times$ oracle)}}"
        r" \\",
        r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}",
        r"\textbf{Method} & $d/\sigma$ & Mean ARI & $d/\sigma$ & Mean ARI \\",
        r"\midrule",
    ]
    for a in ORDER:
        r = t.loc[a]
        lines.append(
            f"{SHORT[a]} & {cell(r['abs_fails_at_ratio'])} & "
            f"{cell(r['abs_ari_at_failure'], 3)} & "
            f"{cell(r['rel_fails_at_ratio'])} & "
            f"{cell(r['rel_ari_at_failure'], 3)} \\\\"
        )
    lines += [r"\bottomrule", r"\end{tabular}"]
    write("separation_thresholds.tex", lines)


if __name__ == "__main__":
    table_characteristics()
    table_shape()
    table_size()
    table_separation()
