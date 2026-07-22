"""Part A: paired difference CIs for the co-primary comparisons, computed
ONLY from already-committed per-donor sealed predictions
(results/l2_sealed_predictions_regenerated.json). No sealed raw data is
accessed. No new sealed prediction is produced -- every number here is a
difference or resampling of predictions that already exist and were
already verified (in that file's own generation, scripts/22) to match
results/l2_sealed_results.json exactly.

This script performs an independent cross-check of the already-committed
co-primary comparison results: same predictions, same seed convention, same
math as scripts/20_sealed_cohort_scoring.py's paired_bootstrap_ci_diff /
paired_permutation_p_diff / holm_two (reproduced here rather than imported,
since scripts/20 calls require_valid_freeze() at import time and would
correctly refuse now that SEALED_OPENED.json exists -- importing it would
itself be inappropriate here). If this script's recomputed CI/p/decision
does not match the already-committed results/l2_sealed_results.json, that
is reported as a real discrepancy, not silently resolved.

Hard gate: aborts before computing anything if any arm's recomputed AUROC
does not match results/l2_sealed_results.json bit-for-bit (tolerance 1e-9).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_ROOT / "results"

RANDOM_STATE = 20260721  # same seed convention as scripts/20
N_BOOTSTRAP = 5000
N_PERMUTATIONS = 1000
ALPHA = 0.05


def paired_bootstrap_ci_diff(y, proba_a, proba_b, n_bootstrap, seed):
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


def paired_permutation_p_diff(y, proba_a, proba_b, observed_diff, n_perm, seed):
    rng = np.random.RandomState(seed)
    null = np.empty(n_perm)
    for i in range(n_perm):
        y_perm = rng.permutation(y)
        null[i] = roc_auc_score(y_perm, proba_a) - roc_auc_score(y_perm, proba_b)
    extreme = np.sum(np.abs(null) >= np.abs(observed_diff))
    p = (1 + extreme) / (n_perm + 1)
    return float(p), float(null.mean()), float(null.std())


def holm_two(p_values: dict, alpha: float = ALPHA) -> dict:
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


def main() -> None:
    with open(RESULTS_DIR / "l2_sealed_predictions_regenerated.json") as f:
        preds = json.load(f)
    with open(RESULTS_DIR / "l2_sealed_results.json") as f:
        committed = json.load(f)

    # --- hard gate: bit-for-bit AUROC cross-check before trusting anything ---
    print("=== bit-for-bit cross-check: recomputed AUROC vs. committed ===")
    for arm in ("geneformer", "pseudobulk", "metadata_only_age"):
        y = np.array(preds[arm]["y"])
        proba = np.array(preds[arm]["proba"])
        recomputed = roc_auc_score(y, proba)
        committed_auroc = committed["arms"][arm]["sealed_auroc_overall"]
        match = abs(recomputed - committed_auroc) < 1e-9
        print(f"[{arm}] recomputed={recomputed!r} committed={committed_auroc!r} match={match}")
        if not match:
            raise SystemExit(
                f"ABORT: {arm} recomputed AUROC does not match committed value. "
                "Refusing to compute paired differences from unverified predictions."
            )
    print("All three arms match bit-for-bit. Proceeding.\n")

    y = np.array(preds["geneformer"]["y"])
    assert np.array_equal(y, np.array(preds["pseudobulk"]["y"]))
    assert np.array_equal(y, np.array(preds["metadata_only_age"]["y"]))
    proba_gf = np.array(preds["geneformer"]["proba"])
    proba_pb = np.array(preds["pseudobulk"]["proba"])
    proba_meta = np.array(preds["metadata_only_age"]["proba"])

    comparisons = {}
    for name, proba_a, proba_b in [
        ("A_geneformer_vs_metadata", proba_gf, proba_meta),
        ("B_geneformer_vs_pseudobulk", proba_gf, proba_pb),
    ]:
        observed_diff = float(roc_auc_score(y, proba_a) - roc_auc_score(y, proba_b))
        ci_lo, ci_hi, boot_mean, boot_skipped = paired_bootstrap_ci_diff(
            y, proba_a, proba_b, N_BOOTSTRAP, RANDOM_STATE
        )
        p_value, null_mean, null_std = paired_permutation_p_diff(
            y, proba_a, proba_b, observed_diff, N_PERMUTATIONS, RANDOM_STATE
        )
        print(f"[{name}] diff={observed_diff:+.4f} CI=[{ci_lo:+.4f}, {ci_hi:+.4f}] "
              f"p={p_value:.5f} (pre-Holm)")
        comparisons[name] = {
            "observed_auroc_diff": observed_diff,
            "bootstrap_ci95_diff": [ci_lo, ci_hi],
            "bootstrap_diff_mean": boot_mean,
            "bootstrap_degenerate_skipped": boot_skipped,
            "permutation_p_two_sided_pre_holm": p_value,
            "permutation_null_mean": null_mean,
            "permutation_null_std": null_std,
            "ci_condition_met": ci_lo > 0,
        }

    holm = holm_two({k: v["permutation_p_two_sided_pre_holm"] for k, v in comparisons.items()})
    print(f"\nHolm step-down: {holm}")

    for name, c in comparisons.items():
        holm_sig = name in holm["significant"]
        c["holm_significant"] = holm_sig
        c["decision"] = "GO" if (c["ci_condition_met"] and holm_sig) else "REJECTED"
        print(f"[{name}] decision = {c['decision']}")

    # --- cross-check against the already-committed co-primary comparisons ---
    print("\n=== cross-check vs. already-committed co_primary_comparisons ===")
    all_match = True
    for name in comparisons:
        committed_c = committed["co_primary_comparisons"][name]
        diff_match = abs(comparisons[name]["observed_auroc_diff"] - committed_c["observed_auroc_diff"]) < 1e-9
        p_match = abs(comparisons[name]["permutation_p_two_sided_pre_holm"] -
                       committed_c["permutation_p_two_sided_pre_holm"]) < 1e-6
        decision_match = comparisons[name]["decision"] == committed_c["decision"]
        print(f"[{name}] diff_match={diff_match} p_match={p_match} decision_match={decision_match}")
        all_match = all_match and diff_match and p_match and decision_match
    print(f"\nFull agreement with committed results: {all_match}")

    output = {
        "purpose": (
            "Independent Part-A recomputation of the co-primary comparison paired "
            "difference CIs, from already-committed per-donor sealed predictions "
            "only (results/l2_sealed_predictions_regenerated.json). No sealed raw "
            "data accessed; no new sealed prediction produced -- only differences "
            "and resamplings of predictions that already existed and were already "
            "verified against results/l2_sealed_results.json."
        ),
        "bit_for_bit_auroc_cross_check": "PASS (see console log; aborted before this point if any mismatch)",
        "agreement_with_committed_results": all_match,
        "comparisons": comparisons,
        "holm_step_down": holm,
        "random_state": RANDOM_STATE,
        "bootstrap_n": N_BOOTSTRAP,
        "permutation_n": N_PERMUTATIONS,
    }
    out_path = RESULTS_DIR / "l2_coprimary_difference_ci.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
