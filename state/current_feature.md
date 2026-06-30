# Current Feature

## STAGE3-F001 - Embedding artifact schema contract

Status: in progress
Branch: `feat/stage3-embedding-artifact-schema`

## Objective

Define the metadata-only schema contract for future frozen Geneformer embedding
artifacts before any patient-level aggregation, leakage-safe evaluation, or
modeling is considered.

This feature does not load real embedding artifacts, load AnnData files,
download data, execute Geneformer, execute tokenizers, extract embeddings,
aggregate embeddings, train models, perform external validation, or add
performance claims.

## Contract scope

The schema validates future artifact metadata such as:

- approved dataset ID
- approved CELLxGENE Census version
- donor/patient identifier column
- cell or sampled-cell identifier column
- embedding column
- embedding dimensionality
- embedding source
- artifact format
- record level
- split level
- model provenance reference
- extraction config reference
- declared artifact paths

## Safety rules

- Patient/donor split level only.
- No cell-level split assignments.
- No model artifacts.
- No training artifacts.
- No modeling.
- No training.
- No external validation.
- No performance claims.
- Fake-data tests only.

## Countdown

Stage 3 step: F001
Remaining before modeling can be considered: aggregation contract, leakage-safe
split utilities, evaluation protocol scaffold, baseline/control plan, and
modeling readiness gate.
