# Current Feature

## STAGE4-F004 - Real evaluation input readiness validation

Status: in_progress
Branch: `feat/stage4-real-evaluation-input-readiness-validation`

## Objective

Validate metadata-only readiness for connecting the completed Stage 4 upstream
contracts:

- STAGE4-F001 - real embedding artifact validation
- STAGE4-F002 - real donor-level aggregation run plan
- STAGE4-F003 - real leakage-safe split manifest validation

This feature checks whether the donor-level artifact contract, identity donor
aggregation plan, and leakage-safe split manifest contract are compatible enough
for a future evaluation-input wiring step.

## Required readiness gates

- Real artifact validation must be completed.
- Donor aggregation run plan must be completed.
- Leakage-safe split manifest validation must be completed.
- Input artifact format must remain `npy_directory`.
- Input record level must remain `donor`.
- Split level must remain `donor`.
- Expected donor count must match observed donor count.
- Unique donor IDs across splits must remain required.
- Cell-level split assignments must remain prohibited.
- Prediction, probability, metric, and model-output columns must remain prohibited.

## Allowed in this feature

- Define evaluation input readiness metadata contract.
- Validate completed upstream Stage 4 metadata contracts.
- Validate donor count compatibility.
- Validate leakage-safety gates remain enabled.
- Summarize readiness gates without materializing evaluation inputs.

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

STAGE4-F005 - Real pre-modeling audit gate

The next feature should define a final pre-modeling audit gate before any real
modeling, metric computation, or performance claim can be considered.
