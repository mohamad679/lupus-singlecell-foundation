# Stage 7 confounding audit

Confounding audit is an internal dataset-structure analysis only. It does not constitute external validation, clinical validation, or evidence of clinical diagnostic utility.

This audit evaluates whether labels are associated with simple technical or compositional variables.
Detected imbalance indicates confounding risk, not causal explanation.
Lack of detected imbalance does not prove absence of confounding.
Internal dataset-structure audit only.

- Status: blocked_metadata_extraction
- Metadata artifact: `data/processed/lupus_qc_processed.h5ad`
- Output directory: `reports/post_stage7_confounding_audit`
- Patient identifier available: true
- Label available: true
- Cell counts available: true
- Cell-type annotations available: true
- Source/batch-like fields available: true
- Detected source/batch-like fields: source, dataset, center
- Geneformer execution: not run
- Geneformer embeddings: not used
- Evaluation unit: patient
- Split policy: no train/test split; internal audit summary only

## TODO

Local .h5ad metadata artifact exists, but `anndata` is not installed. Install `anndata` to extract patient-level metadata features.
