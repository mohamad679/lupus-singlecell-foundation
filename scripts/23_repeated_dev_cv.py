"""Q2-hardening item 1: repeated nested CV on the DEV cohort only.

Purely additive robustness check. Does not touch GSE135779, FREEZE.json,
SEALED_OPENED.json, results/l2_sealed_results.json, or
results/l2_dev_sle_vs_healthy.csv. Writes a NEW artifact only:
results/l2_dev_repeated_cv.csv.

This cannot alter any sealed result: it never loads sealed data, never
refits the frozen sealed-scoring models (those live in
scripts/20_sealed_cohort_scoring.py / scripts/22, untouched here), and the
frozen hyperparameters in FREEZE.json are read-only inputs elsewhere, not
touched by this script at all -- this script does its own independent
hyperparameter search per repeat (matching the ORIGINAL dev-CV protocol
exactly), which is a dev-side robustness check, not a change to the frozen
pipeline.

Method: reuses scripts/15_l2_dev_cv_pseudobulk_metadata.py's load_data() and
fit_logreg_oof() UNCHANGED (imported, not copied or modified), run 10 times
per arm with a different outer/inner CV random_state each repeat
(RepeatedStratifiedKFold-equivalent: same n_splits=5 protocol as the
original single committed run, repeated with 10 different seeds). Each
repeat's out-of-fold AUROC is one independent estimate of dev-cohort CV
performance under fold-assignment randomness.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib.util

spec = importlib.util.spec_from_file_location(
    "l2_dev_cv", Path(__file__).resolve().parent / "15_l2_dev_cv_pseudobulk_metadata.py"
)
l2_dev_cv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(l2_dev_cv)  # module-level code only (constants, defs) -- no main() runs

REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = REPO_ROOT / "results"

N_REPEATS = 10
BASE_SEED = 20260722  # distinct from the original committed run's seed (20260719)


def main() -> None:
    gf, pb, meta = l2_dev_cv.load_data()

    y_gf = meta["sle_label"].to_numpy()
    X_gf = gf.to_numpy()

    y_pb = meta["sle_label"].to_numpy()
    X_pb = pb.to_numpy()

    meta_eligible = meta[meta["metadata_arm_eligible"]]
    y_age = meta_eligible["sle_label"].to_numpy()
    X_age = meta_eligible[["age"]].to_numpy().astype(float)

    arms = {
        "geneformer": (X_gf, y_gf),
        "pseudobulk": (X_pb, y_pb),
        "metadata_only_age": (X_age, y_age),
    }

    records = []
    for arm_name, (X, y) in arms.items():
        print(f"=== {arm_name}: {N_REPEATS} repeats of nested 5-fold CV ===")
        for repeat_idx in range(N_REPEATS):
            seed = BASE_SEED + repeat_idx
            t0 = time.time()
            oof_proba, selected_cs = l2_dev_cv.fit_logreg_oof(
                X, y, random_state=seed, tune_c=True, fixed_c=None
            )
            auroc = roc_auc_score(y, oof_proba)
            elapsed = time.time() - t0
            print(f"  repeat {repeat_idx} (seed={seed}): AUROC={auroc:.4f}, "
                  f"selected_C={selected_cs}, {elapsed:.1f}s")
            records.append({
                "arm": arm_name,
                "repeat_index": repeat_idx,
                "random_state": seed,
                "auroc": auroc,
                "selected_c_per_outer_fold": selected_cs,
                "n": int(len(y)),
                "n_features": int(X.shape[1]),
            })

    df = pd.DataFrame(records)
    out_path = RESULTS_DIR / "l2_dev_repeated_cv.csv"
    df.to_csv(out_path, index=False)
    print(f"\nwrote {out_path}")

    print("\n=== summary: repeated-CV mean +/- SD vs. original single-run AUROC ===")
    original = pd.read_csv(RESULTS_DIR / "l2_dev_sle_vs_healthy.csv").set_index("arm")
    for arm_name in arms:
        sub = df[df["arm"] == arm_name]["auroc"]
        orig_auroc = original.loc[arm_name, "auroc"]
        print(f"[{arm_name}] repeated: mean={sub.mean():.4f}, sd={sub.std(ddof=1):.4f}, "
              f"min={sub.min():.4f}, max={sub.max():.4f}, n_repeats={len(sub)} | "
              f"original single-run={orig_auroc:.4f}")

    print("\nConfirmation: results/l2_dev_sle_vs_healthy.csv was not opened for writing "
          "by this script, and no sealed-cohort file was read or written. Only "
          "results/l2_dev_repeated_cv.csv was created.")


if __name__ == "__main__":
    main()
