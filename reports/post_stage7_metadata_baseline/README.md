# Stage 7 metadata-only baseline

Metadata-only baseline testing is an internal confounding-control analysis only. It does not constitute external validation, clinical validation, or evidence of clinical diagnostic utility.

This baseline uses only patient-level metadata and cell-composition features.
This control assesses whether simple metadata features can reproduce the internal LOOCV signal.
Internal confounding-control only.

- Status: blocked_metadata_extraction
- Metadata artifact: `data/processed/lupus_qc_processed.h5ad`
- Output directory: `reports/post_stage7_metadata_baseline`
- Age available: true
- Sex available: true
- Cell-type annotations available: true
- Cell counts available: true
- Geneformer execution: not run
- Geneformer embeddings: not used
- Evaluation unit: patient
- Split policy: leave-one-patient-out

## TODO

Local .h5ad metadata artifact exists, but `anndata` is not installed. Install `anndata` to extract patient-level metadata features.
