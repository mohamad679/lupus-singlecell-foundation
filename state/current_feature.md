# Current Feature

## STAGE4-F005 - Real pre-modeling audit gate

Status: in_progress
Branch: `feat/stage4-real-pre-modeling-audit-gate`

## Objective

Define a metadata-only pre-modeling audit gate after completion of the upstream
Stage 4 contracts:

- STAGE4-F001 - real embedding artifact validation
- STAGE4-F002 - real donor-level aggregation run plan
- STAGE4-F003 - real leakage-safe split manifest validation
- STAGE4-F004 - real evaluation input readiness validation

This feature confirms that all pre-modeling review gates remain required before
any real modeling, metric computation, or performance claim can be considered.

## Required audit gates

- Human review before modeling remains required.
- Explicit modeling permission remains required.
- Reproducibility review remains required.
- Leakage review remains required.
- Artifact integrity review remains required.
- Scope review remains required.

## Allowed in this feature

- Define pre-modeling audit gate metadata contract.
- Validate completed upstream Stage 4 metadata contracts.
- Verify all pre-modeling review gates remain required.
- Summarize audit status without granting modeling permission.

## Not allowed in this feature

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

## Next expected feature

STAGE4-F006 - Stage 4 final closeout and modeling handoff decision

The next feature should close Stage 4 and record whether the project remains
blocked or can move toward a separately approved modeling stage.
