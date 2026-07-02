# Restricted proxy external scoring design

## Primary analysis

The future scoring analysis must use included GSE135779 SLE samples only:

- positive proxy: `SLEDAI > 4`;
- negative proxy: `SLEDAI <= 4`.

Healthy controls and missing-SLEDAI samples remain excluded from the primary endpoint.

## Required scoring flow

1. Load frozen Stage 6 PCA.
2. Load frozen Stage 6 classifier.
3. Load external sample embeddings.
4. Align sample IDs to the approved sample manifest.
5. Exclude non-primary samples before metric computation.
6. Apply PCA transform only.
7. Generate continuous model scores.
8. Compute continuous metrics.
9. Apply frozen threshold only if threshold policy exists.
10. Write proxy-only report with caveat language.

## Primary metrics

- ROC-AUC;
- AUPRC;
- bootstrap confidence intervals over sample units.

## Secondary metrics

Only if a frozen threshold is available:

- balanced accuracy;
- sensitivity;
- specificity;
- confusion matrix.

## Prohibited scoring behavior

- no PCA fitting on external data;
- no classifier fitting on external data;
- no threshold selection on external data;
- no changing exclusions after seeing predictions;
- no strict external validation claim.

## Interpretation

A successful result supports transfer to a related high-activity versus low-activity SLE proxy endpoint. It does not validate the original Stage 6 FLARE-versus-managed-SLE endpoint.
