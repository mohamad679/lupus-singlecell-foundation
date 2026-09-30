"""Rebuild donor/cell and gene-availability diagnostics from released files."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
OUTPUT = RESULTS / "correction_2026-09"


def main():
    development = pd.read_csv(RESULTS / "l2_dev_donor_metadata.csv", dtype={"donor_id": str})
    external = pd.read_csv(RESULTS / "l2_sealed_donor_metadata.csv", dtype={"gsm_id": str})
    if development.donor_id.duplicated().any() or external.gsm_id.duplicated().any():
        raise ValueError("duplicate donor/sample identifier")
    if set(development.sle_label) != {0, 1} or set(external.sle_label) != {0, 1}:
        raise ValueError("unexpected disease label")
    if (development.n_cells <= 0).any() or (external.n_cells <= 0).any():
        raise ValueError("nonpositive donor cell count")
    rows = []
    for cohort, frame, group_col in (("development", development, None),
                                      ("external", external, "age_group")):
        groups = [("all", frame)] if group_col is None else list(frame.groupby(group_col))
        for group, subset in groups:
            for label in (0, 1):
                part = subset[subset.sle_label == label]
                rows.append({"cohort": cohort, "source_age_group": group,
                             "outcome": "SLE" if label else "healthy",
                             "n_donors": int(len(part)), "n_cells_source": int(part.n_cells.sum()),
                             "n_cells_tokenized": "pending corrected extraction",
                             "n_cells_embedded": "pending corrected extraction"})
    OUTPUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUTPUT / "historical_donor_cell_accounting.csv", index=False)

    dev_features = pd.read_parquet(RESULTS / "l2_dev_pseudobulk_counts_restricted.parquet")
    external_features = pd.read_parquet(RESULTS / "l2_sealed_pseudobulk_counts.parquet")
    if set(dev_features.columns) != set(external_features.columns):
        raise ValueError("released shared-gene feature sets differ")
    dev_zero = (dev_features == 0).all(axis=0)
    external_expressed = (external_features.loc[:, dev_zero] > 0).any(axis=0)
    diagnostic = {
        "interpretation": "post-hoc descriptive feature-availability diagnostic, not a causal batch-effect estimate",
        "shared_genes": len(dev_features.columns),
        "development_zero_genes": int(dev_zero.sum()),
        "development_zero_but_external_expressed_genes": int(external_expressed.sum()),
        "external_donors_with_any_such_gene": int((external_features.loc[:, dev_zero.index[dev_zero]] > 0).any(axis=1).sum()),
        "development_donors": len(development), "development_cells": int(development.n_cells.sum()),
        "external_donors": len(external), "external_cells": int(external.n_cells.sum()),
    }
    with (OUTPUT / "historical_gene_availability.json").open("w") as file:
        json.dump(diagnostic, file, indent=2)
    print(json.dumps(diagnostic, indent=2))


if __name__ == "__main__":
    main()
