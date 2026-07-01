# Stage 6 real-artifact evaluation package

This package records the first real donor-embedding evaluation produced from the uploaded `all_embeddings.zip` artifact. The raw embedding archive is not committed because it is a large derived data artifact; only reports, summaries, audits, and compact figures are stored in Git.

## Scope

- Primary task: `FLARE` vs managed SLE.
- Donor-level evaluation only; no cell-level split is used.
- Healthy controls and `ICC_control` are excluded from the primary binary task.
- External validation remains unresolved and is not claimed here.

## Primary result

Best fast primary model: `mean embedding + PCA(20) + balanced logistic regression`.

| Metric | Result |
|---|---:|
| ROC-AUC | ≈ 0.998–0.999 |
| AUPRC | ≈ 0.987 |
| Donor-level task size | 14 FLARE vs 148 managed SLE |
| Embedding shape per donor | 300 × 1152 |

## Internal robustness result

| Check | Result |
|---|---|
| Ablation | `mean_pca20_logreg_balanced` remains the strongest compact model. |
| Baseline | Dummy baseline remains at chance. |
| Artifact proxy | Norm-only proxy is weaker than embedding model. |
| Threshold calibration | Default and specificity-targeted thresholds preserve strong internal separation. |
| Permutation | Observed ROC-AUC remains above the fast null distribution; empirical p≈0.0476 with 20 permutations. |
| Leakage audit | Donor-level split confirmed; no cell-level leakage is introduced in this package. |

## Paper-safe claim

The current results support an internal zero-shot donor-level embedding signal claim for active SLE flare discrimination in the primary cohort. They do **not** support clinical generalization or deployment claims until an independent external cohort is evaluated.

## Included files

- `primary_eval/primary_cv_summary_metrics.csv`
- `primary_eval/dataset_summary.json`
- `internal_robustness/02_ablation_cv_summary_with_ci.csv`
- `internal_robustness/03_threshold_policy_summary_with_ci.csv`
- `internal_robustness/04_permutation_test_summary.csv`
- `internal_robustness/05_leakage_and_artifact_audit.json`
- `figures/stage6_result_summary.svg`
- `artifact_manifest.json`
