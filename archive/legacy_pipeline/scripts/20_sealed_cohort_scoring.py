"""Phase 3: score the sealed cohort (GSE135779) with the frozen pipeline.

This is the single sealed-cohort opening, per PREREG.md/FREEZE.json. Every
methodological choice here was locked BEFORE this script was run against
real sealed predictions:

- Frozen hyperparameters (C) per arm: pulled from FREEZE.json, never
  reselected here.
- "Frozen pipeline, no retraining/refitting": nested CV on dev data only
  ever produced out-of-fold predictions, never a persisted final model. This
  script performs the one standard, necessary "final fit at the already-
  chosen hyperparameter" step per arm -- fit once, on all of dev, at
  C_frozen, BEFORE loading or touching any sealed prediction. Once fit,
  these coefficients are used to score sealed data and are never refit
  afterward regardless of what the sealed result shows.
- Pseudobulk gene-space handling: human-locked decision (2026-07-21) to
  restrict raw counts to the 30,165-gene intersection first, then
  CPM-normalize over that restricted total, for BOTH cohorts (matches
  PREREG Section 8's literal text). Dev's restricted representation was
  re-derived via kaggle_kernels/l2_dev_pseudobulk_restricted/ specifically
  for this purpose; the ORIGINAL committed dev pseudobulk AUROC (0.9839,
  full 61,497-gene space) is unchanged and is not what is used to fit the
  sealed-scoring model.
- Geneformer and metadata-age arms need no gene-space restriction: Geneformer
  embeddings are a fixed 256-dim space regardless of gene universe (the
  tokenizer handles gene-vocabulary differences internally, same as it did
  for dev), and metadata-age involves no genes at all.

Permutation test on sealed data: since sealed scoring is a single frozen
prediction vector (no CV, no refitting), the permutation null is the
standard, cheap form -- shuffle sealed LABELS against the FIXED predicted
probabilities and recompute AUROC, 1000 times. No model refitting occurs in
this step at all.

Co-primary comparisons A (Geneformer vs metadata) and B (Geneformer vs
pseudobulk): implemented exactly per PREREG Sections 5 and 6 -- paired
patient-bootstrap CI on the AUROC difference (same resampled patient index
set applied to both arms per replicate, preserving pairing), paired
permutation test (same permuted label vector applied to both arms per
replicate) for the two-sided p-value, then the literal Holm step-down
procedure from Section 6 (p(1) vs alpha/2, then p(2) vs alpha).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, str(Path(__file__).resolve().parent))
from freeze_guard import mark_sealed_opened, require_valid_freeze  # noqa: E402

require_valid_freeze()

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_ROOT / "results"

RANDOM_STATE = 20260721
N_BOOTSTRAP = 5000
N_PERMUTATIONS = 1000
ALPHA = 0.05


def load_freeze() -> dict:
    with open(REPO_ROOT / "FREEZE.json") as f:
        return json.load(f)


def fit_final_model(X: np.ndarray, y: np.ndarray, C: float) -> tuple[StandardScaler, LogisticRegression]:
    """The one necessary 'final fit at the frozen hyperparameter' step.
    Not hyperparameter selection (C is passed in, already chosen). Called
    exactly once per arm, before any sealed data is loaded or scored.
    """
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    clf = LogisticRegression(C=C, l1_ratio=0, max_iter=2000, solver="lbfgs")
    clf.fit(Xs, y)
    return scaler, clf


def score_frozen(scaler: StandardScaler, clf: LogisticRegression, X_sealed: np.ndarray) -> np.ndarray:
    """Apply an already-fit, frozen scaler+classifier to sealed data. No
    fitting happens here -- transform() and predict_proba() only."""
    Xs = scaler.transform(X_sealed)
    return clf.predict_proba(Xs)[:, 1]


def patient_bootstrap_ci(y: np.ndarray, proba: np.ndarray, n_bootstrap: int, seed: int) -> tuple[float, float, int]:
    rng = np.random.RandomState(seed)
    n = len(y)
    boot = []
    skipped = 0
    for _ in range(n_bootstrap):
        idx = rng.randint(0, n, size=n)
        y_b, p_b = y[idx], proba[idx]
        if len(np.unique(y_b)) < 2:
            skipped += 1
            continue
        boot.append(roc_auc_score(y_b, p_b))
    lo, hi = np.percentile(boot, [2.5, 97.5])
    return float(lo), float(hi), skipped


def permutation_p_single_arm(y: np.ndarray, proba: np.ndarray, observed_auroc: float,
                              n_perm: int, seed: int) -> tuple[float, float, float]:
    """Fixed predictions, shuffled labels -- no refitting. Returns
    (p_value, null_mean, null_std)."""
    rng = np.random.RandomState(seed)
    null = np.empty(n_perm)
    for i in range(n_perm):
        y_perm = rng.permutation(y)
        null[i] = roc_auc_score(y_perm, proba)
    extreme = np.sum(np.abs(null - 0.5) >= np.abs(observed_auroc - 0.5))
    p = (1 + extreme) / (n_perm + 1)
    return float(p), float(null.mean()), float(null.std())


def paired_bootstrap_ci_diff(y: np.ndarray, proba_a: np.ndarray, proba_b: np.ndarray,
                              n_bootstrap: int, seed: int) -> tuple[float, float, float, int]:
    """Bootstrap CI on AUROC(a) - AUROC(b), same resampled patient index set
    for both arms per replicate (preserves pairing)."""
    rng = np.random.RandomState(seed)
    n = len(y)
    diffs = []
    skipped = 0
    for _ in range(n_bootstrap):
        idx = rng.randint(0, n, size=n)
        y_b = y[idx]
        if len(np.unique(y_b)) < 2:
            skipped += 1
            continue
        auroc_a = roc_auc_score(y_b, proba_a[idx])
        auroc_b = roc_auc_score(y_b, proba_b[idx])
        diffs.append(auroc_a - auroc_b)
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return float(lo), float(hi), float(np.mean(diffs)), skipped


def paired_permutation_p_diff(y: np.ndarray, proba_a: np.ndarray, proba_b: np.ndarray,
                               observed_diff: float, n_perm: int, seed: int) -> tuple[float, float, float]:
    """Two-sided permutation p-value on the paired AUROC difference: same
    permuted label vector applied to both arms per replicate. No refitting."""
    rng = np.random.RandomState(seed)
    null = np.empty(n_perm)
    for i in range(n_perm):
        y_perm = rng.permutation(y)
        null[i] = roc_auc_score(y_perm, proba_a) - roc_auc_score(y_perm, proba_b)
    extreme = np.sum(np.abs(null) >= np.abs(observed_diff))
    p = (1 + extreme) / (n_perm + 1)
    return float(p), float(null.mean()), float(null.std())


def holm_two(p_values: dict[str, float], alpha: float = ALPHA) -> dict:
    """Literal PREREG Section 6 procedure for exactly 2 tests."""
    ranked = sorted(p_values.items(), key=lambda kv: kv[1])
    (name1, p1), (name2, p2) = ranked
    result = {
        "ranked_order": [name1, name2],
        "p1_name": name1, "p1": p1, "threshold1": alpha / 2,
        "p2_name": name2, "p2": p2, "threshold2": alpha,
        "significant": [],
    }
    if p1 > alpha / 2:
        result["stop_reason"] = f"p(1)={p1:.6f} > alpha/2={alpha/2}: stop, neither significant"
        return result
    result["significant"].append(name1)
    if p2 <= alpha:
        result["significant"].append(name2)
        result["stop_reason"] = f"p(1) significant; p(2)={p2:.6f} <= alpha={alpha}: both significant"
    else:
        result["stop_reason"] = f"p(1) significant; p(2)={p2:.6f} > alpha={alpha}: only p(1) significant"
    return result


def load_dev_metadata() -> pd.DataFrame:
    return pd.read_csv(RESULTS_DIR / "l2_dev_donor_metadata.csv", dtype={"donor_id": str}).set_index("donor_id")


def load_sealed_metadata() -> pd.DataFrame:
    return pd.read_csv(RESULTS_DIR / "l2_sealed_donor_metadata.csv", dtype={"gsm_id": str}).set_index("gsm_id")


def fit_and_score_arm(arm_name: str, X_dev: np.ndarray, y_dev: np.ndarray, C_frozen: float,
                       X_sealed: np.ndarray, y_sealed: np.ndarray) -> dict:
    print(f"[{arm_name}] final fit on dev: n={len(y_dev)}, n_features={X_dev.shape[1]}, C={C_frozen} (frozen)")
    scaler, clf = fit_final_model(X_dev, y_dev, C_frozen)

    proba_sealed = score_frozen(scaler, clf, X_sealed)
    auroc = roc_auc_score(y_sealed, proba_sealed)
    print(f"[{arm_name}] sealed AUROC (overall, n={len(y_sealed)}) = {auroc:.4f}")

    ci_lo, ci_hi, boot_skipped = patient_bootstrap_ci(y_sealed, proba_sealed, N_BOOTSTRAP, RANDOM_STATE)
    print(f"[{arm_name}] sealed 95% CI = [{ci_lo:.4f}, {ci_hi:.4f}] ({boot_skipped} degenerate skipped)")

    p_value, null_mean, null_std = permutation_p_single_arm(y_sealed, proba_sealed, auroc, N_PERMUTATIONS, RANDOM_STATE)
    print(f"[{arm_name}] sealed permutation p={p_value:.5f}, null_mean={null_mean:.4f}")

    return {
        "arm": arm_name,
        "n_sealed": int(len(y_sealed)),
        "n_features": int(X_dev.shape[1]),
        "C_frozen": C_frozen,
        "sealed_auroc_overall": float(auroc),
        "sealed_ci95_overall": [ci_lo, ci_hi],
        "sealed_permutation_p_overall": p_value,
        "sealed_permutation_null_mean_overall": null_mean,
        "sealed_permutation_null_std_overall": null_std,
        "bootstrap_degenerate_skipped": boot_skipped,
        "_scaler": scaler, "_clf": clf, "_proba_sealed": proba_sealed, "_y_sealed": y_sealed,
    }


def stratified_scores(arm_result: dict, age_group: pd.Series) -> dict:
    """Recompute AUROC + CI on age-group subsets, using the SAME frozen
    predictions already computed -- no refitting, just subsetting."""
    proba = arm_result["_proba_sealed"]
    y = arm_result["_y_sealed"]
    out = {}
    for group_name in ["Children", "Adult"]:
        mask = (age_group == group_name).to_numpy()
        n = int(mask.sum())
        y_g, p_g = y[mask], proba[mask]
        if len(np.unique(y_g)) < 2:
            out[group_name] = {"n": n, "auroc": None, "note": "single class in this stratum, AUROC undefined"}
            continue
        auroc_g = roc_auc_score(y_g, p_g)
        ci_lo, ci_hi, skipped = patient_bootstrap_ci(y_g, p_g, N_BOOTSTRAP, RANDOM_STATE)
        out[group_name] = {
            "n": n, "auroc": float(auroc_g), "ci95": [ci_lo, ci_hi],
            "bootstrap_degenerate_skipped": skipped,
        }
        print(f"    [{arm_result['arm']}] {group_name} (n={n}): AUROC={auroc_g:.4f}, CI=[{ci_lo:.4f}, {ci_hi:.4f}]")
    return out


def main() -> dict:
    freeze = load_freeze()
    hp = freeze["hyperparameters"]

    dev_meta = load_dev_metadata()
    sealed_meta = load_sealed_metadata()

    print("=== sealed cohort structural check ===")
    print(f"sealed samples: {len(sealed_meta)} (expected 56)")
    assert len(sealed_meta) == 56
    print(f"sealed SLE/healthy: {sealed_meta['sle_label'].sum()}/{(sealed_meta['sle_label']==0).sum()} "
          f"(expected 40/16)")
    assert sealed_meta["sle_label"].sum() == 40 and (sealed_meta["sle_label"] == 0).sum() == 16
    print(f"sealed age groups: {sealed_meta['age_group'].value_counts().to_dict()} (expected Children:44, Adult:12)")

    results = {}

    # --- Arm: pseudobulk (gene-restricted, 30165 genes) ---
    pb_dev = pd.read_parquet(RESULTS_DIR / "l2_dev_pseudobulk_counts_restricted.parquet")
    pb_sealed = pd.read_parquet(RESULTS_DIR / "l2_sealed_pseudobulk_counts.parquet")
    assert set(pb_dev.columns) == set(pb_sealed.columns), "dev/sealed pseudobulk gene SETS must match exactly"
    # Same 30,165-gene set, but the two Kaggle kernels produced different
    # (both internally consistent) column orders -- dev used the census var
    # table's order, sealed used GSE135779's own genes.tsv row order.
    # Reindex both to one canonical, deterministic order before fitting/scoring.
    canonical_gene_order = sorted(pb_dev.columns)
    pb_dev = pb_dev.loc[dev_meta.index, canonical_gene_order]
    pb_sealed = pb_sealed.loc[sealed_meta.index, canonical_gene_order]
    assert list(pb_dev.columns) == list(pb_sealed.columns), "canonical reindex failed"

    y_dev_pb = dev_meta["sle_label"].to_numpy()
    y_sealed_pb = sealed_meta["sle_label"].to_numpy()
    results["pseudobulk"] = fit_and_score_arm(
        "pseudobulk", pb_dev.to_numpy(), y_dev_pb, hp["pseudobulk"]["C_frozen"],
        pb_sealed.to_numpy(), y_sealed_pb,
    )
    results["pseudobulk"]["stratified"] = stratified_scores(results["pseudobulk"], sealed_meta["age_group"])

    # --- Arm: metadata-only (age) ---
    dev_meta_eligible = dev_meta[dev_meta["metadata_arm_eligible"]]
    y_dev_age = dev_meta_eligible["sle_label"].to_numpy()
    X_dev_age = dev_meta_eligible[["age"]].to_numpy().astype(float)
    y_sealed_age = sealed_meta["sle_label"].to_numpy()
    X_sealed_age = sealed_meta[["age"]].to_numpy().astype(float)
    results["metadata_only_age"] = fit_and_score_arm(
        "metadata_only_age", X_dev_age, y_dev_age, hp["metadata_only_age"]["C_frozen"],
        X_sealed_age, y_sealed_age,
    )
    results["metadata_only_age"]["stratified"] = stratified_scores(results["metadata_only_age"], sealed_meta["age_group"])

    # --- Arm: Geneformer ---
    gf_sealed_path = RESULTS_DIR / "l2_sealed_geneformer_embeddings.parquet"
    if gf_sealed_path.exists():
        gf_dev = pd.read_parquet(RESULTS_DIR / "l2_dev_geneformer_embeddings.parquet").loc[dev_meta.index]
        gf_sealed = pd.read_parquet(gf_sealed_path).loc[sealed_meta.index]
        y_dev_gf = dev_meta["sle_label"].to_numpy()
        y_sealed_gf = sealed_meta["sle_label"].to_numpy()
        results["geneformer"] = fit_and_score_arm(
            "geneformer", gf_dev.to_numpy(), y_dev_gf, hp["geneformer"]["C_frozen"],
            gf_sealed.to_numpy(), y_sealed_gf,
        )
        results["geneformer"]["stratified"] = stratified_scores(results["geneformer"], sealed_meta["age_group"])
    else:
        print(f"\n[geneformer] SKIPPED: {gf_sealed_path} does not exist yet.")
        results["geneformer"] = None

    return results


def co_primary_comparison(name: str, arm_a: dict, arm_b: dict) -> dict:
    """PREREG Section 5: H = AUROC(a) - AUROC(b) > 0 on the sealed cohort,
    one-sided directional hypothesis, decision rule combines a paired
    bootstrap CI (must exclude 0 and lie entirely above 0) with Holm-
    corrected significance (Section 6) -- computed separately by the caller
    across the two-comparison family.
    """
    y = arm_a["_y_sealed"]
    assert np.array_equal(y, arm_b["_y_sealed"]), "paired comparison requires the same sealed labels for both arms"
    proba_a, proba_b = arm_a["_proba_sealed"], arm_b["_proba_sealed"]

    observed_diff = arm_a["sealed_auroc_overall"] - arm_b["sealed_auroc_overall"]
    ci_lo, ci_hi, boot_mean, boot_skipped = paired_bootstrap_ci_diff(y, proba_a, proba_b, N_BOOTSTRAP, RANDOM_STATE)
    p_value, null_mean, null_std = paired_permutation_p_diff(y, proba_a, proba_b, observed_diff, N_PERMUTATIONS, RANDOM_STATE)

    ci_excludes_zero_and_positive = ci_lo > 0
    print(f"[{name}] observed diff = {observed_diff:.4f}, bootstrap 95% CI = [{ci_lo:.4f}, {ci_hi:.4f}], "
          f"permutation p (pre-Holm) = {p_value:.5f}")

    return {
        "comparison": name,
        "arm_a": arm_a["arm"], "arm_b": arm_b["arm"],
        "observed_auroc_diff": float(observed_diff),
        "bootstrap_ci95_diff": [ci_lo, ci_hi],
        "bootstrap_diff_mean": boot_mean,
        "bootstrap_degenerate_skipped": boot_skipped,
        "permutation_p_two_sided_pre_holm": p_value,
        "permutation_null_mean": null_mean,
        "permutation_null_std": null_std,
        "ci_condition_met": ci_excludes_zero_and_positive,
    }


def strip_internal(arm_result: dict) -> dict:
    return {k: v for k, v in arm_result.items() if not k.startswith("_")}


def main_full() -> None:
    results = main()
    if not all(results.get(a) is not None for a in ("geneformer", "pseudobulk", "metadata_only_age")):
        print("\nNot all arms scored -- stopping without writing the final artifact or co-primary comparisons.")
        return

    print("\n=== co-primary comparisons (PREREG Section 5/6) ===")
    comp_a = co_primary_comparison("A_geneformer_vs_metadata", results["geneformer"], results["metadata_only_age"])
    comp_b = co_primary_comparison("B_geneformer_vs_pseudobulk", results["geneformer"], results["pseudobulk"])

    holm = holm_two({
        "A_geneformer_vs_metadata": comp_a["permutation_p_two_sided_pre_holm"],
        "B_geneformer_vs_pseudobulk": comp_b["permutation_p_two_sided_pre_holm"],
    })
    print(f"\nHolm step-down: {holm}")

    for comp in (comp_a, comp_b):
        name = comp["comparison"]
        holm_significant = name in holm["significant"]
        comp["holm_significant"] = holm_significant
        comp["decision"] = "GO" if (comp["ci_condition_met"] and holm_significant) else "REJECTED"
        print(f"[{name}] decision = {comp['decision']} "
              f"(ci_condition_met={comp['ci_condition_met']}, holm_significant={holm_significant})")

    freeze = load_freeze()
    from datetime import datetime, timezone

    output = {
        "phase": 3,
        "opened_at_utc": datetime.now(timezone.utc).isoformat(),
        "freeze_commit_sha": freeze["commit_sha"],
        "random_state": RANDOM_STATE,
        "bootstrap_n": N_BOOTSTRAP,
        "permutation_n": N_PERMUTATIONS,
        "sealed_cohort": {
            "accession": "GSE135779",
            "n_samples": 56,
            "breakdown": "33 cSLE + 11 cHD (pediatric primary) + 7 aSLE + 5 aHD (adult, of 8/6 described)",
            "sle_label_counts": {"SLE": 40, "healthy": 16},
            "age_group_counts": {"Children": 44, "Adult": 12},
        },
        "arms": {
            "geneformer": strip_internal(results["geneformer"]),
            "pseudobulk": strip_internal(results["pseudobulk"]),
            "metadata_only_age": strip_internal(results["metadata_only_age"]),
        },
        "co_primary_comparisons": {
            "A_geneformer_vs_metadata": comp_a,
            "B_geneformer_vs_pseudobulk": comp_b,
            "holm_step_down": holm,
        },
        "chain_of_custody": {
            "gene_reference_downloaded_from": "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE135nnn/GSE135779/suppl/GSE135779_genes.tsv.gz",
            "raw_counts_downloaded_from": "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE135nnn/GSE135779/suppl/GSE135779_RAW.tar",
            "raw_counts_local_download_path": "data/raw/GSE135779/GSE135779_RAW.tar",
            "sealed_pseudobulk_processed_by": "scripts/19_sealed_pseudobulk.py (local)",
            "sealed_geneformer_processed_by": "kaggle_kernels/l2_geneformer_sealed/ (Kaggle T4, real GPU embedding of real sealed cells)",
            "dev_pseudobulk_restricted_derived_by": "kaggle_kernels/l2_dev_pseudobulk_restricted/ (Kaggle, CPU)",
            "dev_geneformer_embeddings_source": "results/l2_dev_geneformer_embeddings.parquet (already committed, unchanged)",
            "freeze_manifest": "FREEZE.json",
            "gene_space_intersection_source": "results/gene_space_intersection.txt (30,165 genes, already committed)",
        },
    }

    out_path = RESULTS_DIR / "l2_sealed_results.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nwrote {out_path}")

    mark_sealed_opened(results_path=out_path)


if __name__ == "__main__":
    main_full()
