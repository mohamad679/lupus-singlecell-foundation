# Current Feature

## Stage 6 active

Status: in_progress
Branch: `feat/stage6-f006-prediction-metric-computation`

## Active stage

Stage 6 - Controlled donor-level modeling execution

Stage 6 remains the single controlled execution stage.

No Stage 7 is required for execution.

## Active feature

## STAGE6-F007 - Stage 6 final result report and closeout

Status: ready
Branch: `feat/stage6-f006-prediction-metric-computation`

STAGE6-F006 is complete.

STAGE6-F007 is the final Stage 6 closeout feature.

## Completed Stage 6 feature

## STAGE6-F006 - Prediction and metric computation

Status: completed
Branch: `feat/stage6-f006-prediction-metric-computation`

Closeout feature: STAGE6-F006-CLOSEOUT

Prediction generation is allowed only for in-memory donor-level records.

Metric computation is allowed only for in-memory donor-level predictions.

F006 does not write report tables or prediction artifacts.

No filesystem artifact access is performed.
No real artifact file is loaded.
No `.npy` embedding payload is loaded.
No embedding vector is parsed from disk.
No split assignment is executed from files.
No model refit is performed.
No training is performed.
No model artifact is persisted.
No prediction manifest is written.
No metric table is written.
No external validation is performed.
No performance claims are added.

---

# Current Feature

## Stage 6 active

Status: in_progress
Branch: `feat/stage6-f005-controlled-baseline-execution`

## Active stage

Stage 6 - Controlled donor-level modeling execution

Stage 6 remains the single controlled execution stage.

No Stage 7 is required for execution.

## Active feature

## STAGE6-F006 - Prediction and metric computation

Status: ready
Branch: `feat/stage6-f005-controlled-baseline-execution`

STAGE6-F005 is complete.

STAGE6-F006 is the next required feature.

## Completed Stage 6 feature

## STAGE6-F005 - Controlled baseline execution

Status: completed
Branch: `feat/stage6-f005-controlled-baseline-execution`

Closeout feature: STAGE6-F005-CLOSEOUT

Controlled baseline fitting is allowed only for in-memory donor-level records.

F005 adds a dependency-free nearest-centroid baseline fit path using train donors only.

No filesystem artifact access is performed.
No real artifact file is loaded.
No `.npy` embedding payload is loaded.
No embedding vector is parsed from disk.
No input arrays are materialized from files.
No label arrays are materialized from files.
No split assignment is executed from files.
No global preprocessing is performed.
No scalers are fit outside training folds.
No model artifact is persisted.
No predictions are generated in F005.
No metrics are computed in F005.
No external validation is performed.
No performance claims are added.

---

# Current Feature

## Stage 6 active

Status: in_progress
Branch: `feat/stage6-f004-split-leakage-control-gate`

## Active stage

Stage 6 - Controlled donor-level modeling execution

Stage 6 remains the single controlled execution stage.

No Stage 7 is required for execution.

## Active feature

## STAGE6-F005 - Controlled baseline execution

Status: ready
Branch: `feat/stage6-f004-split-leakage-control-gate`

STAGE6-F003 and STAGE6-F004 are complete.

STAGE6-F005 is the next required feature.

STAGE6-F005 is the first controlled runtime execution feature and must remain donor-level only.

## Completed Stage 6 feature

## STAGE6-F004 - Split and leakage-control gate

Status: completed
Branch: `feat/stage6-f004-split-leakage-control-gate`

Closeout feature: STAGE6-F004-CLOSEOUT

The split and leakage-control gate is closed as metadata-only.

No real split assignment is executed.
No fold index is materialized.
No `.npy` embedding payload is loaded.
No embedding vector is parsed.
No feature matrix is constructed.
No label array is created from real data.
No evaluation array is materialized.
No global preprocessing is performed.
No fold preprocessor is fit.
No scalers are fit.
No models are fit.
No predictions are generated.
No real metrics are computed.
No training is performed.
No external validation is performed.
No performance claims are added.

---

# Current Feature

## Stage 6 active

Status: in_progress
Branch: `feat/stage6-donor-level-input-materialization-gate`

## Active stage

Stage 6 - Controlled donor-level modeling execution

Stage 6 remains the single controlled execution stage.

No Stage 7 is required for execution.

## Active feature

## STAGE6-F003 - Donor-level input materialization gate

Status: in_progress
Branch: `feat/stage6-donor-level-input-materialization-gate`

STAGE6-F003 records the donor-level materialization contract only.

It defines future donor-index, artifact-to-donor alignment, label-mapping,
split-alignment, feature-matrix, fold-local preprocessing, and leakage-control
contracts.

It does not materialize real arrays.

## Next Stage 6 feature

## STAGE6-F004 - Split and leakage-control gate

STAGE6-F004 is the next required gate after STAGE6-F003.

## Runtime safety locks retained in STAGE6-F003

No filesystem artifact access is performed.
No real embedding artifact is committed.
No `.npy` embedding payload is loaded.
No embedding vector is parsed.
No feature matrix is constructed.
No label array is created from real data.
No evaluation array is materialized.
No materialized array is persisted.
No real split assignment is executed.
No fold preprocessor is fit.
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

---

# Current Feature

## Stage 6 active

Status: in_progress
Branch: `chore/stage6-f002-closeout`

## Active stage

Stage 6 - Controlled donor-level modeling execution

Stage 6 remains the single controlled execution stage.

No Stage 7 is required for execution.

## Active feature

## STAGE6-F003 - Donor-level input materialization gate

Status: ready
Branch: `chore/stage6-f002-closeout`

STAGE6-F002 is complete.

STAGE6-F003 is the next required gate.

STAGE6-F003 may define the donor-level input materialization contract, but it must not materialize real arrays until an explicit Stage 6 execution gate allows it.

## Completed Stage 6 feature

## STAGE6-F002 - Real artifact access and integrity gate

Status: completed
Branch: `chore/stage6-f002-closeout`

Closeout feature: STAGE6-F002-CLOSEOUT

The real artifact access and integrity gate is closed as metadata-only.

No filesystem artifact access is performed.
No real embedding artifact is committed.
No real artifact file count is scanned.
No checksum is calculated over real artifacts.
No `.npy` embedding payload is loaded.
No embedding vector is parsed.
No evaluation array is materialized.
No labels are created from real data.
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

---

# Current Feature

## Stage 6 active

Status: in_progress
Branch: `feat/stage6-real-artifact-access-integrity-gate`

## Active stage

Stage 6 - Controlled donor-level modeling execution

Stage 6 remains the single controlled execution stage.

No Stage 7 is required for execution.

## Active feature

## STAGE6-F002 - Real artifact access and integrity gate

Status: in_progress
Branch: `feat/stage6-real-artifact-access-integrity-gate`

STAGE6-F002 records path/schema/permission/integrity contracts only.

It identifies the expected donor-level artifact family, format, layout,
record level, and no-large-artifact-commit policy.

It does not perform runtime execution.

## Next Stage 6 feature

## STAGE6-F003 - Donor-level input materialization gate

STAGE6-F003 is the next required gate after STAGE6-F002.

## Runtime safety locks retained in STAGE6-F002

No filesystem artifact access is performed.
No real embedding artifact is committed.
No real artifact file count is scanned.
No checksum is calculated over real artifacts.
No `.npy` embedding payload is loaded.
No embedding vector is parsed.
No evaluation array is materialized.
No labels are created from real data.
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

---

# Current Feature

## Stage 6 active

Status: in_progress
Branch: `chore/stage6-f001-closeout`

## Active stage

Stage 6 - Controlled donor-level modeling execution

Stage 6 remains the single controlled execution stage.

No Stage 7 is required for execution.

## Active feature

## STAGE6-F002 - Real artifact access and integrity gate

Status: ready
Branch: `chore/stage6-f001-closeout`

STAGE6-F001 is complete.

STAGE6-F002 is the next required gate.

STAGE6-F002 may define and verify real artifact access and integrity
requirements, but it must not load `.npy` payloads, parse embedding
vectors, materialize evaluation arrays, create real labels, execute
splits, fit models, generate predictions, compute metrics, train models,
run external validation, or add performance claims.

## Completed Stage 6 feature

## STAGE6-F001 - Modeling execution authorization

Status: completed
Branch: `chore/stage6-f001-closeout`

Stage 6-F001 opened Stage 6 as the controlled donor-level modeling
execution stage.

It recorded that execution must proceed inside Stage 6 and that no
Stage 7 is required for execution.

It did not perform runtime execution.

## Stage 6 execution structure

- STAGE6-F001 - Modeling execution authorization
- STAGE6-F002 - Real artifact access and integrity gate
- STAGE6-F003 - Donor-level input materialization gate
- STAGE6-F004 - Split and leakage-control gate
- STAGE6-F005 - Controlled baseline execution
- STAGE6-F006 - Prediction and metric computation
- STAGE6-F007 - Stage 6 final result report and closeout

## Runtime safety locks retained after STAGE6-F001 closeout

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

---

# Current Feature

## Stage 6 active

Status: in_progress
Branch: `feat/stage6-controlled-donor-level-modeling-execution`

## Active stage

Stage 6 - Controlled donor-level modeling execution

Stage 6 is now the single controlled execution stage.

No Stage 7 is required for execution.

Real execution must proceed inside Stage 6 after explicit feature gates.

## Active feature

## STAGE6-F001 - Modeling execution authorization

Status: in_progress
Branch: `feat/stage6-controlled-donor-level-modeling-execution`

Stage 6-F001 records the authorization to open Stage 6 as the controlled
donor-level modeling execution stage.

It does not perform runtime execution.

It does not authorize immediate real artifact loading, input materialization,
label creation, split execution, model fitting, prediction generation, metric
computation, training, external validation, or performance claims.

## Stage 6 execution structure

- STAGE6-F001 - Modeling execution authorization
- STAGE6-F002 - Real artifact access and integrity gate
- STAGE6-F003 - Donor-level input materialization gate
- STAGE6-F004 - Split and leakage-control gate
- STAGE6-F005 - Controlled baseline execution
- STAGE6-F006 - Prediction and metric computation
- STAGE6-F007 - Stage 6 final result report and closeout

## Runtime safety locks retained in STAGE6-F001

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

## Required controls retained

- donor-level controls are required
- cell-level split is forbidden
- no large real artifact may be committed
- runtime execution requires explicit Stage 6 feature gates
- all real execution must remain leakage-controlled

---

# Current Feature

## Stage 5 complete

Status: completed
Branch: `chore/stage5-final-closeout`

## Completed stage

Stage 5 - Modeling stage approval and execution planning

Stage 5 is complete.

Stage 5 has started, but modeling is still not authorized.

Stage 5-F005 records the final Stage 5 modeling handoff decision only.

A separate explicitly approved modeling execution stage is required.

A separate modeling execution stage is required.

## Final Stage 5 handoff decision

The final Stage 5 handoff decision is:

`separate_modeling_execution_stage_required`

Stage 5 does not authorize modeling execution.

A separate explicitly approved modeling execution stage is required before any
real modeling, prediction generation, metric computation, training, external
validation, or performance claim can be considered.

## Completed Stage 5 feature chain

- STAGE5-F001 - Modeling approval scaffold
- STAGE5-F002 - Modeling execution protocol scaffold
- STAGE5-F003 - Donor-level execution contract approval
- STAGE5-F004 - Pre-execution audit gate
- STAGE5-F005 - Final Stage 5 modeling handoff decision

## Required gates retained for any future modeling execution stage

- explicit modeling approval remains required
- a separate execution stage remains required
- human review before modeling remains required
- reproducibility review remains required
- leakage review remains required
- artifact integrity review remains required
- scope review remains required
- donor-level controls are required
- cell-level split is forbidden
- large real artifacts must not be committed
- protocol before execution remains required

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

## Completed feature

## STAGE5-F005 - Final Stage 5 modeling handoff decision

Status: completed
Branch: `chore/stage5-final-closeout`

Stage 5-F005 recorded the final Stage 5 modeling handoff decision only.

It did not authorize input materialization, label creation, split execution,
model fitting, prediction generation, metric computation, training, external
validation, or performance claims.

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
