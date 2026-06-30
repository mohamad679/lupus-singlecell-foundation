# Current Feature

## STAGE2-F005 - Actual Geneformer extraction runner

Status: in progress
Branch: `feat/stage2-geneformer-extraction-runner`

## Objective

Add a permission-gated and dependency-injected Geneformer extraction runner.

This feature defines the runner interface that can later execute extraction only
when a human-approved runtime environment, explicit execution permission, and
caller-provided callbacks are supplied.

The package itself still does not import Geneformer, tokenizer runtimes, Scanpy,
AnnData, CELLxGENE, PyTorch, or any deep-learning runtime. It also does not
download data, load real AnnData files, run extraction during tests, train
models, perform external validation, or add performance claims.

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
- `STAGE2-F004`: dry-run extraction readiness merged on `main`.

## Planned package additions

- `src/lupusfm/embeddings/extraction.py`
- `tests/test_lupusfm_geneformer_extraction_runner.py`

## Stage 2 extraction-runner scope

The runner must:

- require the dry-run readiness gate to pass first
- require explicit runtime extraction permission
- require a named approved runtime environment
- require a named approver and reason
- keep downloads disabled
- keep modeling/training/external validation/performance claims disabled
- use caller-provided callbacks for runtime actions
- avoid importing runtime stacks at package import time
- return result metadata from a permitted extraction call

## Still not allowed in this PR

- No real Geneformer execution.
- No real tokenizer execution.
- No real AnnData loading.
- No CELLxGENE download.
- No runtime dependency import in package code.
- No extraction run committed to the repository.
- No embedding artifacts committed to the repository.
- No modeling or training.
- No performance claims.
- No external validation.
- No cell-level train/test split.

## Countdown

Stage 2 step: 5/5
Remaining after this feature: 0

## Next action

Add the permission-gated extraction runner, run targeted and full tests, then
open the final Stage 2 pull request.
