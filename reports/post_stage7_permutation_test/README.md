# Stage 7 permutation-label negative control

Permutation testing is an internal negative-control analysis only. It does not constitute external validation, clinical validation, or evidence of clinical diagnostic utility.

Internal negative-control only.

Under patient-level label permutation, AUROC is expected to approach chance.
This supports that the observed internal LOOCV result is not trivially reproduced after destroying label-feature association.

- Status: completed
- Embedding directory: `<external-local-artifact:all_embeddings>`
- Output directory: `reports/post_stage7_permutation_test`
- Label shuffle unit: patient
- Patient identity preserved: true
- Split policy: leave-one-patient-out
- Scaler fit scope: train fold only
- Model fit scope: train fold only
- Geneformer execution: not run
- Embedding extraction: not run

## Summary

| task | observed_auroc_internal_loocv | n_permutations | permutation_mean_auroc | empirical_p_value |
| --- | ---: | ---: | ---: | ---: |
| flare_vs_managed | 0.996165 | 100 | 0.483135 | 0.009901 |
| flare_vs_healthy | 0.992711 | 100 | 0.472566 | 0.009901 |
