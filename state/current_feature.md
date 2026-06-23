# Current Feature

Feature: P2-F011 - Human Gate 2 Decision.

Status: completed with restricted Human Gate 2 approval.

Planner and Scientific Judge decision:

- Human Gate 2 is `approved_with_restrictions`.
- Only Phase 3 baseline design for SLE diagnosis / case-control prediction is
  allowed next.
- This decision does not approve data acquisition, preprocessing, model
  implementation, or training.
- `allow_modeling` remains false until a later explicit Phase 3 feature changes
  it.

Scientific decision:

- SLE vs healthy diagnosis: restricted primary task for baseline design.
- Disease activity prediction: `blocked`.
- Flare prediction: `blocked`.
- Lupus nephritis prediction: `blocked`.
- Foundation models, deep patient-level MIL, uncertainty modeling, and dashboard
  work are not approved.

Main blockers:

- Patient-level label mapping and provenance require verification before
  reporting results.
- Disease activity and flare labels are not explicitly verified.
- Lupus nephritis labels and compatible comparators are unresolved.
- Cross-cohort overlap and external validation independence are unresolved.
- Biological interpretation and uncertainty prerequisites remain pending.

Explicitly forbidden:

- Downloads.
- Preprocessing.
- Modeling or training.
- Model files.
- Dataset approval for modeling.
- Assigning `selected_datasets`.
- Assigning `external_validation_cohort`.
- Starting Phase 3.
- Implementing Phase 3 backlog items.

Phase 2 is complete. Phase 3 exists only as a backlog scaffold.
`selected_datasets` remains `[]`, `external_validation_cohort` remains TODO, and
any future baseline result must be marked preliminary until labels are verified.
