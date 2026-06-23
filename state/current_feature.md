# Current Feature

Feature: P1-F014 - Final Dataset Feasibility Decision Table.

Status: completed pending human review.

Allowed work:

- Produce a final pre-Human Gate 1 decision table.
- Summarize candidate readiness without approval.
- Preserve unresolved repair blockers.
- Keep all candidates as `candidate_pending_audit`.

Final dataset decision:

- `GSE162577`: `limited_candidate`.
- `GSE137029`: `continue_audit`.
- `GSE174188`: `needs_manual_verification`.
- `436154da-bcf1-4130-9c8b-120ff9a888f2::218acb0f-9f2f-4f76-b90b-15a4b7c7f629`: `continue_audit`.

Blocking findings:

- No dataset is approved for modeling.
- Human Gate 1 remains PENDING.
- `selected_datasets` remains `[]`.
- `external_validation_cohort` remains TODO.
- Project remains blocked by unresolved dataset feasibility blockers before Human Gate 1.
- Repair queue evidence must be reviewed before any human gate decision.

Blocked work:

- Dataset downloads.
- Dataset approval.
- Human Gate 1 closure.
- Assigning `selected_datasets`.
- Assigning `external_validation_cohort`.
- Resolving blockers by guessing.
- Model implementation.
- Model training.
- Any Phase 2 work.

Acceptance criteria:

- `reports/tables/final_dataset_feasibility_decision.csv` exists.
- `state/judge_reports/P1-F014_final_dataset_decision_report.md` exists.
- Every known candidate has one final decision row.
- No candidate is marked approved.
- Overall readiness values are valid.
- Human Gate 1 remains PENDING.
- `selected_datasets` remains `[]`.
- `external_validation_cohort` remains TODO.
- `project.blocked` remains true.
