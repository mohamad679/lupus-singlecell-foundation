# Current Feature

## STAGE3-F002 - Patient-level aggregation design

Status: in progress
Branch: `feat/stage3-patient-aggregation-design`

## Objective

Define the fake-data patient-level aggregation contract for converting future
cell-level frozen Geneformer embeddings into donor/patient-level embedding
records before leakage-safe split utilities, evaluation protocol scaffolding,
baselines, or modeling readiness gates are considered.

This feature does not load real embedding artifacts, load AnnData files,
download data, execute Geneformer, execute tokenizers, extract embeddings,
train models, perform external validation, or add performance claims.

## Contract scope

The aggregation design validates:

- aggregation method
- split level
- expected embedding dimensionality
- minimum cells per donor
- donor identifiers
- cell identifiers
- finite numeric embedding vectors
- consistent embedding dimensions
- duplicate cell identifiers
- donor-level output record metadata

## Safety rules

- Patient/donor split level only.
- No cell-level split assignments.
- No real artifact loading.
- No AnnData loading.
- No Geneformer execution.
- No tokenizer execution.
- No embedding extraction.
- No modeling.
- No training.
- No external validation.
- No performance claims.
- Fake-data records only.

## Countdown

Stage 3 step: F002
Remaining before modeling can be considered: leakage-safe split utilities,
evaluation protocol scaffold, baseline/control plan, and modeling readiness gate.
