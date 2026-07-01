# Current Feature

## STAGE5-F002 - Modeling execution protocol scaffold

Status: in_progress
Branch: `feat/stage5-modeling-execution-protocol-scaffold`

## Current stage

Stage 5 - Modeling stage approval and execution planning

Stage 5-F002 defines protocol boundaries only.

Stage 5 has started, but modeling is still not authorized.

Modeling is still not authorized.

## Scope

This feature is metadata-only.

It records the required protocol boundaries for future execution planning:

- protocol record level must remain donor
- split policy must remain donor-level only
- cell-level split remains forbidden
- artifact loading remains prohibited until an explicit later gate
- input materialization remains prohibited until an explicit later gate
- label creation remains prohibited until an explicit later gate
- aggregation execution remains prohibited until an explicit later gate
- modeling execution remains prohibited until an explicit later gate
- prediction generation remains prohibited until an explicit later gate
- metric computation is future-only and not computed here
- external validation remains prohibited until an explicit later gate
- performance claims remain prohibited until an explicit later gate

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

## Next planned feature

## STAGE5-F003 - Donor-level execution contract approval

Status: planned
Branch: `TODO`

The next feature should review the donor-level execution contract before any
real input materialization, split execution, or modeling can be considered.

## Previous completed feature

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
