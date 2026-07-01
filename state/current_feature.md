# Current Feature

## STAGE4-F002-CLOSEOUT - Real donor-level aggregation run plan closeout

Status: completed
Branch: `chore/stage4-f002-closeout`

## Completed feature

STAGE4-F002 - Real donor-level aggregation run plan

## Result

Stage 4-F002 defined a guarded metadata-only run plan for the observed real
donor-level embedding artifact.

The observed artifact from STAGE4-F001 remains:

- artifact format: `npy_directory`
- artifact layout: `directory`
- input record level: `donor`
- output record level: `donor`
- split level: `donor`
- observed files: 261
- total observed size: 360,839,808 bytes / 344.12 MB
- all files same size: true

The selected F002 strategy is:

`identity_donor_embedding_directory`

This confirms that the artifact is treated as already donor-level. No cell-to-
donor pooling is planned or executed in F002.

## Safety rules preserved

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

## Next feature

STAGE4-F003 - Real leakage-safe split manifest validation

The next feature should define and validate donor-level split manifest
requirements before any evaluation input preparation.
