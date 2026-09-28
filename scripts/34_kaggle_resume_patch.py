"""Patch the first Kaggle development job in place after a TBB fork failure.

The completed batch-0 checkpoint stays byte-for-byte unchanged. The revised
runner accepts it only when every protocol field, donor, count, and parquet
digest matches; the original script hash remains in its metadata.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

RUNNER = Path("/kaggle/working/lupus_correction_code/corrected_run.py")
CHECKPOINT = Path("/kaggle/working/correction_checkpoints/dev_shared")
OLD_SHA = "591e91e36b95c808084407361570a50f472709ef526b2919ac328b37b2a79be0"
NEW_SHA = "12f7cc03d4ff41dd30645e5b518f2957042ce457b66f53a33ab12e0214eec504"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise ValueError(f"Expected exactly one patch anchor: {old[:80]!r}")
    return source.replace(old, new, 1)


def patch_source(source):
    source = replace_once(
        source, "N_BATCHES_TARGET = 8\n",
        "N_BATCHES_TARGET = 8\n"
        f'LEGACY_MULTIPROCESS_SCRIPT_SHA256 = "{OLD_SHA}"\n',
    )
    source = replace_once(
        source, "def load_batch_checkpoint(batch_idx, donors, expected_counts, config):\n",
        '''def checkpoint_config_compatible(saved, current):
    if saved == current:
        return True
    if not isinstance(saved, dict):
        return False
    if saved.get("extraction_script_sha256") != LEGACY_MULTIPROCESS_SCRIPT_SHA256:
        return False
    normalized = dict(saved)
    normalized["extraction_script_sha256"] = current["extraction_script_sha256"]
    return normalized == current


def load_batch_checkpoint(batch_idx, donors, expected_counts, config):
''',
    )
    source = replace_once(
        source,
        'if metadata.get("config") != config or metadata.get("donors") != sorted(donors):',
        'if not checkpoint_config_compatible(metadata.get("config"), config) or metadata.get("donors") != sorted(donors):',
    )
    source = replace_once(
        source,
        '        raise ValueError(f"invalid checkpoint embeddings: {parquet_path}")\n',
        '        raise ValueError(f"invalid checkpoint embeddings: {parquet_path}")\n'
        '    if metadata["config"] != config:\n'
        '        log(f"reused validated batch {batch_idx} from earlier two-process extraction")\n',
    )
    source = replace_once(
        source,
        '        batch_dir = f"{WORK}/batch_{batch_idx}"\n'
        '        os.makedirs(f"{batch_dir}/input", exist_ok=True)\n',
        '        batch_dir = f"{WORK}/batch_{batch_idx}"\n'
        '        # A failed tokenization can leave an incomplete output directory.\n'
        '        # Only complete, hash-checked checkpoints are eligible for reuse.\n'
        '        if os.path.isdir(batch_dir):\n'
        '            shutil.rmtree(batch_dir)\n'
        '        os.makedirs(f"{batch_dir}/input", exist_ok=True)\n',
    )
    if source.count("            nproc=2,\n") != 2:
        raise ValueError("Expected exactly two Geneformer nproc=2 settings")
    source = source.replace("            nproc=2,\n", "            nproc=1,\n")
    if hashlib.sha256(source.encode()).hexdigest() != NEW_SHA:
        raise ValueError("Patched runner does not match the versioned correction")
    return source


def main():
    if sha256(RUNNER) != OLD_SHA:
        raise ValueError("Staged runner differs from the expected pre-patch version")
    metadata_path = CHECKPOINT / "batch_00.json"
    parquet_path = CHECKPOINT / "batch_00.parquet"
    metadata = json.loads(metadata_path.read_text())
    if metadata["config"]["extraction_script_sha256"] != OLD_SHA:
        raise ValueError("Batch-0 checkpoint was made by a different runner")
    if metadata["config"]["gene_input_mode"] != "shared":
        raise ValueError("Batch-0 checkpoint is not the shared-gene job")
    if len(metadata["donors"]) != 33 or sum(metadata["cell_counts"].values()) != 158835:
        raise ValueError("Batch-0 donor/cell counts differ from the completed batch")
    if sha256(parquet_path) != metadata["parquet_sha256"]:
        raise ValueError("Batch-0 parquet checksum mismatch")
    patched = patch_source(RUNNER.read_text())
    RUNNER.write_text(patched)
    print("SINGLE_PROCESS_PATCH_OK", sha256(RUNNER))
    print("Batch-0 checkpoint validated and preserved:", metadata["parquet_sha256"])
    print("Rerun Cell 4 in this session; it should restore batch 0.")


if __name__ == "__main__":
    main()
