# Current Feature

Feature: P3-F008 - Baseline Scientific Judge review.

Status: completed; training remains blocked.

Scientific Judge decision:

- Phase 3 scaffold is `accepted_with_restrictions` as a baseline design
  framework.
- The patient-level pseudobulk, logistic, tree, composition, evaluation, and
  calibration contracts are scientifically adequate for future gate review.
- Training is allowed now: NO.
- Modeling readiness is `not_ready`.

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
real leakage checks, sample-size review, and an external validation plan.

Phase 3 scaffold is complete. The next action is a separate controlled baseline
modeling/training gate, not training itself.
`allow_modeling` remains false, `selected_datasets` remains `[]`, and
`external_validation_cohort` remains TODO.
