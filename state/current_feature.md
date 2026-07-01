# Current Feature

## STAGE5-F005 - Final Stage 5 modeling handoff decision

Status: planned
Branch: `TODO`

## Current stage

Stage 5 - Modeling stage approval and execution planning

Stage 5 has started, but modeling is still not authorized.

## Required next step

The next feature should record the final Stage 5 modeling handoff decision.

This decision must verify the completed Stage 5 approval chain and decide whether
future modeling may be handed off to a separate explicitly approved execution
stage.

## Required gates retained

- explicit modeling approval remains required
- human review before modeling remains required
- reproducibility review remains required
- leakage review remains required
- artifact integrity review remains required
- scope review remains required
- donor-level controls are required
- cell-level split is forbidden
- large real artifacts must not be committed
- a separate execution gate remains required
- no modeling execution is authorized by this closeout

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

## Previous completed feature

## STAGE5-F004 - Pre-execution audit gate

Status: completed
Branch: `chore/stage5-f004-closeout`

Stage 5-F004 recorded the metadata-only pre-execution audit gate.

It did not authorize input materialization, label creation, split execution,
model fitting, prediction generation, metric computation, training, external
validation, or performance claims.

## Earlier completed feature

## STAGE5-F003 - Donor-level execution contract approval

Status: completed
Branch: `chore/stage5-f003-closeout`

Stage 5-F003 recorded donor-level execution contract constraints only.

It did not authorize input materialization, label creation, split execution,
model fitting, prediction generation, metric computation, training, external
validation, or performance claims.

## Earlier completed feature

## STAGE5-F002 - Modeling execution protocol scaffold

Status: completed
Branch: `chore/stage5-f002-closeout`

Stage 5-F002 recorded metadata-only execution protocol boundaries.

It did not authorize model fitting, prediction generation, metric computation,
training, external validation, or performance claims.

## Earlier completed feature

## STAGE5-F001 - Modeling approval scaffold

Status: completed
Branch: `chore/stage5-f001-closeout`

Stage 5-F001 recorded the modeling approval scaffold only.

It did not authorize model fitting, prediction generation, metric computation,
training, external validation, or performance claims.

## Historical completed Stage 4 handoff

## STAGE4-F006 - Stage 4 final closeout and modeling handoff decision

Status: completed

Stage 4 is complete.

The Stage 4 handoff decision was:

`separate_modeling_stage_required`

Stage 4 does not authorize modeling.

No `.npy` embedding payload is loaded.
No evaluation array is materialized.
No predictions are generated.
No real metrics are computed.
No training is performed.
No performance claims are added.

A separate modeling stage may be planned only after explicit approval.
