# Corrected V1 reanalysis runbook

1. Start from the historical commit and keep all old artifacts immutable.
   Use the correction branch and a new output directory. The scripts under
   `kaggle_kernels/l2_geneformer_v1_corrected_*` are **new**; the original
   `l2_geneformer_full` and `l2_geneformer_sealed` scripts remain historical.
2. Make `results/gene_space_intersection.txt` available to each Kaggle job
   as `/kaggle/input/lupus-correction/gene_space_intersection.txt`, or set
   `GENE_INTERSECTION_PATH` to its location. Its required SHA-256 is
   `482f113c433ac76eb19940442e4f3b1a24ae73d387c4ec75ecb19b8116eea29b`.
3. Run a small, real-cell fixture through the V1 tokenizer and extractor on
   GPU. Confirm the run summary reports V1, `emb_mode=cell`, nonempty token
   sequences, exact donor/cell retention, finite embeddings, and checkpoint
   hashes. Do not start the complete run if this fails.
4. Run `kaggle_kernels/l2_geneformer_v1_corrected_dev/run.py` and
   `kaggle_kernels/l2_geneformer_v1_corrected_external/run.py` with
   `GENE_INPUT_MODE=shared`. Save both parquet files and JSON summaries. Repeat
   with `GENE_INPUT_MODE=native` for the sensitivity analysis. These jobs need
   Census/GEO network access and GPU compute.
5. Download the four outputs for each mode. For shared mode, run:

   ```bash
   python scripts/28_corrected_geneformer_scoring.py \
     --dev-embeddings PATH_TO_DEV_PARQUET \
     --external-embeddings PATH_TO_EXTERNAL_PARQUET \
     --dev-summary PATH_TO_DEV_SUMMARY \
     --external-summary PATH_TO_EXTERNAL_SUMMARY \
     --mode shared
   python scripts/27_correction_analysis.py \
     --predictions results/correction_2026-09/corrected_v1_shared_predictions.json \
     --output results/correction_2026-09/corrected_v1_shared_analysis.json
   ```

6. Repeat step 5 with `--mode native` and distinct output paths. Check that
   both summaries name the same checkpoint hashes and source revision, that
   the donor order and embedding columns match, and that no output reports a
   failed or partial extraction.
7. Update the Word manuscript, supplement, and figures from the final JSON
   only. Keep the released historical result table and explain the
   post-hoc correction and already examined external cohort.

The Kaggle jobs have not been executed in this checkout. The pinned source
revision is documented, but full runtime dependency compatibility and raw-
data-to-embedding behavior require the small fixture before a full run.
