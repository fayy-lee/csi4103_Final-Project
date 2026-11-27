"""
build_slides.py

Builds slides/K-Means_vs_Hierarchical.pptx (16:9, ~10 slides for a 10-12
minute talk) from the figures in results/figures/ and the numbers in
results/tables/. Speaker notes are included on every slide.

Run from the repository root:
    python slides/build_slides.py
"""

from pathlib import Path

import pandas as pd
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "results" / "figures"
TAB = ROOT / "results" / "tables"
OUT = ROOT / "slides" / "K-Means_vs_Hierarchical.pptx"

# Palette (algorithm colours match the matplotlib figures)
INK = RGBColor(0x1F, 0x29, 0x37)
MUTED = RGBColor(0x6B, 0x72, 0x80)
BG = RGBColor(0xFF, 0xFF, 0xFF)
PANEL = RGBColor(0xF3, 0xF4, 0xF6)
ACCENT = RGBColor(0x1D, 0x4E, 0x89)
KMEANS = RGBColor(0x1F, 0x77, 0xB4)
WARD = RGBColor(0x2C, 0xA0, 0x2C)
AVERAGE = RGBColor(0xFF, 0x7F, 0x0E)
SINGLE = RGBColor(0xD6, 0x27, 0x28)
FONT = "Calibri"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]


# ---------------------------------------------------------------- helpers
def add_text(slide, x, y, w, h, text, size=18, bold=False, color=INK,
             align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = Inches(0.03)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = FONT
    return box


def add_bullets(slide, x, y, w, h, items, size=18, gap=8):
    """items: list of str or (str, RGBColor) -- bullet text, optional accent."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        text, color = item if isinstance(item, tuple) else (item, INK)
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(gap)
        bullet = p.add_run()
        bullet.text = "■  "
        bullet.font.size = Pt(size - 6)
        bullet.font.color.rgb = ACCENT
        bullet.font.name = FONT
        run = p.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.color.rgb = color
        run.font.name = FONT
    return box


def add_panel(slide, x, y, w, h, fill=PANEL, line=None):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w),
        Inches(h))
    shape.adjustments[0] = 0.04
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(1.5)
    shape.shadow.inherit = False
    return shape


def add_chip(slide, x, y, w, text, color, size=13):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w),
        Inches(0.36))
    shape.adjustments[0] = 0.5
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()
    shape.shadow.inherit = False
    tf = shape.text_frame
    tf.margin_top = tf.margin_bottom = 0
    tf.margin_left = tf.margin_right = 0
    tf.word_wrap = False
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    run.font.name = FONT


def legend(slide, x, y):
    for i, (name, color) in enumerate(
            [("K-Means", KMEANS), ("Ward", WARD), ("Average", AVERAGE),
             ("Single", SINGLE)]):
        add_chip(slide, x + i * 0.97, y, 0.9, name, color, size=12)


def new_slide(title, subtitle=None, notes=""):
    slide = prs.slides.add_slide(BLANK)
    bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.18), prs.slide_height)
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()
    add_text(slide, 0.6, 0.35, 12.2, 0.8, title, size=32, bold=True)
    if subtitle:
        add_text(slide, 0.6, 1.1, 12.2, 0.5, subtitle, size=18, color=MUTED)
    slide.notes_slide.notes_text_frame.text = notes
    return slide


def add_picture_fit(slide, path, x, y, max_w, max_h):
    """Place a picture inside the box (x, y, max_w, max_h), keeping aspect."""
    from PIL import Image
    with Image.open(path) as im:
        w, h = im.size
    scale = min(max_w / (w / 100), max_h / (h / 100))
    pw, ph = (w / 100) * scale, (h / 100) * scale
    slide.shapes.add_picture(
        str(path), Inches(x + (max_w - pw) / 2), Inches(y + (max_h - ph) / 2),
        Inches(pw), Inches(ph))


def add_table(slide, x, y, w, rows, col_widths, font=15, header_fill=ACCENT,
              row_h=0.5, center_cols=()):
    n_rows, n_cols = len(rows), len(rows[0])
    shape = slide.shapes.add_table(
        n_rows, n_cols, Inches(x), Inches(y), Inches(w),
        Inches(row_h * n_rows))
    table = shape.table
    for j, cw in enumerate(col_widths):
        table.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        table.rows[i].height = Inches(row_h)
        for j, value in enumerate(row):
            cell = table.cell(i, j)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_left = cell.margin_right = Inches(0.1)
            cell.fill.solid()
            cell.fill.fore_color.rgb = (
                header_fill if i == 0 else (PANEL if i % 2 else BG))
            tf = cell.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = str(value)
            run.font.size = Pt(font)
            run.font.name = FONT
            run.font.bold = i == 0 or j == 0
            run.font.color.rgb = (
                RGBColor(0xFF, 0xFF, 0xFF) if i == 0 else INK)
            if j in center_cols:
                p.alignment = PP_ALIGN.CENTER
    return table


# ---------------------------------------------------------------- numbers
size = pd.read_csv(TAB / "dataset_size_results.csv")
shape = pd.read_csv(TAB / "cluster_shape_results.csv")
sep = pd.read_csv(TAB / "separation_summary.csv")


def rt(alg, n):
    return size[(size.algorithm == alg) & (size.n_samples == n)][
        "runtime_seconds"].iloc[0]


def sh(method, name, col):
    return shape[(shape.method == method) & (shape["shape"] == name)][
        col].iloc[0]


def sp(alg, ratio, col):
    return sep[(sep.algorithm == alg) & (sep.separation_ratio == ratio)][
        col].iloc[0] + 0.0


def f2(x):
    """Two decimals, never '-0.00'."""
    return f"{round(float(x), 2) + 0.0:.2f}"


# ---------------------------------------------------------------- slide 1
s = prs.slides.add_slide(BLANK)
bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width,
                        prs.slide_height)
bg.fill.solid()
bg.fill.fore_color.rgb = ACCENT
bg.line.fill.background()
add_text(s, 0.9, 2.1, 11.5, 1.2, "K-Means vs. Hierarchical Clustering",
         size=48, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
add_text(s, 0.9, 3.35, 11.5, 0.7, "When does each one win?", size=28,
         color=RGBColor(0xDB, 0xE7, 0xF5))
add_text(s, 0.9, 5.3, 11.5, 0.9,
         "Iaroslav Volkov  ·  Elizabeth Lam  ·  Fay Lee\n"
         "CSI 4103 Great Algorithms  ·  University of Ottawa",
         size=18, color=RGBColor(0xDB, 0xE7, 0xF5))
s.notes_slide.notes_text_frame.text = (
    "~20 s. We compared two of the most common clustering approaches and "
    "asked a practical question: when should you use which? We varied three "
    "properties of the data -- size, shape and separation -- one at a time.")

# ---------------------------------------------------------------- slide 2
s = new_slide(
    "Two very different ideas of a “cluster”",
    notes=(
        "~1 min. K-Means: guess k centres, assign points to the nearest, move "
        "the centres to the mean, repeat. It is cheap but only knows about "
        "centres, so it assumes round, similar-sized blobs. Hierarchical: "
        "start with every point alone and keep merging the two closest "
        "clusters. What 'closest' means is the linkage. Ward merges the pair "
        "that adds the least variance, so it behaves like K-Means. Average "
        "uses the mean pairwise distance. Single uses the nearest pair of "
        "points, so it follows chains of nearby points. The catch: it needs "
        "all pairwise distances, so quadratic memory."))
add_panel(s, 0.6, 1.5, 5.9, 5.2)
add_text(s, 0.85, 1.65, 5.4, 0.5, "K-Means", size=26, bold=True, color=KMEANS)
add_bullets(s, 0.85, 2.3, 5.4, 3.0, [
    "Pick k centres",
    "Assign each point to its nearest centre",
    "Move each centre to the mean of its points; repeat",
], size=19)
add_text(s, 0.85, 5.0, 5.4, 1.6,
         "Assumes compact, round clusters.\nCheap: about O(n·k) per step.",
         size=18, color=MUTED)

add_panel(s, 6.85, 1.5, 5.9, 5.2)
add_text(s, 7.1, 1.65, 5.4, 0.5, "Hierarchical (agglomerative)", size=26,
         bold=True, color=ACCENT)
add_text(s, 7.1, 2.3, 5.4, 0.9,
         "Every point starts alone; repeatedly merge the two closest "
         "clusters. “Closest” = the linkage:", size=19)
add_chip(s, 7.1, 3.5, 1.2, "Ward", WARD, 14)
add_text(s, 8.45, 3.47, 4.2, 0.45, "least increase in variance", size=17)
add_chip(s, 7.1, 4.05, 1.2, "Average", AVERAGE, 14)
add_text(s, 8.45, 4.02, 4.2, 0.45, "mean pairwise distance", size=17)
add_chip(s, 7.1, 4.6, 1.2, "Single", SINGLE, 14)
add_text(s, 8.45, 4.57, 4.2, 0.45, "nearest pair of points", size=17)
add_text(s, 7.1, 5.5, 5.4, 1.1,
         "Needs all pairwise distances:\nO(n²) memory.", size=18,
         color=MUTED)

# ---------------------------------------------------------------- slide 3
s = new_slide(
    "What we tested",
    notes=(
        "~1 min. Synthetic 2-D data so we know the true clusters. Three "
        "knobs, changed one at a time: size, shape, separation. We score "
        "with runtime, ARI (agreement with the truth, 1 is perfect, 0 is "
        "random) and the Silhouette Score (how compact and separated the "
        "clusters look, with no labels). Everything uses a fixed random "
        "seed. Our hypotheses were: K-Means wins on big, round data; "
        "hierarchical wins on odd shapes depending on linkage; and "
        "hierarchical cannot scale."))
for i, (head, body) in enumerate([
        ("Size", "500 → 20,000 points\n(hierarchical capped at 5,000)"),
        ("Shape", "blobs, stretched blobs,\ntwo moons, concentric circles"),
        ("Separation", "3 clusters from far apart\nto heavily overlapping")]):
    x = 0.6 + i * 4.15
    add_panel(s, x, 1.5, 3.95, 2.1)
    add_text(s, x + 0.2, 1.6, 3.6, 0.5, head, size=24, bold=True,
             color=ACCENT)
    add_text(s, x + 0.2, 2.2, 3.6, 1.3, body, size=17)
add_text(s, 0.6, 3.9, 6, 0.4, "Metrics", size=22, bold=True, color=ACCENT)
add_bullets(s, 0.6, 4.4, 6.1, 2.6, [
    "Runtime (median of 5 runs)",
    "ARI – agrees with the true labels? (1 = perfect)",
    "Silhouette – looks compact and separated? (no labels)",
], size=17)
add_text(s, 7.0, 3.9, 6, 0.4, "Hypotheses", size=22, bold=True,
         color=ACCENT)
add_bullets(s, 7.0, 4.4, 5.8, 2.6, [
    "H1  K-Means is cheaper on large, round data",
    "H2  Hierarchical finds odd shapes (some linkages)",
    "H3  Hierarchical does not scale",
], size=17)

# ---------------------------------------------------------------- slide 4
s = new_slide(
    "Size: K-Means stays flat, hierarchical grows like n²",
    notes=(
        "~1.5 min. Log-log plot. K-Means is flat around a tenth of a second "
        "-- at these sizes its cost is dominated by the fixed overhead of 10 "
        "restarts. The hierarchical curves are straight lines with slope "
        "about 2: quadratic. At 5,000 points Ward takes 0.7 s versus 0.13 s "
        "for K-Means. Honest caveat: below about 1,000 points hierarchical "
        "is actually faster. And we stopped it at 5,000 because the distance "
        "matrix is already 100 MB there and 1.6 GB at 20,000. On these easy "
        "blobs every method was perfect (ARI = 1), so size only affects "
        "cost, not quality."))
add_picture_fit(s, FIG / "runtime_vs_size.png", 0.5, 1.4, 7.7, 5.5)
add_bullets(s, 8.4, 1.6, 4.5, 5.0, [
    f"At 5,000 points: K-Means {rt('K-Means', 5000):.2f} s, "
    f"Ward {rt('Hierarchical (Ward)', 5000):.2f} s, "
    f"Average {rt('Hierarchical (Average)', 5000):.2f} s",
    "Fitted slope ≈ 2 for hierarchical, ≈ 0 for K-Means",
    "Below ~1,000 points hierarchical is faster",
    "Distance matrix: 100 MB at 5k, 1.6 GB at 20k",
    "Quality identical (ARI = 1) on easy blobs",
], size=17, gap=10)

# ---------------------------------------------------------------- slide 5
s = new_slide(
    "Shape: only Single linkage follows non-convex clusters",
    notes=(
        "~1.5 min. Rows are shapes, columns are the truth then each method. "
        "On round blobs, and on our mildly stretched blobs, everyone is "
        "perfect. On two moons and concentric circles, K-Means and Ward cut "
        "with straight boundaries and get ARI near zero to 0.26. Average is "
        "only a bit better. Single linkage gets exactly 1.0 on both, "
        "because it merges nearest neighbours and so follows a connected "
        "curve. This supports H2 -- but only for one of the three "
        "linkages. Caveat: our stretched blobs are too easy and don't yet "
        "test K-Means on elongated clusters."))
add_picture_fit(s, FIG / "cluster_shape_comparison.png", 0.5, 1.4, 8.4, 5.6)
add_bullets(s, 9.1, 1.6, 3.9, 3.6, [
    ("Moons & circles: Single ARI = "
     + f2(sh('Hierarchical (single)', 'Two moons', 'ari')),
     SINGLE),
    "K-Means, Ward, Average: ARI ≤ 0.36",
    "Round blobs: everyone is perfect",
], size=17, gap=10)
legend(s, 9.1, 5.6)
add_text(s, 9.1, 6.1, 3.9, 0.8, "(figure columns: truth, K-Means, "
         "Single, Ward, Average)", size=12, color=MUTED)

# ---------------------------------------------------------------- slide 6
s = new_slide(
    "Separation: from clearly apart to heavily overlapping",
    notes=(
        "~1 min. Three equal Gaussian clusters at the corners of a "
        "triangle; we keep the distance fixed and grow the spread sigma, "
        "so d over sigma goes from 12 down to 1.2. Ten random datasets per "
        "level. Look at the rows: at the top it is trivial, at the bottom "
        "even a human cannot find the groups. That is why we added an "
        "ORACLE: assign each point to its nearest TRUE centre. It is the "
        "best score any algorithm could reach at that overlap, so a low ARI "
        "with heavy overlap is not automatically the algorithm's fault."))
add_picture_fit(s, FIG / "separation_examples.png", 0.5, 1.3, 7.0, 5.9)
add_bullets(s, 7.8, 1.7, 5.0, 3.6, [
    "3 Gaussian clusters, centre distance d = 6",
    "Spread σ from 0.5 to 5, so d/σ from 12 down to 1.2",
    "10 random datasets per level",
], size=18, gap=10)
add_panel(s, 7.8, 4.6, 5.0, 2.1, fill=RGBColor(0xE8, 0xF0, 0xFA))
add_text(s, 8.0, 4.7, 4.6, 0.4, "Oracle reference", size=20, bold=True,
         color=ACCENT)
add_text(s, 8.0, 5.2, 4.6, 1.5,
         "Assign each point to its nearest true centre: the best any method "
         "can score at that overlap.", size=17)

# ---------------------------------------------------------------- slide 7
s = new_slide(
    "Separation: who breaks first?",
    notes=(
        "~2 min -- the main result. Left plot is ARI; x-axis is d over "
        "sigma, well separated on the right. Single linkage (red) "
        "collapses first, around d/sigma = 6, while the clusters are still "
        "clearly visible. Why: random Gaussian tails create isolated "
        "points, single linkage absorbs isolated points last, so cutting at "
        "k = 3 peels off two outliers -- the clusters had sizes 998, 1 "
        "and 1. Average goes next, Ward after, degrading smoothly. The "
        "surprise is K-Means (blue): it sits right on top of the grey "
        "oracle line the whole way. When its ARI drops at heavy overlap, "
        "that is the data being ambiguous, not the algorithm failing. "
        "Caveat: these are exactly the spherical Gaussians K-Means assumes, "
        "so this is its home turf."))
add_picture_fit(s, FIG / "separation_comparison.png", 0.5, 1.3, 12.3, 4.6)
for i, (head, body, color) in enumerate([
        ("Single fails first (d/σ ≈ 6)",
         "outliers peel off: clusters of size 998 / 1 / 1", SINGLE),
        ("Average, then Ward",
         "relative failure at d/σ = 4 and 3", AVERAGE),
        ("K-Means = oracle",
         "low ARI at heavy overlap is the data, not the algorithm", KMEANS)]):
    x = 0.6 + i * 4.15
    add_panel(s, x, 5.95, 3.95, 1.2)
    stripe = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(5.95),
                                Inches(0.09), Inches(1.2))
    stripe.fill.solid()
    stripe.fill.fore_color.rgb = color
    stripe.line.fill.background()
    add_text(s, x + 0.2, 6.0, 3.7, 0.4, head, size=16, bold=True)
    add_text(s, x + 0.2, 6.4, 3.7, 0.75, body, size=13, color=MUTED)

# ---------------------------------------------------------------- slide 8
s = new_slide(
    "A surprise: the Silhouette Score can point the wrong way",
    notes=(
        "~1 min. Silhouette needs no labels, it just rewards compact, "
        "well-separated, round clusters. On two moons K-Means scores a "
        "HIGHER silhouette than Single linkage even though Single is "
        "perfect and K-Means is wrong. At heavy overlap it is worse: "
        "Single linkage returns one giant cluster plus two lone points, "
        "ARI zero, yet gets the highest silhouette of all methods. So "
        "Silhouette encodes K-Means' own assumptions and can't be used "
        "alone to compare different kinds of algorithms. Use ARI when you "
        "have labels."))
rows = [
    ["Dataset", "Method", "Silhouette", "ARI"],
    ["Two moons", "K-Means",
     f2(sh('K-Means', 'Two moons', 'silhouette')),
     f2(sh('K-Means', 'Two moons', 'ari'))],
    ["Two moons", "Single",
     f2(sh('Hierarchical (single)', 'Two moons', 'silhouette')),
     f2(sh('Hierarchical (single)', 'Two moons', 'ari'))],
    ["Overlapping (d/σ = 1.5)", "K-Means",
     f2(sp('K-Means', 1.5, 'silhouette_mean')),
     f2(sp('K-Means', 1.5, 'ari_mean'))],
    ["Overlapping (d/σ = 1.5)", "Single",
     f2(sp('Hierarchical (Single)', 1.5, 'silhouette_mean')),
     f2(sp('Hierarchical (Single)', 1.5, 'ari_mean'))],
]
add_table(s, 0.6, 1.7, 7.6, rows, [3.2, 1.6, 1.5, 1.3], font=17, row_h=0.62,
          center_cols=(2, 3))
add_bullets(s, 8.6, 1.8, 4.3, 4.5, [
    "Silhouette rewards round, compact clusters",
    "Perfect moons look “worse” than wrong ones",
    "At heavy overlap, Single scores highest with ARI = 0",
    "Use ARI when labels exist",
], size=18, gap=12)

# ---------------------------------------------------------------- slide 9
s = new_slide(
    "Takeaways: which one should you use?",
    notes=(
        "~1 min. Summary: no universal winner. The linkage matters more "
        "than the family: Single is the best on non-convex shapes and the "
        "worst with noise; Ward is basically a slightly worse K-Means. "
        "K-Means is the efficient, robust default for compact clusters. "
        "Hierarchical is fine for small data. Always pick a metric that "
        "matches what you care about."))
rows = [
    ["Situation", "Reasonable choice"],
    ["Large n, compact clusters", "K-Means"],
    ["Small n, want a full hierarchy", "Ward or Average"],
    ["Non-convex shapes, clean and well separated", "Single linkage"],
    ["Noisy or overlapping clusters", "K-Means or Ward (avoid Single)"],
    ["Very different cluster sizes or densities", "Ward, then K-Means"],
]
add_table(s, 0.6, 1.6, 12.1, rows, [7.1, 5.0], font=19, row_h=0.62)
add_text(s, 0.6, 5.6, 12.1, 1.3,
         "No algorithm wins everywhere – the linkage matters more than "
         "“K-Means vs. hierarchical”.", size=22, bold=True,
         color=ACCENT)

# ---------------------------------------------------------------- slide 10
s = new_slide(
    "Caveats and next steps",
    notes=(
        "~30 s, then questions. Be upfront about limits: 2-D synthetic "
        "data, k given to every method, one seed for most experiments, and "
        "our separation data match K-Means' assumptions. Next: harder "
        "shapes, noise, DBSCAN and spectral clustering, measuring memory "
        "directly, real data and unknown k."))
add_text(s, 0.6, 1.5, 6, 0.5, "Caveats", size=24, bold=True, color=ACCENT)
add_bullets(s, 0.6, 2.1, 5.9, 4.5, [
    "2-D synthetic data; k is given",
    "One seed for size and shape; 10 for separation",
    "Separation data matches K-Means' assumptions",
    "Timing: one machine, K-Means dominated by overhead",
], size=18, gap=10)
add_text(s, 6.9, 1.5, 6, 0.5, "Next steps", size=24, bold=True, color=ACCENT)
add_bullets(s, 6.9, 2.1, 5.9, 4.5, [
    "Stronger stretching, noisy moons/circles",
    "DBSCAN and spectral clustering",
    "Measure memory; push hierarchical past 5k",
    "Real data, unknown k",
], size=18, gap=10)
add_text(s, 0.6, 5.2, 12, 0.9, "Questions?", size=36, bold=True,
         color=ACCENT)

prs.save(OUT)
print(f"Saved: {OUT}")
