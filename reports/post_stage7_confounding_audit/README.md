# Post-Stage 7 Confounding Audit

Status: real_result

This report contains an internal descriptive confounding audit using full CELLxGENE obs metadata.

This is not clinical validation, not external validation, not diagnostic evidence, and not deployment evidence.

## Input

- Metadata source: `/kaggle/working/gse174188_cellxgene_obs_metadata.csv`
- Cells used: 1262189
- Patients used: 260
- Patient counts: {'managed': 148, 'healthy': 98, 'flare': 14}

## Audited Metadata

- Patient-level categorical metadata: ['sex', 'tissue', 'assay', 'suspension_type', 'development_stage', 'disease']
- Donor-level cell-type composition: True

## Outputs

- `patient_metadata_categorical_audit.csv`
- `cell_counts_by_group.csv`
- `cell_type_composition_audit.csv`
- `run_summary.json`

## Boundary

Internal descriptive audit only.

No clinical claim, no external validation claim, no diagnostic claim, no deployment claim.
