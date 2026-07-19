# L2 Kaggle notebook plan — dev-cohort SLE-vs-healthy (Perez 2022)

Status: plan only. No cell in this plan has been executed on Kaggle. This
document is a report, not a gate/scaffold artifact — it does not authorize or
block anything; it describes what the notebook should contain when someone
chooses to run it.

Scope: dev cohort only (CELLxGENE Perez 2022, `dataset_id
218acb0f-9f2f-4f76-b90b-15a4b7c7f629`). Never touches GSE135779.

## Why Kaggle instead of local

- Full H5AD is 12.2 GB; local disk has 16 GB free — too tight to download
  whole (per prior session's finding, still true).
- `cellxgene_census` streams obs/X without a full download, but a real
  single-donor timing probe run locally (donor `HC-546`, 4,102 cells, dense
  `to_anndata` fetch) took 327 seconds — roughly 0.08 s/cell. Naively
  extrapolated across all 1,263,676 cells in the dataset, sequential
  per-donor fetches at that rate would take on the order of a day. This is
  one data point from a residential network path to the census S3 bucket,
  not a robust benchmark, and it used a per-donor `to_anndata` call rather
  than the chunked streaming path — but it's enough to conclude local
  full-cohort pseudobulk extraction is impractical. Kaggle's compute has a
  different (likely better-peered) network path and should be re-benchmarked
  before committing to a full run — see Cell 2 below.

## Cell plan

**Cell 1 — environment**
```
!pip install -q cellxgene_census
```
No repo clone needed for this notebook; it only needs the one new script's
logic (or the script itself uploaded as a Kaggle dataset/utility file) plus
`cellxgene_census`. If reusing `scripts/14_l2_census_pipeline.py` directly,
upload it as a Kaggle Dataset or paste its functions into a cell — the
script has no dependency on any `stageN_*` module.

**Cell 2 — re-benchmark streaming throughput on Kaggle (do this before Cell 4)**
```python
import time, sys
sys.path.insert(0, "/kaggle/input/l2-census-pipeline")  # or paste inline
from l2_census_pipeline import stream_donor_pseudobulk

t0 = time.time()
stream_donor_pseudobulk(["HC-546"])  # same donor as the local probe, for a fair comparison
print("kaggle donor fetch seconds:", time.time() - t0)
```
Compare against the local 327s figure. If Kaggle is meaningfully faster
(likely, given cloud-to-cloud networking), recompute the full-cohort ETA
before running Cell 4. If it is not meaningfully faster, do not run Cell 4
sequentially — restructure to a single chunked whole-dataset `axis_query`
(one query, not 261) before attempting a full run, since most of the 327s is
plausibly per-query overhead rather than per-cell bandwidth.

**Cell 3 — donor metadata (cheap, already validated)**
```python
from l2_census_pipeline import fetch_donor_metadata, write_metadata_csv
records = fetch_donor_metadata()
write_metadata_csv(records, "/kaggle/working/l2_dev_donor_metadata.csv")
```
This path was already run for real locally (obs-only query, no X data) and
returned 261 donors / 162 SLE / 99 healthy, matching PREREG exactly, plus a
flagged data-quality note for donors `1130` and `1772` (inconsistent
`development_stage` across cells — resolved by taking the minimum age and
recorded in `age_flag`). Re-running on Kaggle should reproduce the identical
counts; if it doesn't, stop and investigate before anything downstream runs.

**Cell 4 — full-cohort pseudobulk (the heavy step; only after Cell 2 confirms it's tractable)**
```python
from l2_census_pipeline import stream_donor_pseudobulk
import numpy as np

pseudobulk = stream_donor_pseudobulk(None)  # all 261 donors
np.savez("/kaggle/working/l2_dev_pseudobulk.npz", **pseudobulk)
```
CPM-normalize + log1p per PREREG Section 3 (already implemented as real,
unit-tested math in `compute_donor_pseudobulk_from_counts`). Output is one
vector per donor over the full census gene set (61,497 genes as of Census
2025-11-08) — gene-space intersection with GSE135779 (PREREG Section 8)
happens later, at sealed-cohort time, not here.

**Cell 5 — Geneformer embeddings (conditional — see feasibility below)**

**Cell 6 — download artifacts back to local**
```python
# Kaggle Output tab: l2_dev_donor_metadata.csv, l2_dev_pseudobulk.npz,
# l2_dev_geneformer_embeddings.npz (if Cell 5 ran)
```
CV/modeling (GroupKFold by donor, patient-bootstrap CI, permutation test)
stays local per PREREG — Kaggle only produces features, not the CV result.

## Geneformer-on-Kaggle feasibility

**I do not have a verified, sourced throughput benchmark for Geneformer
inference on a T4** — stating one as fact would violate "never invent a
number." What follows is an explicitly-labeled order-of-magnitude estimate,
built the same way F009 estimated FOOOF cost: state the assumptions, give a
range, and require an empirical calibration step before committing to the
full run.

Assumptions (stated, not verified):
- Geneformer-6L (~10M params) or Geneformer-12L (~40M params), rank-value
  encoded gene tokens, sequence length up to 2048 per cell.
- On a T4 (16 GB, free Kaggle tier), a small (~10-40M param) transformer
  doing forward-pass-only inference at batch size 16-32 and seq length
  ~2048 plausibly processes on the order of **10-50 cells/sec** — this range
  is a rough analogy to BERT-scale inference throughput on T4 adjusted for
  Geneformer's longer sequence length and smaller model, not a Geneformer-
  specific measurement.
- Full dataset: 1,263,676 cells. At 10-50 cells/sec: **7-35 hours** of pure
  compute.
- Kaggle free-tier GPU quota: 30 GPU-hours/week, sessions capped at ~9-12
  hours (subject to Kaggle's current limits, not independently re-verified
  this session). A single session cannot cover the pessimistic end of this
  range, and the whole weekly quota is tight even at the optimistic end.

**Required calibration step (must run before trusting this estimate):**
first cell of the Geneformer step should embed a fixed small sample (e.g.
2,000-5,000 cells from one donor) and report measured cells/sec, then
recompute the full-cohort ETA from that real number before deciding whether
to proceed, batch, or subsample.

**Batching plan if infeasible in one session:**
- Split the 261 donors into shards (e.g. 10-15 donors each) sized to fit a
  ~6-8 hour session with margin.
- Process shards across multiple Kaggle sessions/days within the 30 GPU-
  hour/week quota, writing one `.npz` of embeddings per shard to Kaggle
  Output, then concatenating locally.
- Persist a shard-completion manifest (donor IDs done, embedding dim, cell
  count) so a restart doesn't silently skip or duplicate a donor — this is
  data bookkeeping, not a new gate/scaffold framework, and belongs in the
  notebook's own working directory, not as a new `src/lupusfm` module.
- If the full 1.26M-cell run is still impractical inside the quota, the
  documented fallback is per-donor cell subsampling (e.g. cap at 2,000 cells/
  donor before mean-pooling) — but that is a deviation from "mean-pooled over
  all of a donor's cells" as PREREG currently states the Geneformer arm, so
  it would need a PREREG amendment (Section 3), not a silent substitution.

## What stays out of scope for this plan

- No GSE135779 access of any kind.
- No CV/AUROC computation on Kaggle — PREREG requires train-fold-only
  fitting and donor-grouped splits, which happens locally against the
  downloaded feature CSVs/NPZs.
- No new `stageN_*` files, gate files, or scaffold contracts anywhere in this
  plan.
