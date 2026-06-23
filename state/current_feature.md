# Current Feature

Feature: P3-F001 - Baseline modeling scaffold.

Status: completed pending review.

Builder scope:

- Baseline modeling scaffold only.
- Define baseline families, input contracts, split requirements, evaluation
  planning, and safety checks.
- Keep every baseline disabled for training.
- Preserve restricted Human Gate 2 scope.

Scientific decision:

- SLE diagnosis / case-control prediction: approved for baseline design only.
- Disease activity prediction: `blocked`.
- Flare prediction: `blocked`.
- Lupus nephritis prediction: `blocked`.
- Foundation models, deep patient-level MIL, uncertainty modeling, and dashboard
  work are not approved.

Explicitly forbidden:

- Actual training or real model fitting.
- Loading or preprocessing real data.
- Deep learning or DeepSets.
- Foundation models.
- Uncertainty modeling.
- Dashboard work.
- Model artifacts.
- Dataset approval or selection.
- External validation assignment.
- Cell-level splitting.
- Starting P3-F002 or later features.

The empty `src/models` package is organizational scaffolding only; it contains
no estimator or training implementation. `allow_modeling` remains false,
`selected_datasets` remains `[]`, and `external_validation_cohort` remains TODO.
