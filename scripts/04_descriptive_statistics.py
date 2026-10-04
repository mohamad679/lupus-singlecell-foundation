"""Fixed-prediction donor summaries for corrected V1 paper tables and figures."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score


def auc_ci(y, p, *, seed=20260930, n_bootstrap=5000):
    y, p = np.asarray(y, dtype=int), np.asarray(p, dtype=float)
    if len(y) != len(p) or len(np.unique(y)) != 2 or not np.isfinite(p).all():
        raise ValueError("invalid aligned binary predictions")
    rng = np.random.RandomState(seed)
    draws = []
    skipped = 0
    for _ in range(n_bootstrap):
        idx = rng.randint(0, len(y), len(y))
        if len(np.unique(y[idx])) < 2:
            skipped += 1
            continue
        draws.append(roc_auc_score(y[idx], p[idx]))
    if not draws:
        raise ValueError("all bootstrap draws were single class")
    return {"auroc": float(roc_auc_score(y, p)),
            "ci95": [float(x) for x in np.percentile(draws, [2.5, 97.5])],
            "n": len(y), "n_case": int(y.sum()), "n_control": int(len(y)-y.sum()),
            "valid_draws": len(draws), "degenerate_draws": skipped}


def run(root: Path):
    return run_in_dir(root, root / "results/published")


def run_in_dir(root: Path, corr: Path):
    results = root / "results"
    metadata = pd.read_csv(results / "reference/external_donor_metadata.csv", dtype={"gsm_id": str})
    if metadata.gsm_id.duplicated().any():
        raise ValueError("duplicate external sample keys")
    metadata = metadata.set_index("gsm_id")
    output = {"method": "5000 percentile bootstrap resamples of donors with fixed predictions; descriptive CIs",
              "external_age_groups": "source metadata categories Children and Adult; Children includes some ages 18-19",
              "modes": {}}
    for mode in ("shared", "native"):
        path = corr / f"corrected_v1_{mode}_predictions.json"
        predictions = json.loads(path.read_text())
        groups = {}
        canonical = predictions["geneformer"]
        ids = canonical["donor_ids"]
        if len(ids) != 56 or len(set(ids)) != 56 or set(ids) != set(metadata.index):
            raise ValueError("external donor keys mismatch metadata")
        y = np.asarray(canonical["y"])
        if not np.array_equal(y, metadata.loc[ids, "sle_label"].to_numpy()):
            raise ValueError("external labels mismatch metadata")
        strata = metadata.loc[ids, "age_group"].to_numpy()
        if set(strata) != {"Children", "Adult"}:
            raise ValueError("unexpected source age-group categories")
        for arm, row in predictions.items():
            if row["donor_ids"] != ids or row["y"] != canonical["y"]:
                raise ValueError(f"{arm} misaligned")
            p = np.asarray(row["proba"])
            groups[arm] = {"overall": auc_ci(y, p),
                           "Children": auc_ci(y[strata == "Children"], p[strata == "Children"]),
                           "Adult": auc_ci(y[strata == "Adult"], p[strata == "Adult"])}
        dev = json.loads((corr / f"corrected_v1_{mode}_development_oof_predictions.json").read_text())
        if len(dev["donor_ids"]) != 261 or len(set(dev["donor_ids"])) != 261:
            raise ValueError("development donor count or key mismatch")
        output["modes"][mode] = {"external": groups,
                                  "development_geneformer": auc_ci(dev["y"], dev["proba"]),
                                  "external_predictions_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--correction-dir", type=Path)
    args = parser.parse_args()
    corr = args.correction_dir or args.repo_root / "results/published"
    result = run_in_dir(args.repo_root, corr)
    out = corr / "corrected_v1_descriptive.json"
    out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(out)
