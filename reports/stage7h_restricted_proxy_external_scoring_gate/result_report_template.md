# Restricted proxy external scoring report template

## Execution status

- `not_run_blocked_missing_artifacts`, or
- `completed_restricted_proxy_transfer`.

## Required caveat

GSE135779 does not provide explicit sample-level flare-versus-managed-SLE labels in the parsed metadata used for this project. Results must be interpreted only as restricted proxy transfer on high-activity versus low-activity SLE.

## Dataset and endpoint

- Cohort: GSE135779.
- Endpoint: SLEDAI-thresholded proxy.
- Positive proxy: `SLEDAI > 4`.
- Negative proxy: `SLEDAI <= 4`.
- Exclusions: healthy controls and missing explicit SLEDAI.

## Model policy

- PCA: frozen Stage 6 object only.
- Classifier: frozen Stage 6 object only.
- Threshold: frozen internal threshold only, if available.
- External fitting: not allowed.

## Metrics section

Report only if execution gate passes:

| Metric | Value | CI | Notes |
|---|---:|---:|---|
| ROC-AUC | pending | pending | continuous metric |
| AUPRC | pending | pending | positive class: high activity |
| Balanced accuracy | pending | pending | thresholded, only if frozen threshold exists |
| Sensitivity | pending | pending | thresholded |
| Specificity | pending | pending | thresholded |

## Claim-safe conclusion

Use:

`The frozen Stage 6-derived scoring pipeline was evaluated on GSE135779 as a restricted proxy transfer task distinguishing high-activity from low-activity SLE.`

Do not use:

`The model was externally validated for FLARE versus managed SLE.`
