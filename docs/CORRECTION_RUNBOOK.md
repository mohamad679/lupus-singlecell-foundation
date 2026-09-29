# Corrected V1 reanalysis runbook

## Kaggle GPU notebooks (current execution path)

Four self-contained notebooks are in the parent `lupuspaper` folder. Run each
in a separate Kaggle GPU session with Internet enabled, in this order:

The development/shared, external/shared, and development/native ZIPs have
passed local validation. Use the uniquely named
`Lupus_Kaggle_External_Native_Complete.ipynb` copy for the final extraction
run so Kaggle does not reuse an older notebook upload. It is identical to the
fourth notebook below.

1. `CBC_Kaggle_1_Development_Shared.ipynb`
2. `CBC_Kaggle_2_External_Shared.ipynb`
3. `CBC_Kaggle_3_Development_Native.ipynb`
4. `CBC_Kaggle_4_External_Native.ipynb`

Each notebook contains five numbered code cells: stage checksum-verified code
and the shared-gene list; install/verify the pinned Geneformer source and GPU;
run an eight-cell synthetic V1 technical fixture; run exactly one cohort/mode;
verify and package results. Run them in order or use Kaggle's Save & Run All.
Stop and share the error if the fixture or a cohort cell fails. The synthetic
fixture checks tokenizer/extractor compatibility; each full cohort run then
checks its real-cell IDs, donors, counts, token sequences, and finite outputs.
The fixture now asserts that Datasets mapping stays in the main process and
repeats tokenization after GPU embedding. In the pinned Geneformer tokenizer,
`nproc=1` still causes a one-worker `Dataset.map`; the corrected runners use
`nproc=None` for tokenization to prevent the TBB fork failure seen on the
second development batch. Cell 4 requires the updated fixture summary.
The first Kaggle attempt exposed a `boto3`/`botocore` import mismatch before
tokenization. The rebuilt notebooks pin compatible AWS package versions in
Cell 2 and import Geneformer there, so this failure is caught before Cell 3.

The cohort scripts keep large raw matrices and temporary embeddings under
`/kaggle/temp/lupus-correction`. Final donor parquet, JSON summary, a small
fixture summary, a share ZIP, and per-batch checkpoints are written under
`/kaggle/working`. Kaggle preserves that working directory with saved notebook
outputs, while scratch files are temporary. Each completed batch gets a
checksum-verified checkpoint. If a run is interrupted within a session,
rerunning its cohort cell reuses those batches. To resume from a previously
saved Kaggle version, attach its output as notebook input and set `RESUME_INPUT`
in Cell 4 to its `correction_checkpoints/<cohort>_<mode>` directory. The
checkpoint loader rejects changes to the data mode, source revision, model
files, donor set, cell counts, or parquet checksum. It accepts only explicitly
listed prior correction-script hashes when every other field matches, allowing
a completed batch to survive a multiprocessing-only code repair.

After Cell 5, download `lupus_correction_external_native_share.zip` for the
native-input sensitivity analysis. Rebuild the notebooks with
`python scripts/33_build_kaggle_notebooks.py --output-dir ..` if their source
changes.

## VS Code with a Google Colab GPU

The prepared notebook is
`../CBC_Correction_Colab_GPU.ipynb` (relative to this repository). Open it in
VS Code, select the **Colab** kernel, sign in, and choose a GPU runtime. Run
the numbered code cells in order. The first cell stages exact copies of the
correction scripts and shared-gene list with checksum checks; the next installs
Geneformer, and the third mounts Google Drive for persistent outputs. The
fourth cell runs an eight-cell synthetic V1 tokenizer and extractor fixture.
Continue to the cohort cells only if `fixture_summary.json` reports
`"status": "pass"`. This fixture checks technical compatibility; it cannot
verify Census/GEO access or cohort-specific preprocessing.

The notebook saves four parquet files and four JSON summaries to
`MyDrive/lupus-correction-2026-09`. Keep the runtime connected until each
cohort cell prints its archive confirmation. Download these eight files into
the local correction results folder, then use the scoring commands below.
The notebook can be rebuilt after a script change with
`python scripts/32_build_colab_notebook.py --output ../CBC_Correction_Colab_GPU.ipynb`.

## Extraction and scoring gates

1. Start from the historical commit and keep all old artifacts immutable.
   Use the correction branch and a new output directory. The scripts under
   `kaggle_kernels/l2_geneformer_v1_corrected_*` are **new**; the original
   `l2_geneformer_full` and `l2_geneformer_sealed` scripts remain historical.
2. Make `results/gene_space_intersection.txt` available to each Kaggle job
   as `/kaggle/input/lupus-correction/gene_space_intersection.txt`, or set
   `GENE_INTERSECTION_PATH` to its location. Its required SHA-256 is
   `482f113c433ac76eb19940442e4f3b1a24ae73d387c4ec75ecb19b8116eea29b`.
3. Run the eight-cell synthetic V1 fixture on GPU, then check the first real
   cohort batch before proceeding. Confirm V1, `emb_mode=cell`, nonempty token
   sequences, exact donor/cell retention, finite embeddings, and checkpoint
   hashes. Stop if either validation fails.
4. Run `kaggle_kernels/l2_geneformer_v1_corrected_dev/run.py` and
   `kaggle_kernels/l2_geneformer_v1_corrected_external/run.py` with
   `GENE_INPUT_MODE=shared`. Save both parquet files and JSON summaries. Repeat
   with `GENE_INPUT_MODE=native` for the sensitivity analysis. These jobs need
   Census/GEO network access and GPU compute.
5. Download the four outputs for each mode. For shared mode, run:

   ```bash
   uv run --no-project --with-requirements requirements_correction_scoring.txt \
     python scripts/28_corrected_geneformer_scoring.py \
     --dev-embeddings PATH_TO_DEV_PARQUET \
     --external-embeddings PATH_TO_EXTERNAL_PARQUET \
     --dev-summary PATH_TO_DEV_SUMMARY \
     --external-summary PATH_TO_EXTERNAL_SUMMARY \
     --mode shared
   uv run --no-project --with-requirements requirements_correction_scoring.txt \
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

The development/shared, external/shared, and development/native jobs were run
on Kaggle and their ZIPs passed local fixture, provenance, cohort accounting,
and embedding-table checks. The external/native job remains pending.
