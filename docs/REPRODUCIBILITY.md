# Reproducibility

## Supported reproduction target

The publication-facing reproduction target is the corrected donor-level scoring and statistical analysis from the already generated, provenance-checked Geneformer V1 feature artifacts.

Tested Python: **3.11.15**.

## One-command CPU reproduction

```bash
bash scripts/reproduce.sh
```

The script creates `reproductions/publication-*`, never overwrites `results/published/`, and verifies the fresh rerun against the committed publication artifacts.

Expected shared-gene external AUROCs:

- Geneformer V1: **0.734375**
- Pseudobulk: **0.8984375**
- Age only: **0.578125**

Expected external sample count: **56** (40 SLE, 16 healthy).

## Environment

The CPU environment is pinned in `requirements.txt`. The script uses `uv` with Python 3.11.15 and does not install the repository as a package.

GPU extraction dependencies are documented separately in `environments/gpu-requirements.txt`. The successful extraction notebooks also preserve their complete runtime provenance in the committed run summaries.

## What is and is not reproduced

The CPU command reproduces corrected shared/native donor scoring, paired statistical analyses, gene-input sensitivity, descriptive bootstrap summaries, the cohort-membership diagnostic, publication figures in the isolated reproduction directory, and numerical comparison to the committed publication package.

It does **not** redownload raw single-cell datasets or repeat the multi-hour GPU Geneformer extraction. Those steps are documented in `notebooks/extraction/` and the archived extraction provenance.

## Continuous integration

`.github/workflows/reproducibility.yml` runs the active tests and the full CPU reproduction from a fresh GitHub Actions checkout.
