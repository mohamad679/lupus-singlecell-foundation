# Current Feature

Feature: P3-F017 - Training Permission Re-evaluation.

Status: completed; training and Phase 4 remain blocked.

Scientific Judge decision:

- `training_permission`: `blocked`
- `allow_modeling`: false
- `decision`: `continue_metadata_inspection`
- `phase4_permission`: `blocked`
- `pivot_status`: `not_activated`

Blocking reasons:

- dataset selection unresolved;
- patient/donor-linked label provenance unresolved;
- patient/donor mapping unresolved;
- split manifest unavailable;
- real leakage checks not executable;
- real-data QC not approved;
- feature manifest unavailable;
- external validation unresolved.

No dataset is selected and no external-validation cohort is assigned.

Next allowed work:

- controlled metadata inspection or evidence expansion;
- dataset strategy reassessment planning;
- future permission re-evaluation after new evidence.

Pivot trigger conditions are documented, but pivot is not active. Downloading,
preprocessing, training, model artifacts, metadata guessing, dataset
assignment, external-validation assignment, and Phase 4 remain forbidden.
