"""Fit and score corrected V1 donor embeddings in a new output directory.

This reanalysis never calls the historical freeze guard or overwrites the
original release. It uses the originally recorded nested CV C-selection
rule on the corrected development representation and copies the regenerated
historical baseline predictions after exact donor-key alignment.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DEFAULT_OUTPUT = RESULTS / "correction_2026-09"


def read_summary(path, mode):
    with path.open() as file:
        summary = json.load(file)
    if (summary.get("status") != "success" or summary.get("model_version") != "V1"
            or summary.get("emb_mode") != "cell" or summary.get("gene_input_mode") != mode):
        raise ValueError(f"invalid corrected extraction summary: {path}")
    if not summary.get("checkpoint_sha256_by_file"):
        raise ValueError(f"checkpoint hashes absent: {path}")
    if not summary.get("embedding_sha256"):
        raise ValueError(f"embedding hash absent: {path}")
    return summary


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_features(frame, donors, name):
    if frame.index.has_duplicates or set(frame.index) != set(donors):
        raise ValueError(f"{name} donor IDs differ from metadata")
    if frame.shape[1] < 1 or not np.isfinite(frame.to_numpy(dtype=float)).all():
        raise ValueError(f"{name} contains invalid embeddings")
    return frame.loc[donors]


def selected_c_from_corrected_development(X, y):
    spec = importlib.util.spec_from_file_location("historical_cv", ROOT / "scripts/15_l2_dev_cv_pseudobulk_metadata.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    oof, selected = module.fit_logreg_oof(
        X, y, random_state=module.RANDOM_STATE, tune_c=True, fixed_c=None,
    )
    return oof, [float(c) for c in selected], float(np.median(selected))


def score(dev_path, external_path, dev_summary_path, external_summary_path, output_dir, mode):
    if output_dir.resolve() == RESULTS.resolve():
        raise ValueError("corrected output must be a separate directory")
    dev_summary = read_summary(dev_summary_path, mode)
    external_summary = read_summary(external_summary_path, mode)
    if (file_sha256(dev_path) != dev_summary["embedding_sha256"] or
            file_sha256(external_path) != external_summary["embedding_sha256"]):
        raise ValueError("embedding parquet does not match extraction summary")
    if (dev_summary["geneformer_revision"] != external_summary["geneformer_revision"] or
            dev_summary["checkpoint_sha256_by_file"] != external_summary["checkpoint_sha256_by_file"] or
            dev_summary.get("intersection_sha256") != external_summary.get("intersection_sha256")):
        raise ValueError("development and external extraction provenance differs")

    dev_meta = pd.read_csv(RESULTS / "l2_dev_donor_metadata.csv", dtype={"donor_id": str}).set_index("donor_id")
    external_meta = pd.read_csv(RESULTS / "l2_sealed_donor_metadata.csv", dtype={"gsm_id": str}).set_index("gsm_id")
    if dev_meta.index.has_duplicates or external_meta.index.has_duplicates:
        raise ValueError("metadata donor IDs must be unique")
    dev = validate_features(pd.read_parquet(dev_path), dev_meta.index, "development")
    external = validate_features(pd.read_parquet(external_path), external_meta.index, "external")
    if list(dev.columns) != list(external.columns):
        raise ValueError("ordered embedding dimensions differ")

    y_dev = dev_meta["sle_label"].to_numpy(dtype=int)
    y_external = external_meta["sle_label"].to_numpy(dtype=int)
    if set(y_dev) != {0, 1} or set(y_external) != {0, 1}:
        raise ValueError("both cohorts need explicit binary outcomes")
    X_dev, X_external = dev.to_numpy(dtype=float), external.to_numpy(dtype=float)
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        oof, selected_cs, c_final = selected_c_from_corrected_development(X_dev, y_dev)
        scaler = StandardScaler().fit(X_dev)
        model = LogisticRegression(C=c_final, l1_ratio=0, max_iter=2000, solver="lbfgs")
        model.fit(scaler.transform(X_dev), y_dev)
    probability = model.predict_proba(scaler.transform(X_external))[:, 1]
    if not np.isfinite(probability).all():
        raise ValueError("nonfinite external probabilities")

    with (RESULTS / "l2_sealed_predictions_regenerated.json").open() as file:
        historical = json.load(file)
    donor_ids = external_meta.index.tolist()
    for arm in ("pseudobulk", "metadata_only_age"):
        if historical[arm]["donor_ids"] != donor_ids or historical[arm]["y"] != y_external.tolist():
            raise ValueError(f"historical {arm} predictions are misaligned")
    predictions = {
        "geneformer": {"donor_ids": donor_ids, "y": y_external.tolist(),
                       "proba": probability.tolist()},
        "pseudobulk": {key: historical["pseudobulk"][key] for key in ("donor_ids", "y", "proba")},
        "metadata_only_age": {key: historical["metadata_only_age"][key] for key in ("donor_ids", "y", "proba")},
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    prediction_path = output_dir / f"corrected_v1_{mode}_predictions.json"
    fit_path = output_dir / f"corrected_v1_{mode}_fit.joblib"
    with prediction_path.open("w") as file:
        json.dump(predictions, file, indent=2, allow_nan=False)
    joblib.dump({"scaler": scaler, "model": model, "columns": list(dev.columns)}, fit_path)
    report = {
        "analysis": "corrected reanalysis on previously examined external cohort",
        "gene_input_mode": mode,
        "development_selected_c_per_outer_fold": selected_cs,
        "final_c_median": c_final,
        "development_oof_auroc": float(roc_auc_score(y_dev, oof)),
        "external_geneformer_auroc": float(roc_auc_score(y_external, probability)),
        "development_summary": str(dev_summary_path),
        "external_summary": str(external_summary_path),
        "prediction_path": str(prediction_path),
        "fit_path": str(fit_path),
        "regenerated_historical_baselines_reused": ["pseudobulk", "metadata_only_age"],
    }
    with (output_dir / f"corrected_v1_{mode}_fit_report.json").open("w") as file:
        json.dump(report, file, indent=2)
    return prediction_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dev-embeddings", type=Path, required=True)
    parser.add_argument("--external-embeddings", type=Path, required=True)
    parser.add_argument("--dev-summary", type=Path, required=True)
    parser.add_argument("--external-summary", type=Path, required=True)
    parser.add_argument("--mode", choices=("shared", "native"), default="shared")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(score(args.dev_embeddings, args.external_embeddings,
                args.dev_summary, args.external_summary, args.output_dir, args.mode))


if __name__ == "__main__":
    main()
