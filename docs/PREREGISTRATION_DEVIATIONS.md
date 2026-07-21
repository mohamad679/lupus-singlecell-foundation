# Preregistration deviations

Every deviation from PREREG.md's original text that occurred during L2/Phase 3
execution, consolidated in one place. Each entry states what PREREG said, what was
actually done, why, and whether it could affect a reported result. All facts here
are pulled verbatim or near-verbatim from PREREG.md's own amendment log and from
the commit messages that recorded each decision at the time it was made — nothing
below is reconstructed from memory or invented after the fact.

This document does not change PREREG.md or FREEZE.json. It is a summary, not a new
amendment; each item below already has a primary source (cited per entry).

---

## 1. Gene-space restriction convention (pseudobulk arm)

**What PREREG said:** Section 8: "features are restricted to the intersection of
genes present and comparably identified... in both the dev and sealed cohort's raw
count matrices." Read literally, this specifies restriction at the *raw-count*
level, before CPM normalization, applied symmetrically to both cohorts.

**What was done:** The originally committed dev-cohort pseudobulk artifact
(`results/l2_dev_pseudobulk_counts.parquet`, CPM+log1p over the full 61,497-gene
dev transcriptome) had no raw per-donor gene-count layer persisted separately —
only the final CPM+log1p features were saved. At Phase 3 (sealed scoring), this
created a genuine fork: restrict the *already-fitted* model's coefficients to the
30,165-gene intersection post hoc, or restrict *raw counts* first (for both
cohorts) and re-normalize, matching PREREG's literal text. The human chose the
latter. This required re-deriving a second, distinct dev-cohort pseudobulk
artifact restricted to the 30,165-gene intersection from raw counts
(`results/l2_dev_pseudobulk_counts_restricted.parquet`, via
`kaggle_kernels/l2_dev_pseudobulk_restricted/`), used only to fit the
sealed-scoring model.

**Why:** PREREG Section 8's literal wording supports raw-count-level, symmetric
restriction; the coefficient-restriction alternative was not what the document
specified.

**Could it affect results:** The originally committed dev-cohort internal-CV
AUROC for the pseudobulk arm (**0.9839**, `results/l2_dev_sle_vs_healthy.csv`) is
unaffected — it was computed before this fork existed and was never
recomputed or overwritten. This deviation affects only the *sealed*-scoring
pseudobulk model, which is downstream of this choice: the sealed pseudobulk AUROC
(0.8984) would plausibly have come out numerically different under the
coefficient-restriction alternative. This is the single most consequential
disclosed judgment call in Phase 3.

**Source:** commit `364761c` (Phase 3 opening); conversation record of the
methodological fork and the human's explicit choice, made *before* any sealed
prediction was computed.

---

## 2. Cell-type annotation / cohort-signature-probe deferral

**What PREREG said:** Section 5.1 pre-specifies a cohort-signature probe
(classifying dev-vs-sealed donor origin per feature arm) as a secondary,
pre-declared confirmatory analysis. Section 8 describes cell-type-level
harmonization via a Scanpy-ingest + k-NN label-transfer protocol.

**What was done:** Phase 2 pre-flight (2026-07-21) verified two things directly:
(1) GSE135779's public deposit has no cell-type annotation anywhere (checked the
full series file listing, every sample's supplementary files, and the family SOFT
metadata record — only `barcodes.tsv.gz` + `matrix.mtx.gz` per sample plus one
series-level gene reference); (2) the Scanpy-ingest label-transfer code PREREG
Section 8 cites does not exist in this repository
(`src/data/metadata_harmonization.py` is an unimplemented fake-data-contract
stub). Per human decision, Section 5.1 and the cell-type-dependent parts of
Section 8 were **deferred to future work**. Co-primary comparisons A and B
proceeded using only the mean-pooled arms (Geneformer, pseudobulk), which
aggregate over the entirety of a donor's cells and do not structurally require
cell-type labels.

**Why:** Writing and validating real ingest/label-transfer code immediately
before a one-time sealed-cohort opening was judged higher-risk than deferring a
secondary, non-Holm-corrected analysis that the primary/co-primary results do not
depend on.

**Could it affect results:** Does not affect the primary AUROC results or the
co-primary comparisons A/B — neither arm used in those comparisons depends on
cell-type labels. It does mean the pre-registered cohort-signature probe (an
interpretive check for cohort/batch confounding) was never run, so PREREG's
intended confounding-diagnostic is currently missing, not merely deferred in a way
that's cost-free to the science.

**Source:** PREREG.md amendment log, entry dated **2026-07-21**, "Sealed-cohort
pre-flight: cell-type / cohort-signature-probe deferral."

---

## 3. Freeze-guard not called by the scripts that actually touched sealed data

**What FREEZE.json's guard mechanism specified:** `scripts/freeze_guard.py`'s
`require_valid_freeze()` is designed so "any script that will touch GSE135779
must refuse to run unless FREEZE.json exists and its hashes still match the live
files."

**What was done:** The real sealed-data access happened via
`scripts/19_sealed_pseudobulk.py` (local processing of downloaded raw counts) and
`scripts/20_sealed_cohort_scoring.py` (frozen-model scoring) — neither called
`require_valid_freeze()` at the time they were actually run. The guard call was
added to both files only in commit `364761c`, the same commit that recorded the
sealed opening (i.e., concurrently with, not before, the real access). The
intended Phase 3 gateway, `scripts/18_sealed_cohort_open.py`, did call the guard
correctly, but the real work ended up running through scripts/19/20 directly
rather than being routed through it.

**Why:** Architectural gap — the guard was designed and wired into the intended
entry point, but the actual execution path diverged from that design. A human/
agent judgment call ("is FREEZE.json currently valid?") substituted for the
automated check at each real access point.

**Could it affect results:** No evidence that it does — `FREEZE.json` was valid
(hashes matched, `SEALED_OPENED.json` did not yet exist) at the time of every real
access, confirmed by the fact that the guard, once retroactively added and run,
reported `PASS` immediately before `SEALED_OPENED.json` was written. This is a
disclosed *process* gap (automated enforcement wasn't literally in the executed
code path), not a demonstrated data-integrity failure. Closed for any future rerun
in the same commit.

**Source:** commit `364761c`'s message, "Process note, disclosed rather than
hidden" section.

---

## 4. GSE135779 sample count: 56 deposited vs. 58 described

**What PREREG said (from verified context provided before L1):** the sealed
cohort was described as "33 cSLE + 11 cHD pediatric + 8 aSLE + 6 aHD adult" — 58
donors.

**What was done:** L1 metadata inspection (2026-07-19) found only **56** public
per-sample GEO records in GSE135779's deposit: 33 cSLE + 11 cHD (pediatric,
matches) + **7** aSLE + **5** aHD (adult; 2 fewer than described). This was
logged as an unresolved discrepancy at L1. The 2026-07-21 PREREG amendment
reconfirmed 56 as the real, verified, usable count and locked it as the N for
Phase 3 — no further attempt was made to chase the missing 2 samples down against
the source publication's supplementary tables.

**Why:** The public GEO deposit simply does not contain records for 2 of the
originally described 58 samples. Accepting the real, verifiable deposit size was
judged more honest than working around the gap.

**Could it affect results:** Yes, directly and by construction — every sealed
AUROC/CI/permutation-p number in `results/l2_sealed_results.json` is computed on
the real n=56 (adult stratum n=12, not the originally described n=14). This
is baked into every sealed-cohort statistic reported, not a peripheral footnote.

**Source:** PREREG.md amendment log, entries dated **2026-07-19** ("L1
metadata-only inspection") and **2026-07-21** ("Sample count: reconfirmed 56...").

---

## 5. Age-ambiguous donor exclusion from the metadata-only arm (dev n=259, not 261)

**What PREREG said:** No mechanism was pre-specified for donors with
internally-inconsistent age annotation; the metadata-only arm was implicitly
expected to use all available dev donors with a valid age.

**What was done:** L2 metadata processing (2026-07-19) found two dev donors
(`1130`, `1772`) with two distinct `development_stage` values recorded across
their own cells (a likely birthday-crossing artifact, not independently confirmed
against the source publication). Per human decision, these were **not** resolved
by imputation (e.g., taking the minimum or an average) — both are flagged
`age_flag=age_ambiguous` and **excluded from the metadata-only arm specifically**.
The metadata-only arm's effective dev n is **259**, not 261. Both donors remain
in the full 261-donor set for the Geneformer and pseudobulk arms, which do not
use the age field.

**Why:** Imputing a specific value for genuinely ambiguous source data would be
an undisclosed assumption; exclusion with an explicit flag is more honest given
no way to determine the correct value from available metadata.

**Could it affect results:** Yes, marginally — the metadata-only arm's committed
dev-CV AUROC (0.6453) and its Phase 3 frozen final-fit (used to produce the
sealed AUROC of 0.5781) are both computed on n=259, not n=261. A roughly
0.8%-of-cohort exclusion; small but real and disclosed, not silently absorbed.

**Source:** PREREG.md amendment log, entry dated **2026-07-19**, "L2 dev-cohort
metadata: age-ambiguous donor exclusion."

---

## 6. Pseudobulk (and all three arms') final-coefficient refit at frozen hyperparameters

**What PREREG said:** The frozen pipeline should be applied to sealed data with
"no retraining, no refitting" of hyperparameters after dev-cohort nested CV
selects them.

**What was done:** The dev-cohort nested cross-validation that produced every
committed dev AUROC (`results/l2_dev_sle_vs_healthy.csv`) only ever generated
out-of-fold *predictions* for honest AUROC estimation — it never persisted a
single final fitted model. Consequently, no coefficient vector existed anywhere
that could literally be "applied" to sealed data. Before touching any sealed
prediction, one standard final fit — `StandardScaler` + `LogisticRegression` at
the *already-selected, frozen* `C` from `FREEZE.json` (pseudobulk C=0.01 on the
30,165-gene-restricted dev representation; Geneformer C=1.0 on the unchanged
256-dim dev embeddings; metadata-age C=0.001 on dev age) — was performed once per
arm on the full dev cohort. These fitted parameters were used to score sealed
data and were never touched again afterward.

**Why:** There is no way to produce an actual scoring function from a
nested-CV protocol that only ever yields out-of-fold predictions, other than one
final fit at the hyperparameter nested CV already selected. This is standard
practice (a final refit at chosen hyperparameters), not a re-selection of those
hyperparameters — the `C` values themselves were pulled unchanged from
`FREEZE.json` and are identical to the values nested CV originally selected.

**Could it affect results:** This step is a *precondition* for Phase 3 to exist
at all — every sealed AUROC number is downstream of it, by necessity. It is
disclosed clearly as a required, one-time, pre-sealed-data step, distinct in kind
from "retuning" (which would mean changing `C` in response to a sealed result —
verified not to have happened: the `C` values used exactly match `FREEZE.json`).

**Source:** commit `364761c`'s message, "Methodology locked before any sealed
prediction was computed" section; `FREEZE.json`'s
`hyperparameter_selection_rule` field.

---

## Summary table

| # | Deviation | Affects committed dev CV numbers? | Affects sealed-cohort numbers? |
|---|---|---|---|
| 1 | Gene-space restriction convention (raw-count-first) | No | Yes — pseudobulk sealed AUROC is downstream of this choice |
| 2 | Cell-type / cohort-signature-probe deferral | No | No effect on primary/co-primary results; the pre-registered confounding probe was not run |
| 3 | Freeze-guard not wired into scripts 19/20 at run time | No | No evidence of effect (freeze was valid throughout); process gap only |
| 4 | 56 vs. 58 GSE135779 samples | No | Yes — all sealed statistics are computed on real n=56 |
| 5 | Age-ambiguous donor exclusion (n=259) | Yes — metadata-arm dev AUROC is on n=259, not 261 | Yes — the frozen metadata-arm model was fit on n=259 |
| 6 | Final-coefficient refit at frozen C | No — dev CV numbers predate and are independent of this step | Yes — required for every sealed prediction to exist |
