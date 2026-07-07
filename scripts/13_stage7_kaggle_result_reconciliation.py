"""Stage 7 Kaggle result reconciliation and leakage-safe reproduction.

This script converts the exploratory Kaggle notebook results into
artifact-backed, leakage-safe CSV outputs.

It is intended to run in Kaggle or another environment where the patient-level
Geneformer embedding .npy files are available. It keeps heavy dependencies
optional and imports numpy/sklearn only inside the execution path so the core
package can remain lightweight.

Outputs:
- reports/tables/stage7_prediction_manifest.csv
- reports/tables/stage7_metric_results.csv

Safety policy:
- patient-level evaluation only
- no cell-level split
- StandardScaler is fit inside each LOOCV fold on train patients only
- LogisticRegression is fit inside each LOOCV fold on train patients only
- no external validation claim
- no clinical deployment claim
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EMB_DIR = Path("/kaggle/input/datasets/mohamadasgari/lupus-embeddings")
DEFAULT_OUTPUT_DIR = REPO_ROOT / "reports" / "tables"
DATASET_ID = "GSE174188_CELLxGENE_Geneformer_patient_embeddings"
MODEL_FAMILY = "mean_pooled_geneformer_logistic_regression"
SPLIT_POLICY = "leave_one_patient_out"
EVALUATION_UNIT = "patient"
POSITIVE_LABEL = "Flare"


class Stage7ReconciliationError(ValueError):
    """Raised when Stage 7 reconciliation cannot be safely executed."""


@dataclass(frozen=True)
class PatientEmbeddingRecord:
    """One patient-level embedding summary."""

    patient_id: str
    group: str
    embedding_path: Path
    n_cells: int
    embedding_dim: int


def infer_group(patient_id: str) -> str:
    """Infer label group from the Kaggle embedding filename convention."""

    if patient_id.startswith("FLARE"):
        return "Flare"
    if patient_id.startswith("HC") or patient_id.startswith("IGTB"):
        return "Healthy"
    return "Managed"


def load_runtime_dependencies() -> dict[str, Any]:
    """Import heavy runtime dependencies only when executing the script."""

    try:
        import numpy as np
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import average_precision_score, roc_auc_score
        from sklearn.model_selection import LeaveOneOut
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:
        raise Stage7ReconciliationError(
            "Stage 7 execution requires numpy and scikit-learn. "
            "Run this script in Kaggle or install the runtime dependencies there."
        ) from exc

    return {
        "np": np,
        "LogisticRegression": LogisticRegression,
        "average_precision_score": average_precision_score,
        "roc_auc_score": roc_auc_score,
        "LeaveOneOut": LeaveOneOut,
        "StandardScaler": StandardScaler,
    }


def discover_embedding_records(emb_dir: Path) -> list[PatientEmbeddingRecord]:
    """Discover .npy patient embedding files and validate basic shape."""

    deps = load_runtime_dependencies()
    np = deps["np"]

    if not emb_dir.exists():
        raise Stage7ReconciliationError(f"Embedding directory not found: {emb_dir}")

    records: list[PatientEmbeddingRecord] = []
    for path in sorted(emb_dir.glob("*.npy")):
        patient_id = path.stem
        embedding = np.load(path, mmap_mode="r")
        if embedding.ndim != 2:
            raise Stage7ReconciliationError(
                f"{path.name} must be a 2D cell-by-embedding matrix."
            )
        n_cells, embedding_dim = int(embedding.shape[0]), int(embedding.shape[1])
        if n_cells < 1 or embedding_dim < 1:
            raise Stage7ReconciliationError(
                f"{path.name} has invalid shape: {embedding.shape}"
            )
        records.append(
            PatientEmbeddingRecord(
                patient_id=patient_id,
                group=infer_group(patient_id),
                embedding_path=path,
                n_cells=n_cells,
                embedding_dim=embedding_dim,
            )
        )

    if not records:
        raise Stage7ReconciliationError(f"No .npy embedding files found in {emb_dir}")

    dims = {record.embedding_dim for record in records}
    if len(dims) != 1:
        raise Stage7ReconciliationError(
            "All patient embeddings must have the same embedding dimension."
        )

    return records


def mean_pool_embeddings(records: Iterable[PatientEmbeddingRecord]):
    """Mean-pool cell embeddings to one vector per patient."""

    deps = load_runtime_dependencies()
    np = deps["np"]

    rows = []
    labels = []
    patient_ids = []
    groups = []

    for record in records:
        embedding = np.load(record.embedding_path)
        rows.append(embedding.mean(axis=0))
        labels.append(1 if record.group == POSITIVE_LABEL else 0)
        patient_ids.append(record.patient_id)
        groups.append(record.group)

    return np.asarray(rows), np.asarray(labels), patient_ids, groups


def binary_metrics(y_true, y_score, threshold: float = 0.5) -> dict[str, float]:
    """Compute binary metrics from patient-level out-of-fold scores."""

    deps = load_runtime_dependencies()
    np = deps["np"]
    roc_auc_score = deps["roc_auc_score"]
    average_precision_score = deps["average_precision_score"]

    y_true = np.asarray(y_true, dtype=int)
    y_score = np.asarray(y_score, dtype=float)
    y_pred = (y_score >= threshold).astype(int)

    tp = int(((y_true == 1) & (y_pred == 1)).sum())
    tn = int(((y_true == 0) & (y_pred == 0)).sum())
    fp = int(((y_true == 0) & (y_pred == 1)).sum())
    fn = int(((y_true == 1) & (y_pred == 0)).sum())

    n = int(len(y_true))
    sensitivity = tp / (tp + fn) if (tp + fn) else math.nan
    specificity = tn / (tn + fp) if (tn + fp) else math.nan
    precision = tp / (tp + fp) if (tp + fp) else math.nan
    accuracy = (tp + tn) / n if n else math.nan
    balanced_accuracy = (
        (sensitivity + specificity) / 2
        if math.isfinite(sensitivity) and math.isfinite(specificity)
        else math.nan
    )
    f1 = (
        2 * precision * sensitivity / (precision + sensitivity)
        if math.isfinite(precision)
        and math.isfinite(sensitivity)
        and (precision + sensitivity) > 0
        else 0.0
    )
    brier_score = float(np.mean((y_score - y_true) ** 2))

    return {
        "n_patients": n,
        "n_cases": int((y_true == 1).sum()),
        "n_controls": int((y_true == 0).sum()),
        "auroc": float(roc_auc_score(y_true, y_score)),
        "auprc": float(average_precision_score(y_true, y_score)),
        "accuracy": float(accuracy),
        "balanced_accuracy": float(balanced_accuracy),
        "f1": float(f1),
        "sensitivity": float(sensitivity),
        "specificity": float(specificity),
        "precision": float(precision) if math.isfinite(precision) else math.nan,
        "brier_score": brier_score,
        "true_positive": tp,
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
    }


def bootstrap_auc_ci(y_true, y_score, *, n_bootstrap: int, seed: int) -> tuple[float, float]:
    """Patient-level bootstrap confidence interval for AUROC."""

    deps = load_runtime_dependencies()
    np = deps["np"]
    roc_auc_score = deps["roc_auc_score"]

    if n_bootstrap <= 0:
        return math.nan, math.nan

    rng = np.random.default_rng(seed)
    y_true = np.asarray(y_true, dtype=int)
    y_score = np.asarray(y_score, dtype=float)
    n = len(y_true)
    aucs = []

    for _ in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        sampled_y = y_true[idx]
        if len(np.unique(sampled_y)) < 2:
            continue
        aucs.append(float(roc_auc_score(sampled_y, y_score[idx])))

    if not aucs:
        return math.nan, math.nan

    lower, upper = np.percentile(np.asarray(aucs), [2.5, 97.5])
    return float(lower), float(upper)


def run_loocv_task(
    *,
    task_name: str,
    all_records: list[PatientEmbeddingRecord],
    case_group: str,
    control_group: str,
    c_value: float,
    max_iter: int,
    bootstrap: int,
    seed: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run leakage-safe LOOCV for one binary task."""

    deps = load_runtime_dependencies()
    np = deps["np"]
    LogisticRegression = deps["LogisticRegression"]
    LeaveOneOut = deps["LeaveOneOut"]
    StandardScaler = deps["StandardScaler"]

    task_records = [
        record for record in all_records if record.group in {case_group, control_group}
    ]

    if len(task_records) < 3:
        raise Stage7ReconciliationError(f"{task_name} requires at least 3 patients.")

    groups = [record.group for record in task_records]
    if case_group not in groups or control_group not in groups:
        raise Stage7ReconciliationError(f"{task_name} requires both classes.")

    X, y, patient_ids, label_names = mean_pool_embeddings(task_records)

    loo = LeaveOneOut()
    y_scores = []
    y_true = []
    manifest_rows: list[dict[str, Any]] = []

    for fold_id, (train_idx, test_idx) in enumerate(loo.split(X), start=1):
        x_train = X[train_idx]
        x_test = X[test_idx]
        y_train = y[train_idx]
        y_test = y[test_idx]

        if len(np.unique(y_train)) < 2:
            raise Stage7ReconciliationError(
                f"{task_name} fold {fold_id} train split has one class only."
            )

        scaler = StandardScaler()
        x_train_scaled = scaler.fit_transform(x_train)
        x_test_scaled = scaler.transform(x_test)

        clf = LogisticRegression(
            class_weight="balanced",
            max_iter=max_iter,
            C=c_value,
            random_state=seed,
        )
        clf.fit(x_train_scaled, y_train)

        score = float(clf.predict_proba(x_test_scaled)[0][1])
        pred = int(score >= 0.5)
        truth = int(y_test[0])
        test_pos = int(test_idx[0])

        y_scores.append(score)
        y_true.append(truth)

        manifest_rows.append(
            {
                "run_id": f"stage7_{task_name}_loocv",
                "dataset_id": DATASET_ID,
                "task": task_name,
                "model_family": MODEL_FAMILY,
                "split_policy": SPLIT_POLICY,
                "fold_id": fold_id,
                "patient_id": patient_ids[test_pos],
                "true_label": label_names[test_pos],
                "y_true": truth,
                "positive_label_score": score,
                "predicted_label": case_group if pred == 1 else control_group,
                "y_pred": pred,
                "n_train": int(len(train_idx)),
                "n_train_cases": int((y_train == 1).sum()),
                "n_train_controls": int((y_train == 0).sum()),
                "feature_policy": "mean_pool_cells_per_patient",
                "scaler_fit_scope": "train_fold_only",
                "model_fit_scope": "train_fold_only",
                "leakage_control": "no_global_scaler_no_cell_level_split",
            }
        )

    metric_values = binary_metrics(y_true, y_scores)
    ci_lower, ci_upper = bootstrap_auc_ci(
        y_true,
        y_scores,
        n_bootstrap=bootstrap,
        seed=seed,
    )

    metric_row = {
        "run_id": f"stage7_{task_name}_loocv",
        "dataset_id": DATASET_ID,
        "model_family": MODEL_FAMILY,
        "task": task_name,
        "split_policy": SPLIT_POLICY,
        "evaluation_unit": EVALUATION_UNIT,
        **metric_values,
        "ci_method": "patient_bootstrap_95" if bootstrap > 0 else "not_computed",
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "c_value": c_value,
        "max_iter": max_iter,
        "status": "completed",
        "audit_status": "leakage_safe_internal_loocv_no_external_validation",
        "notes": (
            "Internal patient-level LOOCV only. No external validation or clinical "
            "deployment claim. StandardScaler and LogisticRegression are fit within "
            "each train fold only."
        ),
    }

    return manifest_rows, metric_row


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write rows to CSV with deterministic column order."""

    if not rows:
        raise Stage7ReconciliationError(f"No rows to write for {path}")

    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_run_summary(path: Path, summary: dict[str, Any]) -> None:
    """Write a compact JSON run summary."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")


def run_reconciliation(
    *,
    emb_dir: Path,
    output_dir: Path,
    c_value: float,
    max_iter: int,
    bootstrap: int,
    seed: int,
) -> dict[str, Any]:
    """Run Stage 7 leakage-safe reconciliation."""

    records = discover_embedding_records(emb_dir)
    group_counts: dict[str, int] = {}
    for record in records:
        group_counts[record.group] = group_counts.get(record.group, 0) + 1

    tasks = [
        {
            "task_name": "flare_vs_healthy",
            "case_group": "Flare",
            "control_group": "Healthy",
        },
        {
            "task_name": "flare_vs_managed",
            "case_group": "Flare",
            "control_group": "Managed",
        },
    ]

    all_manifest_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []

    for task in tasks:
        manifest_rows, metric_row = run_loocv_task(
            task_name=task["task_name"],
            all_records=records,
            case_group=task["case_group"],
            control_group=task["control_group"],
            c_value=c_value,
            max_iter=max_iter,
            bootstrap=bootstrap,
            seed=seed,
        )
        all_manifest_rows.extend(manifest_rows)
        metric_rows.append(metric_row)

    prediction_manifest_path = output_dir / "stage7_prediction_manifest.csv"
    metric_results_path = output_dir / "stage7_metric_results.csv"
    run_summary_path = output_dir / "stage7_run_summary.json"

    write_csv(prediction_manifest_path, all_manifest_rows)
    write_csv(metric_results_path, metric_rows)

    summary = {
        "stage": "Stage 7",
        "status": "completed",
        "scope": "kaggle_result_reconciliation_leakage_safe_internal_loocv",
        "embedding_dir": str(emb_dir),
        "dataset_id": DATASET_ID,
        "n_patients_total": len(records),
        "group_counts": group_counts,
        "tasks": [task["task_name"] for task in tasks],
        "prediction_manifest": str(prediction_manifest_path),
        "metric_results": str(metric_results_path),
        "external_validation_performed": False,
        "clinical_claim_allowed": False,
        "leakage_controls": [
            "patient_level_only",
            "leave_one_patient_out",
            "scaler_fit_train_fold_only",
            "model_fit_train_fold_only",
            "no_cell_level_split",
        ],
    }
    write_run_summary(run_summary_path, summary)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Stage 7 leakage-safe Kaggle result reconciliation."
    )
    parser.add_argument(
        "--emb-dir",
        type=Path,
        default=DEFAULT_EMB_DIR,
        help="Directory containing patient-level .npy embedding files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for Stage 7 CSV/JSON outputs.",
    )
    parser.add_argument("--c-value", type=float, default=0.1)
    parser.add_argument("--max-iter", type=int, default=1000)
    parser.add_argument("--bootstrap", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = run_reconciliation(
        emb_dir=args.emb_dir,
        output_dir=args.output_dir,
        c_value=args.c_value,
        max_iter=args.max_iter,
        bootstrap=args.bootstrap,
        seed=args.seed,
    )

    print("Stage 7 Kaggle result reconciliation completed")
    for key, value in summary.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
