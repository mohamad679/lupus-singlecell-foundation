"""Build the four corrected, publication-resolution figures from versioned results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/published"
OUTPUT = ROOT / "figures/main"
COLORS = {"geneformer": "#355c9a", "pseudobulk": "#b45726", "metadata_only_age": "#56805b"}
LABELS = {"geneformer": "Geneformer V1", "pseudobulk": "Pseudobulk", "metadata_only_age": "Age"}


def read(name):
    return json.loads((RESULTS / name).read_text())


def setup():
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.labelcolor": "#25303a", "text.color": "#25303a",
                         "figure.facecolor": "white", "savefig.facecolor": "white"})
    OUTPUT.mkdir(parents=True, exist_ok=True)


def save(fig, stem):
    fig.savefig(OUTPUT / f"{stem}.tiff", dpi=300, bbox_inches="tight", pil_kwargs={"compression": "tiff_lzw"})
    fig.savefig(OUTPUT / f"{stem}.png", dpi=180, bbox_inches="tight")
    fig.savefig(OUTPUT / f"{stem}.pdf", bbox_inches="tight")
    plt.close(fig)


def errorbar(ax, x, row, color, marker="o", label=None):
    v = row["auroc"]
    lo, hi = row["ci95"]
    ax.errorbar(x, v, yerr=[[v-lo], [hi-v]], color=color, marker=marker,
                capsize=3, lw=1.5, markersize=6, label=label)


def figure1(descriptive):
    shared = descriptive["modes"]["shared"]
    # Comparator development values come from the released restricted-space/age CV artifacts.
    restricted = json.loads((ROOT / "results/reference/historical_pseudobulk_restricted_cv.json").read_text())
    historical = pd.read_csv(ROOT / "results/reference/historical_dev_sle_vs_healthy.csv").set_index("arm")
    age = historical.loc["metadata_only_age"]
    dev = {"geneformer": shared["development_geneformer"],
           "pseudobulk": {"auroc": restricted["auroc"],
                          "ci95": [restricted["ci_lower_95"], restricted["ci_upper_95"]]},
           "metadata_only_age": {"auroc": age["auroc"],
                                 "ci95": [age["ci_lower_95"], age["ci_upper_95"]]}}
    fig, ax = plt.subplots(figsize=(7.2, 4.6), layout="constrained")
    offsets = {"geneformer": -.15, "pseudobulk": 0, "metadata_only_age": .15}
    for arm in LABELS:
        x = np.array([0, 1]) + offsets[arm]
        a = dev[arm]
        b = shared["external"][arm]["overall"]
        ax.plot(x, [a["auroc"], b["auroc"]], color=COLORS[arm], alpha=.55, lw=1)
        errorbar(ax, x[0], a, COLORS[arm], label=LABELS[arm])
        errorbar(ax, x[1], b, COLORS[arm])
    ax.set(xlim=(-.38, 1.38), ylim=(0, 1.06), ylabel="Donor-level AUROC",
           xticks=[0, 1], xticklabels=["Development (nested CV)", "External (fixed model)"])
    ax.axhline(.5, color="#abb2b9", ls="--", lw=.8)
    ax.legend(frameon=False, ncol=3, loc="lower left", fontsize=9)
    ax.set_title("Corrected shared-gene primary analysis", loc="left", weight="bold")
    save(fig, "Figure_1")


def figure2(descriptive):
    rows = descriptive["modes"]["shared"]["external"]
    fig, ax = plt.subplots(figsize=(7.2, 4.6), layout="constrained")
    for i, arm in enumerate(LABELS):
        for j, group in enumerate(("Children", "Adult")):
            x = j + (i-1)*.18
            errorbar(ax, x, rows[arm][group], COLORS[arm], label=LABELS[arm] if j == 0 else None)
    ax.set(xlim=(-.48, 1.48), ylim=(0, 1.06), ylabel="External donor-level AUROC",
           xticks=[0, 1], xticklabels=["Source Children (n=44)", "Source Adult (n=12)"])
    ax.axhline(.5, color="#abb2b9", ls="--", lw=.8)
    ax.legend(frameon=False, ncol=3, loc="lower left", fontsize=9)
    ax.set_title("External performance by source age group", loc="left", weight="bold")
    save(fig, "Figure_2")


def figure3(analysis):
    fig, ax = plt.subplots(figsize=(7.2, 3.7), layout="constrained")
    names = [("geneformer_vs_age", "Geneformer − age"),
             ("geneformer_vs_pseudobulk", "Geneformer − pseudobulk")]
    for i, (key, label) in enumerate(names):
        r = analysis["comparisons"][key]
        x, (lo, hi) = r["difference"], r["ci95"]
        ax.errorbar(x, 1-i, xerr=[[x-lo], [hi-x]], fmt="o", color=COLORS["geneformer"],
                    capsize=4, lw=1.7, markersize=7)
        ax.text(.43, 1-i, f"Holm p={r['holm_adjusted_p']:.3f}; rule not met", va="center", fontsize=9)
    ax.axvline(0, color="#737b82", ls="--", lw=1)
    ax.set(xlim=(-.4, .86), ylim=(-.55, 1.55), yticks=[0, 1],
           yticklabels=[names[1][1], names[0][1]], xlabel="Paired AUROC difference (95% donor-bootstrap CI)")
    ax.set_title("Corrected co-primary comparisons", loc="left", weight="bold")
    save(fig, "Figure_3")


def figure4(probe, historical):
    rows = [probe, historical["arms"]["pseudobulk"], historical["arms"]["metadata_only_age"]]
    fig, ax = plt.subplots(figsize=(7.2, 3.7), layout="constrained")
    for i, (arm, r) in enumerate(zip(LABELS, rows)):
        v = r.get("cohort_membership_auroc", r.get("cohort_signature_auroc"))
        lo, hi = r["ci95"]
        ax.errorbar(v, 2-i, xerr=[[max(0, v-lo)], [max(0, hi-v)]], fmt="o",
                    color=COLORS[arm], capsize=3, lw=1.5, markersize=7)
    ax.axvline(.5, color="#abb2b9", ls="--", lw=.8)
    legend_handles = [
        Line2D([0], [0], marker="o", color="#355c9a", linestyle="none",
               markersize=7, label="Point: AUROC"),
        Line2D([0], [0], marker="|", color="#56805b", linestyle="-",
               markersize=10, lw=1.5, label="Whisker: 95% donor-bootstrap CI"),
        Line2D([0], [0], color="#abb2b9", linestyle="--", lw=.8,
               label="Dashed line: chance (0.5)"),
    ]
    ax.legend(handles=legend_handles, loc="upper left", bbox_to_anchor=(.01, .98),
              frameon=False, fontsize=8)
    ax.set(xlim=(.47, 1.025), ylim=(-.55, 2.55), yticks=[0, 1, 2],
           yticklabels=["Age", "Pseudobulk", "Corrected Geneformer V1"],
           xlabel="Cohort-membership AUROC (95% donor-bootstrap CI)")
    ax.set_title("Post-hoc development versus external cohort probe", loc="left", weight="bold")
    save(fig, "Figure_4")


def main():
    global RESULTS, OUTPUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=RESULTS)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    RESULTS, OUTPUT = args.results_dir, args.output_dir
    setup()
    descriptive = read("corrected_v1_descriptive.json")
    figure1(descriptive)
    figure2(descriptive)
    figure3(read("corrected_v1_shared_analysis.json"))
    historical = json.loads((ROOT / "results/reference/historical_cohort_signature_probe.json").read_text())
    figure4(read("corrected_v1_shared_cohort_probe.json"), historical)
    print(OUTPUT)


if __name__ == "__main__":
    main()
