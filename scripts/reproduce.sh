#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
published="$repo_root/results/published"
offline=0
output=""
while (($#)); do
  case "$1" in
    --offline) offline=1; shift ;;
    --output-dir) output="$2"; shift 2 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
  esac
done
if [[ -z "$output" ]]; then
  mkdir -p "$repo_root/reproductions"
  output="$(mktemp -d "$repo_root/reproductions/publication-XXXXXXXX")"
fi
mkdir -p "$output"
output="$(cd "$output" && pwd)"
if [[ "$output" == "$published" || "$output" == "$repo_root/results" ]]; then
  printf 'Refusing to write over published results: %s\n' "$output" >&2
  exit 2
fi

uv_options=(--python 3.11.15 --no-project --with-requirements requirements.txt)
if ((offline)); then uv_options+=(--offline); fi
py=(uv run "${uv_options[@]}" python)

for mode in shared native; do
  "${py[@]}" scripts/01_score_corrected_models.py \
    --dev-embeddings "$published/${mode}_features/l2_dev_geneformer_v1_${mode}_embeddings.parquet" \
    --external-embeddings "$published/${mode}_features/l2_sealed_geneformer_v1_${mode}_embeddings.parquet" \
    --dev-summary "$published/${mode}_features/l2_dev_geneformer_v1_${mode}_run_summary.json" \
    --external-summary "$published/${mode}_features/l2_sealed_geneformer_v1_${mode}_run_summary.json" \
    --mode "$mode" --output-dir "$output"
  "${py[@]}" scripts/02_statistical_analysis.py \
    --predictions "$output/corrected_v1_${mode}_predictions.json" \
    --output "$output/corrected_v1_${mode}_analysis.json"
done

"${py[@]}" scripts/03_gene_input_sensitivity.py \
  --shared-predictions "$output/corrected_v1_shared_predictions.json" \
  --native-predictions "$output/corrected_v1_native_predictions.json" \
  --output "$output/corrected_v1_gene_input_sensitivity.json"
"${py[@]}" scripts/04_descriptive_statistics.py --correction-dir "$output"
"${py[@]}" scripts/05_cohort_probe.py --feature-root "$published" --output-dir "$output"
"${py[@]}" scripts/06_generate_figures.py --results-dir "$output" --output-dir "$output/figures"
"${py[@]}" scripts/07_compare_reproduction.py --published "$published" --rerun "$output"

printf 'Independent corrected rerun passed: %s\n' "$output"
