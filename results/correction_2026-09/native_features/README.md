# Corrected V1 model-native features

Both development/native and external/native ZIPs passed
`scripts/35_ingest_corrected_kaggle_zip.py`. Validation reports record source
ZIP and member SHA-256 hashes, fixture status, donor keys, cell totals, and
finite 256-dimensional embeddings. Development has 261 donors and 1,263,676
cells; external has 56 samples and 363,083 cells. The original ZIPs are
retained in the paper workspace.

This mode is a labeled exploratory sensitivity analysis. Native-input
external Geneformer AUROC was 0.7484375; results and paired comparisons are in
`../corrected_v1_native_analysis.json`. The direct paired comparison with the
shared-gene main analysis is in `../corrected_v1_gene_input_sensitivity.json`.
The shared-gene analysis under `../shared_features` remains the main result.
