# Lupus Primary Embedding Evaluation — FLARE vs Managed SLE

## Data inventory
- NPY donor files: 261
- Label counts: {'managed_sle': 148, 'healthy': 98, 'flare': 14, 'unknown': 1}
- Shape counts: {'(300, 1152)': 261}
- Dtype counts: {'float32': 261}
- All arrays finite: True
- Unknown donor IDs excluded: ['ICC_control']

## Protocol
- Primary task: FLARE vs managed SLE; healthy controls and unknown excluded.
- Donor-level aggregation: mean or mean+std over 300 embedding rows per donor.
- 5-fold × 10-repeat stratified CV. Threshold chosen on the training fold only by balanced accuracy.

## Summary

| task                         | feature_model                  |   n_splits |   roc_auc_mean |   roc_auc_std |   auprc_mean |   auprc_std |   balanced_accuracy_mean |   balanced_accuracy_std |   f1_positive_mean |   f1_positive_std |   precision_positive_mean |   precision_positive_std |   recall_positive_mean |   recall_positive_std |   specificity_negative_mean |   specificity_negative_std |   tp_sum |   fp_sum |   tn_sum |   fn_sum |
|:-----------------------------|:-------------------------------|-----------:|---------------:|--------------:|-------------:|------------:|-------------------------:|------------------------:|-------------------:|------------------:|--------------------------:|-------------------------:|-----------------------:|----------------------:|----------------------------:|---------------------------:|---------:|---------:|---------:|---------:|
| primary_flare_vs_managed_sle | dummy_prior                    |         50 |          0.500 |         0.000 |        0.086 |       0.012 |                    0.500 |                   0.000 |              0.159 |             0.021 |                     0.086 |                    0.012 |                  1.000 |                 0.000 |                       0.000 |                      0.000 |      140 |     1480 |        0 |        0 |
| primary_flare_vs_managed_sle | mean_pca20_logreg_balanced     |         50 |          0.999 |         0.005 |        0.987 |       0.046 |                    0.750 |                   0.141 |              0.614 |             0.294 |                     0.860 |                    0.351 |                  0.500 |                 0.282 |                       1.000 |                      0.000 |       71 |        0 |     1480 |       69 |
| primary_flare_vs_managed_sle | mean_std_pca20_logreg_balanced |         50 |          0.996 |         0.010 |        0.964 |       0.094 |                    0.675 |                   0.134 |              0.456 |             0.305 |                     0.715 |                    0.440 |                  0.353 |                 0.269 |                       0.997 |                      0.009 |       51 |        4 |     1476 |       89 |
