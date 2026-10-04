# Stage 7 random gene-set controls

Random gene-set controls for Geneformer-level perturbation are hypothesis-generating controls only. They do not constitute causal validation, external validation, clinical validation, or evidence of clinical diagnostic utility.

This scaffold prepares size-matched random gene-set controls for a future empirical null comparison.
It is a hypothesis-generating control only.
Upstream Geneformer-level perturbation required before any score-shift analysis.
The downstream classifier must remain fixed; no refit is allowed.
Do not perturb fixed patient-level embeddings.
Do not interpret downstream LR coefficients as gene importance.
Do not use SHAP on embedding dimensions as gene-level interpretation.
Synthetic dry-run rows, if present, are synthetic output only and not biological results.
No causal validation, clinical validation, or external validation is performed here.

- Status: plan_only
- Output directory: `reports/post_stage7_random_gene_set_controls`
- Upstream perturbation API available in repo: false
- Extraction callback fields inspected: load_anndata, sample_cells, tokenize_cells, embed_tokens, write_artifacts
- Real Geneformer perturbation run: false
- Real embeddings recomputed: false
- Downstream classifier fixed: true
- Synthetic random control rows written: 0

## TODO / Blocker

TODO: define the Geneformer token gene universe and any token-availability filters before sampling real size-matched random gene-set controls. No safe upstream Geneformer perturbation API is implemented in this repository. Real Geneformer-level perturbation must run in a controlled cloud/GPU environment that perturbs raw or tokenized gene input before embedding extraction, recomputes embeddings, and then applies the fixed downstream classifier without refitting.

## Output Notes

- `random_gene_set_control_plan.csv` is a planning artifact only.
- `random_gene_set_control_schema.csv` is header-only in plan-only mode.
- `random_gene_set_control_schema.csv` contains toy deterministic controls in synthetic dry-run mode.
- `random_gene_set_control_summary_schema.csv` is a schema only; no real score-shift metrics are written.
