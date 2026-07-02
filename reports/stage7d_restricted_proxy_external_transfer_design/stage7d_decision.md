# Stage 7D decision

## Final decision

Proceed to implementation only as a restricted proxy external transfer evaluation.

`GSE135779` is approved for:

- high-activity versus low-activity SLE proxy scoring;
- frozen external transfer analysis;
- SLEDAI-thresholded activity evaluation.

`GSE135779` is not approved for:

- strict FLARE-versus-managed SLE external validation;
- training or tuning using external labels;
- threshold selection using external labels;
- claiming that low SLEDAI equals managed SLE.

## Primary endpoint

| Class | Definition | Count from Stage 7C parse |
|---|---|---:|
| Positive | SLEDAI > 4 | 16 |
| Negative | SLEDAI <= 4 | 23 |
| Excluded by default | missing explicit SLEDAI | 2 |

## Primary model policy

Use the frozen Stage 6 primary scoring pipeline if all required objects are available:

1. Geneformer embeddings;
2. donor/sample mean aggregation;
3. internally fitted PCA(20);
4. internally fitted balanced logistic regression;
5. frozen internal threshold only for thresholded metrics.

If any frozen model object is unavailable, Stage 7D implementation must stop and first create a reproducible model artifact export from Stage 6.

## Minimum implementation deliverables for next stage

Before running external scoring, create:

1. GSE135779 sample manifest with sample ID, group, SLEDAI, proxy label, exclusion reason;
2. frozen Stage 6 model artifact manifest;
3. external embedding generation manifest;
4. scoring script that does not fit anything on external labels;
5. final report separating continuous metrics from thresholded metrics;
6. explicit caveat language in every result summary.

## Stage handoff

Stage 7D is complete as a design gate. The next stage may be an implementation stage only if the project accepts proxy external transfer rather than strict external validation.
