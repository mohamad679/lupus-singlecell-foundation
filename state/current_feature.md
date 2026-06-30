# Current Feature

## STAGE1-F002 - Metadata extraction and QC utilities

Status: in progress
Branch: `feat/stage1-metadata-qc`

## Objective

Continue moving production-safe dataset-ingestion logic out of exploratory
notebooks and into the tested `lupusfm` Python package.

This feature adds small, explicit utilities for AnnData/CELLxGENE metadata
inspection and QC annotation safety before any embedding extraction or modeling
is allowed.

## Completed in this branch

- Added `src/lupusfm/data/metadata.py`.
- Added tests for required `adata.obs` columns.
- Added tests for donor-id extraction from `adata.obs`.
- Added tests for first-seen donor deduplication and missing donor rejection.
- Added `src/lupusfm/qc/mitochondrial.py`.
- Added tests requiring an explicit gene-symbol column for mitochondrial-gene
  detection.
- Added tests preventing silent fallback to `adata.var_names`.
- Added tests for mitochondrial-gene masks, counts, summaries, and custom
  prefixes.

## Validation

Current targeted test:

`python3 -m pytest tests/test_lupusfm_labels.py tests/test_lupusfm_metadata.py tests/test_lupusfm_mitochondrial.py -q`

Current result:

`49 passed`

Note: the local `pytest_asyncio` deprecation warning is unrelated to these
modules.

## Not allowed in this feature

- No modeling or training.
- No embedding extraction.
- No new performance claims.
- No external validation.
- No large data downloads.
- No AnnData filtering or matrix preprocessing.
- No silent donor-label assignment.
- No silent mitochondrial annotation from `var_names`.

## Next action

Update state documentation, run targeted tests, then open a small pull request
for Stage 1 metadata/QC utilities.
