# Limitations

## Scope of the corrected analysis

Version 2.0.0 reports a corrected reanalysis of donor-level SLE-versus-healthy classification using corrected Geneformer V1 embeddings, pseudobulk expression, and age-only baselines. The external cohort had already been examined before this corrected analysis; it is therefore not a newly untouched confirmatory cohort.

## 1. External cohort was previously examined

The strongest design limitation is that GSE135779 was not untouched at the time of the corrected Geneformer V1 rerun. The corrected external estimates are valid as a versioned reanalysis of the same donor set, but they should not be described as a new independent confirmatory validation.

## 2. Small external sample size

The external analysis contains 56 samples (40 SLE, 16 healthy). Bootstrap uncertainty remains substantial, especially in the source-defined adult subgroup (n=12; 7 SLE, 5 healthy). Subgroup results are descriptive and should not be overinterpreted.

## 3. Cohort shift and confounding

Development and external cohorts differ substantially in age structure and other acquisition/context characteristics. The corrected shared-gene cohort-membership diagnostic shows strong separability of cohort origin, so disease-discrimination performance cannot be interpreted as isolated from cohort/batch/platform structure.

## 4. Age-group labels are source-defined

The external source category `Children` includes some participants aged 18–19. Age-stratified analyses therefore follow source metadata categories and are not a clean pediatric-versus-adult causal comparison.

## 5. Gene-space dependence

The primary corrected Geneformer analysis uses a validated shared-gene representation. A model-native representation is reported as a sensitivity analysis. Differences between these representations quantify input-definition sensitivity on the same donors; they do not constitute independent replication.

## 6. Pseudobulk comparator and historical protocol choices

The pseudobulk comparator retains historical preprocessing and model-selection choices needed for faithful comparison with the corrected Geneformer analysis. Relevant historical deviations and frozen-protocol decisions are preserved in `docs/provenance/` rather than silently rewritten.

## 7. No prospective or clinical validation

The repository does not establish:

- diagnostic readiness,
- prospective prediction,
- treatment-response prediction,
- clinical decision support,
- clinical deployment,
- generalization to other cohorts or platforms.

## 8. Embedding interpretation boundary

The downstream classifier operates on donor-level Geneformer embeddings rather than directly interpretable gene coefficients. Downstream logistic-regression weights must not be presented as gene-level biological importance. Mechanistic interpretation would require separate upstream perturbation experiments and independent validation.

## 9. Reproduction boundary

The one-command CPU workflow reproduces the corrected donor-level scoring, statistics, diagnostics, and figures from committed, provenance-checked feature artifacts. It does not repeat raw single-cell download or the multi-hour GPU extraction. The extraction pathway and runtime provenance are preserved separately in `notebooks/extraction/` and the run-summary artifacts.

## Follow-up evidence needed

A stronger confirmatory study would require a genuinely new independent cohort evaluated under a prospectively frozen analysis plan, ideally with reduced cohort/platform confounding and adequate sample size for subgroup analysis.
