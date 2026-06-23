# Current Feature

Feature: P2-F005 - QC protocol scaffold.

Status: completed pending human review.

Builder scope:

- Define QC policy and scaffold only.
- Create local QC config, empty report templates, mock-safe validation utilities, documentation, and tests.
- Preserve all thresholds as TODO until future audit approval.

Explicitly forbidden:

- Downloads.
- Real preprocessing.
- Creating real AnnData outputs.
- Cell filtering on real data.
- Modeling.
- Training.
- Model files.
- Dataset approval.
- Threshold guessing.
- Unlogged cell removal.
- Creating `selected_datasets`.
- Assigning `external_validation_cohort`.

QC scaffold summary:

- Real filtering is disabled.
- QC threshold source remains `TODO`.
- QC reports must include sample-level and patient-level summaries.
- Threshold decisions cannot be marked applied without `approved_by`.
- Guessed threshold sources are rejected.

Acceptance criteria:

- `configs/qc.yaml` exists.
- `reports/tables/qc_summary.csv` exists with headers only.
- `reports/tables/qc_threshold_decisions.csv` exists with headers only.
- `src/qc/qc_policy.py` exists.
- `tests/test_qc_protocol_config.py` and `tests/test_qc_policy.py` exist and pass.
- No data is downloaded.
- No real preprocessing is added.
- No modeling code is created.
- `selected_datasets` remains `[]`.
- `external_validation_cohort` remains TODO.
