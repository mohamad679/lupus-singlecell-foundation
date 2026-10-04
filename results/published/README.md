# Published corrected results

This directory is the authoritative v2.0.0 result package used by the reviewer-facing reproduction workflow.

Key files:

- `corrected_v1_shared_analysis.json` — primary corrected shared-gene external analysis.
- `corrected_v1_native_analysis.json` — model-native sensitivity analysis.
- `corrected_v1_descriptive.json` — donor-bootstrap descriptive intervals and age-stratified summaries.
- `corrected_v1_gene_input_sensitivity.json` — paired shared-versus-native sensitivity analysis.
- `corrected_v1_shared_cohort_probe.json` — post-hoc cohort-membership diagnostic.
- `corrected_artifact_manifest.json` — provenance/checksum manifest.
- `shared_features/` and `native_features/` — validated corrected Geneformer feature artifacts and run summaries.

The primary shared-gene external AUROCs are Geneformer V1 0.734375, pseudobulk 0.8984375, and age only 0.578125.
