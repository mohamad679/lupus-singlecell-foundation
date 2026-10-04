"""Q2-hardening item 4: dev-vs-sealed confounder comparison from
already-committed metadata only. No sealed expression/cell data is read;
only results/l2_dev_donor_metadata.csv and results/l2_sealed_donor_metadata.csv
(both already-committed, real, previously verified artifacts).

Confounders quantified:
- Age: both cohorts have this field. Real, quantitative comparison.
- Sex: dev has it (real, committed); GSE135779's public GEO metadata has no
  sex field anywhere (verified during Phase 2 pre-flight, PREREG.md
  amendment log 2026-07-19) -- reported as explicitly unavailable, not
  approximated or omitted silently.
- Ancestry/self-reported ethnicity: same situation as sex -- dev has it,
  sealed does not have it in public metadata. Explicitly unavailable.
- Platform/chemistry: NEITHER cohort has this as a committed, structured,
  comparable field. PREREG.md Section 7 records only a qualitative
  statement ("different sequencing platform/generation... per their source
  publications"), not a structured field in any committed metadata CSV.
  Not included as a quantitative row for that reason -- see the note in the
  output file instead of a fabricated row.

Writes results/l2_cohort_confounders.csv (tidy long format) and
figures/cohort_confounders_age.png/.pdf (age distribution comparison).
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_ROOT / "results"
FIGURES_DIR = REPO_ROOT / "figures"

BLUE = "#2a78d6"
AQUA = "#1baf7a"
GRID_GRAY = "#c9c8c0"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"


def load_dev() -> pd.DataFrame:
    return pd.read_csv(RESULTS_DIR / "l2_dev_donor_metadata.csv", dtype={"donor_id": str})


def load_sealed() -> pd.DataFrame:
    return pd.read_csv(RESULTS_DIR / "l2_sealed_donor_metadata.csv", dtype={"gsm_id": str})


def age_rows(dev: pd.DataFrame, sealed: pd.DataFrame) -> list[dict]:
    rows = []
    for cohort, df, col in [("dev", dev, "age"), ("sealed", sealed, "age")]:
        ages = df[col].dropna().astype(float)
        stats = {
            "n": int(len(ages)), "mean": float(ages.mean()), "sd": float(ages.std(ddof=1)),
            "min": float(ages.min()), "median": float(ages.median()), "max": float(ages.max()),
        }
        for stat_name, value in stats.items():
            rows.append({"cohort": cohort, "variable": "age", "category": stat_name,
                         "value": value, "note": ""})
    return rows


def categorical_rows(dev: pd.DataFrame, variable: str, dev_col: str) -> list[dict]:
    rows = []
    counts = dev[dev_col].value_counts()
    total = counts.sum()
    for category, n in counts.items():
        rows.append({"cohort": "dev", "variable": variable, "category": category,
                     "value": int(n), "note": f"{n / total * 100:.1f}% of n={total}"})
    rows.append({"cohort": "sealed", "variable": variable, "category": "NOT_AVAILABLE",
                 "value": None,
                 "note": f"GSE135779 public GEO metadata has no {variable} field "
                         "(verified Phase 2 pre-flight, PREREG.md amendment 2026-07-19)"})
    return rows


def platform_note_row() -> dict:
    return {
        "cohort": "both", "variable": "platform_chemistry", "category": "NOT_A_STRUCTURED_FIELD",
        "value": None,
        "note": "Neither cohort has platform/chemistry as a committed, structured metadata "
                "field. PREREG.md Section 7 records only a qualitative statement "
                "('different sequencing platform/generation... per their source publications'). "
                "Not fabricated as a quantitative row.",
    }


def fig_age_comparison(dev: pd.DataFrame, sealed: pd.DataFrame) -> None:
    dev_ages = dev["age"].dropna().astype(float)
    sealed_ages = sealed["age"].dropna().astype(float)

    fig, ax = plt.subplots(figsize=(7.5, 5))
    bins = np.arange(0, 90, 5)
    ax.hist(dev_ages, bins=bins, color=BLUE, alpha=0.75, label=f"Dev (Perez 2022), n={len(dev_ages)}",
            edgecolor="white", linewidth=0.4)
    ax.hist(sealed_ages, bins=bins, color=AQUA, alpha=0.75, label=f"Sealed (GSE135779), n={len(sealed_ages)}",
            edgecolor="white", linewidth=0.4)
    ax.set_xlabel("Age (years)")
    ax.set_ylabel("Donor count")
    ax.set_title("Dev vs. sealed cohort age distribution\n"
                  "Dev is 100% adult (20-83); sealed is pediatric-primary + a small adult stratum",
                  fontsize=10.5)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_facecolor("#fcfcfb")
    fig.patch.set_facecolor("#fcfcfb")

    FIGURES_DIR.mkdir(exist_ok=True)
    fig.savefig(FIGURES_DIR / "cohort_confounders_age.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIGURES_DIR / "cohort_confounders_age.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote figures/cohort_confounders_age.png and .pdf")


def main() -> None:
    dev = load_dev()
    sealed = load_sealed()

    rows = []
    rows += age_rows(dev, sealed)
    rows += categorical_rows(dev, "sex", "sex")
    rows += categorical_rows(dev, "ancestry_self_reported_ethnicity", "self_reported_ethnicity")
    rows.append(platform_note_row())

    df = pd.DataFrame(rows)
    out_path = RESULTS_DIR / "l2_cohort_confounders.csv"
    df.to_csv(out_path, index=False)
    print(f"wrote {out_path}")
    print(df.to_string(index=False))

    fig_age_comparison(dev, sealed)


if __name__ == "__main__":
    main()
