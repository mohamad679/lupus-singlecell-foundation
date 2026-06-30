# Current Feature

## STAGE1-F007 - Stage 1 closeout gate

Status: in progress
Branch: `chore/stage1-closeout-gate`

## Objective

Close Stage 1 formally after completing the production-safe ingestion/QC
foundation.

This feature records that the Stage 1 `lupusfm` package foundation is complete,
keeps all Stage 2 work locked, and defines the gate conditions required before
Geneformer embedding extraction or any modeling can begin.

No code in this feature downloads data, loads real AnnData files, executes
Geneformer, extracts embeddings, trains models, performs external validation,
or adds performance claims.

## Completed before this branch

- `STAGE1-F001`: donor label extraction package and tests.
- `STAGE1-F002`: metadata extraction and mitochondrial QC utilities.
- `STAGE1-F003`: cohort summary utilities.
- `STAGE1-F004`: AnnData schema validation utilities.
- `STAGE1-F005`: ingestion-readiness report utilities.
- `STAGE1-F006`: manifest/reproducibility contract utilities.

## Stage 1 package modules now on main

- `src/lupusfm/data/labels.py`
- `src/lupusfm/data/metadata.py`
- `src/lupusfm/data/cohort.py`
- `src/lupusfm/data/anndata_schema.py`
- `src/lupusfm/data/ingestion_readiness.py`
- `src/lupusfm/data/manifest.py`
- `src/lupusfm/qc/mitochondrial.py`

## Validation

Current full repository test:

`python3 -m pytest -q`

Current result on `main` after PR #8:

`499 passed`

Note: the local `pytest_asyncio` deprecation warning is unrelated to Stage 1
package functionality.

## Still not allowed

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

## Gate required before Stage 2

Stage 2 may start only after this closeout PR is merged and the next feature
explicitly defines a locked, reproducible Geneformer embedding-extraction plan.

That Stage 2 plan must keep patient-level leakage controls, manifest checks,
dataset/version identifiers, seed handling, model/vocab/config provenance, and
output-artifact restrictions explicit before any extraction is run.

## Next action

Update closeout state documentation, run targeted and full tests, then open a
small Stage 1 closeout pull request.
