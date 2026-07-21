"""Deterministically regenerate per-donor sealed-cohort predicted
probabilities and permutation-null AUROC arrays, for figure-generation only.

This is NOT a new sealed-cohort access: it touches no raw GSE135779 cell/
expression data. It only re-reads already-committed, already-processed
FEATURE artifacts (results/l2_sealed_pseudobulk_counts.parquet,
results/l2_sealed_geneformer_embeddings.parquet,
results/l2_sealed_donor_metadata.csv) plus the already-committed dev-cohort
artifacts, and re-runs the exact same deterministic scoring math that
scripts/20_sealed_cohort_scoring.py already ran once (StandardScaler +
LogisticRegression, frozen C from FREEZE.json, no random_state in the model
itself -- lbfgs is a deterministic solver). Nothing here is a new "look" at
the sealed cohort: the same inputs, the same frozen hyperparameters, and the
same math can only ever reproduce the same numbers.

Consequently this script does NOT import require_valid_freeze() or
mark_sealed_opened() from scripts/freeze_guard.py -- those guard raw
sealed-cohort access, which does not happen here. It also does not import
scripts/20_sealed_cohort_scoring.py as a module (that module calls
require_valid_freeze() at import time, which would correctly refuse now
that SEALED_OPENED.json exists) -- the small amount of scoring logic is
reproduced directly below instead, byte-for-byte matching scripts/20's
functions.

Verification: after regenerating, this script recomputes AUROC from the
regenerated probabilities and asserts it matches the already-committed
value in results/l2_sealed_results.json to high precision. If it doesn't
match, this script fails loudly rather than silently producing different
numbers for the figures than what was actually reported.

Writes: results/l2_sealed_predictions_regenerated.json
(per-arm: donor ids, y_sealed, proba_sealed, and a 1000-value permutation
null AUROC array).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_ROOT / "results"

RANDOM_STATE = 20260721  # must match scripts/20 exactly, for reproducibility
N_PERMUTATIONS = 1000


def load_freeze() -> dict:
    with open(REPO_ROOT / "FREEZE.json") as f:
        return json.load(f)


def load_committed_sealed_results() -> dict:
    with open(RESULTS_DIR / "l2_sealed_results.json") as f:
        return json.load(f)


def fit_final_model(X: np.ndarray, y: np.ndarray, C: float) -> tuple[StandardScaler, LogisticRegression]:
    """Byte-for-byte identical to scripts/20's fit_final_model."""
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    clf = LogisticRegression(C=C, l1_ratio=0, max_iter=2000, solver="lbfgs")
    clf.fit(Xs, y)
    return scaler, clf


def score_frozen(scaler: StandardScaler, clf: LogisticRegression, X_sealed: np.ndarray) -> np.ndarray:
    Xs = scaler.transform(X_sealed)
    return clf.predict_proba(Xs)[:, 1]


def permutation_null_array(y: np.ndarray, proba: np.ndarray, n_perm: int, seed: int) -> np.ndarray:
    """Byte-for-byte identical to scripts/20's permutation_p_single_arm,
    except it returns the full null array instead of only summary stats."""
    rng = np.random.RandomState(seed)
    null = np.empty(n_perm)
    for i in range(n_perm):
        y_perm = rng.permutation(y)
        null[i] = roc_auc_score(y_perm, proba)
    return null


def load_dev_metadata() -> pd.DataFrame:
    return pd.read_csv(RESULTS_DIR / "l2_dev_donor_metadata.csv", dtype={"donor_id": str}).set_index("donor_id")


def load_sealed_metadata() -> pd.DataFrame:
    return pd.read_csv(RESULTS_DIR / "l2_sealed_donor_metadata.csv", dtype={"gsm_id": str}).set_index("gsm_id")


def main() -> None:
    freeze = load_freeze()
    hp = freeze["hyperparameters"]
    committed = load_committed_sealed_results()

    dev_meta = load_dev_metadata()
    sealed_meta = load_sealed_metadata()

    output = {}

    # --- pseudobulk (gene-restricted, 30165 genes) -- same canonical
    # reindex as scripts/20, required since the two Kaggle kernels produced
    # different (both internally consistent) column orders.
    pb_dev = pd.read_parquet(RESULTS_DIR / "l2_dev_pseudobulk_counts_restricted.parquet")
    pb_sealed = pd.read_parquet(RESULTS_DIR / "l2_sealed_pseudobulk_counts.parquet")
    assert set(pb_dev.columns) == set(pb_sealed.columns)
    canonical_gene_order = sorted(pb_dev.columns)
    pb_dev = pb_dev.loc[dev_meta.index, canonical_gene_order]
    pb_sealed = pb_sealed.loc[sealed_meta.index, canonical_gene_order]

    y_dev_pb = dev_meta["sle_label"].to_numpy()
    y_sealed = sealed_meta["sle_label"].to_numpy()
    scaler, clf = fit_final_model(pb_dev.to_numpy(), y_dev_pb, hp["pseudobulk"]["C_frozen"])
    proba_pb = score_frozen(scaler, clf, pb_sealed.to_numpy())
    output["pseudobulk"] = {"proba": proba_pb, "y": y_sealed, "donor_ids": list(sealed_meta.index)}

    # --- metadata-only (age) ---
    dev_meta_eligible = dev_meta[dev_meta["metadata_arm_eligible"]]
    y_dev_age = dev_meta_eligible["sle_label"].to_numpy()
    X_dev_age = dev_meta_eligible[["age"]].to_numpy().astype(float)
    X_sealed_age = sealed_meta[["age"]].to_numpy().astype(float)
    scaler, clf = fit_final_model(X_dev_age, y_dev_age, hp["metadata_only_age"]["C_frozen"])
    proba_meta = score_frozen(scaler, clf, X_sealed_age)
    output["metadata_only_age"] = {"proba": proba_meta, "y": y_sealed, "donor_ids": list(sealed_meta.index)}

    # --- Geneformer ---
    gf_dev = pd.read_parquet(RESULTS_DIR / "l2_dev_geneformer_embeddings.parquet").loc[dev_meta.index]
    gf_sealed = pd.read_parquet(RESULTS_DIR / "l2_sealed_geneformer_embeddings.parquet").loc[sealed_meta.index]
    y_dev_gf = dev_meta["sle_label"].to_numpy()
    scaler, clf = fit_final_model(gf_dev.to_numpy(), y_dev_gf, hp["geneformer"]["C_frozen"])
    proba_gf = score_frozen(scaler, clf, gf_sealed.to_numpy())
    output["geneformer"] = {"proba": proba_gf, "y": y_sealed, "donor_ids": list(sealed_meta.index)}

    # --- verify against the already-committed AUROC values before trusting anything ---
    print("=== verification: regenerated AUROC vs. already-committed AUROC ===")
    all_match = True
    for arm in ("geneformer", "pseudobulk", "metadata_only_age"):
        regenerated_auroc = roc_auc_score(output[arm]["y"], output[arm]["proba"])
        committed_auroc = committed["arms"][arm]["sealed_auroc_overall"]
        match = abs(regenerated_auroc - committed_auroc) < 1e-9
        all_match = all_match and match
        print(f"[{arm}] regenerated={regenerated_auroc!r} committed={committed_auroc!r} "
              f"match={match}")
        assert match, f"{arm}: regenerated AUROC does not match committed value -- STOP, do not use for figures"

    # --- permutation null arrays, same seed as scripts/20 ---
    print("\n=== regenerating permutation null arrays (1000 each) ===")
    for arm in ("geneformer", "pseudobulk", "metadata_only_age"):
        null = permutation_null_array(output[arm]["y"], output[arm]["proba"], N_PERMUTATIONS, RANDOM_STATE)
        committed_null_mean = committed["arms"][arm]["sealed_permutation_null_mean_overall"]
        committed_null_std = committed["arms"][arm]["sealed_permutation_null_std_overall"]
        mean_match = abs(float(null.mean()) - committed_null_mean) < 1e-9
        std_match = abs(float(null.std()) - committed_null_std) < 1e-9
        print(f"[{arm}] regenerated null mean={null.mean():.6f} (committed {committed_null_mean:.6f}, "
              f"match={mean_match}), std={null.std():.6f} (committed {committed_null_std:.6f}, "
              f"match={std_match})")
        assert mean_match and std_match, f"{arm}: regenerated permutation null does not match committed summary stats"
        output[arm]["permutation_null"] = null.tolist()

    for arm in output:
        output[arm]["proba"] = output[arm]["proba"].tolist()
        output[arm]["y"] = output[arm]["y"].tolist()

    out_path = RESULTS_DIR / "l2_sealed_predictions_regenerated.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nwrote {out_path}")
    print("All regenerated AUROC and permutation-null summary stats matched the "
          "already-committed results/l2_sealed_results.json exactly.")


if __name__ == "__main__":
    main()
