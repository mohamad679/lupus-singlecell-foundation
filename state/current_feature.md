# Current Feature

## STAGE4-F001-CLOSEOUT - Real embedding artifact validation closeout

Status: completed
Branch: `chore/stage4-f001-closeout`

## Completed feature

STAGE4-F001 - Real embedding artifact validation

## Result

Stage 4-F001 established a safe real embedding artifact validation scaffold and
extended it to support the observed local artifact layout:

- artifact format: `npy_directory`
- artifact layout: `directory`
- record level: `donor`
- file suffix: `.npy`
- observed files: 261
- total observed size: 360,839,808 bytes / 344.12 MB
- all files same size: true
- min/max file size: 1,382,528 bytes
- filename category counts:
  - flare_like: 14
  - healthy_hc_like: 48
  - healthy_igtb_like: 50
  - managed_sle_numeric_like: 148
  - control_like: 1

The absolute local artifact path is not committed.

## Safety rules preserved

No real embedding artifact is committed.
No model artifact is committed.
No AnnData files are loaded.
No downloads are performed.
No Geneformer execution is performed.
No tokenizer execution is performed.
No embedding extraction is performed.
No embedding payload table is parsed.
No `.npy` embedding payload is loaded.
No real donor-level aggregation is performed.
No baseline feature extraction is performed.
No scalers are fit.
No models are fit.
No real metrics are computed.
No training is performed.
No external validation is performed.
No performance claims are added.

## Next feature

STAGE4-F002 - Real donor-level aggregation run plan

The next feature may define a guarded plan for donor-level aggregation inputs,
but real aggregation remains blocked until the plan and required gates are
explicitly added.
