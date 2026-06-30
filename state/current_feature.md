# Current Feature

## STAGE2-F004 - Dry-run extraction readiness

Status: in progress
Branch: `feat/stage2-dry-run-readiness`

## Objective

Add a metadata-only dry-run readiness gate for future Geneformer embedding
extraction.

This feature combines the Stage 1 ingestion manifest, ingestion-readiness report,
Stage 2 embedding config, and Stage 2 embedding provenance manifest to determine
whether a later extraction feature is allowed to proceed.

No code in this feature downloads data, loads real AnnData files, loads model
runtimes, tokenizes cells, extracts embeddings, trains models, performs external
validation, writes artifacts, or adds new performance claims.

## Completed before this branch

- `STAGE0`: repository reconciliation completed.
- `STAGE1-F001`: donor label extraction package and tests.
- `STAGE1-F002`: metadata extraction and mitochondrial QC utilities.
- `STAGE1-F003`: cohort summary utilities.
- `STAGE1-F004`: AnnData schema validation utilities.
- `STAGE1-F005`: ingestion-readiness report utilities.
- `STAGE1-F006`: manifest/reproducibility contract utilities.
- `STAGE1-F007`: Stage 1 closeout gate merged on `main`.
- `STAGE2-F001`: reproducible Geneformer embedding extraction plan merged on
  `main`.
- `STAGE2-F002`: embedding config contract merged on `main`.
- `STAGE2-F003`: embedding provenance manifest merged on `main`.

## Planned package additions

- `src/lupusfm/embeddings/readiness.py`
- `tests/test_lupusfm_embedding_readiness.py`

## Stage 2 dry-run scope

The dry-run readiness gate must validate:

- Stage 1 ingestion manifest against ingestion-readiness report
- embedding config contract
- embedding config against ingestion manifest
- embedding provenance manifest contract
- embedding provenance against embedding config
- distinct Stage 2 output paths
- extraction remains not performed
- execution/modeling/download/performance gates remain disabled

## Required leakage and reproducibility controls

- No cell-level split may be introduced.
- Patient-level split and aggregation policies must remain explicit.
- Dry-run reports must collect failures instead of starting runtime work.
- The dry-run gate must be pass/fail only; it must not add metrics or claims.

## Still not allowed

- No modeling or training.
- No embedding extraction.
- No Geneformer execution.
- No tokenizer execution.
- No new performance claims.
- No external validation.
- No large data downloads.
- No real AnnData file loading.
- No AnnData filtering or matrix preprocessing.
- No cell-level train/test split.
- No model or training artifacts.

## Countdown

Stage 2 step: 4/5
Remaining after this feature: 1

## Next action

Add the metadata-only dry-run readiness gate, run targeted and full tests, then
open a small Stage 2 dry-run readiness pull request.
