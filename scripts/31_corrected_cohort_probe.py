"""Post-hoc cohort membership probe on validated corrected shared-gene vectors."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from importlib.machinery import SourceFileLoader

ROOT = Path(__file__).resolve().parents[1]
CORR = ROOT / "results/correction_2026-09"
spec = importlib.util.spec_from_loader("historical_cohort_probe", SourceFileLoader(
    "historical_cohort_probe", str(ROOT / "scripts/25_cohort_signature_probe.py")))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def run(feature_root: Path, output_dir: Path):
    d = pd.read_parquet(feature_root / "shared_features/l2_dev_geneformer_v1_shared_embeddings.parquet")
    e = pd.read_parquet(feature_root / "shared_features/l2_sealed_geneformer_v1_shared_embeddings.parquet")
    if list(d.columns) != list(e.columns) or len(d) != 261 or len(e) != 56:
        raise ValueError("corrected embedding feature or donor mismatch")
    X = np.vstack([d.to_numpy(), e.to_numpy()])
    if not np.isfinite(X).all():
        raise ValueError("non-finite corrected cohort probe features")
    y = np.r_[np.zeros(len(d), dtype=int), np.ones(len(e), dtype=int)]
    p, cs = module.fit_logreg_oof(X, y, module.RANDOM_STATE, tune_c=True, fixed_c=None)
    lo, hi, skipped = module.patient_bootstrap_ci(y, p, 5000, module.RANDOM_STATE)
    result = {"status": "post-hoc diagnostic; no SLE label prediction",
              "arm": "corrected V1 shared-gene Geneformer", "n_development": len(d),
              "n_external": len(e), "n_features": X.shape[1],
              "cohort_membership_auroc": float(roc_auc_score(y, p)), "ci95": [lo, hi],
              "selected_c_per_outer_fold": cs, "bootstrap_degenerate_draws": skipped,
              "method": "same nested 5x5 donor CV settings as released cohort-signature probe; fixed-prediction bootstrap",
              "interpretation": "Separability of cohort origin does not identify a causal source of SLE discrimination."}
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "corrected_v1_shared_cohort_probe.json"
    path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--feature-root", type=Path, default=CORR)
    parser.add_argument("--output-dir", type=Path, default=CORR)
    args = parser.parse_args()
    run(args.feature_root, args.output_dir)


if __name__ == "__main__":
    main()
