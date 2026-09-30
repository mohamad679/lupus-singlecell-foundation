#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
results="results/correction_2026-09"
scoring=(uv run --offline --no-project --with-requirements requirements_correction_scoring.txt python)
plotting=(uv run --offline --no-project --with-requirements requirements_correction_scoring.txt --with matplotlib==3.11.2 python)

for mode in shared native; do
  "${scoring[@]}" scripts/28_corrected_geneformer_scoring.py \
    --dev-embeddings "$results/${mode}_features/l2_dev_geneformer_v1_${mode}_embeddings.parquet" \
    --external-embeddings "$results/${mode}_features/l2_sealed_geneformer_v1_${mode}_embeddings.parquet" \
    --dev-summary "$results/${mode}_features/l2_dev_geneformer_v1_${mode}_run_summary.json" \
    --external-summary "$results/${mode}_features/l2_sealed_geneformer_v1_${mode}_run_summary.json" \
    --mode "$mode" --output-dir "$results"
  "${scoring[@]}" scripts/27_correction_analysis.py \
    --predictions "$results/corrected_v1_${mode}_predictions.json" \
    --output "$results/corrected_v1_${mode}_analysis.json"
done

"${scoring[@]}" scripts/29_gene_input_sensitivity.py \
  --shared-predictions "$results/corrected_v1_shared_predictions.json" \
  --native-predictions "$results/corrected_v1_native_predictions.json" \
  --output "$results/corrected_v1_gene_input_sensitivity.json"
"${scoring[@]}" scripts/30_corrected_descriptive.py
"${plotting[@]}" scripts/31_corrected_cohort_probe.py
"${plotting[@]}" scripts/32_corrected_figures.py

printf 'Corrected feature-to-figure run completed. Run the focused tests and inspect the versioned JSON/figures.\n'
