# Current Feature

Feature: P2-F010 - Human Gate 2 preparation: labels and prediction task.

Status: completed pending human review.

Planner and Scientific Judge scope:

- Define candidate prediction tasks and their minimum label evidence.
- Assess current scientific feasibility without selecting a primary task.
- Create a pending Human Gate 2 checklist.
- Preserve all Phase 2 safety restrictions.

Scientific decision:

- SLE vs healthy diagnosis: `partially_feasible`.
- Disease activity prediction: `blocked`.
- Flare prediction: `blocked`.
- Lupus nephritis prediction: `blocked`.
- No task is approved.
- `primary_task` remains TODO.

Main blockers:

- Patient-level label mapping and provenance are unresolved.
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

Human Gate 2 remains pending. All checklist items require human-reviewed
evidence before a primary prediction task can be selected.
