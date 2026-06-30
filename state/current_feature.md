# Current Feature

## STAGE1-F004 - AnnData schema validation utilities

Status: in progress
Branch: `feat/stage1-anndata-schema`

## Objective

Add lightweight, production-safe AnnData-like schema validation utilities inside
the tested `lupusfm` package.

This feature validates observation metadata, variable metadata, X/layer shapes,
required keys, and patient/cohort-level split policy constraints. It does not
import Scanpy, load AnnData files, download data, filter cells, extract
embeddings, train models, or add performance claims.

## Completed in this branch

- Added `src/lupusfm/data/anndata_schema.py`.
- Added `tests/test_lupusfm_anndata_schema.py`.
- Added configurable `AnnDataSchemaContract`.
- Added compact `AnnDataSchemaReport`.
- Added validation for required `obs` columns.
- Added validation for required `var` columns.
- Added validation for required `uns` keys and `layers`.
- Added X/layer shape checks against inferred obs/var dimensions.
- Added split-policy checks that reject cell-level split assignments.
- Added mapping-like and AnnData-like object support without Scanpy imports.

## Validation

Current targeted test:

`python3 -m pytest tests/test_lupusfm_labels.py tests/test_lupusfm_metadata.py tests/test_lupusfm_mitochondrial.py tests/test_lupusfm_cohort.py tests/test_lupusfm_anndata_schema.py -q`

Current result:

`71 passed`

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

## Next action

Update state documentation, run targeted and full tests, then open a small pull
request for Stage 1 AnnData schema validation utilities.
