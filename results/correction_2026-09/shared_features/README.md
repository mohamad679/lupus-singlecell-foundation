# Corrected V1 shared-gene features

These development and external donor embeddings were extracted with the
versioned Kaggle notebooks and validated with
`scripts/35_ingest_corrected_kaggle_zip.py`. The two
`*_ingestion_validation.json` files record ZIP and member SHA-256 hashes,
fixture status, cell counts, and embedding-table checks. The original ZIPs
were retained outside this repository in the paper workspace.

The development table has 261 donors and 1,263,676 contributing cells. The
external table has 56 samples and 363,083 contributing cells. Both have 256
Geneformer V1 dimensions and used the recorded shared-gene input set.

`scripts/28_corrected_geneformer_scoring.py` fitted the development model and
wrote `../corrected_v1_shared_predictions.json`, the fit artifact, and report.
`scripts/27_correction_analysis.py` wrote
`../corrected_v1_shared_analysis.json`. Its input SHA-256 ties the analysis
to the prediction JSON. This external result is a corrected reanalysis of a
previously examined cohort. Local scoring package versions are pinned in
`requirements_correction_scoring.txt` at the repository root.
