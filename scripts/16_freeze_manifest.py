"""Write FREEZE.json: the hash manifest that locks the dev-cohort-selected
pipeline before any GSE135779 (sealed cohort) access, per PREREG.md.

This is a hash manifest, not a framework: it hashes the files that
determine a sealed-cohort prediction, pulls the hyperparameters already
selected by nested CV on dev data (does not re-select anything), and
records the commit SHA + a human-readable reason citing the committed dev
results. See scripts/freeze_guard.py for the corresponding guard that any
future sealed-cohort script must pass before running.

Frozen files and why each is included:
- PREREG.md: the binding preregistration itself.
- scripts/14_l2_census_pipeline.py: donor metadata fetch, age-parsing
  (parse_development_stage_age), and the CPM+log1p pseudobulk aggregation
  math (compute_donor_pseudobulk_from_counts / stream_donor_pseudobulk).
- scripts/15_l2_dev_cv_pseudobulk_metadata.py: the actual model pipeline
  (StandardScaler + LogisticRegression construction, fit_logreg_oof) that
  would be reused with the frozen hyperparameters to score a sealed-cohort
  donor. Hyperparameters alone are not sufficient to reproduce a prediction
  without this file. Included even though the task's own file list didn't
  name it, because it is a real determinant -- flagged in the freeze
  report, not silently added.
- kaggle_kernels/l2_pseudobulk/l2_pseudobulk.py +
  kaggle_kernels/l2_pseudobulk/kernel-metadata.json: the actual code (and
  its execution config) that produced the committed dev pseudobulk
  embeddings at full scale. Also not in the task's literal file list but a
  real determinant -- scripts/14_l2_census_pipeline.py contains equivalent
  logic but this is what actually ran.
- kaggle_kernels/l2_geneformer_full/l2_geneformer_full.py +
  kernel-metadata.json: the Geneformer arm's extraction code and its GPU/
  accelerator execution config.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]

FROZEN_FILES = [
    "PREREG.md",
    "scripts/14_l2_census_pipeline.py",
    "scripts/15_l2_dev_cv_pseudobulk_metadata.py",
    "kaggle_kernels/l2_pseudobulk/l2_pseudobulk.py",
    "kaggle_kernels/l2_pseudobulk/kernel-metadata.json",
    "kaggle_kernels/l2_geneformer_full/l2_geneformer_full.py",
    "kaggle_kernels/l2_geneformer_full/kernel-metadata.json",
    # Added 2026-07-21: gene-space intersection code and its input reference
    # data determine which genes a sealed-cohort prediction would even see;
    # a change to either changes what "the pipeline" computes.
    "scripts/17_gene_space_intersection.py",
    "results/gse135779_genes_reference.tsv",
]

HYPERPARAMETER_SELECTION_RULE = (
    "Each arm's nested CV (scripts/15_l2_dev_cv_pseudobulk_metadata.py, "
    "fit_logreg_oof) selects a regularization strength C independently in "
    "each of 5 outer StratifiedKFold folds, via inner 5-fold grid search "
    "over C_GRID=[0.001, 0.01, 0.1, 1.0, 10.0, 100.0]. The frozen C for a "
    "sealed-cohort prediction (C_frozen) is the median of those 5 per-fold "
    "selections -- not the value from a single fold, not a re-selection on "
    "the full dev set. This rule, not just its resulting values, is what is "
    "frozen: re-running scripts/15 on the same committed dev-cohort inputs "
    "must reproduce the same C_per_outer_fold list and therefore the same "
    "C_frozen via this same median rule."
)


def sha256_of(path: Path) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def current_commit_sha() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def selected_hyperparameters() -> dict:
    """Pull the already-selected C per arm from the committed CV run.
    Does not re-select -- takes the median of the 5 outer-fold selections
    already recorded in results/l2_dev_sle_vs_healthy.csv.
    """
    df = pd.read_csv(REPO_ROOT / "results" / "l2_dev_sle_vs_healthy.csv")
    out = {}
    for _, row in df.iterrows():
        per_fold = json.loads(row["selected_c_per_outer_fold_real_fit"])
        out[row["arm"]] = {
            "C_per_outer_fold": per_fold,
            "C_frozen": float(pd.Series(per_fold).median()),
            "model_family": "StandardScaler + LogisticRegression(l1_ratio=0, solver=lbfgs)",
            "auroc_dev_cv": float(row["auroc"]),
            "ci_95_dev_cv": [float(row["ci_lower_95"]), float(row["ci_upper_95"])],
            "permutation_p_dev_cv": float(row["permutation_p_value_two_sided"]),
        }
    return out


def main() -> None:
    hashes = {f: sha256_of(REPO_ROOT / f) for f in FROZEN_FILES}
    hyperparams = selected_hyperparameters()

    manifest = {
        "freeze_version": 1,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "commit_sha": current_commit_sha(),
        "frozen_files_sha256": hashes,
        "hyperparameter_selection_rule": HYPERPARAMETER_SELECTION_RULE,
        "hyperparameters": hyperparams,
        "gene_space_intersection": {
            "dev_gene_count": 61497,
            "sealed_gene_count": 32738,
            "overlap_count": 30165,
            "identifier_system": "Ensembl gene ID (both cohorts, no symbol mapping needed)",
            "source": "scripts/17_gene_space_intersection.py, self-tested against "
            "results/l2_dev_pseudobulk_counts.parquet and "
            "results/gse135779_genes_reference.tsv",
        },
        "deferred_to_future_work": (
            "PREREG.md Section 5.1 (cohort-signature probe) and the cell-type-level "
            "harmonization steps of Section 8, per the 2026-07-21 PREREG.md "
            "amendment: GSE135779's public deposit has no cell-type annotation, and "
            "no Scanpy-ingest label-transfer code exists in this repository "
            "(src/data/metadata_harmonization.py is an unimplemented fake-data "
            "contract stub). Co-primary comparisons A and B proceed on the "
            "mean-pooled arms only, which do not require cell-type labels."
        ),
        "reason": (
            "Dev-cohort (Perez 2022) honest CV complete and committed for all "
            "three PREREG arms: Geneformer AUROC 0.9676 (95% CI [0.9446, 0.9865], "
            "permutation p=0.001), pseudobulk AUROC 0.9839 (95% CI [0.9703, 0.9938], "
            "permutation p=0.001), metadata-only-age AUROC 0.6453 (95% CI "
            "[0.5741, 0.7184], permutation p=0.001). Feature extraction code, "
            "model family, and hyperparameters are locked at these values before "
            "any GSE135779 (sealed cohort) access, per PREREG.md's freeze/one-look "
            "discipline. No hyperparameter, feature-extraction, or model-family "
            "change is permitted after this point without a dated PREREG.md "
            "amendment."
        ),
    }

    out_path = REPO_ROOT / "FREEZE.json"
    with open(out_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"wrote {out_path}")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
