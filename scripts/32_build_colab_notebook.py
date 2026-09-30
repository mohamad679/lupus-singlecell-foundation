"""Build a self-contained VS Code / Colab notebook for the correction jobs.

Embeds the exact local scripts and shared-gene list so the hosted runtime
does not depend on an unpublished correction branch or VS Code file sync.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_FILES = {
    "corrected_dev.py": ROOT / "kaggle_kernels/l2_geneformer_v1_corrected_dev/run.py",
    "corrected_external.py": ROOT / "kaggle_kernels/l2_geneformer_v1_corrected_external/run.py",
    "v1_fixture.py": ROOT / "scripts/31_v1_gpu_fixture.py",
    "gene_space_intersection.txt": ROOT / "results/gene_space_intersection.txt",
}


def markdown(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source):
    return {"cell_type": "code", "metadata": {}, "source": source.splitlines(keepends=True),
            "execution_count": None, "outputs": []}


def build():
    payload = {}
    checksums = {}
    for name, path in SOURCE_FILES.items():
        data = path.read_bytes()
        payload[name] = base64.b64encode(gzip.compress(data, mtime=0)).decode()
        checksums[name] = hashlib.sha256(data).hexdigest()
    payload_json = json.dumps(payload, sort_keys=True)
    checksums_json = json.dumps(checksums, sort_keys=True)
    bootstrap = f'''import base64, gzip, hashlib, json, os
from pathlib import Path
base = Path("/content/lupus-correction")
base.mkdir(parents=True, exist_ok=True)
Path("/kaggle/working").mkdir(parents=True, exist_ok=True)
payload = json.loads({payload_json!r})
expected = json.loads({checksums_json!r})
for name, encoded in payload.items():
    data = gzip.decompress(base64.b64decode(encoded))
    if hashlib.sha256(data).hexdigest() != expected[name]:
        raise ValueError("notebook payload checksum mismatch: " + name)
    (base / name).write_bytes(data)
print("Staged correction scripts and shared genes:", sorted(payload))
'''
    install = '''import importlib.metadata, json, os, subprocess, sys
packages = [
    "git+https://huggingface.co/ctheodoris/Geneformer.git@04c2b2e84da7c0f385c3f9ad8f3ec24bab6650e5",
    "transformers>=4.35,<4.50", "huggingface_hub", "anndata", "scipy",
    "datasets", "cellxgene_census", "pyarrow",
]
install_env = os.environ.copy()
install_env["GIT_LFS_SKIP_SMUDGE"] = "1"  # fetch V1 weights once via snapshot_download
subprocess.run([sys.executable, "-m", "pip", "install", "-q", *packages], check=True, env=install_env)
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--force-reinstall",
                "boto3==1.40.46", "botocore==1.40.46", "s3transfer==0.14.0"],
               check=True)
revisions = []
for distribution_name in importlib.metadata.packages_distributions().get("geneformer", []):
    direct_url = importlib.metadata.distribution(distribution_name).read_text("direct_url.json")
    if direct_url:
        revisions.append(json.loads(direct_url).get("vcs_info", {}).get("commit_id"))
if "04c2b2e84da7c0f385c3f9ad8f3ec24bab6650e5" not in revisions:
    raise RuntimeError("Installed Geneformer source revision is not the pinned V1 source")
subprocess.run(["nvidia-smi"], check=True)
'''
    mount = '''from google.colab import drive
from pathlib import Path
drive.mount("/content/drive")
archive = Path("/content/drive/MyDrive/lupus-correction-2026-09")
archive.mkdir(parents=True, exist_ok=True)
print("Persistent result folder:", archive)
'''
    fixture = '''import shutil, subprocess, sys
from pathlib import Path
subprocess.run([sys.executable, "/content/lupus-correction/v1_fixture.py",
                "--output-dir", "/kaggle/working/v1_fixture"], check=True)
shutil.copy2("/kaggle/working/v1_fixture/fixture_summary.json", archive / "fixture_summary.json")
print("Fixture passed; full extraction may now begin.")
'''

    def cohort_cell(cohort, mode):
        script = "corrected_dev.py" if cohort == "dev" else "corrected_external.py"
        prefix = "l2_dev" if cohort == "dev" else "l2_sealed"
        return f'''import os, shutil, subprocess, sys
from pathlib import Path
env = os.environ.copy()
env["GENE_INPUT_MODE"] = "{mode}"
env["GENE_INTERSECTION_PATH"] = "/content/lupus-correction/gene_space_intersection.txt"
env["GENEFORMER_FORWARD_BATCH_SIZE"] = "8"  # safe initial Colab GPU budget
env["GENEFORMER_SKIP_INSTALL"] = "1"  # pinned source installed by cell 2
subprocess.run([sys.executable, "/content/lupus-correction/{script}"], check=True, env=env)
for suffix in ("embeddings.parquet", "run_summary.json"):
    name = "{prefix}_geneformer_v1_{mode}_" + suffix
    shutil.copy2(Path("/kaggle/working") / name, archive / name)
print("Archived {cohort} {mode} outputs.")
'''

    cells = [
        markdown("# Lupus Geneformer V1 correction — GPU execution\n\n"
                 "Open this notebook in VS Code. Select a **Google Colab GPU runtime** as the notebook kernel. "
                 "Run cells in order. The fixture must pass before any cohort run. "
                 "Outputs are saved to Google Drive because Colab runtimes are temporary. "
                 "This is a corrected reanalysis on an already examined external cohort.\n"),
        markdown("## 1. Stage versioned code and the shared-gene file\n"), code(bootstrap),
        markdown("## 2. Install pinned Geneformer source and check the GPU\n"), code(install),
        markdown("## 3. Mount a persistent output folder\n"), code(mount),
        markdown("## 4. Run the small V1 technical fixture\n"), code(fixture),
        markdown("## 5. Primary shared-gene development extraction\n"), code(cohort_cell("dev", "shared")),
        markdown("## 6. Primary shared-gene external extraction\n"), code(cohort_cell("external", "shared")),
        markdown("## 7. Model-native development sensitivity\n"), code(cohort_cell("dev", "native")),
        markdown("## 8. Model-native external sensitivity\n"), code(cohort_cell("external", "native")),
        markdown("After all four extraction outputs and summaries are archived, download them "
                 "to the local correction folder and run `scripts/28_corrected_geneformer_scoring.py` "
                 "followed by `scripts/27_correction_analysis.py`. Do not revise the manuscript "
                 "from partial runs.\n"),
    ]
    for index, cell in enumerate(cells):
        cell["id"] = f"colab-{index:02d}"
    return {"cells": cells,
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
            "nbformat": 4, "nbformat_minor": 5}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(json.dumps(build(), indent=1) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
