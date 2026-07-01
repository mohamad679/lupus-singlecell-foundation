# Current Feature

## STAGE3-F003 - Leakage-safe split utilities

Status: in progress
Branch: `feat/stage3-leakage-safe-splits`

## Objective

Define fake-data leakage-safe split utilities for donor/patient-level analysis
before evaluation protocol scaffolding, baselines, or modeling readiness gates
are considered.

This feature does not load real embedding artifacts, load AnnData files,
download data, execute Geneformer, execute tokenizers, extract embeddings, fit
scalers, train models, perform external validation, or add performance claims.

## Contract scope

The split design validates:

- split method
- split level
- donor-level label records
- duplicate donor identifiers
- leave-one-donor-out folds
- deterministic GroupKFold-like folds
- feasible label stratification
- train/test donor disjointness
- held-out donor coverage
- fold identifier uniqueness
- no global preprocessing across folds
- no scaler fitting outside training folds
- no model fitting

## Safety rules

- Patient/donor split level only.
- No cell-level split assignments.
- No real artifact loading.
- No AnnData loading.
- No global preprocessing across folds.
- No scaler fitting outside training folds.
- No model fitting.
- No modeling.
- No training.
- No external validation.
- No performance claims.
- Fake donor-level records only.

## Countdown

Stage 3 step: F003
Remaining before modeling can be considered: evaluation protocol scaffold,
baseline/control plan, and modeling readiness gate.
