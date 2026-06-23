# Current Feature

Feature: P2-F003 - Metadata harmonization schema.

Status: completed pending human review.

Builder scope:

- Define canonical metadata fields and source mapping rules only.
- Create mock-safe harmonization validation utilities, documentation, and tests.
- Preserve unknown values as `TODO` or `unclear`.

Explicitly forbidden:

- Downloads.
- Preprocessing real datasets.
- Creating AnnData objects.
- Modeling.
- Training.
- Model files.
- Metadata guessing.
- Label inference.
- Creating `selected_datasets`.
- Assigning `external_validation_cohort`.

Schema summary:

- Canonical fields cover patient, donor, sample, cell, cohort, batch, dataset, source, organism, tissue, assay, disease, activity, cell type, treatment, demographics, timepoint, and split policy metadata.
- Source mappings for GEO, CELLxGENE, and HCA are placeholders with `TODO` original fields until manually verified.
- Validation rejects missing required canonical fields such as `dataset_id` and `disease_label`.
- The utility works with dictionaries and mock metadata only.

Acceptance criteria:

- `metadata/metadata_harmonization_schema.yaml` exists.
- `metadata/source_field_mapping.yaml` exists.
- `src/data/metadata_harmonization.py` exists.
- `tests/test_metadata_harmonization_schema.py` exists and passes.
- No data is downloaded.
- No preprocessing is added.
- No modeling code is created.
- `selected_datasets` remains `[]`.
- `external_validation_cohort` remains TODO.
