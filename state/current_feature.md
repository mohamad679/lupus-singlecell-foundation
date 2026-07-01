# Current Feature

## STAGE4-F002 - Real donor-level aggregation run plan

Status: in_progress
Branch: `feat/stage4-real-donor-aggregation-run-plan`

## Objective

Define a guarded run plan for the observed real donor-level embedding artifact
without loading `.npy` payloads or executing real aggregation.

The artifact observed in STAGE4-F001 is already donor-level:

- artifact format: `npy_directory`
- artifact layout: `directory`
- input record level: `donor`
- output record level: `donor`
- observed files: 261
- total observed size: 360,839,808 bytes / 344.12 MB
- all files same size: true

Therefore the F002 aggregation strategy is:

`identity_donor_embedding_directory`

This means the plan treats each donor `.npy` file as one donor-level embedding
candidate, but does not open, load, parse, or aggregate the file payloads.

## Allowed in this feature

- Define donor-level aggregation run plan metadata.
- Validate that expected and observed donor file counts match.
- Validate that filename category counts sum to observed donor file count.
- Preserve identity strategy for an already donor-level artifact.
- Record that real aggregation execution remains blocked.

## Not allowed in this feature

No real embedding artifact is committed.
No `.npy` embedding payload is loaded.
No embedding vector is parsed.
No real donor-level aggregation is executed.
No AnnData files are loaded.
No downloads are performed.
No Geneformer execution is performed.
No tokenizer execution is performed.
No embedding extraction is performed.
No baseline feature extraction is performed.
No scalers are fit.
No models are fit.
No real metrics are computed.
No training is performed.
No external validation is performed.
No performance claims are added.

## Next expected feature

STAGE4-F003 - Real leakage-safe split manifest validation

The next feature should define and validate donor-level split manifest
requirements before any evaluation input preparation.
