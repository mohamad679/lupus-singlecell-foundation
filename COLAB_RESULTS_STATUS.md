# Stage 7 Colab control-analysis results

## Completed real result
- post_stage7_permutation_test: completed
- n_permutations: 100
- empirical p-value: 0.009900990099009901 for both tasks

## Blocked results
- post_stage7_metadata_baseline: blocked_insufficient_metadata_h5ad
- post_stage7_confounding_audit: blocked_insufficient_label_classes

## Blocker
The available h5ad is not the real 1.2M-cell metadata artifact.
It contains only:
- 450 obs rows
- 10 patients
- all labels = managed

Therefore metadata-only baseline and confounding audit cannot be real until the real full metadata h5ad is provided.
