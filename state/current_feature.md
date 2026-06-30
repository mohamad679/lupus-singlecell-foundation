# Current Feature

## STAGE2-F002 - Embedding config contract

Status: in progress
Branch: `feat/stage2-embedding-config-contract`

## Objective

Add a lightweight, metadata-only configuration contract for future Geneformer
embedding extraction.

This feature adds validation utilities for Stage 2 extraction configuration, but
does not implement extraction. It keeps all execution and modeling gates closed
while making the required dataset, manifest, model, tokenizer, vocabulary, gene
identifier, split, aggregation, seed, and output-path policies explicit.

No code in this feature downloads data, loads real AnnData files, imports or
executes Geneformer, tokenizes cells, extracts embeddings, trains models,
performs external validation, or adds new performance claims.

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

## Planned package additions

- `src/lupusfm/embeddings/__init__.py`
- `src/lupusfm/embeddings/config.py`
- `tests/test_lupusfm_embedding_config.py`

## Stage 2 config contract scope

The config contract must validate:

- approved primary CELLxGENE dataset ID
- approved CELLxGENE Census version
- explicit donor column
- explicit gene-symbol column
- explicit gene-ID mapping policy
- required ingestion manifest path
- Geneformer model source and revision
- tokenizer and vocabulary source
- cells per donor
- maximum sequence length
- batch size
- random seed
- patient-level split policy
- patient-level aggregation policy
- Stage 2 output paths
- model/training artifact suffix restrictions

## Required leakage controls

- Split level must remain patient/donor/cohort-level, never cell-level.
- Patient aggregation must be declared before extraction.
- No supervised evaluation, standardization, cross-validation, or metric claim is
  introduced by this feature.
- No model or training artifact path is allowed.

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

## Next action

Add the metadata-only embedding config contract, run targeted and full tests,
then open a small Stage 2 config-contract pull request.
