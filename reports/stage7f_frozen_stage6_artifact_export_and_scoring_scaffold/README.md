# Stage 7F frozen Stage 6 model artifact export and external scoring scaffold

This package prepares the repository for a future restricted proxy external transfer run on GSE135779.

## Scope

Stage 7F is implementation-preparation only.

It creates the scripts, schemas, and guardrails needed to export frozen Stage 6 scoring artifacts and to score external proxy samples without refitting. It does not run GSE135779 external scoring.

## Why this stage exists

Stage 7E concluded that the proxy design was scientifically ready but implementation was blocked because the repository did not yet contain a reproducible frozen Stage 6 scoring artifact bundle.

Stage 6 reports show strong internal performance, but reports alone are not executable scoring artifacts. A valid external transfer run requires the exact fitted objects and preprocessing policy.

## Added scaffold

Stage 7F adds scaffold scripts for:

1. exporting a frozen Stage 6 PCA(20) + balanced logistic regression scoring bundle from a local donor-embedding artifact;
2. building a GSE135779 proxy sample manifest from parsed Supplementary Table 1b clinical metadata;
3. scoring external sample embeddings with frozen objects only, without any external-label fitting.

## Expected artifact bundle

The export script writes a bundle containing:

- `pca20.joblib`;
- `balanced_logreg.joblib`;
- `threshold_policy.json`;
- `preprocessing_manifest.json`;
- `model_artifact_manifest.json`;
- `environment_manifest.json`.

## Required external proxy manifest

The manifest builder converts ST1b clinical metadata into a claim-safe proxy label table:

- `SLEDAI > 4` -> `high_activity_sle`;
- `SLEDAI <= 4` -> `low_activity_sle`;
- missing explicit SLEDAI -> excluded by default;
- healthy controls -> excluded from primary proxy endpoint.

## Current decision

The scaffold is ready to be used, but real external scoring remains blocked until the local Stage 6 donor embeddings and parsed ST1b clinical table are provided to the scripts.

No strict FLARE-versus-managed SLE validation claim is allowed.
