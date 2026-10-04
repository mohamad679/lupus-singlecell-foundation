# Stage 7 Geneformer-level perturbation plausibility scaffold

Geneformer-level perturbation plausibility analysis is hypothesis-generating only. It does not constitute external validation, clinical validation, causal validation, or evidence of clinical diagnostic utility.

This scaffold is for biological plausibility assessment only.
This is not downstream LR/SHAP gene interpretation.
Do not interpret downstream logistic regression coefficients as gene importance.
Do not use SHAP on downstream embedding dimensions as gene-level interpretation.
Perturbation must happen upstream before embedding extraction.
Correct execution path: raw/tokenized gene input -> gene/gene-program perturbation -> recompute Geneformer embeddings -> apply fixed downstream classifier -> compare prediction-score shifts.
Do not perform gene masking on the fixed patient-level embedding table.
The downstream classifier must remain fixed.
Score shifts are plausibility signals only.
Real execution requires a Geneformer-capable environment and recomputation of embeddings.
Synthetic dry-run outputs, if any, are not biological results.
Geneformer-level perturbation does not constitute causal validation.
Geneformer-level perturbation does not constitute clinical validation.
Geneformer-level perturbation does not constitute external validation.

- Status: plan_only
- Output directory: `reports/post_stage7_geneformer_perturbation_plausibility`
- Upstream perturbation API available in repo: false
- Extraction callback fields inspected: load_anndata, sample_cells, tokenize_cells, embed_tokens, write_artifacts
- Downstream classifier policy: fixed downstream classifier only
- Real Geneformer perturbation run: false
- Real embeddings recomputed: false
- Synthetic score-shift rows written: 0

## TODO / Blocker

No safe upstream Geneformer perturbation API is implemented in this repository. Real Geneformer-level perturbation must run in a controlled cloud/GPU environment that perturbs raw or tokenized gene input before embedding extraction, recomputes embeddings, and then applies the fixed downstream classifier without refitting.

## Output Notes

- `perturbation_plan.csv` is a planning artifact only.
- `perturbation_score_shift_schema.csv` is an empty schema in plan-only mode.
- `perturbation_score_shift_schema.csv` contains synthetic placeholder rows in synthetic dry-run mode.
