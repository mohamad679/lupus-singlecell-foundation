# Stage 7 — Kaggle Result Reconciliation

This directory contains leakage-controlled internal validation outputs generated from patient-level Geneformer embedding files.

## Scope

- Dataset: GSE174188 CELLxGENE-derived patient-level Geneformer embeddings
- Evaluation unit: patient
- Split policy: leave-one-patient-out cross-validation
- Model: mean-pooled Geneformer embeddings + logistic regression
- Leakage controls:
  - patient-level evaluation only
  - no cell-level split
  - StandardScaler fit within each train fold only
  - LogisticRegression fit within each train fold only

## Outputs

- `stage7_run_summary.json`: run metadata and claim boundaries
- `stage7_metric_results.csv`: task-level internal validation metrics
- `stage7_prediction_manifest.csv`: row-level patient predictions

## Claim boundary

These results are internal patient-level LOOCV results only.

No independent external validation was performed.
No clinical deployment or diagnostic claim is made.
