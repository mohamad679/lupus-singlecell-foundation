# Colab Results Status

## Post-Stage 7 Controls

### Label permutation control

Status: real_result

100 permutations were completed and committed previously in `reports/post_stage7_permutation_test/`.

### Metadata-only baseline

Status: real_result

Full CELLxGENE obs metadata was fetched for dataset `218acb0f-9f2f-4f76-b90b-15a4b7c7f629`.

Observed metadata-only internal LOOCV control results:

| task             | status      | result_type                          |   n_patients |   n_positive |   n_negative |   auroc_internal_loocv_only |   auprc_internal_loocv_only |   accuracy_at_0_5 |   balanced_accuracy_at_0_5 |
|:-----------------|:------------|:-------------------------------------|-------------:|-------------:|-------------:|----------------------------:|----------------------------:|------------------:|---------------------------:|
| flare_vs_managed | real_result | metadata_only_internal_LOOCV_control |          162 |           14 |          148 |                    0.655405 |                    0.142849 |          0.759259 |                   0.544884 |
| flare_vs_healthy | real_result | metadata_only_internal_LOOCV_control |          112 |           14 |           98 |                    0.940962 |                    0.836111 |          0.928571 |                   0.867347 |

Boundary: internal-only metadata control. No clinical claim. No external validation claim. No diagnostic claim. No deployment claim.

### Confounding audit

Status: real_result

Full CELLxGENE obs metadata was used for an internal descriptive confounding audit.

Boundary: internal-only descriptive audit. No clinical claim. No external validation claim. No diagnostic claim. No deployment claim.

### Geneformer perturbation

Status: scaffold_only

Reason: real perturbation requires upstream Geneformer-level perturbation before embedding extraction.

### Random gene-set controls

Status: scaffold_only

Reason: real random gene-set controls require real perturbation score-shift outputs first.
