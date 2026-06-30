# Current Feature

## STAGE2-CLOSEOUT - Stage 2 closeout gate

Status: in progress
Branch: `chore/stage2-closeout`

## Objective

Mark Stage 2 as complete after the final permission-gated Geneformer extraction
runner was merged on `main`.

This closeout does not add runtime code, download data, load AnnData files,
execute Geneformer, execute tokenizers, extract embeddings, train models,
perform external validation, commit artifacts, or add performance claims.

## Completed Stage 2 features

- `STAGE2-F001 - Reproducible Geneformer embedding extraction plan`
- `STAGE2-F002 - Embedding config contract`
- `STAGE2-F003 - Embedding provenance manifest`
- `STAGE2-F004 - Dry-run extraction readiness`
- `STAGE2-F005 - Actual Geneformer extraction runner`

## Stage 2 package foundation completed

- `src/lupusfm/embeddings/config.py`
- `tests/test_lupusfm_embedding_config.py`
- `src/lupusfm/embeddings/provenance.py`
- `tests/test_lupusfm_embedding_provenance.py`
- `src/lupusfm/embeddings/readiness.py`
- `tests/test_lupusfm_embedding_readiness.py`
- `src/lupusfm/embeddings/extraction.py`
- `tests/test_lupusfm_geneformer_extraction_runner.py`

## Closeout guarantees

- No real Geneformer execution was performed.
- No real tokenizer execution was performed.
- No real AnnData loading was performed.
- No CELLxGENE download was performed.
- No embedding artifacts were committed.
- No model artifacts were committed.
- No modeling or training was performed.
- No performance claims were added.
- No external validation was performed.
- No cell-level train/test split was introduced.

## Next scientific stage

The next stage should begin only after this closeout is merged.

Recommended next stage:

`STAGE3 - Patient-level embedding aggregation and leakage-safe evaluation design`

Stage 3 should remain conservative and patient-level only. It should not claim
future flare prediction. It should first define aggregation, split policy,
baseline controls, and evaluation contracts before any modeling is allowed.

## Countdown

Stage 2 step: closeout
Remaining in Stage 2 after merge: 0
