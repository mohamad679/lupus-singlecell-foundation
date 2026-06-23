# Current Feature

Feature: P2-F004 - Gene identifier policy.

Status: completed pending human review.

Builder scope:

- Define gene identifier policy only.
- Create policy metadata, an empty mapping report, mock-safe validation utilities, documentation, and tests.
- Support future single-cell preprocessing, cross-cohort harmonization, pathway analysis, and foundation model compatibility planning.

Explicitly forbidden:

- Downloads.
- Preprocessing real data.
- Creating AnnData objects.
- Modeling.
- Training.
- Model files.
- Inferring gene identifiers from real data.
- Silent gene dropping.
- Silent duplicate gene collapse.
- Unsupported ID conversion.
- Creating `selected_datasets`.
- Assigning `external_validation_cohort`.

Policy summary:

- Original gene IDs and gene symbols must be preserved.
- `var` indexes must be unique.
- Gene drops, unmapped genes, duplicate genes, and vocabulary mismatches require explicit reports.
- Foundation model vocabulary compatibility requires a tracked vocabulary version and unmatched-gene report.
- Pathway claims are forbidden without valid gene mapping and later statistical correction.

Acceptance criteria:

- `metadata/gene_identifier_policy.yaml` exists.
- `reports/tables/gene_mapping_report.csv` exists with headers only.
- `src/data/gene_identifier_policy.py` exists.
- `tests/test_gene_identifier_policy.py` exists and passes.
- No data is downloaded.
- No preprocessing is added.
- No modeling code is created.
- `selected_datasets` remains `[]`.
- `external_validation_cohort` remains TODO.
