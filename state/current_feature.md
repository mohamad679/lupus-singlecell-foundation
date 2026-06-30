# Current Feature

## STAGE2-F001 - Reproducible Geneformer embedding extraction plan

Status: in progress
Branch: `docs/stage2-embedding-plan`

## Objective

Define the locked Stage 2 plan for reproducible, leakage-safe Geneformer
embedding extraction before any extraction work is implemented or run.

This feature is documentation/state/test synchronization only. It defines the
inputs, outputs, provenance requirements, leakage controls, and safety gates
that must be satisfied before a later feature may add an embedding configuration
contract or dry-run validator.

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

## Stage 2 extraction plan scope

A later extraction implementation must explicitly define and validate:

- primary dataset accession and CELLxGENE dataset ID
- CELLxGENE Census version
- donor identifier column
- gene-symbol and gene-ID mapping policy
- Geneformer model source and version
- tokenizer and vocabulary source
- model/config/vocabulary provenance hashes when available
- random seed
- sampled cell IDs per donor
- cells per donor and maximum sequence length
- patient-level aggregation rule
- output directory and file naming convention
- embedding dtype and expected shape checks
- finite-value checks
- patient-level metadata consistency checks

## Required leakage controls

- All downstream evaluation must remain patient-level.
- Cell-level train/test split assignments remain forbidden.
- Standardization or preprocessing for supervised evaluation must occur inside
  each patient-level cross-validation fold.
- No performance claim may be added from this planning feature.
- No supervised model artifact may be created in Stage 2 planning.

## Required safety gates before actual extraction

Actual Geneformer embedding extraction remains blocked until a later approved
feature verifies that:

- the Stage 1 manifest validates successfully
- ingestion readiness passes
- dataset ID and Census version match the approved contract
- donor and gene-symbol columns are explicit
- token IDs are validated against the model vocabulary size
- output paths do not use model/training artifact suffixes
- sampled cell IDs can be recorded reproducibly
- no modeling, training, or external validation is triggered

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

Update Stage 2 planning documentation and stale state tests, run the repository
test suite, then open a small Stage 2 planning pull request.
