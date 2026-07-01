# Current Feature

## STAGE3-F004 - Evaluation protocol scaffold

Status: in progress
Branch: `feat/stage3-evaluation-protocol-scaffold`

## Objective

Define the metadata-only patient-level evaluation protocol scaffold before
baseline/control planning or modeling readiness gates are considered.

This feature does not load real embedding artifacts, load AnnData files,
download data, execute Geneformer, execute tokenizers, extract embeddings, fit
scalers, train models, compute real metrics, perform external validation, or add
performance claims.

## Contract scope

The evaluation protocol scaffold validates:

- approved evaluation task
- patient/donor split level
- required primary metrics
- optional secondary metrics
- uncertainty reporting plan
- permutation control plan
- baseline comparison requirement
- confounder control requirement
- no metric computation in the scaffold
- no model fitting in the scaffold
- no performance claims

## Safety rules

- Patient/donor split level only.
- No cell-level split assignments.
- No real artifact loading.
- No AnnData loading.
- No global preprocessing across folds.
- No scaler fitting outside training folds.
- No model fitting.
- No metric computation.
- No modeling.
- No training.
- No external validation.
- No performance claims.
- Metadata-only protocol contract.

## Countdown

Stage 3 step: F004
Remaining before modeling can be considered: baseline/control plan and modeling
readiness gate.
