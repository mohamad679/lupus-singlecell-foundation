# Stage 7F artifact export scaffold

## Purpose

This scaffold defines what must be exported from the Stage 6 internal model before any GSE135779 proxy transfer scoring can run.

## Required local inputs

- local Stage 6 donor embedding artifact, for example the donor `.npy` bundle used in Stage 6;
- Stage 6 label policy: `FLARE*` as positive and numeric donor IDs as managed-SLE internal negatives;
- the exact Stage 6 aggregation policy, preferably mean cell embedding per donor.

## Required exported bundle

The export step must create:

| File | Role |
|---|---|
| `pca20.joblib` | PCA transform fitted only on Stage 6 internal donors |
| `balanced_logreg.joblib` | balanced logistic regression fitted only on Stage 6 internal donors |
| `threshold_policy.json` | frozen internal threshold or explicit threshold-disabled policy |
| `preprocessing_manifest.json` | cell cap, aggregation, label, feature and random seed policy |
| `model_artifact_manifest.json` | hashes and artifact metadata |
| `environment_manifest.json` | Python and package versions |

## Safety rules

- Fit PCA only on Stage 6 internal donor embeddings.
- Fit logistic regression only on Stage 6 internal donor embeddings.
- Do not use GSE135779 labels for fitting, feature selection, PCA, or thresholding.
- Do not report this artifact as strict external validation.

## Export status

Scaffold created. Real artifact export is still pending local execution with the Stage 6 donor embedding bundle.
