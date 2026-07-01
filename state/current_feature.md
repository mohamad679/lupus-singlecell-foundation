# Current Feature

## STAGE4-F003-CLOSEOUT - Real leakage-safe split manifest validation closeout

Status: completed
Branch: `chore/stage4-f003-closeout`

## Completed feature

STAGE4-F003 - Real leakage-safe split manifest validation

## Result

Stage 4-F003 defined a guarded donor-level split manifest validation contract for
the observed real donor-level embedding artifact.

The completed validation contract requires:

- split level: `donor`
- unique donor IDs across the split manifest
- no donor ID appearing in multiple splits
- required split names: `train`, `validation`, and `test`
- allowed label groups:
  - `flare_like`
  - `healthy_hc_like`
  - `healthy_igtb_like`
  - `managed_sle_numeric_like`
  - `control_like`
- no cell-level split columns
- no prediction, probability, metric, or model-output columns

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

STAGE4-F004 - Real evaluation input readiness validation

The next feature should validate whether donor-level embeddings, leakage-safe
split manifest metadata, and evaluation input metadata are ready to be connected
without running models or computing performance.
