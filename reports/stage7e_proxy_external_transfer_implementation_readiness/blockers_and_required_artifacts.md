# Blockers and required artifacts

## Execution blocker

Stage 7E is not ready for external scoring because the frozen Stage 6 scoring pipeline is not yet exported as a reproducible artifact bundle.

The current repository has Stage 6 performance reports, but reports are not enough to safely score an external cohort. External transfer requires the exact fitted objects that produced the Stage 6 primary model.

## Required Stage 6 frozen artifact bundle

Create an artifact bundle containing:

1. `pca20.joblib` or equivalent serialized PCA object fitted only on Stage 6 internal data;
2. `balanced_logreg.joblib` or equivalent serialized classifier fitted only on Stage 6 internal data;
3. `threshold_policy.json` with the frozen internal threshold or a statement that thresholded metrics are disabled;
4. `preprocessing_manifest.json` with aggregation, cell cap, random seed, input shape, and feature policy;
5. `model_artifact_manifest.json` with SHA256 hashes for all frozen objects;
6. `environment_manifest.json` with Python, numpy, scikit-learn, and Geneformer-related versions.

## Required GSE135779 manifest

Create a sample manifest with one row per sample:

- sample ID;
- group (`cSLE`, `aSLE`, `cHD`, `aHD`);
- numeric SLEDAI;
- proxy label (`high_activity_sle`, `low_activity_sle`, `excluded_missing_sledai`, `excluded_healthy_control`);
- inclusion flag;
- exclusion reason;
- age group;
- batch if available;
- notes for missing or ambiguous metadata.

## Required external expression and embedding plan

Create an import plan for GSE135779 processed matrices:

- list all matrix/barcode/gene files to download;
- define gene identifier mapping to Geneformer tokens;
- define QC policy;
- define cell cap / sampling policy;
- define sample-level aggregation policy;
- define output embedding format.

## Required no-fit scoring script

The scoring script must:

- load frozen Stage 6 PCA and classifier only;
- load external sample embeddings;
- apply PCA transform only, never fit PCA;
- generate continuous scores;
- optionally apply frozen internal threshold;
- write metrics and bootstrapped confidence intervals;
- write a claim-safe report.

## Stop condition

If any required frozen object is unavailable, Stage 7E must stop before external scoring.
