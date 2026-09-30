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
OLD_SHA_WITH_AWS_INSTALL = "591e91e36b95c808084407361570a50f472709ef526b2919ac328b37b2a79be0"
OLD_SHA_FIRST_NOTEBOOK = "be18c4d09531f211b5729fbd1380d76165f12ab02fd243af3e861688d4be509c"
NEW_SHA = "90966854faa6e5e6d7902462cd429cc3f504a145053a5eea8a790420f122aed2"


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
    old_hash = hashlib.sha256(source.encode()).hexdigest()
    if old_hash == OLD_SHA_FIRST_NOTEBOOK:
        source = replace_once(
            source,
            '    run(f"{sys.executable} -m pip install -q \'transformers>=4.35,<4.50\'")\n',
            '    run(f"{sys.executable} -m pip install -q \'transformers>=4.35,<4.50\'")\n'
            '    run(f"{sys.executable} -m pip install -q --force-reinstall "\n'
            '        "boto3==1.40.46 botocore==1.40.46 s3transfer==0.14.0")\n',
        )
    elif old_hash != OLD_SHA_WITH_AWS_INSTALL:
        raise ValueError("Staged runner differs from the two supported versions")
    source = replace_once(
        source, "N_BATCHES_TARGET = 8\n",
        "N_BATCHES_TARGET = 8\n"
        'LEGACY_MULTIPROCESS_SCRIPT_SHA256S = {\n'
        f'    "{OLD_SHA_WITH_AWS_INSTALL}",\n'
        f'    "{OLD_SHA_FIRST_NOTEBOOK}",\n'
        '}\n',
    )
    source = replace_once(
        source, "def load_batch_checkpoint(batch_idx, donors, expected_counts, config):\n",
        '''def checkpoint_config_compatible(saved, current):
    if saved == current:
        return True
    if not isinstance(saved, dict):
        return False
    if saved.get("extraction_script_sha256") not in LEGACY_MULTIPROCESS_SCRIPT_SHA256S:
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
    original_hash = sha256(RUNNER)
    if original_hash not in {OLD_SHA_FIRST_NOTEBOOK, OLD_SHA_WITH_AWS_INSTALL}:
        raise ValueError("Staged runner differs from the two supported versions")
    metadata_path = CHECKPOINT / "batch_00.json"
    parquet_path = CHECKPOINT / "batch_00.parquet"
    metadata = json.loads(metadata_path.read_text())
    if metadata["config"]["extraction_script_sha256"] != original_hash:
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
