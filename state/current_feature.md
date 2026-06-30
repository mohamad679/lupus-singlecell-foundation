# Current Feature

## STAGE2-F003 - Embedding provenance manifest

Status: in progress
Branch: `feat/stage2-embedding-provenance`

## Objective

Add a metadata-only provenance manifest contract for future Geneformer embedding
extraction.

This feature records dataset, config, model, tokenizer, vocabulary, gene mapping,
seed, split, aggregation, output, and hash-resolution provenance requirements
before any runtime extraction feature is allowed.

No code in this feature downloads data, loads real AnnData files, loads model
runtimes, tokenizes cells, extracts embeddings, trains models, performs external
validation, or adds new performance claims.

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

## Planned package additions

- `src/lupusfm/embeddings/provenance.py`
- `tests/test_lupusfm_embedding_provenance.py`

## Stage 2 provenance scope

The provenance contract must validate:

- approved primary CELLxGENE dataset ID
- approved CELLxGENE Census version
- explicit donor column
- explicit gene-symbol column
- explicit gene-ID mapping policy
- Geneformer model source and revision
- tokenizer source
- vocabulary source
- pending or recorded sha256 hash status for model/config/tokenizer/vocabulary
- cells per donor
- maximum sequence length
- batch size
- random seed
- patient-level split policy
- patient-level aggregation policy
- output path consistency with the embedding config
- explicit record that extraction has not yet been performed

## Required leakage and reproducibility controls

- Provenance must match the validated embedding config.
- Runtime hashes may be pending at this stage, but fake hashes are rejected.
- Recorded hashes must be valid sha256 hex digests.
- Extraction performed must remain false in this feature.
- No supervised evaluation, cross-validation, metric report, or performance claim
  is introduced by this feature.

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

Stage 2 step: 3/5
Remaining after this feature: 2

## Next action

Add the metadata-only provenance manifest contract, run targeted and full tests,
then open a small Stage 2 provenance pull request.
