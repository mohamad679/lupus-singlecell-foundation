# Current Feature

## STAGE1-F003 - Cohort summary utilities

Status: in progress
Branch: `feat/stage1-cohort-summary`

## Objective

Add small, production-safe donor/cell summary utilities for AnnData/CELLxGENE
observation metadata.

This feature summarizes donor-level cell counts and clinical-status group
counts using the approved donor-id label rule. It does not load expression
matrices, filter cells, extract embeddings, train models, or download data.

## Completed in this branch

- Added `src/lupusfm/data/cohort.py`.
- Added `tests/test_lupusfm_cohort.py`.
- Added donor-level cell counting from explicit `adata.obs` donor columns.
- Added clinical-status donor/cell summaries for Flare, Managed, and Healthy.
- Added cohort-level total donor and total cell summaries.
- Added tests for whitespace normalization, missing donor rejection, unknown
  donor-pattern rejection, custom donor columns, and zero-count status groups.

## Validation

Current targeted test:

`python3 -m pytest tests/test_lupusfm_labels.py tests/test_lupusfm_metadata.py tests/test_lupusfm_mitochondrial.py tests/test_lupusfm_cohort.py -q`

Current result:

`59 passed`

Note: the local `pytest_asyncio` deprecation warning is unrelated to these
modules.

## Not allowed in this feature

- No modeling or training.
- No embedding extraction.
- No new performance claims.
- No external validation.
- No large data downloads.
- No AnnData filtering or matrix preprocessing.
- No cell-level train/test split.
- No silent donor-label assignment.

## Next action

Update state documentation, run targeted and full tests, then open a small pull
request for Stage 1 cohort summary utilities.
