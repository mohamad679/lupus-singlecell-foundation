# Current Feature

## STAGE3-F006 - Modeling readiness gate

Status: in progress
Branch: `feat/stage3-modeling-readiness-gate`

## Objective

Define the final metadata-only Stage 3 readiness gate before the future
real-data validation or downstream modeling path can be considered.

This feature does not load real embedding artifacts, load AnnData files,
download data, execute Geneformer, execute tokenizers, extract embeddings,
extract baseline features, fit scalers, train models, compute real metrics,
perform external validation, or add performance claims.

## Contract scope

The readiness gate validates:

- embedding artifact schema completed
- patient aggregation design completed
- leakage-safe split utilities completed
- evaluation protocol scaffold completed
- baseline/control plan completed
- patient/donor-level evaluation unit
- same candidate and baseline split policy
- fold-internal preprocessing requirement
- uncertainty plan requirement
- permutation plan requirement
- next-stage real-data validation decision
- no runtime execution inside the gate
- no model fitting inside the gate
- no metric computation inside the gate
- no performance claims

## Safety rules

- Patient/donor split level only.
- No cell-level split assignments.
- No cell-level features.
- No real artifact loading inside the gate.
- No AnnData loading.
- No Geneformer execution.
- No tokenizer execution.
- No embedding extraction.
- No baseline feature extraction.
- No global preprocessing across folds.
- No scaler fitting outside training folds.
- No model fitting.
- No metric computation.
- No modeling.
- No training.
- No external validation.
- No performance claims.

## Countdown

Stage 3 step: F006
Remaining before real-data validation path can be considered: none after this
gate is merged.
