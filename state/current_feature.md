# Current Feature

## STAGE1-F006 - Manifest / reproducibility contract utilities

Status: in progress
Branch: `feat/stage1-manifest-contract`

## Objective

Add a lightweight ingestion manifest and reproducibility contract before any
Stage 2 embedding extraction or modeling is allowed.

This feature records and validates dataset/source identifiers, metadata column
names, expected cohort counts, random seed, and Stage 1 output locations. It
does not download data, load AnnData files, extract Geneformer embeddings,
train models, approve datasets for modeling, or add performance claims.

## Completed in this branch

- Added `src/lupusfm/data/manifest.py`.
- Added `tests/test_lupusfm_manifest.py`.
- Added `ManifestOutputPaths`.
- Added `IngestionManifest`.
- Added `IngestionManifestError`.
- Added validation for dataset ID, source, census version, donor column, gene
  symbol column, expected donor/cell counts, random seed, and output paths.
- Added locked primary CELLxGENE/Perez lupus manifest constants.
- Added manifest serialization to plain dictionaries.
- Added mapping-based manifest construction.
- Added checks that downloads, embedding extraction, modeling, and training
  remain disabled in Stage 1.
- Added checks that model-artifact-like output suffixes are rejected.
- Added validation of manifest counts/columns against ingestion-readiness
  reports.

## Validation

Current targeted test:

`python3 -m pytest tests/test_lupusfm_labels.py tests/test_lupusfm_metadata.py tests/test_lupusfm_mitochondrial.py tests/test_lupusfm_cohort.py tests/test_lupusfm_anndata_schema.py tests/test_lupusfm_ingestion_readiness.py tests/test_lupusfm_manifest.py -q`

Current result:

`103 passed`

Note: the local `pytest_asyncio` deprecation warning is unrelated to these
modules.

## Not allowed in this feature

- No modeling or training.
- No embedding extraction.
- No Geneformer execution.
- No new performance claims.
- No external validation.
- No large data downloads.
- No real AnnData file loading.
- No AnnData filtering or matrix preprocessing.
- No cell-level train/test split.
- No silent donor-label assignment.
- No silent mitochondrial annotation from `adata.var_names`.

## Next action

Update state documentation, run targeted and full tests, then open a small pull
request for Stage 1 manifest/reproducibility contract utilities.
