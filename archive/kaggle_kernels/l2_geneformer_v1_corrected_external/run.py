"""Versioned correction of GSE135779 V1 cell embeddings: 56 samples.

This changes the historical extraction recipe. The shared-gene input is
primary; GENE_INPUT_MODE=native is a separately labeled sensitivity run.
Source and checkpoint revision are pinned, and V1 tokenizer/extractor
settings and all cell/donor outputs are validated before pooling.

This is real data from the public GEO deposit (GSE135779_RAW.tar,
downloaded directly from NCBI FTP within this kernel), processed in
cell-count-balanced batches with per-batch throughput logged.

mean_pool_per_donor: per-cell V1 embeddings are mean-pooled to one vector
per sample (donor) immediately after each batch, then discarded -- no
attempt to hold all ~363,083 sealed cells' embeddings in memory at once.

Writes:
- /kaggle/working/l2_sealed_geneformer_v1_<mode>_embeddings.parquet
- /kaggle/working/l2_sealed_geneformer_v1_<mode>_run_summary.json
"""

import json
import hashlib
import gc
import os
import shutil
import subprocess
import sys
import time
import traceback

MODEL_SUBDIR = "Geneformer-V1-10M"
GENEFORMER_REVISION = "04c2b2e84da7c0f385c3f9ad8f3ec24bab6650e5"
GENE_INPUT_MODE = os.environ.get("GENE_INPUT_MODE", "shared")
BATCH_SIZE = int(os.environ.get("GENEFORMER_FORWARD_BATCH_SIZE", "32"))
SCRATCH = os.environ.get("GENEFORMER_SCRATCH_DIR", "/kaggle/temp")
CHECKPOINT_ROOT = os.environ.get(
    "GENEFORMER_CHECKPOINT_DIR",
    f"/kaggle/working/correction_checkpoints/external_{GENE_INPUT_MODE}",
)
RESUME_ROOT = os.environ.get("GENEFORMER_RESUME_DIR", CHECKPOINT_ROOT)
RAW_DIR = f"{SCRATCH}/gse135779_raw"
INTERSECTION_PATH = os.environ.get("GENE_INTERSECTION_PATH", "/kaggle/input/lupus-correction/gene_space_intersection.txt")
INTERSECTION_SHA256 = "482f113c433ac76eb19940442e4f3b1a24ae73d387c4ec75ecb19b8116eea29b"
assert GENE_INPUT_MODE in {"shared", "native"}
assert BATCH_SIZE > 0
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


if os.environ.get("GENEFORMER_SKIP_INSTALL") != "1":
    log("installing dependencies")
    run(f"{sys.executable} -m pip install -q git+https://huggingface.co/ctheodoris/Geneformer.git@{GENEFORMER_REVISION}")
    run(f"{sys.executable} -m pip install -q huggingface_hub anndata scipy")
    run(f"{sys.executable} -m pip install -q 'transformers>=4.35,<4.50'")
    run(f"{sys.executable} -m pip install -q --force-reinstall "
        "boto3==1.40.46 botocore==1.40.46 s3transfer==0.14.0")

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import scipy.io  # noqa: E402
import scipy.sparse  # noqa: E402
import anndata as ad  # noqa: E402
from huggingface_hub import snapshot_download  # noqa: E402
from geneformer import TranscriptomeTokenizer, EmbExtractor  # noqa: E402
from datasets import load_from_disk  # noqa: E402


def shared_genes():
    if GENE_INPUT_MODE == "native":
        return None
    raw = open(INTERSECTION_PATH, "rb").read()
    if hashlib.sha256(raw).hexdigest() != INTERSECTION_SHA256:
        raise ValueError("shared-gene list checksum mismatch")
    genes = set(raw.decode().splitlines())
    if len(genes) != 30165:
        raise ValueError("shared-gene list is incomplete or contains duplicates")
    return genes


def model_hashes(model_path):
    hashes = {}
    for root, _, files in os.walk(model_path):
        for name in sorted(files):
            path = os.path.join(root, name)
            digest = hashlib.sha256()
            with open(path, "rb") as stream:
                for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
                    digest.update(chunk)
            hashes[os.path.relpath(path, model_path)] = digest.hexdigest()
    if not hashes:
        raise ValueError("checkpoint download is empty")
    return hashes


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_batch_checkpoint(batch_idx, donors, expected_counts, config):
    stem = f"batch_{batch_idx:02d}"
    metadata_path = os.path.join(RESUME_ROOT, stem + ".json")
    parquet_path = os.path.join(RESUME_ROOT, stem + ".parquet")
    if not (os.path.isfile(metadata_path) and os.path.isfile(parquet_path)):
        return None
    with open(metadata_path) as stream:
        metadata = json.load(stream)
    if metadata.get("config") != config or metadata.get("donors") != sorted(donors):
        raise ValueError(f"incompatible batch checkpoint: {metadata_path}")
    if metadata.get("cell_counts") != expected_counts:
        raise ValueError(f"cell counts changed since checkpoint: {metadata_path}")
    if file_sha256(parquet_path) != metadata.get("parquet_sha256"):
        raise ValueError(f"corrupted batch checkpoint: {parquet_path}")
    frame = pd.read_parquet(parquet_path)
    if frame.index.name != "donor_id" or sorted(frame.index.tolist()) != sorted(donors):
        raise ValueError(f"donor IDs changed in checkpoint: {parquet_path}")
    if not all(str(column).startswith("gf_dim_") for column in frame.columns):
        raise ValueError(f"invalid checkpoint embedding columns: {parquet_path}")
    if frame.shape[1] == 0 or not np.isfinite(frame.to_numpy(dtype=float)).all():
        raise ValueError(f"invalid checkpoint embeddings: {parquet_path}")
    if os.path.abspath(RESUME_ROOT) != os.path.abspath(CHECKPOINT_ROOT):
        os.makedirs(CHECKPOINT_ROOT, exist_ok=True)
        shutil.copy2(parquet_path, os.path.join(CHECKPOINT_ROOT, stem + ".parquet"))
        shutil.copy2(metadata_path, os.path.join(CHECKPOINT_ROOT, stem + ".json"))
    return frame, metadata


def save_batch_checkpoint(batch_idx, donors, expected_counts, grouped, config, audit):
    os.makedirs(CHECKPOINT_ROOT, exist_ok=True)
    stem = f"batch_{batch_idx:02d}"
    parquet_path = os.path.join(CHECKPOINT_ROOT, stem + ".parquet")
    metadata_path = os.path.join(CHECKPOINT_ROOT, stem + ".json")
    frame = grouped.sort_index().copy()
    frame.index.name = "donor_id"
    frame.columns = [f"gf_dim_{i}" for i in range(frame.shape[1])]
    tmp_parquet = parquet_path + ".tmp"
    frame.to_parquet(tmp_parquet, compression="zstd")
    os.replace(tmp_parquet, parquet_path)
    metadata = {"config": config, "donors": sorted(donors),
                "cell_counts": expected_counts, "batch_audit": audit,
                "embedding_dim": frame.shape[1],
                "parquet_sha256": file_sha256(parquet_path)}
    tmp_metadata = metadata_path + ".tmp"
    with open(tmp_metadata, "w") as stream:
        json.dump(metadata, stream, indent=2, sort_keys=True)
    os.replace(tmp_metadata, metadata_path)
    return metadata


def validate_tokenizer(tk):
    expected = {"ENSG00000000003": 2, "ENSG00000000005": 3,
                "ENSG00000141510": 8088, "ENSG00000139618": 7809}
    if tk.model_version != "V1" or tk.special_token or tk.model_input_size != 2048:
        raise ValueError("Geneformer V1 tokenizer settings are invalid")
    if any(tk.gene_token_dict.get(gene) != token for gene, token in expected.items()):
        raise ValueError("Geneformer V1 vocabulary mapping mismatch")
    if "<cls>" in tk.gene_token_dict or "<eos>" in tk.gene_token_dict:
        raise ValueError("V1 vocabulary unexpectedly contains special tokens")


def validate_batch(dataset_path, embs, expected_counts, vocab_size):
    tokenized = load_from_disk(dataset_path)
    if len(tokenized) != sum(expected_counts.values()) or len(embs) != len(tokenized):
        raise ValueError("cells were lost during tokenization or embedding")
    lengths = [len(ids) for ids in tokenized["input_ids"]]
    if not lengths or min(lengths) < 1 or max(lengths) > 2048:
        raise ValueError("empty or overlong token sequence")
    if any(token < 0 or token >= vocab_size for ids in tokenized["input_ids"] for token in ids):
        raise ValueError("token outside V1 vocabulary")
    if embs["cell_id"].duplicated().any() or embs["cell_id"].isna().any():
        raise ValueError("missing or duplicate embedded cell ID")
    if set(embs["cell_id"]) != set(tokenized["cell_id"]):
        raise ValueError("embedded cell IDs differ from tokenized cells")
    counts = embs["donor_id"].value_counts().to_dict()
    if counts != expected_counts:
        raise ValueError(f"embedded donor counts differ: {counts}")
    values = embs.drop(columns=["cell_id", "donor_id"]).to_numpy(dtype=float)
    if values.shape[1] == 0 or not np.isfinite(values).all():
        raise ValueError("invalid cell embeddings")
    return {"tokenized": len(tokenized), "embedded": len(embs),
            "min_sequence_length": min(lengths), "max_sequence_length": max(lengths)}

SUMMARY = {"batches": []}
donor_embeddings: dict[str, np.ndarray] = {}
donor_cell_counts_observed: dict[str, int] = {}

try:
    t_run_start = time.time()

    log("downloading GSE135779 public deposit (genes reference + raw counts archive)")
    os.makedirs(RAW_DIR, exist_ok=True)
    extracted_dir = f"{RAW_DIR}/extracted"
    already_extracted = (os.path.isfile(f"{RAW_DIR}/genes.tsv") and
                         os.path.isdir(extracted_dir) and
                         len(os.listdir(extracted_dir)) == 112)
    if not already_extracted:
        run(f"curl -fLsS --retry 3 --retry-delay 5 '{GENES_URL}' -o '{RAW_DIR}/genes.tsv.gz'")
        run(f"gunzip -f '{RAW_DIR}/genes.tsv.gz'")
        run(f"curl -fLsS --retry 3 --retry-delay 5 '{RAW_TAR_URL}' -o '{RAW_DIR}/GSE135779_RAW.tar'")
        os.makedirs(extracted_dir, exist_ok=True)
        run(f"tar -xf '{RAW_DIR}/GSE135779_RAW.tar' -C '{extracted_dir}'")
    else:
        log("reusing extracted GSE135779 source files in Kaggle scratch space")

    n_extracted = len(os.listdir(extracted_dir))
    log(f"extracted {n_extracted} files (expected 112 = 56 samples x 2 files)")
    assert n_extracted == 112, f"expected 112 files, got {n_extracted}"

    gene_ids = []
    with open(f"{RAW_DIR}/genes.tsv") as f:
        for line in f:
            gene_ids.append(line.rstrip("\n").split("\t")[0])
    n_genes_ref = len(gene_ids)
    log(f"gene reference: {n_genes_ref} genes (expected 32738)")
    assert n_genes_ref == 32738, f"expected 32738 genes, got {n_genes_ref}"
    input_genes = shared_genes()
    if input_genes is not None and not input_genes.issubset(set(gene_ids)):
        raise ValueError("external reference lacks shared genes")
    gene_index = [i for i, gene in enumerate(gene_ids) if input_genes is None or gene in input_genes]
    selected_gene_ids = [gene_ids[i] for i in gene_index]
    if len(selected_gene_ids) != len(set(selected_gene_ids)):
        raise ValueError("duplicate selected Ensembl IDs")

    all_gsm_ids = [m[0] for m in SAMPLE_META]
    assert len(all_gsm_ids) == 56, f"expected 56 samples, got {len(all_gsm_ids)}"

    def find_files(gsm_id):
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
    model_dir = snapshot_download(repo_id="ctheodoris/Geneformer", revision=GENEFORMER_REVISION,
                                  allow_patterns=[f"{MODEL_SUBDIR}/*"])
    model_path = f"{model_dir}/{MODEL_SUBDIR}"
    checkpoint_hashes = model_hashes(model_path)

    WORK = f"{SCRATCH}/gf_sealed_batches_{GENE_INPUT_MODE}"
    os.makedirs(WORK, exist_ok=True)
    checkpoint_config = {
        "cohort": "external", "geo_accession": "GSE135779",
        "gene_input_mode": GENE_INPUT_MODE,
        "intersection_sha256": INTERSECTION_SHA256 if input_genes is not None else None,
        "geneformer_revision": GENEFORMER_REVISION,
        "extraction_script_sha256": file_sha256(__file__),
        "checkpoint_sha256_by_file": checkpoint_hashes,
        "model_version": "V1", "emb_mode": "cell", "emb_layer": -1,
        "aggregation": "mean_pool_per_donor",
    }
    cumulative_cells = 0
    resumed_cells = 0

    for batch_idx, batch_gsms in enumerate(batches):
        expected_counts = {g: int(sample_ncells[g]) for g in batch_gsms}
        prior = load_batch_checkpoint(batch_idx, batch_gsms, expected_counts,
                                      checkpoint_config)
        if prior is not None:
            frame, metadata = prior
            for donor_id, row in frame.iterrows():
                donor_embeddings[donor_id] = row.to_numpy(dtype=np.float64)
                donor_cell_counts_observed[donor_id] = expected_counts[donor_id]
            batch_cells = sum(expected_counts.values())
            cumulative_cells += batch_cells
            resumed_cells += batch_cells
            SUMMARY["batches"].append({"batch_idx": batch_idx, "resumed": True,
                                       "n_samples": len(batch_gsms), "n_cells": batch_cells,
                                       "checkpoint_sha256": metadata["parquet_sha256"],
                                       **metadata["batch_audit"]})
            log(f"batch {batch_idx}: restored {batch_cells} cells from verified checkpoint")
            continue
        t_batch_start = time.time()
        batch_dir = f"{WORK}/batch_{batch_idx}"
        # A failed tokenization can leave an incomplete output directory.
        # Only complete, hash-checked checkpoints are eligible for reuse.
        if os.path.isdir(batch_dir):
            shutil.rmtree(batch_dir)
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
            mat = mat.T.tocsr()[:, gene_index]  # cells x selected genes
            mats.append(mat)
            n_cells_this = mat.shape[0]
            if n_cells_this != expected_counts[gsm_id]:
                raise ValueError(f"{gsm_id}: matrix cell count differs from header")
            cell_donor_ids.extend([gsm_id] * n_cells_this)
            cell_ids.extend([f"{gsm_id}_{i}" for i in range(n_cells_this)])
            donor_cell_counts_observed[gsm_id] = donor_cell_counts_observed.get(gsm_id, 0) + n_cells_this

        X = scipy.sparse.vstack(mats).tocsr()
        var_df = pd.DataFrame({"ensembl_id": selected_gene_ids}, index=selected_gene_ids)
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
            nproc=None,
            model_input_size=2048,
            model_version="V1",
        )
        validate_tokenizer(tk)
        tk.tokenize_data(
            data_directory=f"{batch_dir}/input",
            output_directory=f"{batch_dir}/tokenized",
            output_prefix="batch",
            file_format="h5ad",
        )

        embex = EmbExtractor(
            model_type="Pretrained",
            emb_mode="cell",
            model_version="V1",
            max_ncells=None,
            emb_layer=-1,
            emb_label=["cell_id", "donor_id"],
            forward_batch_size=BATCH_SIZE,
            nproc=1,
        )
        embs = embex.extract_embs(
            model_directory=model_path,
            input_data_file=f"{batch_dir}/tokenized/batch.dataset",
            output_directory=f"{batch_dir}/emb",
            output_prefix="batch_embs",
        )
        batch_audit = validate_batch(f"{batch_dir}/tokenized/batch.dataset", embs,
                                     {g: sample_ncells[g] for g in batch_gsms},
                                     len(tk.gene_token_dict))

        emb_cols = [c for c in embs.columns if c not in ("cell_id", "donor_id")]
        grouped = embs.groupby("donor_id")[emb_cols].mean()
        for donor_id, row in grouped.iterrows():
            donor_embeddings[donor_id] = row.to_numpy(dtype=np.float64)
        checkpoint = save_batch_checkpoint(batch_idx, batch_gsms, expected_counts,
                                           grouped, checkpoint_config, batch_audit)

        batch_seconds = time.time() - t_batch_start
        cumulative_cells += n_cells_batch
        cumulative_seconds = time.time() - t_run_start
        batch_rate = n_cells_batch / batch_seconds
        running_rate = (cumulative_cells - resumed_cells) / cumulative_seconds
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
            "checkpoint_sha256": checkpoint["parquet_sha256"], "resumed": False,
            **batch_audit,
        })

        shutil.rmtree(batch_dir, ignore_errors=True)
        del embs, grouped, tk, embex
        gc.collect()

    total_seconds = time.time() - t_run_start
    overall_rate = (cumulative_cells - resumed_cells) / total_seconds
    log(f"ALL BATCHES DONE: {len(donor_embeddings)} samples, {cumulative_cells} cells, "
        f"{total_seconds:.1f}s, overall_rate={overall_rate:.2f} cells/sec")

    missing = set(all_gsm_ids) - set(donor_embeddings.keys())
    extra = set(donor_embeddings.keys()) - set(all_gsm_ids)
    mismatches = {
        g: {"expected": sample_ncells[g], "observed": donor_cell_counts_observed.get(g, 0)}
        for g in all_gsm_ids if sample_ncells[g] != donor_cell_counts_observed.get(g, 0)
    }
    if missing or extra or mismatches or cumulative_cells != total_cells_expected:
        raise ValueError("external donor/cell integrity check failed")

    SUMMARY.update({
        "status": "success",
        "n_samples_expected": 56,
        "n_samples_embedded": len(donor_embeddings),
        "total_cells_expected": total_cells_expected,
        "total_cells_processed": cumulative_cells,
        "cells_restored_from_checkpoints": resumed_cells,
        "new_cells_processed": cumulative_cells - resumed_cells,
        "total_seconds": total_seconds,
        "overall_cells_per_sec": overall_rate,
        "missing_samples": sorted(missing),
        "extra_samples": sorted(extra),
        "cell_count_mismatches": mismatches,
        "sample_cell_counts_expected": sample_ncells,
        "embedding_dim": int(next(iter(donor_embeddings.values())).shape[0]) if donor_embeddings else None,
        "model": MODEL_SUBDIR,
        "geneformer_revision": GENEFORMER_REVISION,
        "checkpoint_sha256_by_file": checkpoint_hashes,
        "runtime_pip_freeze": subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True).splitlines(),
        "gene_input_mode": GENE_INPUT_MODE,
        "intersection_sha256": INTERSECTION_SHA256 if input_genes is not None else None,
        "model_input_size": 2048,
        "emb_mode": "cell",
        "model_version": "V1",
        "emb_layer": -1,
        "tokenizer_num_proc": None,
        "extractor_nproc": 1,
        "forward_batch_size": BATCH_SIZE,
        "aggregation": "mean_pool_per_donor",
    })

    emb_df = pd.DataFrame.from_dict(donor_embeddings, orient="index")
    emb_df.index.name = "gsm_id"
    emb_df.columns = [f"gf_dim_{i}" for i in range(emb_df.shape[1])]
    emb_df = emb_df.sort_index()
    embedding_path = f"/kaggle/working/l2_sealed_geneformer_v1_{GENE_INPUT_MODE}_embeddings.parquet"
    emb_df.to_parquet(embedding_path, compression="zstd")
    SUMMARY["embedding_sha256"] = file_sha256(embedding_path)
    log(f"wrote embeddings parquet: shape={emb_df.shape}")

except Exception:
    log("FAILED:")
    traceback.print_exc()
    SUMMARY["status"] = "failed"
    SUMMARY["error"] = traceback.format_exc()

with open(f"/kaggle/working/l2_sealed_geneformer_v1_{GENE_INPUT_MODE}_run_summary.json", "w") as f:
    json.dump(SUMMARY, f, indent=2, default=str)

log("=== FINAL SUMMARY (batches omitted) ===")
print(json.dumps({k: v for k, v in SUMMARY.items() if k not in ("batches", "sample_cell_counts_expected")},
                  indent=2, default=str), flush=True)
if SUMMARY["status"] != "success":
    raise SystemExit(1)
