"""Build four self-contained Kaggle GPU notebooks for the V1 correction.

Each notebook runs exactly one cohort/mode, so Save & Run All cannot
accidentally launch the entire multi-hour correction in one Kaggle session.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVISION = "04c2b2e84da7c0f385c3f9ad8f3ec24bab6650e5"
JOBS = (
    ("1_Development_Shared", "dev", "shared"),
    ("2_External_Shared", "external", "shared"),
    ("3_Development_Native", "dev", "native"),
    ("4_External_Native", "external", "native"),
)


def markdown(source):
    return {"cell_type": "markdown", "metadata": {},
            "source": source.splitlines(keepends=True)}


def code(source):
    return {"cell_type": "code", "metadata": {},
            "source": source.splitlines(keepends=True),
            "execution_count": None, "outputs": []}


def build(label, cohort, mode):
    script_path = ROOT / ("kaggle_kernels/l2_geneformer_v1_corrected_dev/run.py"
                          if cohort == "dev" else
                          "kaggle_kernels/l2_geneformer_v1_corrected_external/run.py")
    sources = {
        "corrected_run.py": script_path,
        "v1_fixture.py": ROOT / "scripts/31_v1_gpu_fixture.py",
        "gene_space_intersection.txt": ROOT / "results/gene_space_intersection.txt",
    }
    payload = {}
    checksums = {}
    for name, path in sources.items():
        raw = path.read_bytes()
        payload[name] = base64.b64encode(gzip.compress(raw, mtime=0)).decode("ascii")
        checksums[name] = hashlib.sha256(raw).hexdigest()

    job = f"{cohort}_{mode}"
    prefix = "l2_dev" if cohort == "dev" else "l2_sealed"
    expected_donors = 261 if cohort == "dev" else 56
    expected_cells = 1263676 if cohort == "dev" else 363083
    bootstrap = f'''import base64, gzip, hashlib, json
from pathlib import Path
base = Path("/kaggle/working/lupus_correction_code")
base.mkdir(parents=True, exist_ok=True)
payload = json.loads({json.dumps(payload, sort_keys=True)!r})
expected = json.loads({json.dumps(checksums, sort_keys=True)!r})
for name, encoded in payload.items():
    raw = gzip.decompress(base64.b64decode(encoded))
    if hashlib.sha256(raw).hexdigest() != expected[name]:
        raise ValueError("embedded code/data checksum mismatch: " + name)
    (base / name).write_bytes(raw)
print("Staged and checked:", sorted(payload))
print("Job: {job}; Geneformer source revision: {REVISION}")
'''
    install = f'''import importlib.metadata, json, os, subprocess, sys
from pathlib import Path
Path("/kaggle/temp/lupus-correction").mkdir(parents=True, exist_ok=True)
install_env = os.environ.copy()
install_env["GIT_LFS_SKIP_SMUDGE"] = "1"
packages = [
    "git+https://huggingface.co/ctheodoris/Geneformer.git@{REVISION}",
    "transformers>=4.35,<4.50", "huggingface_hub", "anndata",
    "scipy", "datasets", "cellxgene_census", "pyarrow",
    "aiobotocore==2.26.0",
]
subprocess.run([sys.executable, "-m", "pip", "install", "-q", *packages],
               check=True, env=install_env)
# Geneformer imports boto3, while Census/s3fs imports aiobotocore. These exact
# versions satisfy both import paths; avoid replacing unrelated dependencies.
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--no-deps",
                "--force-reinstall", "boto3==1.41.5", "botocore==1.41.5",
                "s3transfer==0.15.0"],
               check=True)
# The source checkout skips Git LFS to avoid fetching every model checkpoint.
# Fetch the three V1 dictionaries explicitly from the same pinned revision.
dictionary_code = """import hashlib, importlib.util, pickle, shutil
from pathlib import Path
from huggingface_hub import hf_hub_download
revision = '{REVISION}'
package_dir = Path(importlib.util.find_spec('geneformer').origin).parent
for name in ('gene_median_dictionary_gc30M.pkl',
             'token_dictionary_gc30M.pkl',
             'ensembl_mapping_dict_gc30M.pkl'):
    relative = 'geneformer/gene_dictionaries_30m/' + name
    source = Path(hf_hub_download(repo_id='ctheodoris/Geneformer',
                                  revision=revision, filename=relative))
    with source.open('rb') as stream:
        if stream.read(40).startswith(b'version https://git-lfs.github.com'):
            raise RuntimeError('Downloaded a Git LFS pointer: ' + relative)
        stream.seek(0)
        value = pickle.load(stream)
    if not isinstance(value, dict) or not value:
        raise RuntimeError('Invalid V1 dictionary: ' + relative)
    target = package_dir / 'gene_dictionaries_30m' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    print('V1 dictionary:', name, len(value), hashlib.sha256(target.read_bytes()).hexdigest())
"""
subprocess.run([sys.executable, "-c", dictionary_code], check=True)
revisions = []
for name in importlib.metadata.packages_distributions().get("geneformer", []):
    direct_url = importlib.metadata.distribution(name).read_text("direct_url.json")
    if direct_url:
        revisions.append(json.loads(direct_url).get("vcs_info", {{}}).get("commit_id"))
if "{REVISION}" not in revisions:
    raise RuntimeError("Installed Geneformer source is not the pinned revision")
# Pip can replace NumPy's files while this notebook kernel still has its old
# compiled module loaded. Check the installed stack in a fresh process, just
# as the fixture and cohort jobs will run it.
check_code = """import numpy, scipy, anndata, boto3, botocore, s3transfer, torch
import aiobotocore.session, s3fs, cellxgene_census
from geneformer import EmbExtractor, TranscriptomeTokenizer
print("IMPORT_OK", numpy.__version__, scipy.__version__, boto3.__version__,
      botocore.__version__, s3transfer.__version__, aiobotocore.__version__)
if not torch.cuda.is_available():
    raise RuntimeError("Select a Kaggle GPU accelerator before running this notebook")
"""
subprocess.run([sys.executable, "-c", check_code], check=True)
subprocess.run(["nvidia-smi"], check=True)
print("Pinned Geneformer import and GPU verified in a fresh Python process")
'''
    fixture = '''import json, shutil, subprocess, sys, time
from collections import deque
from pathlib import Path
fixture_dir = Path("/kaggle/temp/lupus-correction") / f"v1_fixture_{time.time_ns()}"
command = [sys.executable, "/kaggle/working/lupus_correction_code/v1_fixture.py",
           "--output-dir", str(fixture_dir)]
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           text=True, bufsize=1)
tail = deque(maxlen=250)
for line in process.stdout:
    print(line, end="")
    tail.append(line)
if process.wait() != 0:
    raise RuntimeError("V1 fixture failed. Full process output tail:\\n" +
                       "".join(tail)[-20000:])
fixture_summary = json.loads((fixture_dir / "fixture_summary.json").read_text())
if (fixture_summary.get("status") != "pass" or
        fixture_summary.get("replay_after_embedding_passed") is not True):
    raise RuntimeError("V1 technical fixture failed")
fixture_output = Path("/kaggle/working/v1_fixture")
fixture_output.mkdir(parents=True, exist_ok=True)
shutil.copy2(fixture_dir / "fixture_summary.json", fixture_output / "fixture_summary.json")
print("V1 technical fixture passed; start the cohort cell next")
'''
    run = f'''import json, os, subprocess, sys
from pathlib import Path
# Require the updated fixture, including a tokenization replay after GPU use.
fixture_summary_file = Path("/kaggle/working/v1_fixture/fixture_summary.json")
fixture_summary = json.loads(fixture_summary_file.read_text())
if (fixture_summary.get("status") != "pass" or
        fixture_summary.get("replay_after_embedding_passed") is not True):
    raise RuntimeError("Run the updated Cell 3 fixture before extraction")
# To resume after an interrupted saved version, attach that version as Kaggle
# Input and set this to its correction_checkpoints/{job} directory.
RESUME_INPUT = ""
env = os.environ.copy()
env["GENE_INPUT_MODE"] = "{mode}"
env["GENE_INTERSECTION_PATH"] = "/kaggle/working/lupus_correction_code/gene_space_intersection.txt"
env["GENEFORMER_FORWARD_BATCH_SIZE"] = "16"
env["GENEFORMER_SKIP_INSTALL"] = "1"
env["GENEFORMER_SCRATCH_DIR"] = "/kaggle/temp/lupus-correction"
env["GENEFORMER_CHECKPOINT_DIR"] = "/kaggle/working/correction_checkpoints/{job}"
if RESUME_INPUT:
    if not Path(RESUME_INPUT).is_dir():
        raise FileNotFoundError(RESUME_INPUT)
    env["GENEFORMER_RESUME_DIR"] = RESUME_INPUT
subprocess.run([sys.executable,
                "/kaggle/working/lupus_correction_code/corrected_run.py"],
               check=True, env=env)
print("Extraction finished: {job}")
'''
    package = f'''import hashlib, json, zipfile
from pathlib import Path
from IPython.display import FileLink, display
output = Path("/kaggle/working")
embedding = output / "{prefix}_geneformer_v1_{mode}_embeddings.parquet"
summary_file = output / "{prefix}_geneformer_v1_{mode}_run_summary.json"
fixture_file = output / "v1_fixture/fixture_summary.json"
summary = json.loads(summary_file.read_text())
if summary.get("status") != "success":
    raise RuntimeError("Extraction did not finish successfully")
if summary.get("gene_input_mode") != "{mode}" or summary.get("model_version") != "V1":
    raise ValueError("Extraction protocol in summary differs from notebook")
if summary.get("total_cells_processed") != {expected_cells}:
    raise ValueError("Processed cell count differs from the released source cohort")
if summary.get("{('n_donors_embedded' if cohort == 'dev' else 'n_samples_embedded')}") != {expected_donors}:
    raise ValueError("Embedded donor/sample count differs from the released cohort")
digest = hashlib.sha256(embedding.read_bytes()).hexdigest()
if digest != summary.get("embedding_sha256"):
    raise ValueError("Embedding parquet checksum differs from run summary")
files = [embedding, summary_file, fixture_file]
manifest = {{"job": "{job}", "geneformer_revision": "{REVISION}",
            "files_sha256": {{path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                             for path in files}}}}
manifest_file = output / "{job}_share_manifest.json"
manifest_file.write_text(json.dumps(manifest, indent=2) + "\\n")
share_zip = output / "lupus_correction_{job}_share.zip"
with zipfile.ZipFile(share_zip, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for path in [*files, manifest_file]:
        archive.write(path, arcname=path.name)
print("Verified {expected_donors} donors/samples and {expected_cells} cells")
print("Download this ZIP and upload it to our chat:")
display(FileLink(str(share_zip)))
'''
    cells = [
        markdown(f"# Lupus V1 correction — {cohort} {mode}\n\n"
                 "Run this notebook on Kaggle with **GPU** and **Internet On**. "
                 "It runs exactly one extraction job. Run cells 1–5 in order, "
                 "or use Save & Run All. The technical fixture must pass before "
                 "the full extraction. Raw cell data and temporary files are "
                 "kept in Kaggle scratch space; small verified results and batch "
                 "checkpoints remain in `/kaggle/working`. This is a corrected "
                 "reanalysis of an already examined external cohort.\n"),
        markdown("## Cell 1 — stage the exact correction code and shared-gene file\n"),
        code(bootstrap),
        markdown("## Cell 2 — install pinned Geneformer and check the GPU\n"),
        code(install),
        markdown("## Cell 3 — run the eight-cell V1 technical fixture\n"),
        code(fixture),
        markdown("## Cell 4 — extract this cohort and mode\n\n"
                 "Completed batches are checkpointed under `/kaggle/working/correction_checkpoints`. "
                 "If you rerun in the same session, valid completed batches are reused. "
                 "For a later Kaggle version, attach the prior output as an input and set "
                 "`RESUME_INPUT` below to its checkpoint directory.\n"),
        code(run),
        markdown("## Cell 5 — verify and package results for sharing\n"),
        code(package),
        markdown("Upload the generated `lupus_correction_*_share.zip` file to the chat. "
                 "If a cell fails, share its error and the `*_run_summary.json` file when present. "
                 "The full cohort run is required before manuscript results can be revised.\n"),
    ]
    for index, cell in enumerate(cells):
        cell["id"] = f"{job}-{index:02d}"
    return {"cells": cells,
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                        "name": "python3"},
                         "lupus_correction_job": job,
                         "geneformer_revision": REVISION},
            "nbformat": 4, "nbformat_minor": 5}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for label, cohort, mode in JOBS:
        path = args.output_dir / f"CBC_Kaggle_{label}.ipynb"
        path.write_text(json.dumps(build(label, cohort, mode), indent=1) + "\n")
        print(path)


if __name__ == "__main__":
    main()
