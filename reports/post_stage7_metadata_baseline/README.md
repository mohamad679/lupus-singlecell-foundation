# Post-Stage 7 Metadata-Only Baseline

Status: real_result

This report contains internal-only metadata-only LOOCV control results.

These results are not clinical validation, not external validation, not diagnostic evidence, and not deployment evidence.

## Input

- Metadata source: `/kaggle/working/gse174188_cellxgene_obs_metadata.csv`
- Cells used: 1262189
- Patients used: 260
- Categorical metadata used: ['sex', 'tissue', 'assay', 'suspension_type', 'development_stage']
- Cell-type composition used: True
- Excluded columns: ['disease']

## Internal LOOCV Results

| task             | status      | result_type                          |   n_patients |   n_positive |   n_negative |   auroc_internal_loocv_only |   auprc_internal_loocv_only |   accuracy_at_0_5 |   balanced_accuracy_at_0_5 |
|:-----------------|:------------|:-------------------------------------|-------------:|-------------:|-------------:|----------------------------:|----------------------------:|------------------:|---------------------------:|
| flare_vs_managed | real_result | metadata_only_internal_LOOCV_control |          162 |           14 |          148 |                    0.655405 |                    0.142849 |          0.759259 |                   0.544884 |
| flare_vs_healthy | real_result | metadata_only_internal_LOOCV_control |          112 |           14 |           98 |                    0.940962 |                    0.836111 |          0.928571 |                   0.867347 |

## Boundary

This is a metadata-only internal LOOCV control.

It tests whether non-expression metadata and cell-type composition can carry label-associated signal inside this dataset.

It must not be interpreted as clinical validation, external validation, diagnostic performance, deployment readiness, or biological mechanism evidence.
