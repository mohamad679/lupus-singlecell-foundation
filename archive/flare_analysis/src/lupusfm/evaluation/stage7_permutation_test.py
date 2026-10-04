"""Stage 7 patient-label permutation negative control.

This module uses frozen patient-level Geneformer-derived embeddings only. It
does not run Geneformer, re-extract embeddings, or change existing Stage 7
metric artifacts.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence


REPO_ROOT = Path(__file__).resolve().parents[3]
STAGE7_RECONCILIATION_DIR = REPO_ROOT / "reports" / "stage7_kaggle_result_reconciliation"
STAGE7_RUN_SUMMARY_PATH = STAGE7_RECONCILIATION_DIR / "stage7_run_summary.json"
STAGE7_METRIC_RESULTS_PATH = STAGE7_RECONCILIATION_DIR / "stage7_metric_results.csv"
DEFAULT_KAGGLE_EMB_DIR = Path("/kaggle/input/datasets/mohamadasgari/lupus-embeddings")
DEFAULT_OUTPUT_DIR = REPO_ROOT / "reports" / "post_stage7_permutation_test"

def render_report_path(path: Path) -> str:
    """Render paths for committed reports without leaking machine-local prefixes."""

    candidate = Path(path)
    try:
        return str(candidate.resolve().relative_to(REPO_ROOT.resolve()))
    except (OSError, ValueError):
        return f"<external-local-artifact:{candidate.name}>"


DATASET_ID = "GSE174188_CELLxGENE_Geneformer_patient_embeddings"
MODEL_FAMILY = "mean_pooled_geneformer_logistic_regression"
SPLIT_POLICY = "leave_one_patient_out"
EVALUATION_UNIT = "patient"
POSITIVE_GROUP = "Flare"
CLAIM_BOUNDARY = (
    "Permutation testing is an internal negative-control analysis only. "
    "It does not constitute external validation, clinical validation, or "
    "evidence of clinical diagnostic utility."
)

TASKS = (
    {
        "task": "flare_vs_managed",
        "case_group": "Flare",
        "control_group": "Managed",
    },
    {
        "task": "flare_vs_healthy",
        "case_group": "Flare",
        "control_group": "Healthy",
    },
)

PERMUTATION_FIELDNAMES = [
    "task",
    "permutation_index",
    "seed",
    "status",
    "permuted_auroc",
    "n_patients",
    "n_cases",
    "n_controls",
    "n_valid_folds",
    "label_shuffle_unit",
    "patient_identity_preserved",
    "scaler_fit_scope",
    "model_fit_scope",
    "claim_boundary",
]

SUMMARY_FIELDNAMES = [
    "task",
    "observed_auroc_internal_loocv",
    "n_permutations",
    "n_valid_permutations",
    "permutation_mean_auroc",
    "permutation_std_auroc",
    "permutation_min_auroc",
    "permutation_max_auroc",
    "empirical_p_value",
    "seed",
    "claim_boundary",
]


class Stage7PermutationTestError(ValueError):
    """Raised when the Stage 7 permutation control cannot run safely."""


@dataclass(frozen=True)
class PatientEmbeddingRecord:
    """One frozen patient-level embedding artifact."""

    patient_id: str
    group: str
    embedding_path: Path
    n_cells: int
    embedding_dim: int


def load_runtime_dependencies() -> dict[str, Any]:
    """Import runtime dependencies only when executing the control."""

    try:
        import numpy as np
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import roc_auc_score
        from sklearn.model_selection import LeaveOneOut
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:
        raise Stage7PermutationTestError(
            "Stage 7 permutation testing requires numpy and scikit-learn."
        ) from exc

    return {
        "np": np,
        "LogisticRegression": LogisticRegression,
        "roc_auc_score": roc_auc_score,
        "LeaveOneOut": LeaveOneOut,
        "StandardScaler": StandardScaler,
    }


def infer_group(patient_id: str) -> str:
    """Infer Stage 7 label group from the existing embedding filename policy."""

    if patient_id.startswith("FLARE"):
        return "Flare"
    if patient_id.startswith("HC") or patient_id.startswith("IGTB"):
        return "Healthy"
    return "Managed"


def default_embedding_dir() -> Path:
    """Use the recorded Stage 7 embedding directory when it is locally present."""

    if STAGE7_RUN_SUMMARY_PATH.exists():
        with STAGE7_RUN_SUMMARY_PATH.open(encoding="utf-8") as handle:
            summary = json.load(handle)
        recorded = Path(str(summary.get("embedding_dir", "")))
        if recorded.exists():
            return recorded
    return DEFAULT_KAGGLE_EMB_DIR


def discover_embedding_records(emb_dir: Path) -> list[PatientEmbeddingRecord]:
    """Discover existing frozen patient embedding files and validate shape."""

    deps = load_runtime_dependencies()
    np = deps["np"]

    if not emb_dir.exists():
        raise Stage7PermutationTestError(f"Embedding directory not found: {emb_dir}")

    records: list[PatientEmbeddingRecord] = []
    for path in sorted(emb_dir.glob("*.npy")):
        patient_id = path.stem
        embedding = np.load(path, mmap_mode="r")
        if embedding.ndim != 2:
            raise Stage7PermutationTestError(
                f"{path.name} must be a 2D cell-by-embedding matrix."
            )
        n_cells, embedding_dim = int(embedding.shape[0]), int(embedding.shape[1])
        if n_cells < 1 or embedding_dim < 1:
            raise Stage7PermutationTestError(
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
        raise Stage7PermutationTestError(f"No .npy embedding files found in {emb_dir}")

    dims = {record.embedding_dim for record in records}
    if len(dims) != 1:
        raise Stage7PermutationTestError(
            "All patient embeddings must have the same embedding dimension."
        )

    return records


def mean_pool_embeddings(records: Iterable[PatientEmbeddingRecord]):
    """Mean-pool existing cell embeddings to one vector per patient."""

    deps = load_runtime_dependencies()
    np = deps["np"]

    rows = []
    labels = []
    patient_ids = []
    groups = []

    for record in records:
        embedding = np.load(record.embedding_path)
        rows.append(embedding.mean(axis=0))
        labels.append(1 if record.group == POSITIVE_GROUP else 0)
        patient_ids.append(record.patient_id)
        groups.append(record.group)

    return np.asarray(rows), np.asarray(labels, dtype=int), patient_ids, groups


def load_observed_aurocs(metric_results_path: Path = STAGE7_METRIC_RESULTS_PATH) -> dict[str, float]:
    """Load existing Stage 7 observed AUROCs without editing source metrics."""

    if not metric_results_path.exists():
        return {}

    observed: dict[str, float] = {}
    with metric_results_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            task = str(row.get("task", "")).strip()
            auroc = str(row.get("auroc", "")).strip()
            if task and auroc:
                observed[task] = float(auroc)
    return observed


def run_patient_level_loocv_scores(
    X,
    y,
    *,
    seed: int,
    c_value: float = 0.1,
    max_iter: int = 1000,
):
    """Run patient-level LOOCV with fold-local scaler and logistic regression."""

    deps = load_runtime_dependencies()
    np = deps["np"]
    LogisticRegression = deps["LogisticRegression"]
    LeaveOneOut = deps["LeaveOneOut"]
    StandardScaler = deps["StandardScaler"]

    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=int)
    if X.ndim != 2:
        raise Stage7PermutationTestError("X must be a 2D patient-by-feature matrix.")
    if len(X) != len(y):
        raise Stage7PermutationTestError("X and y must contain the same patients.")
    if len(np.unique(y)) < 2:
        raise Stage7PermutationTestError("LOOCV requires both patient-level classes.")

    y_true = []
    y_score = []
    for fold_id, (train_idx, test_idx) in enumerate(LeaveOneOut().split(X), start=1):
        y_train = y[train_idx]
        if len(np.unique(y_train)) < 2:
            raise Stage7PermutationTestError(
                f"Fold {fold_id} train split has one class only."
            )

        scaler = StandardScaler()
        x_train_scaled = scaler.fit_transform(X[train_idx])
        x_test_scaled = scaler.transform(X[test_idx])

        clf = LogisticRegression(
            class_weight="balanced",
            max_iter=max_iter,
            C=c_value,
            random_state=seed,
        )
        clf.fit(x_train_scaled, y_train)

        y_true.append(int(y[test_idx][0]))
        y_score.append(float(clf.predict_proba(x_test_scaled)[0][1]))

    return np.asarray(y_true, dtype=int), np.asarray(y_score, dtype=float)


def compute_auroc(y_true, y_score) -> float:
    """Compute AUROC when both classes are present."""

    deps = load_runtime_dependencies()
    np = deps["np"]
    roc_auc_score = deps["roc_auc_score"]

    y_true = np.asarray(y_true, dtype=int)
    if len(np.unique(y_true)) < 2:
        raise Stage7PermutationTestError("AUROC requires both classes.")
    return float(roc_auc_score(y_true, y_score))


def run_task_permutation_control(
    *,
    task: str,
    X,
    y,
    patient_ids: Sequence[str],
    observed_auroc: float | None,
    n_permutations: int,
    seed: int,
    c_value: float = 0.1,
    max_iter: int = 1000,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Shuffle patient labels and run full patient-level LOOCV per permutation."""

    deps = load_runtime_dependencies()
    np = deps["np"]

    if n_permutations < 1:
        raise Stage7PermutationTestError("n_permutations must be at least 1.")
    if len(patient_ids) != len(y):
        raise Stage7PermutationTestError("patient_ids and y must align one-to-one.")

    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=int)
    if observed_auroc is None:
        observed_truth, observed_scores = run_patient_level_loocv_scores(
            X,
            y,
            seed=seed,
            c_value=c_value,
            max_iter=max_iter,
        )
        observed_auroc = compute_auroc(observed_truth, observed_scores)

    rng = np.random.default_rng(seed)
    rows: list[dict[str, Any]] = []
    valid_aurocs: list[float] = []

    for permutation_index in range(1, n_permutations + 1):
        permuted_y = np.array(y, copy=True)
        rng.shuffle(permuted_y)

        try:
            y_true, y_score = run_patient_level_loocv_scores(
                X,
                permuted_y,
                seed=seed,
                c_value=c_value,
                max_iter=max_iter,
            )
            auroc = compute_auroc(y_true, y_score)
            status = "completed"
            valid_aurocs.append(auroc)
        except Stage7PermutationTestError:
            auroc = math.nan
            status = "skipped_one_class_fold_or_metric"

        rows.append(
            {
                "task": task,
                "permutation_index": permutation_index,
                "seed": seed,
                "status": status,
                "permuted_auroc": auroc,
                "n_patients": int(len(y)),
                "n_cases": int((permuted_y == 1).sum()),
                "n_controls": int((permuted_y == 0).sum()),
                "n_valid_folds": int(len(y)) if status == "completed" else 0,
                "label_shuffle_unit": "patient",
                "patient_identity_preserved": True,
                "scaler_fit_scope": "train_fold_only",
                "model_fit_scope": "train_fold_only",
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

    summary = summarize_permutations(
        task=task,
        observed_auroc=float(observed_auroc),
        permutation_aurocs=valid_aurocs,
        n_permutations=n_permutations,
        seed=seed,
    )
    return rows, summary


def summarize_permutations(
    *,
    task: str,
    observed_auroc: float,
    permutation_aurocs: Sequence[float],
    n_permutations: int,
    seed: int,
) -> dict[str, Any]:
    """Summarize valid permutation AUROCs with a conservative empirical p-value."""

    deps = load_runtime_dependencies()
    np = deps["np"]

    valid = np.asarray(list(permutation_aurocs), dtype=float)
    valid = valid[np.isfinite(valid)]
    if len(valid) == 0:
        mean = std = minimum = maximum = empirical_p_value = math.nan
    else:
        mean = float(valid.mean())
        std = float(valid.std(ddof=1)) if len(valid) > 1 else 0.0
        minimum = float(valid.min())
        maximum = float(valid.max())
        empirical_p_value = float(
            ((valid >= observed_auroc).sum() + 1) / (len(valid) + 1)
        )

    return {
        "task": task,
        "observed_auroc_internal_loocv": float(observed_auroc),
        "n_permutations": int(n_permutations),
        "n_valid_permutations": int(len(valid)),
        "permutation_mean_auroc": mean,
        "permutation_std_auroc": std,
        "permutation_min_auroc": minimum,
        "permutation_max_auroc": maximum,
        "empirical_p_value": empirical_p_value,
        "seed": int(seed),
        "claim_boundary": CLAIM_BOUNDARY,
    }


def _format_csv_value(value: Any) -> Any:
    if isinstance(value, float) and math.isnan(value):
        return ""
    return value


def write_csv(path: Path, rows: Sequence[dict[str, Any]], fieldnames: Sequence[str]) -> None:
    """Write deterministic CSV output, including header-only TODO tables."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _format_csv_value(row.get(key, "")) for key in fieldnames})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_markdown_report(
    path: Path,
    *,
    status: str,
    output_dir: Path,
    emb_dir: Path,
    summary_rows: Sequence[dict[str, Any]],
    blocker: str | None = None,
) -> None:
    """Write a conservative Markdown report."""

    lines = [
        "# Stage 7 permutation-label negative control",
        "",
        CLAIM_BOUNDARY,
        "",
        "Internal negative-control only.",
        "",
        "Under patient-level label permutation, AUROC is expected to approach chance.",
        (
            "This supports that the observed internal LOOCV result is not trivially "
            "reproduced after destroying label-feature association."
        ),
        "",
        f"- Status: {status}",
        f"- Embedding directory: `{render_report_path(emb_dir)}`",
        f"- Output directory: `{render_report_path(output_dir)}`",
        "- Label shuffle unit: patient",
        "- Patient identity preserved: true",
        "- Split policy: leave-one-patient-out",
        "- Scaler fit scope: train fold only",
        "- Model fit scope: train fold only",
        "- Geneformer execution: not run",
        "- Embedding extraction: not run",
    ]
    if blocker:
        lines.extend(
            [
                "",
                "## TODO",
                "",
                blocker,
                "",
                "Required local embedding artifacts must be made available before "
                "permutation results can be generated.",
            ]
        )
    elif summary_rows:
        lines.extend(["", "## Summary", ""])
        header = (
            "| task | observed_auroc_internal_loocv | n_permutations | "
            "permutation_mean_auroc | empirical_p_value |"
        )
        lines.extend([header, "| --- | ---: | ---: | ---: | ---: |"])
        for row in summary_rows:
            lines.append(
                "| {task} | {observed:.6f} | {n_perm} | {mean:.6f} | {p:.6f} |".format(
                    task=row["task"],
                    observed=row["observed_auroc_internal_loocv"],
                    n_perm=row["n_permutations"],
                    mean=row["permutation_mean_auroc"],
                    p=row["empirical_p_value"],
                )
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_missing_artifact_outputs(
    *,
    output_dir: Path,
    emb_dir: Path,
    n_permutations: int,
    seed: int,
    blocker: str,
) -> dict[str, Any]:
    """Write explicit TODO outputs without fabricating permutation results."""

    permutation_path = output_dir / "permutation_results.csv"
    summary_path = output_dir / "permutation_summary.csv"
    json_path = output_dir / "run_summary.json"
    report_path = output_dir / "README.md"

    write_csv(permutation_path, [], PERMUTATION_FIELDNAMES)
    write_csv(summary_path, [], SUMMARY_FIELDNAMES)
    payload = {
        "status": "blocked_missing_embedding_artifact",
        "scope": "internal_negative_control_only",
        "embedding_dir": render_report_path(emb_dir),
        "n_permutations": int(n_permutations),
        "seed": int(seed),
        "blocker": blocker,
        "permutation_results": render_report_path(permutation_path),
        "permutation_summary": render_report_path(summary_path),
        "report": render_report_path(report_path),
        "claim_boundary": CLAIM_BOUNDARY,
        "external_validation_performed": False,
        "clinical_validation_performed": False,
        "clinical_diagnostic_claim": False,
        "geneformer_run": False,
        "embeddings_reextracted": False,
    }
    write_json(json_path, payload)
    write_markdown_report(
        report_path,
        status="blocked_missing_embedding_artifact",
        output_dir=output_dir,
        emb_dir=emb_dir,
        summary_rows=[],
        blocker=blocker,
    )
    return payload


def run_permutation_test(
    *,
    emb_dir: Path | None = None,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    n_permutations: int = 100,
    seed: int = 42,
    c_value: float = 0.1,
    max_iter: int = 1000,
) -> dict[str, Any]:
    """Run the Stage 7 patient-label permutation negative control."""

    selected_emb_dir = emb_dir or default_embedding_dir()
    try:
        records = discover_embedding_records(selected_emb_dir)
    except Stage7PermutationTestError as exc:
        return write_missing_artifact_outputs(
            output_dir=output_dir,
            emb_dir=selected_emb_dir,
            n_permutations=n_permutations,
            seed=seed,
            blocker=str(exc),
        )

    observed_aurocs = load_observed_aurocs()
    permutation_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for task_config in TASKS:
        task_records = [
            record
            for record in records
            if record.group in {task_config["case_group"], task_config["control_group"]}
        ]
        X, y, patient_ids, _groups = mean_pool_embeddings(task_records)
        rows, summary = run_task_permutation_control(
            task=task_config["task"],
            X=X,
            y=y,
            patient_ids=patient_ids,
            observed_auroc=observed_aurocs.get(task_config["task"]),
            n_permutations=n_permutations,
            seed=seed,
            c_value=c_value,
            max_iter=max_iter,
        )
        permutation_rows.extend(rows)
        summary_rows.append(summary)

    permutation_path = output_dir / "permutation_results.csv"
    summary_path = output_dir / "permutation_summary.csv"
    json_path = output_dir / "run_summary.json"
    report_path = output_dir / "README.md"

    write_csv(permutation_path, permutation_rows, PERMUTATION_FIELDNAMES)
    write_csv(summary_path, summary_rows, SUMMARY_FIELDNAMES)

    payload = {
        "status": "completed",
        "scope": "internal_patient_label_permutation_negative_control",
        "dataset_id": DATASET_ID,
        "model_family": MODEL_FAMILY,
        "split_policy": SPLIT_POLICY,
        "evaluation_unit": EVALUATION_UNIT,
        "embedding_dir": render_report_path(selected_emb_dir),
        "n_permutations": int(n_permutations),
        "seed": int(seed),
        "tasks": [row["task"] for row in summary_rows],
        "permutation_results": render_report_path(permutation_path),
        "permutation_summary": render_report_path(summary_path),
        "report": render_report_path(report_path),
        "summary": summary_rows,
        "claim_boundary": CLAIM_BOUNDARY,
        "external_validation_performed": False,
        "clinical_validation_performed": False,
        "clinical_diagnostic_claim": False,
        "geneformer_run": False,
        "embeddings_reextracted": False,
        "label_shuffle_unit": "patient",
        "patient_identity_preserved": True,
        "scaler_fit_scope": "train_fold_only",
        "model_fit_scope": "train_fold_only",
    }
    write_json(json_path, payload)
    write_markdown_report(
        report_path,
        status="completed",
        output_dir=output_dir,
        emb_dir=selected_emb_dir,
        summary_rows=summary_rows,
    )
    return payload
