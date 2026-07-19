"""L2 dev-cohort CV: pseudobulk arm + metadata-only (age) arm.

SLE vs. healthy control, patient/donor-level, per PREREG.md Section 1/3/4.
Real code, real math, local, CPU-only. Does not touch GSE135779, Geneformer,
or any stageN_*.py module. Loads only the already-committed, already-verified
artifacts: results/l2_dev_pseudobulk_counts.parquet and
results/l2_dev_donor_metadata.csv.

Structural note on "donor-grouped" CV (explicit, per instruction): both input
tables are already one row per donor (pseudobulk was summed/CPM/log1p'd per
donor; metadata is one row per donor). There is no cell-level data left to
leak across folds -- each "group" (donor) already has exactly one row, so
GroupKFold would be a no-op relative to plain StratifiedKFold and would not
provide any additional leakage protection. This is structurally different
from a subject-grouped problem with multiple correlated rows per subject
(e.g. multiple EEG epochs per subject): there, GroupKFold prevents a
subject's rows from splitting across train/test; here, there is only one row
per subject in the first place, so plain StratifiedKFold on donors already
guarantees no donor's data appears in both train and test for a given fold.
We therefore use StratifiedKFold, not GroupKFold, and this file states why
rather than adding a GroupKFold call that would be redundant.

Leaky-vs-honest ablation, reframed (explicit, per instruction): PREREG's
leaky-vs-honest ablation was written for cell-level data (cell-level split
vs. donor-grouped split). There are no cells here -- each row already is a
donor-level aggregate -- so a "leaky" cell-level split is not a coherent
concept for this arm. What we run instead, as the closest honest substitute,
is a label-permutation sanity check: the permutation-test null distribution
(1000 label-shuffled reruns of the exact same honest CV pipeline) should
collapse to a mean AUROC near 0.5 if the honest pipeline has no residual
leakage or degenerate shortcut. This is reported as "leaky_vs_honest_status"
= "not_applicable_no_cell_level_data" plus the null-distribution mean/std as
the sanity-check numbers.

Permutation-test cost note: for the pseudobulk arm (261 donors x 61,497
features), redoing a full inner-CV hyperparameter search inside each of 1000
label permutations was not attempted -- a single nested-CV fit already takes
several minutes, and 1000x that is not tractable in this environment. The
permutation null instead reuses the outer StratifiedKFold architecture with
C fixed at the value selected by nested CV on the real (unpermuted) labels.
This is a standard, documented simplification for permutation testing under
expensive hyperparameter search (see e.g. Ojala & Garriga 2010) and is
reported explicitly here, not hidden. The metadata (age-only) arm has a
single feature, so full nested CV per permutation is cheap and IS run in
full without this simplification.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from joblib import Parallel, delayed
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_ROOT / "results"

RANDOM_STATE = 20260719  # fixed for reproducibility, dated to this run
N_OUTER_SPLITS = 5
N_INNER_SPLITS = 5
C_GRID = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]
N_PERMUTATIONS = 1000
N_BOOTSTRAP = 5000
N_JOBS = -1


class L2ModelingError(RuntimeError):
    pass


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    pb = pd.read_parquet(RESULTS_DIR / "l2_dev_pseudobulk_counts.parquet")
    meta = pd.read_csv(RESULTS_DIR / "l2_dev_donor_metadata.csv", dtype={"donor_id": str})
    meta = meta.set_index("donor_id")

    if set(pb.index) != set(meta.index):
        raise L2ModelingError(
            "pseudobulk and metadata donor sets do not match: "
            f"symmetric diff = {set(pb.index).symmetric_difference(meta.index)}"
        )
    meta = meta.loc[pb.index]  # align order
    return pb, meta


def fit_logreg_oof(
    X: np.ndarray,
    y: np.ndarray,
    random_state: int,
    tune_c: bool,
    fixed_c: float | None,
    n_outer_splits: int = N_OUTER_SPLITS,
    n_inner_splits: int = N_INNER_SPLITS,
) -> tuple[np.ndarray, list[float]]:
    """Out-of-fold predicted P(SLE) via StratifiedKFold, scaler fit train-only.

    If tune_c: inner StratifiedKFold grid search over C_GRID inside each
    outer training fold (nested CV, no test-fold leakage into hyperparameter
    selection). Otherwise uses fixed_c for every outer fold.

    Returns (oof_proba, selected_c_per_fold).
    """

    outer = StratifiedKFold(n_splits=n_outer_splits, shuffle=True, random_state=random_state)
    oof_proba = np.full(len(y), np.nan)
    selected_cs: list[float] = []

    for train_idx, test_idx in outer.split(X, y):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        if tune_c:
            inner = StratifiedKFold(n_splits=n_inner_splits, shuffle=True, random_state=random_state)
            best_c, best_score = C_GRID[0], -np.inf
            for c in C_GRID:
                inner_scores = []
                for inner_train_idx, inner_val_idx in inner.split(X_train, y_train):
                    scaler = StandardScaler()
                    Xi_train = scaler.fit_transform(X_train[inner_train_idx])
                    Xi_val = scaler.transform(X_train[inner_val_idx])
                    clf = LogisticRegression(C=c, l1_ratio=0, max_iter=2000, solver="lbfgs")
                    clf.fit(Xi_train, y_train[inner_train_idx])
                    p = clf.predict_proba(Xi_val)[:, 1]
                    inner_scores.append(roc_auc_score(y_train[inner_val_idx], p))
                mean_score = float(np.mean(inner_scores))
                if mean_score > best_score:
                    best_score, best_c = mean_score, c
            c = best_c
        else:
            c = fixed_c
        selected_cs.append(c)

        scaler = StandardScaler()
        Xs_train = scaler.fit_transform(X_train)
        Xs_test = scaler.transform(X_test)
        clf = LogisticRegression(C=c, l1_ratio=0, max_iter=2000, solver="lbfgs")
        clf.fit(Xs_train, y_train)
        oof_proba[test_idx] = clf.predict_proba(Xs_test)[:, 1]

    if np.isnan(oof_proba).any():
        raise L2ModelingError("some donors never fell into a test fold; outer CV is broken.")

    return oof_proba, selected_cs


def patient_bootstrap_ci(
    y: np.ndarray, proba: np.ndarray, n_bootstrap: int, random_state: int
) -> tuple[float, float, int]:
    rng = np.random.RandomState(random_state)
    n = len(y)
    boot_aurocs = []
    skipped = 0
    for _ in range(n_bootstrap):
        idx = rng.randint(0, n, size=n)
        y_b, p_b = y[idx], proba[idx]
        if len(np.unique(y_b)) < 2:
            skipped += 1
            continue
        boot_aurocs.append(roc_auc_score(y_b, p_b))
    lo, hi = np.percentile(boot_aurocs, [2.5, 97.5])
    return float(lo), float(hi), skipped


def permutation_test(
    X: np.ndarray,
    y: np.ndarray,
    observed_auroc: float,
    n_permutations: int,
    random_state: int,
    tune_c: bool,
    fixed_c: float | None,
) -> tuple[np.ndarray, float]:
    def one_perm(seed: int) -> float:
        rng = np.random.RandomState(seed)
        y_perm = rng.permutation(y)
        proba, _ = fit_logreg_oof(
            X, y_perm, random_state=random_state, tune_c=tune_c, fixed_c=fixed_c
        )
        return roc_auc_score(y_perm, proba)

    seeds = [random_state + 1000 + i for i in range(n_permutations)]
    null_aurocs = Parallel(n_jobs=N_JOBS)(delayed(one_perm)(s) for s in seeds)
    null_aurocs = np.array(null_aurocs)

    extreme = np.sum(np.abs(null_aurocs - 0.5) >= np.abs(observed_auroc - 0.5))
    p_value = (1 + extreme) / (n_permutations + 1)
    return null_aurocs, float(p_value)


def run_arm(
    name: str,
    X: np.ndarray,
    y: np.ndarray,
    tune_c_for_real_fit: bool,
    tune_c_for_permutations: bool,
) -> dict:
    t0 = time.time()
    print(f"[{name}] real fit: n={len(y)}, n_features={X.shape[1]}, "
          f"tune_c={tune_c_for_real_fit}")
    oof_proba, selected_cs = fit_logreg_oof(
        X, y, random_state=RANDOM_STATE, tune_c=tune_c_for_real_fit, fixed_c=None
    )
    observed_auroc = roc_auc_score(y, oof_proba)
    print(f"[{name}] observed OOF AUROC = {observed_auroc:.4f}, "
          f"selected C per outer fold = {selected_cs}, "
          f"{time.time()-t0:.1f}s")

    ci_lo, ci_hi, boot_skipped = patient_bootstrap_ci(
        y, oof_proba, n_bootstrap=N_BOOTSTRAP, random_state=RANDOM_STATE
    )
    print(f"[{name}] patient-bootstrap 95% CI = [{ci_lo:.4f}, {ci_hi:.4f}] "
          f"({boot_skipped} degenerate resamples skipped out of {N_BOOTSTRAP})")

    fixed_c_for_perm = float(np.median(selected_cs)) if not tune_c_for_permutations else None
    t1 = time.time()
    null_aurocs, p_value = permutation_test(
        X, y, observed_auroc,
        n_permutations=N_PERMUTATIONS,
        random_state=RANDOM_STATE,
        tune_c=tune_c_for_permutations,
        fixed_c=fixed_c_for_perm,
    )
    print(f"[{name}] permutation test: {N_PERMUTATIONS} perms, "
          f"null mean={null_aurocs.mean():.4f}, null std={null_aurocs.std():.4f}, "
          f"two-sided p={p_value:.5f}, {time.time()-t1:.1f}s")

    return {
        "arm": name,
        "n_donors": int(len(y)),
        "n_features": int(X.shape[1]),
        "auroc": observed_auroc,
        "ci_lower_95": ci_lo,
        "ci_upper_95": ci_hi,
        "bootstrap_n": N_BOOTSTRAP,
        "bootstrap_degenerate_skipped": boot_skipped,
        "permutation_n": N_PERMUTATIONS,
        "permutation_p_value_two_sided": p_value,
        "permutation_null_mean_auroc": float(null_aurocs.mean()),
        "permutation_null_std_auroc": float(null_aurocs.std()),
        "leaky_vs_honest_status": "not_applicable_no_cell_level_data",
        "leaky_vs_honest_sanity_check": (
            "PASS: permutation null mean AUROC collapses near 0.5"
            if abs(null_aurocs.mean() - 0.5) < 0.05
            else "FLAG: permutation null mean AUROC deviates from 0.5 by >0.05"
        ),
        "cv_scheme": "StratifiedKFold(n_splits=5), not GroupKFold: "
        "each donor is already exactly one row (pre-aggregated), so groups "
        "and samples coincide; GroupKFold would be a no-op here.",
        "hyperparameter_c_grid": C_GRID,
        "selected_c_per_outer_fold_real_fit": selected_cs,
        "permutation_used_fixed_c": fixed_c_for_perm,
        "random_state": RANDOM_STATE,
    }


def main() -> None:
    pb, meta = load_data()

    print("=== label alignment check ===")
    print(f"pseudobulk donors: {len(pb)}, metadata donors: {len(meta)}")
    print(f"overall SLE/healthy: {meta['sle_label'].sum()}/{(meta['sle_label'] == 0).sum()}")
    assert meta["sle_label"].sum() == 162 and (meta["sle_label"] == 0).sum() == 99, \
        "label counts do not match PREREG (162 SLE / 99 healthy)"

    # --- Arm 2: pseudobulk ---
    y_pb = meta["sle_label"].to_numpy()
    X_pb = pb.to_numpy()
    arm2 = run_arm(
        "pseudobulk", X_pb, y_pb,
        tune_c_for_real_fit=True,
        tune_c_for_permutations=False,  # cost simplification, documented above
    )

    # --- Arm 3: metadata-only (age), n=259 ---
    meta_eligible = meta[meta["metadata_arm_eligible"]]
    y_age = meta_eligible["sle_label"].to_numpy()
    X_age = meta_eligible[["age"]].to_numpy().astype(float)
    print()
    print(f"metadata-eligible SLE/healthy: {y_age.sum()}/{(y_age == 0).sum()}, n={len(y_age)}")
    arm3 = run_arm(
        "metadata_only_age", X_age, y_age,
        tune_c_for_real_fit=True,
        tune_c_for_permutations=True,  # cheap (1 feature), no simplification needed
    )

    out_df = pd.DataFrame([arm2, arm3])
    out_path = RESULTS_DIR / "l2_dev_sle_vs_healthy.csv"
    out_df.to_csv(out_path, index=False)
    print()
    print(f"wrote {out_path}")

    with open(RESULTS_DIR / "l2_dev_sle_vs_healthy_full.json", "w") as f:
        json.dump({"pseudobulk": arm2, "metadata_only_age": arm3}, f, indent=2, default=str)


if __name__ == "__main__":
    main()
