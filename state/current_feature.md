# Current Feature

Feature: P2-F002 - AnnData schema and integrity contract.

Status: completed pending human review.

Builder scope:

- Define AnnData schema and integrity rules only.
- Create schema metadata, validation utilities, documentation, and tests.
- Support mock AnnData-like validation without loading real datasets.

Explicitly forbidden:

- Downloads.
- Creating real AnnData objects from datasets.
- Preprocessing real datasets.
- Modeling.
- Training.
- Model files.
- Cell-level splits.
- Dataset approval for modeling.
- Creating `selected_datasets`.
- Assigning `external_validation_cohort`.

Schema contract summary:

- Required `obs` fields include cell, patient, donor, sample, cohort, batch, tissue, assay, disease, cell type, source dataset, and split group fields.
- Required `var` fields include gene ID, gene symbol, feature type, and genome.
- Required layers are `counts`, `normalized`, and `log_normalized`.
- Required `uns` fields include dataset/source provenance, preprocessing version, schema version, audit status, and patient-level split policy.
- Integrity checks reject missing patient IDs, missing disease labels, cell-level split policy, duplicate indexes, and X-shape mismatches.

Acceptance criteria:

- `metadata/anndata_schema.yaml` exists.
- `src/data/anndata_schema.py` exists.
- `tests/test_anndata_schema_contract.py` exists.
- No data is downloaded.
- No modeling code is created.
- `selected_datasets` remains `[]`.
- `external_validation_cohort` remains TODO.
