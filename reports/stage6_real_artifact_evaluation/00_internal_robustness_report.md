# Stage 6 Internal Robustness Package — Fast Closeout

## Scope
- Primary task: FLARE vs managed SLE.
- Unit: donor-level. Healthy and unknown donors excluded.
- Goal: fast internal robustness package before external cohort work.

## Dataset sanity check
- Total donor `.npy` files: 261.
- Primary donors: 162 = 14 FLARE + 148 managed SLE.
- Embedding shape counts: {'(300, 1152)': 261}.
- All arrays finite: True.
- Unknown excluded: ['ICC_control'].

## Main internal robustness result
- Main model: `mean_pca20_logreg_balanced`.
- ROC-AUC: 0.996 [0.977, 1.000] across 5-fold × 3-repeat donor-level CV.
- AUPRC: 0.969 [0.806, 1.000].
- Balanced accuracy: 0.921.
- FLARE recall: 0.856; managed-SLE specificity: 0.987.

## Ablation conclusion
- Best ROC-AUC model: `mean_pca20_logreg_balanced` with ROC-AUC 0.996.
- PCA mean-embedding models remain strong across component settings.
- Artifact proxy based only on embedding norms is included as a negative/control-style sensitivity check.

## Threshold calibration summary
The ranking signal is strong, but threshold policy changes FLARE recall vs managed-SLE specificity. These are internal operating points, not clinical deployment thresholds.

| threshold_policy            |   balanced_accuracy_mean |   precision_positive_mean |   recall_positive_mean |   specificity_negative_mean |   tp_sum |   fp_sum |   tn_sum |   fn_sum |
|:----------------------------|-------------------------:|--------------------------:|-----------------------:|----------------------------:|---------:|---------:|---------:|---------:|
| default_0.50                |                    0.989 |                     0.847 |                  1.000 |                       0.977 |       42 |       10 |      434 |        0 |
| max_balanced_accuracy_train |                    0.921 |                     0.907 |                  0.856 |                       0.987 |       36 |        6 |      438 |        6 |
| target_recall_0.80          |                    0.921 |                     0.907 |                  0.856 |                       0.987 |       36 |        6 |      438 |        6 |
| target_specificity_0.90     |                    0.921 |                     0.907 |                  0.856 |                       0.987 |       36 |        6 |      438 |        6 |
| target_specificity_0.95     |                    0.921 |                     0.907 |                  0.856 |                       0.987 |       36 |        6 |      438 |        6 |
| target_specificity_0.99     |                    0.921 |                     0.907 |                  0.856 |                       0.987 |       36 |        6 |      438 |        6 |

## Permutation test
- Observed 5-fold ROC-AUC: 0.998.
- Permutation ROC-AUC mean: 0.518; p95: 0.701; max: 0.748.
- Empirical p-value ROC-AUC: 0.0476.
- Observed 5-fold AUPRC: 0.983; empirical p-value AUPRC: 0.0476.
- Note: 20 permutations were used for fast closeout; paper-final run can increase this to 100–1000.

## Leakage / artifact audit
- Evaluation uses donor-level splits, so cell-level leakage is avoided.
- All primary donors have the same number of embedding rows; cell-count proxy leakage is not present in the extracted features.
- Duplicate donor IDs: [].
- Max nearest-neighbor cosine similarity after scaling: 0.9651.

## Paper-safe claim
Geneformer zero-shot donor-level embeddings show a strong internally robust signal separating active FLARE donors from managed SLE donors in the primary cohort. External cohort validation remains required before clinical generalization claims.
