# Legacy scaffolding (not used for any reported result)

This repository's development passed through an early Phase 1 scaffolding stage
before the real L2/Phase 3 pipeline (`scripts/14`-`26`) existed. Some of that
early scaffolding remains in the repository for history/traceability but is
**not part of the pipeline that produced any number in `MANUSCRIPT.md`,
`README.md`, or `results/l2_*`**. This document exists so a reader browsing the
tree doesn't mistake it for live code.

## What's legacy

- **`src/lupusfm/evaluation/stage4_*.py`, `stage5_*.py`, `stage6_*.py`,
  `stage7_*.py`** — early-development "contract"/gate modules (e.g.
  `stage5_pre_execution_audit_gate.py`, `stage6_split_leakage_control_gate.py`).
  Several are explicitly self-documented in their own docstrings as fake-data
  contracts that do not load real artifacts (e.g.
  `src/lupusfm/embeddings/aggregation.py`: "This module defines fake-data
  utilities... It does not load real artifacts").
- **`scripts/run_stage7_confounding_audit.py`,
  `run_stage7_geneformer_perturbation_plausibility.py`,
  `run_stage7_metadata_baseline.py`, `run_stage7_permutation_test.py`,
  `run_stage7_random_gene_set_controls.py`** — thin wrapper scripts that import
  and invoke the `src/lupusfm/evaluation/stage7_*` modules above.
- **`src/data/metadata_harmonization.py`** — an unimplemented Scanpy-ingest /
  k-NN label-transfer stub referenced by PREREG.md Section 8; never implemented
  (see `docs/PREREGISTRATION_DEVIATIONS.md` item 2).
- `scripts/00`-`12` — the earlier Phase 1 QC/scaffold pipeline.

## What supersedes it

All of the above is superseded by the real, executed pipeline:
`scripts/14`-`26`, plus the Kaggle kernels under `kaggle_kernels/`, plus the one
retained secondary result, `scripts/13_stage7_kaggle_result_reconciliation.py`
(the internal-only flare-discrimination analysis in the README's "Secondary /
internal-only" section — note this is a *different* file from the
`src/lupusfm/evaluation/stage7_*` modules above, despite the shared "stage7"
name; `scripts/13` implements its own real math directly and does not import
from `src/lupusfm/evaluation/`).

## Disposition

These files are kept, not deleted, for development history. They are not
imported by, and do not affect, any script in `scripts/14`-`26`, any file
under `results/`, `figures/`, `FREEZE.json`, or `SEALED_OPENED.json`, or any
number reported in `MANUSCRIPT.md`.
