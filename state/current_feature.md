# Current Feature

## STAGE4-F003 - Real leakage-safe split manifest validation

Status: in_progress
Branch: `feat/stage4-real-leakage-safe-split-manifest-validation`

## Objective

Define and validate a donor-level split manifest contract for the observed real
donor-level embedding artifact without loading `.npy` payloads, parsing
embedding vectors, executing real aggregation, fitting models, or computing
metrics.

The split manifest must operate at donor/patient level only. Donor IDs must not
leak across train, validation, and test assignments.

## Required split manifest rules

- The split level must be `donor`.
- Each donor ID may appear only once.
- A donor ID must not appear in multiple splits.
- Required split names are `train`, `validation`, and `test`.
- Allowed label groups are:
  - `flare_like`
  - `healthy_hc_like`
  - `healthy_igtb_like`
  - `managed_sle_numeric_like`
  - `control_like`
- Cell-level split columns are prohibited.
- Prediction, probability, metric, and model-output columns are prohibited.

## Allowed in this feature

- Define donor-level split manifest validation schema.
- Validate unique donor IDs across splits.
- Validate allowed split names.
- Validate allowed label group names.
- Summarize split and label counts without computing model metrics.

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

STAGE4-F004 - Real evaluation input readiness validation

The next feature should validate whether donor-level embeddings, leakage-safe
split manifests, and evaluation input metadata are ready to be connected without
running models or computing performance.
