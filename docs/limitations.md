# Limitations and Next Steps

## Scope

This repository currently supports research-stage internal benchmarking of patient-level Geneformer embeddings for active SLE flare discrimination.

The current results are internal leave-one-patient-out cross-validation results only.

## Current limitations

### 1. Small active flare class

The active flare group contains 14 patients. This limits the stability of performance estimates, especially sensitivity and confidence intervals.

### 2. No independent external validation

The current Stage 7 results do not include an independent external validation cohort.

External validation is required before making claims about generalization to other cohorts, protocols, sequencing platforms, or clinical settings.

### 3. Cross-sectional task definition

The current task is active flare discrimination at the time of sampling.

It is not longitudinal flare forecasting and should not be described as future flare prediction.

### 4. Potential cohort and batch confounding

The current analysis requires deeper assessment of technical and cohort-level confounding, including:

- data source effects
- processing cohort effects
- donor-level metadata imbalance
- cell-count differences
- cell-type composition differences

### 5. Demographic and clinical covariates

Sex, ancestry, age, treatment status, disease duration, medication exposure, and other clinical covariates may affect model behavior.

The current repository does not yet provide a complete covariate-adjusted analysis.

### 6. Baseline comparison

Strong internal performance from Geneformer embeddings must be compared against simpler representations, including:

- raw or pseudobulk expression baselines
- PCA-based baselines
- cell-type composition baselines
- metadata-only or batch/source baselines where available

This is required to determine whether frozen foundation-model embeddings provide incremental value.

## Embedding interpretation boundary

The downstream classifier operates on frozen Geneformer-derived patient embeddings, not raw gene-level features. Therefore, logistic-regression coefficients, embedding-dimension weights, or SHAP values computed on the downstream classifier must not be interpreted as gene-level importance or as identification of lupus-associated genes.

Gene-level biological plausibility requires upstream Geneformer-level analysis, such as in silico gene or gene-program perturbation before embedding extraction, followed by re-embedding and fixed-classifier re-scoring. Any such analysis would provide mechanistic plausibility support only, not external validation or clinical validation.

### 7. Mechanistic interpretation

The current Stage 7 evaluation is primarily predictive.

Further work is needed to connect model behavior to biological mechanisms through:

- cell-type contribution analysis
- gene-set or pathway enrichment
- perturbation or sensitivity analysis
- network-level interpretation

### 8. Clinical claim boundary

The repository does not support claims of:

- diagnostic readiness
- clinical deployment
- clinical decision support
- treatment recommendation
- prospective flare prediction
- external generalization

## Gene masking boundary

Gene masking is not a valid operation on the downstream logistic-regression classifier because that classifier receives fixed Geneformer-derived patient embeddings, not raw gene tokens or expression features.

Any gene masking, gene-program masking, or in silico perturbation must be performed upstream before Geneformer embedding extraction. The correct workflow is: perturb raw/tokenized gene input, recompute Geneformer embeddings, keep the downstream classifier fixed, and compare prediction-score shifts.

Results from this workflow may support biological plausibility only. They must not be described as direct logistic-regression gene importance, external validation, or clinical validation.

## Next scientific steps

Recommended next steps:

1. run expanded confounding and robustness controls
2. compare Geneformer embeddings against simpler baselines
3. audit external validation candidates
4. add pathway-level and cell-type-level interpretation
5. report all results with conservative claim boundaries

## Current claim boundary

The current repository supports the following research-stage statement:

> Frozen Geneformer patient-level embeddings show strong internal leave-one-patient-out discrimination of active SLE flare status in an exploratory PBMC single-cell cohort.

No stronger clinical or external-validation claim is supported at this stage.
