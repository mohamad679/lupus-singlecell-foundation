"""Sealed-cohort (GSE135779) Geneformer embedding extraction: all 56 real
deposited samples (33 cSLE + 11 cHD + 7 aSLE + 5 aHD), using the EXACT
frozen config already used and verified for the dev cohort (per FREEZE.json
and kaggle_kernels/l2_geneformer_full/l2_geneformer_full.py): Geneformer-V1-10M,
model_input_size=2048, emb_mode="cls", emb_layer=-1, forward_batch_size=32,
emb_label=["cell_id","donor_id"], transformers pinned >=4.35,<4.50.

This is real data from the public GEO deposit (GSE135779_RAW.tar,
downloaded directly from NCBI FTP within this kernel), processed in
cell-count-balanced batches with real per-batch throughput logged, exactly
mirroring the dev full-extraction kernel's structure and its two real,
previously-fixed bugs (Categorical dtype artifact -- not applicable here,
donor_id is built fresh per batch from a plain Python list, not a census
Categorical column; emb_label required for cell_id/donor_id to survive into
the embeddings output).

mean_pool_per_donor: per-cell CLS embeddings are mean-pooled to one vector
per sample (donor) immediately after each batch, then discarded -- no
attempt to hold all ~363,083 sealed cells' embeddings in memory at once.

Writes:
- /kaggle/working/l2_sealed_geneformer_embeddings.parquet (56 x 256)
- /kaggle/working/l2_sealed_geneformer_run_summary.json
"""

import json
import os
import shutil
import subprocess
import sys
import time
import traceback

MODEL_SUBDIR = "Geneformer-V1-10M"
GENES_URL = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE135nnn/GSE135779/suppl/GSE135779_genes.tsv.gz"
RAW_TAR_URL = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE135nnn/GSE135779/suppl/GSE135779_RAW.tar"
N_BATCHES_TARGET = 6

# [gsm_id, title, age, age_group, group] for all 56 real deposited samples,
# parsed from GSE135779's public family SOFT metadata record (Phase 2
# pre-flight, verified 2026-07-20/21).
SAMPLE_META = [["GSM4029896", "cSLE1 [JB17001]", 17, "Children", "SLE"], ["GSM4029897", "cSLE2 [JB17002]", 18, "Children", "SLE"], ["GSM4029898", "cSLE3 [JB17003]", 16, "Children", "SLE"], ["GSM4029899", "cSLE4 [JB17004]", 17, "Children", "SLE"], ["GSM4029900", "cSLE5 [JB17005]", 14, "Children", "SLE"], ["GSM4029901", "cSLE6 [JB17006]", 16, "Children", "SLE"], ["GSM4029902", "cSLE7 [JB17007]", 17, "Children", "SLE"], ["GSM4029903", "cSLE8 [JB17008]", 16, "Children", "SLE"], ["GSM4029904", "cSLE10 [JB17015]", 18, "Children", "SLE"], ["GSM4029905", "cSLE11 [JB17016]", 17, "Children", "SLE"], ["GSM4029906", "cSLE9 [JB17014]", 16, "Children", "SLE"], ["GSM4029907", "cHD1 [JB17010]", 7, "Children", "HD"], ["GSM4029908", "cSLE12 [JB17019]", 18, "Children", "SLE"], ["GSM4029909", "cSLE13 [JB17020]", 12, "Children", "SLE"], ["GSM4029910", "cSLE14 [JB17021]", 19, "Children", "SLE"], ["GSM4029911", "cSLE15 [JB17022]", 12, "Children", "SLE"], ["GSM4029912", "cSLE16 [JB17023]", 13, "Children", "SLE"], ["GSM4029913", "cSLE17 [JB17024]", 18, "Children", "SLE"], ["GSM4029914", "cHD2 [JB17017]", 8, "Children", "HD"], ["GSM4029915", "cHD3 [JB17018]", 13, "Children", "HD"], ["GSM4029916", "cSLE18 [JB18063]", 17, "Children", "SLE"], ["GSM4029917", "cSLE19 [JB18064]", 16, "Children", "SLE"], ["GSM4029918", "cSLE20 [JB18065]", 16, "Children", "SLE"], ["GSM4029919", "cSLE21 [JB18066]", 13, "Children", "SLE"], ["GSM4029920", "cSLE22 [JB18067]", 17, "Children", "SLE"], ["GSM4029921", "cSLE23 [JB18068]", 17, "Children", "SLE"], ["GSM4029922", "cHD4 [JB18069]", 16, "Children", "HD"], ["GSM4029923", "cHD5 [JB18070]", 12, "Children", "HD"], ["GSM4029924", "cSLE24 [JB18071]", 13, "Children", "SLE"], ["GSM4029925", "cSLE25 [JB18072]", 16, "Children", "SLE"], ["GSM4029926", "cSLE26 [JB18073]", 17, "Children", "SLE"], ["GSM4029927", "cSLE27 [JB18074]", 15, "Children", "SLE"], ["GSM4029928", "cSLE28 [JB18075]", 18, "Children", "SLE"], ["GSM4029929", "cSLE29 [JB18076]", 14, "Children", "SLE"], ["GSM4029930", "cHD6 [JB18077]", 14, "Children", "HD"], ["GSM4029931", "cHD7 [JB18078]", 8, "Children", "HD"], ["GSM4029932", "cSLE30 [JB18079]", 10, "Children", "SLE"], ["GSM4029933", "cSLE31 [JB18080]", 17, "Children", "SLE"], ["GSM4029934", "cSLE32 [JB18081]", 16, "Children", "SLE"], ["GSM4029935", "cSLE33 [JB18082]", 17, "Children", "SLE"], ["GSM4029936", "cHD10 [JB18085]", 18, "Children", "HD"], ["GSM4029937", "cHD11 [JB18086]", 17, "Children", "HD"], ["GSM4029938", "cHD8 [JB18083]", 8, "Children", "HD"], ["GSM4029939", "cHD9 [JB18084]", 14, "Children", "HD"], ["GSM4029940", "aHD1 [JB19001]", 39, "Adult", "HD"], ["GSM4029942", "aHD3 [JB19003]", 50, "Adult", "HD"], ["GSM4029943", "aSLE1 [JB19004]", 37, "Adult", "SLE"], ["GSM4029944", "aSLE2 [JB19006]", 63, "Adult", "SLE"], ["GSM4029945", "aSLE3 [JB19007]", 36, "Adult", "SLE"], ["GSM4029946", "aSLE4 [JB19008]", 58, "Adult", "SLE"], ["GSM4029947", "aHD4 [JB19009]", 36, "Adult", "HD"], ["GSM4029948", "aHD5 [JB19010]", 46, "Adult", "HD"], ["GSM4029949", "aHD6 [JB19011]", 47, "Adult", "HD"], ["GSM4029950", "aSLE5 [JB19013]", 24, "Adult", "SLE"], ["GSM4029951", "aSLE6 [JB19014]", 27, "Adult", "SLE"], ["GSM4029952", "aSLE7 [JB19015]", 47, "Adult", "SLE"]]


def log(msg):
    print(f"[l2-geneformer-sealed] {msg}", flush=True)


def run(cmd):
    log(f"$ {cmd}")
    subprocess.run(cmd, shell=True, check=True)


log("installing dependencies")
run(f"{sys.executable} -m pip install -q git+https://huggingface.co/ctheodoris/Geneformer.git")
run(f"{sys.executable} -m pip install -q huggingface_hub anndata scipy")
run(f"{sys.executable} -m pip install -q 'transformers>=4.35,<4.50'")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import scipy.io  # noqa: E402
import scipy.sparse  # noqa: E402
import anndata as ad  # noqa: E402
from huggingface_hub import snapshot_download  # noqa: E402
from geneformer import TranscriptomeTokenizer, EmbExtractor  # noqa: E402

SUMMARY = {"batches": []}
donor_embeddings: dict[str, np.ndarray] = {}
donor_cell_counts_observed: dict[str, int] = {}

try:
    t_run_start = time.time()

    log("downloading GSE135779 public deposit (genes reference + raw counts archive)")
    os.makedirs("/kaggle/working/gse135779_raw", exist_ok=True)
    run(f"curl -s '{GENES_URL}' -o /kaggle/working/gse135779_raw/genes.tsv.gz")
    run(f"gunzip -f /kaggle/working/gse135779_raw/genes.tsv.gz")
    run(f"curl -s '{RAW_TAR_URL}' -o /kaggle/working/gse135779_raw/GSE135779_RAW.tar")
    os.makedirs("/kaggle/working/gse135779_raw/extracted", exist_ok=True)
    run(f"tar -xf /kaggle/working/gse135779_raw/GSE135779_RAW.tar "
        f"-C /kaggle/working/gse135779_raw/extracted")

    n_extracted = len(os.listdir("/kaggle/working/gse135779_raw/extracted"))
    log(f"extracted {n_extracted} files (expected 112 = 56 samples x 2 files)")
    assert n_extracted == 112, f"expected 112 files, got {n_extracted}"

    gene_ids = []
    with open("/kaggle/working/gse135779_raw/genes.tsv") as f:
        for line in f:
            gene_ids.append(line.rstrip("\n").split("\t")[0])
    n_genes_ref = len(gene_ids)
    log(f"gene reference: {n_genes_ref} genes (expected 32738)")
    assert n_genes_ref == 32738, f"expected 32738 genes, got {n_genes_ref}"

    all_gsm_ids = [m[0] for m in SAMPLE_META]
    assert len(all_gsm_ids) == 56, f"expected 56 samples, got {len(all_gsm_ids)}"

    def find_files(gsm_id):
        extracted_dir = "/kaggle/working/gse135779_raw/extracted"
        matrix = [f for f in os.listdir(extracted_dir) if f.startswith(gsm_id) and f.endswith("matrix.mtx.gz")]
        assert len(matrix) == 1, f"{gsm_id}: expected 1 matrix file, found {matrix}"
        return os.path.join(extracted_dir, matrix[0])

    # cell-count-balanced batching: need real per-sample cell counts first,
    # which requires reading each matrix's header (cheap: MatrixMarket
    # headers give n_genes/n_cells/nnz without reading the full matrix body).
    def peek_ncells(matrix_path):
        import gzip as gz
        with gz.open(matrix_path, "rt") as f:
            f.readline()  # %%MatrixMarket header
            line = f.readline()
            while line.startswith("%"):
                line = f.readline()
            n_g, n_c, nnz = line.split()
            return int(n_c)

    sample_ncells = {}
    for gsm_id, title, age, age_group, group in SAMPLE_META:
        sample_ncells[gsm_id] = peek_ncells(find_files(gsm_id))
    total_cells_expected = sum(sample_ncells.values())
    log(f"total sealed cells (real, from matrix headers): {total_cells_expected}")

    samples_by_count_desc = sorted(all_gsm_ids, key=lambda g: -sample_ncells[g])
    batches = [[] for _ in range(N_BATCHES_TARGET)]
    batch_loads = [0] * N_BATCHES_TARGET
    for gsm_id in samples_by_count_desc:
        i = batch_loads.index(min(batch_loads))
        batches[i].append(gsm_id)
        batch_loads[i] += sample_ncells[gsm_id]
    batches = [b for b in batches if b]
    for i, b in enumerate(batches):
        log(f"batch {i}: {len(b)} samples, {sum(sample_ncells[g] for g in b)} cells")

    log(f"downloading {MODEL_SUBDIR} pretrained model")
    model_dir = snapshot_download(repo_id="ctheodoris/Geneformer", allow_patterns=[f"{MODEL_SUBDIR}/*"])
    model_path = f"{model_dir}/{MODEL_SUBDIR}"

    WORK = "/kaggle/working/gf_sealed_batches"
    os.makedirs(WORK, exist_ok=True)
    cumulative_cells = 0

    for batch_idx, batch_gsms in enumerate(batches):
        t_batch_start = time.time()
        batch_dir = f"{WORK}/batch_{batch_idx}"
        os.makedirs(f"{batch_dir}/input", exist_ok=True)
        os.makedirs(f"{batch_dir}/tokenized", exist_ok=True)
        os.makedirs(f"{batch_dir}/emb", exist_ok=True)

        # build one combined AnnData for this batch of samples
        mats = []
        cell_donor_ids = []
        cell_ids = []
        for gsm_id in batch_gsms:
            matrix_path = find_files(gsm_id)
            mat = scipy.io.mmread(matrix_path).tocsr()  # genes x cells
            mat = mat.T.tocsr()  # cells x genes, to match AnnData convention
            mats.append(mat)
            n_cells_this = mat.shape[0]
            cell_donor_ids.extend([gsm_id] * n_cells_this)
            cell_ids.extend([f"{gsm_id}_{i}" for i in range(n_cells_this)])
            donor_cell_counts_observed[gsm_id] = donor_cell_counts_observed.get(gsm_id, 0) + n_cells_this

        X = scipy.sparse.vstack(mats).tocsr()
        var_df = pd.DataFrame({"ensembl_id": gene_ids}, index=gene_ids)
        obs_df = pd.DataFrame({
            "cell_id": cell_ids,
            "donor_id": cell_donor_ids,
        })
        obs_df.index = cell_ids
        adata = ad.AnnData(X=X, obs=obs_df, var=var_df)
        adata.obs["n_counts"] = np.asarray(adata.X.sum(axis=1)).ravel()

        n_cells_batch = adata.n_obs
        adata.write_h5ad(f"{batch_dir}/input/batch.h5ad")
        del adata, X, mats

        tk = TranscriptomeTokenizer(
            custom_attr_name_dict={"cell_id": "cell_id", "donor_id": "donor_id"},
            nproc=2,
            model_input_size=2048,
        )
        tk.tokenize_data(
            data_directory=f"{batch_dir}/input",
            output_directory=f"{batch_dir}/tokenized",
            output_prefix="batch",
            file_format="h5ad",
        )

        embex = EmbExtractor(
            model_type="Pretrained",
            emb_mode="cls",
            max_ncells=None,
            emb_layer=-1,
            emb_label=["cell_id", "donor_id"],
            forward_batch_size=32,
            nproc=2,
        )
        embs = embex.extract_embs(
            model_directory=model_path,
            input_data_file=f"{batch_dir}/tokenized/batch.dataset",
            output_directory=f"{batch_dir}/emb",
            output_prefix="batch_embs",
        )

        emb_cols = [c for c in embs.columns if c not in ("cell_id", "donor_id")]
        grouped = embs.groupby("donor_id")[emb_cols].mean()
        for donor_id, row in grouped.iterrows():
            donor_embeddings[donor_id] = row.to_numpy(dtype=np.float64)

        batch_seconds = time.time() - t_batch_start
        cumulative_cells += n_cells_batch
        cumulative_seconds = time.time() - t_run_start
        batch_rate = n_cells_batch / batch_seconds
        running_rate = cumulative_cells / cumulative_seconds
        DEV_RATE = 76.34650884018772
        log(f"batch {batch_idx} done: {len(batch_gsms)} samples, {n_cells_batch} cells, "
            f"{batch_seconds:.1f}s, batch_rate={batch_rate:.2f} cells/sec "
            f"(dev full-run rate was {DEV_RATE:.2f}, ratio={batch_rate/DEV_RATE:.2f}x)")
        log(f"  progress: {100.0*cumulative_cells/total_cells_expected:.1f}% "
            f"({cumulative_cells}/{total_cells_expected} cells), "
            f"running_rate={running_rate:.2f} cells/sec")

        SUMMARY["batches"].append({
            "batch_idx": batch_idx, "n_samples": len(batch_gsms), "n_cells": int(n_cells_batch),
            "batch_seconds": batch_seconds, "batch_cells_per_sec": batch_rate,
            "cumulative_cells": cumulative_cells, "running_cells_per_sec": running_rate,
        })

        shutil.rmtree(batch_dir, ignore_errors=True)

    total_seconds = time.time() - t_run_start
    overall_rate = cumulative_cells / total_seconds
    log(f"ALL BATCHES DONE: {len(donor_embeddings)} samples, {cumulative_cells} cells, "
        f"{total_seconds:.1f}s, overall_rate={overall_rate:.2f} cells/sec")

    missing = set(all_gsm_ids) - set(donor_embeddings.keys())
    extra = set(donor_embeddings.keys()) - set(all_gsm_ids)
    mismatches = {
        g: {"expected": sample_ncells[g], "observed": donor_cell_counts_observed.get(g, 0)}
        for g in all_gsm_ids if sample_ncells[g] != donor_cell_counts_observed.get(g, 0)
    }

    SUMMARY.update({
        "status": "success",
        "n_samples_expected": 56,
        "n_samples_embedded": len(donor_embeddings),
        "total_cells_expected": total_cells_expected,
        "total_cells_processed": cumulative_cells,
        "total_seconds": total_seconds,
        "overall_cells_per_sec": overall_rate,
        "missing_samples": sorted(missing),
        "extra_samples": sorted(extra),
        "cell_count_mismatches": mismatches,
        "sample_cell_counts_expected": sample_ncells,
        "embedding_dim": int(next(iter(donor_embeddings.values())).shape[0]) if donor_embeddings else None,
        "model": MODEL_SUBDIR,
        "model_input_size": 2048,
        "emb_mode": "cls",
        "aggregation": "mean_pool_per_donor",
    })

    emb_df = pd.DataFrame.from_dict(donor_embeddings, orient="index")
    emb_df.index.name = "gsm_id"
    emb_df.columns = [f"gf_dim_{i}" for i in range(emb_df.shape[1])]
    emb_df = emb_df.sort_index()
    emb_df.to_parquet("/kaggle/working/l2_sealed_geneformer_embeddings.parquet", compression="zstd")
    log(f"wrote embeddings parquet: shape={emb_df.shape}")

except Exception:
    log("FAILED:")
    traceback.print_exc()
    SUMMARY["status"] = "failed"
    SUMMARY["error"] = traceback.format_exc()

with open("/kaggle/working/l2_sealed_geneformer_run_summary.json", "w") as f:
    json.dump(SUMMARY, f, indent=2, default=str)

log("=== FINAL SUMMARY (batches omitted) ===")
print(json.dumps({k: v for k, v in SUMMARY.items() if k not in ("batches", "sample_cell_counts_expected")},
                  indent=2, default=str), flush=True)
