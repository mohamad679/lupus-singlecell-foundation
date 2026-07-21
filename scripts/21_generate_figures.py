"""Render figures from already-committed L2 artifacts. Read-only: no new
modeling, no sealed-cohort data access. Reads only:
- results/l2_dev_sle_vs_healthy.csv (dev-cohort CV summary, all 3 arms)
- results/l2_sealed_results.json (Phase 3 sealed-cohort summary, all 3 arms
  + both co-primary comparisons)
- results/l2_sealed_predictions_regenerated.json (per-donor sealed
  probabilities + permutation null arrays -- deterministically regenerated
  by scripts/22_regenerate_sealed_predictions.py from already-committed
  feature artifacts, verified to match l2_sealed_results.json's summary
  statistics exactly; not a new sealed-cohort access, see that script's
  docstring)

Does not touch stageN_*.py, FREEZE.json, SEALED_OPENED.json, or any
sealed-access script (scripts/18-20, the Kaggle kernels).

Colors: a validated 3-slot categorical subset (blue/aqua/yellow) and a
validated 2-slot subset (blue/aqua) from the project's standard palette,
checked with the dataviz skill's validate_palette.js before use (both pass;
the WARN on sub-3:1 contrast for aqua/yellow is mitigated here by direct
value labels and a legend on every figure, per that check's own remediation
note). Status red is reserved for the REJECTED label only, never used as a
series color. This is a static, light-mode-only export (matplotlib PNG/PDF
for a written report), not an interactive/dark-mode chart, which is a
deliberate, disclosed simplification of the dataviz skill's full checklist
(hover layer and dark mode do not apply to a static image export).
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_ROOT / "results"
FIGURES_DIR = REPO_ROOT / "figures"
DPI = 300

# Validated categorical palette subset (project standard, see scripts/21's
# docstring / node scripts/validate_palette.js confirmation).
BLUE = "#2a78d6"
AQUA = "#1baf7a"
YELLOW = "#eda100"
CRITICAL_RED = "#d03b3b"   # status color, reserved -- REJECTED label only
GRID_GRAY = "#c9c8c0"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"

ARM_ORDER = ["geneformer", "pseudobulk", "metadata_only_age"]
ARM_LABELS = {"geneformer": "Geneformer", "pseudobulk": "Pseudobulk", "metadata_only_age": "Metadata (age)"}
ARM_COLORS = {"geneformer": BLUE, "pseudobulk": AQUA, "metadata_only_age": YELLOW}

plt.rcParams.update({
    "font.size": 11,
    "axes.edgecolor": GRID_GRAY,
    "axes.labelcolor": TEXT_PRIMARY,
    "text.color": TEXT_PRIMARY,
    "xtick.color": TEXT_SECONDARY,
    "ytick.color": TEXT_SECONDARY,
    "axes.grid": True,
    "grid.color": GRID_GRAY,
    "grid.linewidth": 0.6,
    "axes.axisbelow": True,
    "figure.facecolor": "#fcfcfb",
    "axes.facecolor": "#fcfcfb",
    "savefig.facecolor": "#fcfcfb",
})


def load_dev_summary() -> dict:
    with open(RESULTS_DIR / "l2_dev_sle_vs_healthy.csv") as f:
        rows = {r["arm"]: r for r in csv.DictReader(f)}
    return rows


def load_regenerated_predictions() -> dict | None:
    path = RESULTS_DIR / "l2_sealed_predictions_regenerated.json"
    if not path.exists():
        return None
    with open(path) as f:
        return json.load(f)


def load_sealed_results() -> dict:
    with open(RESULTS_DIR / "l2_sealed_results.json") as f:
        return json.load(f)


def save_fig(fig, name: str) -> None:
    FIGURES_DIR.mkdir(exist_ok=True)
    fig.savefig(FIGURES_DIR / f"{name}.png", dpi=DPI, bbox_inches="tight")
    fig.savefig(FIGURES_DIR / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)
    print(f"wrote figures/{name}.png and figures/{name}.pdf")


def add_value_labels(ax, bars, values, fmt="{:.3f}"):
    for bar, v in zip(bars, values):
        ax.annotate(fmt.format(v), (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                    fontsize=8.5, color=TEXT_SECONDARY)


# --- Figure 1: dev vs sealed AUROC, grouped bar with 95% CI ---------------

def fig_dev_vs_sealed(dev: dict, sealed: dict) -> None:
    x = np.arange(len(ARM_ORDER))
    width = 0.36

    dev_auroc = [float(dev[a]["auroc"]) for a in ARM_ORDER]
    dev_lo = [float(dev[a]["auroc"]) - float(dev[a]["ci_lower_95"]) for a in ARM_ORDER]
    dev_hi = [float(dev[a]["ci_upper_95"]) - float(dev[a]["auroc"]) for a in ARM_ORDER]

    sealed_auroc = [sealed["arms"][a]["sealed_auroc_overall"] for a in ARM_ORDER]
    sealed_lo = [sealed["arms"][a]["sealed_auroc_overall"] - sealed["arms"][a]["sealed_ci95_overall"][0] for a in ARM_ORDER]
    sealed_hi = [sealed["arms"][a]["sealed_ci95_overall"][1] - sealed["arms"][a]["sealed_auroc_overall"] for a in ARM_ORDER]

    fig, ax = plt.subplots(figsize=(7.5, 5))
    b1 = ax.bar(x - width / 2, dev_auroc, width, yerr=[dev_lo, dev_hi], capsize=4,
                color=BLUE, label="Dev-cohort internal CV (n=261, or 259 for metadata)", edgecolor="white", linewidth=0.5)
    b2 = ax.bar(x + width / 2, sealed_auroc, width, yerr=[sealed_lo, sealed_hi], capsize=4,
                color=AQUA, label="Sealed cohort, GSE135779 (n=56)", edgecolor="white", linewidth=0.5)
    add_value_labels(ax, b1, dev_auroc)
    add_value_labels(ax, b2, sealed_auroc)

    ax.axhline(0.5, color=GRID_GRAY, linewidth=1, linestyle="--", zorder=0)
    ax.set_xticks(x)
    ax.set_xticklabels([ARM_LABELS[a] for a in ARM_ORDER])
    ax.set_ylabel("Patient-level AUROC")
    ax.set_ylim(0, 1.05)
    ax.set_title("Dev-cohort internal CV vs. sealed-cohort AUROC, all three arms\n"
                  "Error bars: 95% patient-bootstrap CI", fontsize=11)
    ax.legend(loc="lower left", frameon=False, fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    save_fig(fig, "dev_vs_sealed_auroc")


# --- Figure 2: age-stratified sealed AUROC ---------------------------------

def fig_age_stratified(sealed: dict) -> None:
    x = np.arange(len(ARM_ORDER))
    width = 0.36

    def get(arm, group, key):
        return sealed["arms"][arm]["stratified"][group][key]

    ped_auroc = [get(a, "Children", "auroc") for a in ARM_ORDER]
    ped_lo = [ped_auroc[i] - get(a, "Children", "ci95")[0] for i, a in enumerate(ARM_ORDER)]
    ped_hi = [get(a, "Children", "ci95")[1] - ped_auroc[i] for i, a in enumerate(ARM_ORDER)]

    adult_auroc = [get(a, "Adult", "auroc") for a in ARM_ORDER]
    adult_lo = [adult_auroc[i] - get(a, "Adult", "ci95")[0] for i, a in enumerate(ARM_ORDER)]
    adult_hi = [get(a, "Adult", "ci95")[1] - adult_auroc[i] for i, a in enumerate(ARM_ORDER)]

    fig, ax = plt.subplots(figsize=(7.5, 5))
    b1 = ax.bar(x - width / 2, ped_auroc, width, yerr=[ped_lo, ped_hi], capsize=4,
                color=BLUE, label="Pediatric (n=44)", edgecolor="white", linewidth=0.5)
    b2 = ax.bar(x + width / 2, adult_auroc, width, yerr=[adult_lo, adult_hi], capsize=4,
                color=AQUA, label="Adult (n=12)", edgecolor="white", linewidth=0.5)
    add_value_labels(ax, b1, ped_auroc)
    add_value_labels(ax, b2, adult_auroc)

    ax.axhline(0.5, color=GRID_GRAY, linewidth=1, linestyle="--", zorder=0)
    ax.set_xticks(x)
    ax.set_xticklabels([ARM_LABELS[a] for a in ARM_ORDER])
    ax.set_ylabel("Patient-level AUROC")
    ax.set_ylim(0, 1.15)
    ax.set_title("Sealed-cohort AUROC, stratified by age group\n"
                  "Error bars: 95% patient-bootstrap CI. Adult stratum is small (n=12); CIs are wide.",
                  fontsize=11)
    ax.legend(loc="lower left", frameon=False, fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    save_fig(fig, "age_stratified_sealed")


# --- Figure 4: co-primary forest plot --------------------------------------

def fig_forest_plot(sealed: dict) -> None:
    comps = [
        ("A: Geneformer − Metadata", sealed["co_primary_comparisons"]["A_geneformer_vs_metadata"]),
        ("B: Geneformer − Pseudobulk", sealed["co_primary_comparisons"]["B_geneformer_vs_pseudobulk"]),
    ]
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    y_pos = [1, 0]
    colors = [BLUE, AQUA]
    for (label, c), y, color in zip(comps, y_pos, colors):
        diff = c["observed_auroc_diff"]
        lo, hi = c["bootstrap_ci95_diff"]
        ax.errorbar(diff, y, xerr=[[diff - lo], [hi - diff]], fmt="o", color=color,
                    ecolor=color, elinewidth=2, capsize=5, markersize=9, zorder=3)
        ax.annotate(
            f"diff={diff:+.4f}, CI=[{lo:+.4f}, {hi:+.4f}], p={c['permutation_p_two_sided_pre_holm']:.5f} (pre-Holm)",
            (hi, y), xytext=(8, 0), textcoords="offset points", va="center", fontsize=8.5, color=TEXT_SECONDARY,
        )
        ax.annotate("REJECTED", (lo, y), xytext=(-8, 0), textcoords="offset points",
                     va="center", ha="right", fontsize=9, color=CRITICAL_RED, fontweight="bold")

    ax.axvline(0, color=TEXT_SECONDARY, linewidth=1.2, linestyle="-", zorder=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels([c[0] for c in comps])
    ax.set_xlabel("AUROC difference (Geneformer − comparator), sealed cohort")
    ax.set_xlim(-0.45, 0.75)
    ax.set_ylim(-0.7, 1.7)
    ax.set_title("Co-primary comparisons: paired patient-bootstrap CI on AUROC difference\n"
                  "Decision rule: CI must exclude 0 (entirely positive) AND be Holm-significant. Both REJECTED.",
                  fontsize=10.5)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.tick_params(left=False)
    save_fig(fig, "coprimary_forest_plot")


# --- Figure 3: sealed ROC curves, all three arms ---------------------------

def fig_roc_curves(regenerated: dict, sealed: dict) -> None:
    from sklearn.metrics import roc_curve

    fig, ax = plt.subplots(figsize=(6.2, 6.2))
    ax.plot([0, 1], [0, 1], color=GRID_GRAY, linestyle="--", linewidth=1, zorder=0)

    for arm in ARM_ORDER:
        y = np.array(regenerated[arm]["y"])
        proba = np.array(regenerated[arm]["proba"])
        fpr, tpr, _ = roc_curve(y, proba)
        auroc = sealed["arms"][arm]["sealed_auroc_overall"]
        ax.plot(fpr, tpr, color=ARM_COLORS[arm], linewidth=2.2,
                 label=f"{ARM_LABELS[arm]} (AUROC={auroc:.3f})")

    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(-0.02, 1.02)
    ax.set_aspect("equal")
    ax.set_title("Sealed-cohort ROC curves, all three arms (n=56)\n"
                  "Per-donor probabilities regenerated deterministically from frozen, "
                  "already-committed inputs;\nverified to reproduce the committed AUROC exactly.",
                  fontsize=9.5)
    ax.legend(loc="lower right", frameon=False, fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    save_fig(fig, "roc_curves_sealed")


# --- Figure 5: permutation null distribution example ------------------------

def fig_permutation_null(regenerated: dict, sealed: dict, arm: str = "geneformer") -> None:
    null = np.array(regenerated[arm]["permutation_null"])
    observed = sealed["arms"][arm]["sealed_auroc_overall"]
    p_value = sealed["arms"][arm]["sealed_permutation_p_overall"]

    fig, ax = plt.subplots(figsize=(7.5, 5))
    ax.hist(null, bins=40, color=BLUE, alpha=0.85, edgecolor="white", linewidth=0.4,
            label=f"Permutation null (n={len(null)}, label-shuffled, fixed predictions)")
    ax.axvline(observed, color=CRITICAL_RED, linewidth=2.2, linestyle="-",
               label=f"Observed sealed AUROC = {observed:.4f}")
    ax.axvline(0.5, color=GRID_GRAY, linewidth=1, linestyle="--", zorder=0)

    ax.set_xlabel("AUROC")
    ax.set_ylabel("Count (of 1000 permutations)")
    ax.set_title(f"{ARM_LABELS[arm]}: sealed-cohort permutation-null distribution\n"
                  f"Two-sided permutation p = {p_value:.5f} "
                  f"(null mean={null.mean():.4f}, std={null.std():.4f})",
                  fontsize=10.5)
    ax.legend(loc="upper left", frameon=False, fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    save_fig(fig, "permutation_null_example")


def main() -> None:
    dev = load_dev_summary()
    sealed = load_sealed_results()
    regenerated = load_regenerated_predictions()

    fig_dev_vs_sealed(dev, sealed)
    fig_age_stratified(sealed)
    fig_forest_plot(sealed)

    if regenerated is not None:
        fig_roc_curves(regenerated, sealed)
        fig_permutation_null(regenerated, sealed, arm="geneformer")
        print("\nGenerated all 5 requested figures.")
    else:
        print("\nGenerated 3 of 5 requested figures from complete, already-committed data.")
        print("roc_curves_sealed.png and permutation_null_example.png need "
              "results/l2_sealed_predictions_regenerated.json, which does not exist -- "
              "run scripts/22_regenerate_sealed_predictions.py first, or skip these two.")


if __name__ == "__main__":
    main()
