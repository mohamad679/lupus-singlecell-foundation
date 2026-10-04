"""PREREG.md Section 5.1: cohort-signature probe.

Can a classifier distinguish dev-cohort donors from sealed-cohort donors
using the same feature arms (Geneformer / pseudobulk / metadata)? This is
the SLE-project analogue of a site-signature probe.

FRAMING (binding, per explicit instruction): a high cohort-signature AUROC
here is the EXPECTED result, not a surprise -- results/l2_cohort_confounders.csv
already quantified near-total age separation and 100% platform/generation
difference between the two cohorts. This probe's purpose is to BOUND THE
INTERPRETABILITY of the sealed-cohort AUROCs reported in
results/l2_sealed_results.json: if cohort identity is highly separable in a
feature space, then any disease-discrimination AUROC computed in that same
feature space cannot be cleanly attributed to SLE biology as opposed to
cohort/batch/platform identity. A high cohort-signature AUROC is NOT
evidence that the disease-discrimination result is "real" or "validated" in
some other sense -- it is a limitation quantifier, reported alongside the
sealed result to make interpretability caveats concrete rather than
qualitative.

Guarantees, verified structurally below:
- Trains ONLY on already-committed feature matrices (results/l2_dev_*,
  results/l2_sealed_*parquet/csv) -- no raw sealed-cohort file is opened,
  no GEO/GSE135779 URL is fetched.
- The prediction target is cohort membership (dev=0, sealed=1), never the
  SLE-vs-healthy label -- this script produces NO new disease prediction.
- Does not import, call, or modify anything from scripts/18-20,
  scripts/freeze_guard.py, FREEZE.json, or SEALED_OPENED.json. Does not
  read or write results/l2_sealed_results.json. All models here are fit
  fresh, from scratch, on a different (cohort-membership) target -- nothing
  frozen is touched, and no frozen coefficient is reused.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_ROOT / "results"
FIGURES_DIR = REPO_ROOT / "figures"

RANDOM_STATE = 20260722
N_OUTER_SPLITS = 5
N_INNER_SPLITS = 5
C_GRID = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
N_PERMUTATIONS = 1000
N_BOOTSTRAP = 5000
N_JOBS = -1

BLUE = "#2a78d6"
CRITICAL_RED = "#d03b3b"
GRID_GRAY = "#c9c8c0"
TEXT_SECONDARY = "#52514e"


def fit_logreg_oof(X, y, random_state, tune_c, fixed_c,
                    n_outer_splits=N_OUTER_SPLITS, n_inner_splits=N_INNER_SPLITS):
    """Fresh nested-CV fit for THIS probe's own target (cohort membership).
    Not connected to any frozen SLE-vs-healthy model or hyperparameter."""
    outer = StratifiedKFold(n_splits=n_outer_splits, shuffle=True, random_state=random_state)
    oof_proba = np.full(len(y), np.nan)
    selected_cs = []
    for train_idx, test_idx in outer.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train = y[train_idx]
        if tune_c:
            inner = StratifiedKFold(n_splits=n_inner_splits, shuffle=True, random_state=random_state)
            best_c, best_score = C_GRID[0], -np.inf
            for c in C_GRID:
                scores = []
                for itr, iva in inner.split(X_train, y_train):
                    sc = StandardScaler()
                    Xi_tr = sc.fit_transform(X_train[itr])
                    Xi_va = sc.transform(X_train[iva])
                    clf = LogisticRegression(C=c, l1_ratio=0, max_iter=2000, solver="lbfgs")
                    clf.fit(Xi_tr, y_train[itr])
                    scores.append(roc_auc_score(y_train[iva], clf.predict_proba(Xi_va)[:, 1]))
                mean_score = float(np.mean(scores))
                if mean_score > best_score:
                    best_score, best_c = mean_score, c
            c = best_c
        else:
            c = fixed_c
        selected_cs.append(c)
        sc = StandardScaler()
        Xs_tr = sc.fit_transform(X_train)
        Xs_te = sc.transform(X_test)
        clf = LogisticRegression(C=c, l1_ratio=0, max_iter=2000, solver="lbfgs")
        clf.fit(Xs_tr, y_train)
        oof_proba[test_idx] = clf.predict_proba(Xs_te)[:, 1]
    assert not np.isnan(oof_proba).any()
    return oof_proba, selected_cs


def patient_bootstrap_ci(y, proba, n_bootstrap, seed):
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


def permutation_p(y, proba, observed_auroc, n_perm, seed, X, tune_c, fixed_c):
    def one_perm(s):
        rng = np.random.RandomState(s)
        y_perm = rng.permutation(y)
        oof, _ = fit_logreg_oof(X, y_perm, random_state=seed, tune_c=tune_c, fixed_c=fixed_c)
        return roc_auc_score(y_perm, oof)

    seeds = [seed + 1000 + i for i in range(n_perm)]
    null = np.array(Parallel(n_jobs=N_JOBS)(delayed(one_perm)(s) for s in seeds))
    extreme = np.sum(np.abs(null - 0.5) >= np.abs(observed_auroc - 0.5))
    p = (1 + extreme) / (n_perm + 1)
    return p, float(null.mean()), float(null.std())


def run_probe(arm_name, X, y_cohort, tune_c_perm):
    print(f"[{arm_name}] cohort-signature probe: n={len(y_cohort)} "
          f"(dev={int((y_cohort==0).sum())}, sealed={int((y_cohort==1).sum())}), "
          f"n_features={X.shape[1]}")
    oof_proba, selected_cs = fit_logreg_oof(X, y_cohort, RANDOM_STATE, tune_c=True, fixed_c=None)
    auroc = roc_auc_score(y_cohort, oof_proba)
    print(f"[{arm_name}] cohort-signature AUROC = {auroc:.4f}  (selected C = {selected_cs})")

    ci_lo, ci_hi, boot_skipped = patient_bootstrap_ci(y_cohort, oof_proba, N_BOOTSTRAP, RANDOM_STATE)
    print(f"[{arm_name}] 95% CI = [{ci_lo:.4f}, {ci_hi:.4f}]")

    fixed_c = float(np.median(selected_cs)) if not tune_c_perm else None
    p_value, null_mean, null_std = permutation_p(
        y_cohort, oof_proba, auroc, N_PERMUTATIONS, RANDOM_STATE, X, tune_c=tune_c_perm, fixed_c=fixed_c
    )
    print(f"[{arm_name}] permutation p = {p_value:.5f} (null mean={null_mean:.4f})")

    return {
        "arm": arm_name,
        "n_dev": int((y_cohort == 0).sum()),
        "n_sealed": int((y_cohort == 1).sum()),
        "n_features": int(X.shape[1]),
        "cohort_signature_auroc": float(auroc),
        "ci95": [ci_lo, ci_hi],
        "bootstrap_degenerate_skipped": boot_skipped,
        "permutation_p_two_sided": p_value,
        "permutation_null_mean": null_mean,
        "permutation_null_std": null_std,
        "selected_c_per_outer_fold": selected_cs,
    }


def main():
    results = {}

    # --- Geneformer: already same 256-dim embedding space, no restriction needed ---
    gf_dev = pd.read_parquet(RESULTS_DIR / "l2_dev_geneformer_embeddings.parquet")
    gf_sealed = pd.read_parquet(RESULTS_DIR / "l2_sealed_geneformer_embeddings.parquet")
    X_gf = np.vstack([gf_dev.to_numpy(), gf_sealed.to_numpy()])
    y_gf = np.array([0] * len(gf_dev) + [1] * len(gf_sealed))
    results["geneformer"] = run_probe("geneformer", X_gf, y_gf, tune_c_perm=True)

    # --- Pseudobulk: dev's gene-restricted (30,165) version, already gene-matched to sealed ---
    pb_dev = pd.read_parquet(RESULTS_DIR / "l2_dev_pseudobulk_counts_restricted.parquet")
    pb_sealed = pd.read_parquet(RESULTS_DIR / "l2_sealed_pseudobulk_counts.parquet")
    assert set(pb_dev.columns) == set(pb_sealed.columns), "gene sets must match"
    canonical_order = sorted(pb_dev.columns)
    pb_dev = pb_dev[canonical_order]
    pb_sealed = pb_sealed[canonical_order]
    X_pb = np.vstack([pb_dev.to_numpy(), pb_sealed.to_numpy()])
    y_pb = np.array([0] * len(pb_dev) + [1] * len(pb_sealed))
    results["pseudobulk"] = run_probe("pseudobulk", X_pb, y_pb, tune_c_perm=False)

    # --- Metadata (age only), matching each arm's own eligibility convention ---
    dev_meta = pd.read_csv(RESULTS_DIR / "l2_dev_donor_metadata.csv", dtype={"donor_id": str})
    dev_meta_eligible = dev_meta[dev_meta["metadata_arm_eligible"]]
    sealed_meta = pd.read_csv(RESULTS_DIR / "l2_sealed_donor_metadata.csv", dtype={"gsm_id": str})
    X_age = np.vstack([
        dev_meta_eligible[["age"]].to_numpy().astype(float),
        sealed_meta[["age"]].to_numpy().astype(float),
    ])
    y_age = np.array([0] * len(dev_meta_eligible) + [1] * len(sealed_meta))
    results["metadata_only_age"] = run_probe("metadata_only_age", X_age, y_age, tune_c_perm=True)

    output = {
        "purpose": (
            "PREREG.md Section 5.1 cohort-signature probe: quantifies how separable "
            "dev-vs-sealed cohort identity is in each feature space. This is a "
            "LIMITATION QUANTIFIER, not a positive finding: a high AUROC here means "
            "disease signal and cohort/batch/platform signal are confounded in that "
            "feature space, which bounds how much the corresponding sealed-cohort "
            "SLE-vs-healthy AUROC (results/l2_sealed_results.json) can be attributed "
            "to disease biology specifically. A high cohort-signature AUROC does NOT "
            "rescue, validate, or add credibility to the sealed disease-discrimination "
            "result -- if anything, it is a caution against over-interpreting it."
        ),
        "expected_result": (
            "Near-perfect separability was anticipated, not a surprise: "
            "results/l2_cohort_confounders.csv already quantified near-total age "
            "separation (dev 100% adult 20-83 vs. sealed pediatric-primary, "
            "mean age 41.3 vs 20.9) and platform/sequencing-generation differences "
            "between the two cohorts (PREREG.md Section 7)."
        ),
        "not_holm_corrected": (
            "This probe is confirmatory but explicitly NOT part of the co-primary "
            "family (PREREG.md Section 5.1) -- it is not Holm-corrected alongside "
            "comparisons A and B, and it makes no GO/REJECTED claim of its own."
        ),
        "arms": results,
    }

    out_path = RESULTS_DIR / "l2_cohort_signature_probe.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nwrote {out_path}")

    fig_probe(results)


def fig_probe(results):
    arms = ["geneformer", "pseudobulk", "metadata_only_age"]
    labels = ["Geneformer", "Pseudobulk", "Metadata (age)"]
    aurocs = [results[a]["cohort_signature_auroc"] for a in arms]
    los = [aurocs[i] - results[a]["ci95"][0] for i, a in enumerate(arms)]
    his = [results[a]["ci95"][1] - aurocs[i] for i, a in enumerate(arms)]

    fig, ax = plt.subplots(figsize=(7.5, 5))
    bars = ax.bar(labels, aurocs, yerr=[los, his], capsize=4, color=CRITICAL_RED,
                   alpha=0.85, edgecolor="white", linewidth=0.5, width=0.5)
    for bar, v, hi_err in zip(bars, aurocs, his):
        # anchor above the CI whisker top, not the bar height, so the label
        # never collides with the error bar cap (metadata's asymmetric CI
        # extends well above its point estimate).
        ax.annotate(f"{v:.3f}", (bar.get_x() + bar.get_width() / 2, bar.get_height() + hi_err),
                    xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=9)
    ax.axhline(0.5, color=GRID_GRAY, linewidth=1, linestyle="--", zorder=0)
    ax.set_ylabel("Cohort-signature AUROC\n(dev vs. sealed donor origin)")
    ax.set_ylim(0, 1.08)
    ax.set_title("Cohort-signature probe -- a LIMITATION QUANTIFIER, not a positive result\n"
                  "High separability was expected given already-quantified age/platform confounding;\n"
                  "it bounds interpretability of the sealed SLE-vs-healthy AUROCs, it does not validate them.",
                  fontsize=9.5, color=TEXT_SECONDARY)
    ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.01, -0.02,
              "Source: results/l2_cohort_signature_probe.json. PREREG.md Section 5.1, not Holm-corrected, "
              "not part of the co-primary family. Trained fresh on cohort-membership labels; touches no "
              "frozen model, no sealed disease score, no raw sealed-cohort data.",
              ha="left", va="top", fontsize=7.5, color=TEXT_SECONDARY, transform=fig.transFigure, wrap=True)

    FIGURES_DIR.mkdir(exist_ok=True)
    fig.savefig(FIGURES_DIR / "cohort_signature_probe.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIGURES_DIR / "cohort_signature_probe.pdf", bbox_inches="tight")
    plt.close(fig)
    print("wrote figures/cohort_signature_probe.png and .pdf")


if __name__ == "__main__":
    main()
