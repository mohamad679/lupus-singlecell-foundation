# Current Feature

## STAGE4-F004-CLOSEOUT - Real evaluation input readiness validation closeout

Status: completed
Branch: `chore/stage4-f004-closeout`

## Completed feature

STAGE4-F004 - Real evaluation input readiness validation

## Result

Stage 4-F004 defined a metadata-only readiness contract for connecting the
completed Stage 4 upstream contracts:

- STAGE4-F001 - real embedding artifact validation
- STAGE4-F002 - real donor-level aggregation run plan
- STAGE4-F003 - real leakage-safe split manifest validation

The completed readiness contract requires:

- real artifact validation status: `completed`
- donor aggregation run plan status: `completed`
- leakage-safe split manifest validation status: `completed`
- input artifact format: `npy_directory`
- input artifact layout: `directory`
- input record level: `donor`
- aggregation strategy: `identity_donor_embedding_directory`
- split level: `donor`
- expected donor count: 261
- observed donor count: 261
- expected donor count matching observed donor count
- unique donor IDs across splits remaining required
- cell-level split assignments remaining prohibited
- prediction, probability, metric, and model-output columns remaining prohibited

## Safety rules preserved

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

## Next feature

STAGE4-F005 - Real pre-modeling audit gate

The next feature should define a final pre-modeling audit gate before any real
modeling, metric computation, or performance claim can be considered.
