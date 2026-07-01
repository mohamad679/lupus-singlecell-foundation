# Current Feature

## STAGE5-F001 - Modeling approval scaffold

Status: in_progress
Branch: `feat/stage5-modeling-approval-scaffold`

## Current stage

Stage 5 - Modeling stage approval and execution planning

Stage 5 has started, but modeling is not authorized.

## Upstream handoff

Stage 4 is complete.

The Stage 4 handoff decision remains:

`separate_modeling_stage_required`

This means Stage 5 may document approval requirements and execution planning,
but Stage 5-F001 does not authorize model fitting, prediction generation,
metric computation, training, external validation, or performance claims.

## Scope

This feature is metadata-only.

It records:

- explicit modeling approval remains required
- human review before modeling remains required
- reproducibility review remains required
- leakage review remains required
- artifact integrity review remains required
- scope review remains required
- a modeling execution protocol is required before execution
- donor-level controls are required
- cell-level split is forbidden
- large real artifacts must not be committed

## Safety locks retained

No real embedding artifact is committed.
No `.npy` embedding payload is loaded.
No embedding vector is parsed.
No evaluation array is materialized.
No label array is created from real data.
No real split assignment is executed.
No real donor-level aggregation is executed.
No AnnData files are loaded.
No downloads are performed.
No Geneformer execution is performed.
No tokenizer execution is performed.
No embedding extraction is performed.
No baseline feature extraction is performed.
No scalers are fit.
No models are fit.
No predictions are generated.
No real metrics are computed.
No training is performed.
No external validation is performed.
No performance claims are added.

## Previous completed stage

## STAGE4-F006 - Stage 4 final closeout and modeling handoff decision

Status: completed

Stage 4 is complete.

The Stage 4 handoff decision was:

`separate_modeling_stage_required`

Stage 4 does not authorize modeling.

A separate modeling stage may be planned only after explicit approval.
