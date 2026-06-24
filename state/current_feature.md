# Current Feature

Feature: P3-F011 - Training permission decision.

Status: completed; training permission is `blocked`.

Planner and Scientific Judge decision:

- Formal Training Permission Decision recorded.
- Decision: `blocked`.
- Modeling readiness remains `not_ready`.
- All eight verification blockers remain unresolved.
- `allow_modeling` and `training_allowed` remain false.

Scientific decision:

- SLE diagnosis / case-control prediction: approved for baseline design only.
- Disease activity prediction: `blocked`.
- Flare prediction: `blocked`.
- Lupus nephritis prediction: `blocked`.
- Foundation models, deep patient-level MIL, uncertainty modeling, and dashboard
  work are not approved.

Explicitly forbidden:

- Computing real or mock calibration metrics.
- Generating reliability diagrams or calibration curves.
- Implementing uncertainty, abstention, or selective prediction methods.
- Reporting performance or clinical utility claims.
- Fitting or training models.
- Prediction or probability generation.
- Model artifact creation.
- Loading real features, labels, or datasets.
- Loading or preprocessing real cell-level data.
- Real pseudobulk feature extraction or matrix creation.
- Loading or preprocessing real data.
- Deep learning or DeepSets.
- Foundation models.
- Uncertainty modeling.
- Dashboard work.
- Model artifacts.
- Dataset approval or selection.
- External validation assignment.
- Cell-level splitting.
- Starting Phase 4.

Main blockers are dataset selection, verified patient-level labels, approved
data/QC, finalized feature policies, populated patient-level splits, passed
real leakage checks, sample-size review, and training-cohort suitability.

Recommendation: continue verification, not modeling. A future training decision
requires all eight blockers to be verified and all blocking readiness checks to
pass. Phase 4 is not started.
`allow_modeling` remains false, `selected_datasets` remains `[]`, and
`external_validation_cohort` remains TODO.
