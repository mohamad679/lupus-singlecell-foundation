# Current Feature

## STAGE1-F005 - Ingestion readiness report utilities

Status: in progress
Branch: `feat/stage1-ingestion-readiness`

## Objective

Add lightweight ingestion-readiness reporting utilities that combine schema,
cohort, and explicit gene-annotation checks before any downstream embedding
extraction or modeling is allowed.

This feature produces a structured readiness report instead of crashing on the
first validation failure. It does not import Scanpy, load AnnData files,
download data, filter cells, extract embeddings, train models, or add
performance claims.

## Completed in this branch

- Added `src/lupusfm/data/ingestion_readiness.py`.
- Added `tests/test_lupusfm_ingestion_readiness.py`.
- Added `ReadinessCheck`.
- Added `IngestionReadinessReport`.
- Added combined checks for AnnData schema validation.
- Added combined checks for donor/cell cohort summary.
- Added combined checks for explicit mitochondrial gene annotation.
- Added `is_ready` and `failed_checks` report helpers.
- Added tests confirming failures are collected instead of raised.
- Added tests for schema failures, unknown donor patterns, minimum donor count,
  cell-level split rejection, explicit gene-symbol requirements, and optional
  mitochondrial-gene presence requirements.

## Validation

Current targeted test:

`python3 -m pytest tests/test_lupusfm_labels.py tests/test_lupusfm_metadata.py tests/test_lupusfm_mitochondrial.py tests/test_lupusfm_cohort.py tests/test_lupusfm_anndata_schema.py tests/test_lupusfm_ingestion_readiness.py -q`

Current result:

`80 passed`

Note: the local `pytest_asyncio` deprecation warning is unrelated to these
modules.

## Not allowed in this feature

- No modeling or training.
- No embedding extraction.
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
request for Stage 1 ingestion-readiness reporting utilities.
