# Project Status


Current claim boundary: internal LOOCV only; no clinical claim; no external validation.

## Current repository status

The repository is currently in a cleaned research-stage state after Stage 7 reconciliation.

Current completed state:

- Stage 7 leakage-safe reconciliation complete
- patient-level Geneformer embedding evaluation implemented as a script
- internal leave-one-patient-out cross-validation completed
- metric table, prediction manifest, and run summary saved under `reports/stage7_kaggle_result_reconciliation/`
- research-stage README updated
- model card added
- limitations document added

## Current authoritative implementation

The current authoritative Stage 7 implementation is:

- `scripts/13_stage7_kaggle_result_reconciliation.py`

The current authoritative Stage 7 outputs are:

- `reports/stage7_kaggle_result_reconciliation/stage7_run_summary.json`
- `reports/stage7_kaggle_result_reconciliation/stage7_metric_results.csv`
- `reports/stage7_kaggle_result_reconciliation/stage7_prediction_manifest.csv`

## Removed legacy exploratory artifacts

Legacy exploratory notebook and early Phase 1 output files have been removed from the tracked repository.

Removed tracked content:

- legacy exploratory Kaggle notebooks
- early Phase 1 exploratory result files

These files represented exploratory Kaggle-era work and are no longer part of the clean repository interface.

## Current claim boundary

The repository supports the following conservative research-stage statement:

> Frozen Geneformer patient-level embeddings show strong internal leave-one-patient-out discrimination of active SLE flare status in an exploratory PBMC single-cell cohort.

The repository does not support claims of:

- clinical deployment
- diagnostic readiness
- treatment recommendation
- prospective flare prediction
- external validation
- generalized clinical decision support

## Validation status

Current validation status:

- internal patient-level validation: complete
- leakage-controlled LOOCV: complete
- external validation: not complete
- clinical validation: not complete
- prospective validation: not complete

## Next scientific work

Recommended next work:

1. audit robustness and confounding controls
2. compare Geneformer embeddings against simpler baselines
3. evaluate cell-type composition and metadata-only baselines
4. identify and test an independent external validation cohort
5. add pathway-level and cell-type-level interpretation

## Documentation

Current project-facing documentation:

- `README.md`
- `MODEL_CARD.md`
- `docs/limitations.md`

No CV-facing, recruiter-facing, or application-specific files are part of the repository.

## Interpretation boundary

Downstream logistic-regression coefficients, embedding-dimension weights, or SHAP values are not gene-level importance because the classifier operates on Geneformer-derived patient embeddings rather than raw gene features.

## Gene masking boundary

Gene masking is not valid on the downstream logistic-regression classifier. Gene or gene-program perturbation must occur upstream before Geneformer embedding extraction, followed by re-embedding and fixed-classifier re-scoring.
