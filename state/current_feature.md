# Current Feature

## STAGE3-F005 - Baseline/control plan

Status: in progress
Branch: `feat/stage3-baseline-control-plan`

## Objective

Define the metadata-only baseline/control comparison plan before the final
modeling readiness gate is considered.

This feature does not load real embedding artifacts, load AnnData files,
download data, execute Geneformer, execute tokenizers, extract embeddings,
extract baseline features, fit scalers, train models, compute real metrics,
perform external validation, or add performance claims.

## Contract scope

The baseline/control plan validates:

- candidate representation
- patient/donor split level
- required pseudobulk baseline
- required cell-type proportion baseline
- required donor cell-count control
- required metadata confounder control
- required label permutation control
- same splits as candidate representation
- fold-internal preprocessing requirement
- no feature extraction in the scaffold
- no metric computation in the scaffold
- no model fitting in the scaffold
- no performance claims

## Safety rules

- Patient/donor split level only.
- No cell-level features.
- No real artifact loading.
- No AnnData loading.
- No feature extraction.
- No global preprocessing across folds.
- No scaler fitting outside training folds.
- No model fitting.
- No metric computation.
- No modeling.
- No training.
- No external validation.
- No performance claims.
- Metadata-only baseline/control plan.

## Countdown

Stage 3 step: F005
Remaining before modeling can be considered: modeling readiness gate.
