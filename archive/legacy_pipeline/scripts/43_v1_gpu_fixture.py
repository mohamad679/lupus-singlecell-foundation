"""Small technical Geneformer V1 tokenizer/embedding preflight.

Run on the intended GPU runtime before either cohort extraction. Synthetic
counts exercise token semantics and embedding output, but do not validate
biological preprocessing or raw-cohort access.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
from datasets import Dataset, load_from_disk
from geneformer import EmbExtractor, TranscriptomeTokenizer
from huggingface_hub import snapshot_download
from scipy.sparse import csr_matrix

REVISION = "04c2b2e84da7c0f385c3f9ad8f3ec24bab6650e5"
GENES = ["ENSG00000000003", "ENSG00000000005", "ENSG00000141510", "ENSG00000139618"]
TOKENS = [2, 3, 8088, 7809]


def run(output_dir):
    probe = Dataset.from_dict({"cell": [0]}).map(
        lambda _: {"pid": os.getpid()}, num_proc=None,
    )
    if list(probe["pid"]) != [os.getpid()]:
        raise ValueError("Datasets mapping did not stay in the main process")
    input_dir = output_dir / "input"
    token_dir = output_dir / "tokenized"
    embedding_dir = output_dir / "embedded"
    for path in (input_dir, token_dir, embedding_dir):
        path.mkdir(parents=True, exist_ok=True)
    cell_ids = [f"fixture-cell-{i}" for i in range(8)]
    counts = np.array([[1 + (i + j) % 4 for j in range(4)] for i in range(8)], dtype=np.int32)
    obs = pd.DataFrame({"cell_id": cell_ids,
                        "donor_id": ["fixture-a"] * 4 + ["fixture-b"] * 4,
                        "n_counts": counts.sum(axis=1)}, index=cell_ids)
    var = pd.DataFrame({"ensembl_id": GENES}, index=GENES)
    ad.AnnData(X=csr_matrix(counts), obs=obs, var=var).write_h5ad(input_dir / "fixture.h5ad")

    tokenizer = TranscriptomeTokenizer(
        custom_attr_name_dict={"cell_id": "cell_id", "donor_id": "donor_id"},
        nproc=None, model_version="V1", model_input_size=2048,
    )
    if tokenizer.model_version != "V1" or tokenizer.special_token:
        raise ValueError("V1 tokenizer settings invalid")
    if [tokenizer.gene_token_dict.get(gene) for gene in GENES] != TOKENS:
        raise ValueError("V1 gene-to-token mapping mismatch")
    tokenizer.tokenize_data(str(input_dir), str(token_dir), "fixture", file_format="h5ad")
    tokenized_path = token_dir / "fixture.dataset"
    tokenized = load_from_disk(str(tokenized_path))
    if len(tokenized) != len(cell_ids) or set(tokenized["cell_id"]) != set(cell_ids):
        raise ValueError("fixture tokenization lost or changed cells")
    lengths = [len(ids) for ids in tokenized["input_ids"]]
    if min(lengths) < 1 or max(lengths) > 2048:
        raise ValueError("fixture sequence length invalid")
    if any(token < 0 or token >= len(tokenizer.gene_token_dict)
           for ids in tokenized["input_ids"] for token in ids):
        raise ValueError("fixture token outside V1 vocabulary")

    snapshot = snapshot_download(repo_id="ctheodoris/Geneformer", revision=REVISION,
                                 allow_patterns=["Geneformer-V1-10M/*"])
    extractor = EmbExtractor(model_type="Pretrained", model_version="V1",
                             emb_mode="cell", max_ncells=None, emb_layer=-1,
                             emb_label=["cell_id", "donor_id"],
                             forward_batch_size=8, nproc=1)
    embeddings = extractor.extract_embs(
        model_directory=str(Path(snapshot) / "Geneformer-V1-10M"),
        input_data_file=str(tokenized_path), output_directory=str(embedding_dir),
        output_prefix="fixture",
    )
    if len(embeddings) != len(cell_ids) or set(embeddings.cell_id) != set(cell_ids):
        raise ValueError("fixture embeddings lost or changed cells")
    if embeddings.donor_id.value_counts().to_dict() != {"fixture-a": 4, "fixture-b": 4}:
        raise ValueError("fixture donor mapping invalid")
    values = embeddings.drop(columns=["cell_id", "donor_id"]).to_numpy(dtype=float)
    if values.shape[1] < 1 or not np.isfinite(values).all():
        raise ValueError("fixture embedding values invalid")
    # Repeat tokenization after GPU extraction. The previous Kaggle failure
    # appeared on the second batch when a mapping worker forked after TBB init.
    replay_tokenizer = TranscriptomeTokenizer(
        custom_attr_name_dict={"cell_id": "cell_id", "donor_id": "donor_id"},
        nproc=None, model_version="V1", model_input_size=2048,
    )
    replay_tokenizer.tokenize_data(
        str(input_dir), str(token_dir), "fixture_replay", file_format="h5ad",
    )
    replay = load_from_disk(str(token_dir / "fixture_replay.dataset"))
    if (replay["cell_id"] != tokenized["cell_id"] or
            replay["donor_id"] != tokenized["donor_id"] or
            replay["input_ids"] != tokenized["input_ids"]):
        raise ValueError("fixture replay after embedding changed tokens or cell mapping")
    summary = {"status": "pass", "geneformer_revision": REVISION,
               "n_cells": len(cell_ids), "embedding_dim": values.shape[1],
               "min_sequence_length": min(lengths), "max_sequence_length": max(lengths),
               "tokenizer_num_proc": None,
               "replay_after_embedding_passed": True,
               "scope": "technical synthetic-cell preflight only"}
    with (output_dir / "fixture_summary.json").open("w") as file:
        json.dump(summary, file, indent=2)
    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("/kaggle/working/v1_fixture"))
    args = parser.parse_args()
    run(args.output_dir)


if __name__ == "__main__":
    main()
