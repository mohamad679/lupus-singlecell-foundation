# Current Feature

Feature: P3-F013 - Patient/donor ID and label provenance evidence plan.

Status: completed with all modeling-readiness blockers preserved.

Planner, Scientific Judge, and Bioinformatics Judge findings:

- A source-specific patient/donor identifier evidence plan now exists.
- A source-specific diagnosis and comparator label provenance plan now exists.
- GSE137029 requires exact patient/donor fields, sample mapping, and
  case/control linkage.
- CELLxGENE/HCA requires field-level donor completeness, sample relationships,
  disease-label linkage, and original-source provenance.
- GEO/CELLxGENE/HCA cohort overlap remains unresolved.
- Disease activity and lupus nephritis labels remain blocked.
- No evidence-plan row is verified; visible metadata is insufficient to pass a
  modeling-readiness requirement.

Modeling controls:

- `modeling_readiness`: `not_ready`
- `training_permission`: `blocked`
- `allow_modeling`: false
- `selected_datasets`: []
- `external_validation_cohort`: TODO

Explicitly forbidden:

- Guessing or constructing identifiers, labels, or cohort mappings.
- Downloading full datasets.
- Selecting a dataset or assigning an external-validation cohort.
- Creating a real split, features, predictions, or model artifacts.
- Training models or starting Phase 4.

Next work requires a separately approved metadata evidence inspection. The
results must preserve exact source fields and receive human review before any
readiness blocker can pass.
