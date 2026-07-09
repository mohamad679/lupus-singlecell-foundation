"""Stage 7 metadata-only internal LOOCV confounding-control baseline."""

from __future__ import annotations

import csv
import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    roc_auc_score,
)
from sklearn.model_selection import LeaveOneOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "reports" / "post_stage7_metadata_baseline"
DEFAULT_METADATA_ARTIFACT = REPO_ROOT / "data" / "processed" / "lupus_qc_processed.h5ad"

DATASET_ID = "GSE174188_CELLxGENE_patient_metadata_only_control"
MODEL_FAMILY = "metadata_only_logistic_regression"
SPLIT_POLICY = "leave_one_patient_out"
EVALUATION_UNIT = "patient"
POSITIVE_LABEL = "Flare"

CLAIM_BOUNDARY = (
    "Metadata-only baseline testing is an internal confounding-control analysis "
    "only. It does not constitute external validation, clinical validation, or "
    "evidence of clinical diagnostic utility."
)

TASKS = (
    {"task": "flare_vs_managed", "case_group": "Flare", "control_group": "Managed"},
    {"task": "flare_vs_healthy", "case_group": "Flare", "control_group": "Healthy"},
)

METADATA_MANIFEST_FIELDNAMES = [
    "patient_id",
    "task",
    "group",
    "label",
    "age",
    "sex",
    "n_cells",
    "feature_source",
]
PREDICTION_FIELDNAMES = [
    "run_id",
    "dataset_id",
    "task",
    "model_family",
    "split_policy",
    "evaluation_unit",
    "fold_id",
    "patient_id",
    "true_group",
    "label",
    "positive_label_score",
    "predicted_group",
    "predicted_label",
    "n_train",
    "n_train_cases",
    "n_train_controls",
    "feature_policy",
    "numeric_preprocessing_scope",
    "categorical_preprocessing_scope",
    "scaler_fit_scope",
    "model_fit_scope",
    "claim_boundary",
]
METRIC_FIELDNAMES = [
    "run_id",
    "dataset_id",
    "model_family",
    "task",
    "split_policy",
    "evaluation_unit",
    "n_patients",
    "n_cases",
    "n_controls",
    "auroc",
    "auprc",
    "balanced_accuracy",
    "accuracy",
    "status",
    "audit_status",
    "notes",
]

ADMIN_COLUMNS = {"patient_id", "task", "group", "label", "feature_source"}
DISALLOWED_FEATURE_PATTERNS = (
    r"^embedding(_|$)",
    r"^geneformer",
    r"^expr",
    r"^gene_",
    r"^pc\d*$",
)


class Stage7MetadataBaselineError(ValueError):
    """Raised when the metadata-only control cannot run safely."""


@dataclass(frozen=True)
class MetadataAvailability:
    artifact_found: bool
    artifact_path: str
    artifact_type: str
    patient_id_available: bool
    label_available: bool
    age_available: bool
    sex_available: bool
    cell_type_available: bool
    cell_count_available: bool
    field_probe: tuple[str, ...]


@dataclass(frozen=True)
class FoldDebug:
    task: str
    fold_id: str
    test_patient_id: str
    train_patient_ids: tuple[str, ...]
    numeric_columns: tuple[str, ...]
    categorical_columns: tuple[str, ...]
    numeric_imputer_statistics: dict[str, float]
    one_hot_categories: dict[str, tuple[str, ...]]


def render_report_path(path: Path) -> str:
    candidate = Path(path)
    try:
        return str(candidate.resolve().relative_to(REPO_ROOT.resolve()))
    except (OSError, ValueError):
        return f"<external-local-artifact:{candidate.name}>"


def sanitize_column_name(value: Any) -> str:
    normalized = re.sub(r"[^0-9a-zA-Z]+", "_", str(value).strip().lower()).strip("_")
    return normalized or "unknown"


def _format_csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return value


def write_csv(path: Path, rows: Sequence[Mapping[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: _format_csv_value(row.get(key, "")) for key in fieldnames})


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def probe_h5ad_fields(path: Path) -> tuple[str, ...]:
    tokens = (
        "patient_id",
        "donor_id",
        "disease_group",
        "cell_type",
        "age",
        "sex",
        "gender",
    )
    found: set[str] = set()
    if not path.exists():
        return ()

    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            lowered = chunk.lower()
            for token in tokens:
                if token.encode("utf-8") in lowered:
                    found.add(token)
            if len(found) == len(tokens):
                break

    return tuple(sorted(found))


def inspect_metadata_artifact(path: Path) -> MetadataAvailability:
    suffix = path.suffix.lower()
    field_probe = probe_h5ad_fields(path) if suffix == ".h5ad" else ()
    return MetadataAvailability(
        artifact_found=path.exists(),
        artifact_path=render_report_path(path),
        artifact_type=suffix.lstrip(".") or "unknown",
        patient_id_available="patient_id" in field_probe or "donor_id" in field_probe,
        label_available="disease_group" in field_probe,
        age_available="age" in field_probe,
        sex_available="sex" in field_probe or "gender" in field_probe,
        cell_type_available="cell_type" in field_probe,
        cell_count_available=path.exists(),
        field_probe=field_probe,
    )


def load_cell_metadata_frame(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise Stage7MetadataBaselineError(f"Metadata artifact not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix != ".h5ad":
        raise Stage7MetadataBaselineError(
            f"Unsupported metadata artifact type: {path.suffix or '<none>'}"
        )

    try:
        import anndata as ad
    except ImportError as exc:
        raise Stage7MetadataBaselineError(
            "Local .h5ad metadata artifact exists, but `anndata` is not installed. "
            "Install `anndata` to extract patient-level metadata features."
        ) from exc

    adata = ad.read_h5ad(path, backed="r")
    obs = adata.obs.copy()
    return pd.DataFrame(obs)


def _find_column(columns: Iterable[str], candidates: Sequence[str]) -> str | None:
    lowered = {str(column).strip().lower(): str(column) for column in columns}
    for candidate in candidates:
        if candidate in lowered:
            return lowered[candidate]
    return None


def _collapse_patient_scalar(
    frame: pd.DataFrame,
    patient_col: str,
    value_col: str | None,
) -> pd.Series:
    if value_col is None:
        return pd.Series(dtype=object)

    def _single_value(series: pd.Series) -> Any:
        observed = [item for item in series.tolist() if pd.notna(item) and str(item).strip() != ""]
        if not observed:
            return np.nan
        normalized = {str(item).strip() for item in observed}
        if len(normalized) != 1:
            raise Stage7MetadataBaselineError(
                f"Patient-level metadata conflict in column {value_col!r}."
            )
        return observed[0]

    return frame.groupby(patient_col, sort=True)[value_col].apply(_single_value)


def validate_no_disallowed_feature_columns(columns: Iterable[str]) -> None:
    invalid = []
    for column in columns:
        normalized = str(column).strip().lower()
        if normalized in ADMIN_COLUMNS:
            continue
        if any(re.search(pattern, normalized) for pattern in DISALLOWED_FEATURE_PATTERNS):
            invalid.append(str(column))
    if invalid:
        raise Stage7MetadataBaselineError(
            "Metadata-only baseline cannot use Geneformer or expression features: "
            + ", ".join(sorted(invalid))
        )


def build_patient_metadata_feature_table(cell_metadata: pd.DataFrame) -> tuple[pd.DataFrame, MetadataAvailability]:
    if cell_metadata.empty:
        raise Stage7MetadataBaselineError("Cell metadata frame is empty.")

    patient_col = _find_column(cell_metadata.columns, ("patient_id", "donor_id"))
    label_col = _find_column(
        cell_metadata.columns,
        ("disease_group", "disease_label", "disease", "group", "condition"),
    )
    age_col = _find_column(cell_metadata.columns, ("age", "age_years"))
    sex_col = _find_column(cell_metadata.columns, ("sex", "gender"))
    cell_type_col = _find_column(cell_metadata.columns, ("cell_type", "celltype", "cell_type_annotation"))

    if patient_col is None:
        raise Stage7MetadataBaselineError("No patient-level identifier column was found.")
    if label_col is None:
        raise Stage7MetadataBaselineError("No disease-group label column was found.")

    normalized = cell_metadata.copy()
    normalized[patient_col] = normalized[patient_col].astype(str).str.strip()
    normalized[label_col] = normalized[label_col].astype(str).str.strip()
    normalized = normalized[normalized[patient_col] != ""]
    normalized = normalized[normalized[label_col] != ""]
    if normalized.empty:
        raise Stage7MetadataBaselineError("No usable patient rows remain after normalization.")

    label_by_patient = _collapse_patient_scalar(normalized, patient_col, label_col)
    n_cells = normalized.groupby(patient_col, sort=True).size().astype(int)

    patient_table = pd.DataFrame(
        {
            "patient_id": label_by_patient.index.astype(str),
            "group": label_by_patient.astype(str).values,
            "age": _collapse_patient_scalar(normalized, patient_col, age_col).reindex(label_by_patient.index).values
            if age_col
            else np.nan,
            "sex": _collapse_patient_scalar(normalized, patient_col, sex_col).reindex(label_by_patient.index).values
            if sex_col
            else np.nan,
            "n_cells": n_cells.reindex(label_by_patient.index).astype(int).values,
            "feature_source": "patient_level_metadata_and_cell_composition_only",
        }
    )

    if age_col:
        patient_table["age"] = pd.to_numeric(patient_table["age"], errors="coerce")
    else:
        patient_table["age"] = np.nan

    if cell_type_col is not None:
        counts = (
            normalized.groupby([patient_col, cell_type_col], sort=True)
            .size()
            .unstack(fill_value=0)
            .sort_index(axis=1)
        )
        proportions = counts.div(counts.sum(axis=1), axis=0).fillna(0.0)
        proportions.columns = [
            f"cell_type_prop_{sanitize_column_name(column)}" for column in proportions.columns
        ]
        patient_table = patient_table.merge(
            proportions.reset_index().rename(columns={patient_col: "patient_id"}),
            on="patient_id",
            how="left",
        )

    patient_table = patient_table.sort_values("patient_id").reset_index(drop=True)
    validate_no_disallowed_feature_columns(patient_table.columns)

    availability = MetadataAvailability(
        artifact_found=True,
        artifact_path="<in_memory>",
        artifact_type="dataframe",
        patient_id_available=True,
        label_available=True,
        age_available=age_col is not None,
        sex_available=sex_col is not None,
        cell_type_available=cell_type_col is not None,
        cell_count_available=True,
        field_probe=tuple(
            item
            for item, present in (
                ("patient_id", True),
                ("disease_group", True),
                ("age", age_col is not None),
                ("sex", sex_col is not None),
                ("cell_type", cell_type_col is not None),
            )
            if present
        ),
    )
    return patient_table, availability


def build_task_feature_manifest(patient_table: pd.DataFrame) -> pd.DataFrame:
    manifests = []
    for task_config in TASKS:
        task_table = patient_table[
            patient_table["group"].isin(
                [task_config["case_group"], task_config["control_group"]]
            )
        ].copy()
        task_table.insert(1, "task", task_config["task"])
        task_table.insert(
            3,
            "label",
            (task_table["group"] == task_config["case_group"]).astype(int),
        )
        manifests.append(task_table)

    if not manifests:
        raise Stage7MetadataBaselineError("No task rows were created from patient metadata.")
    manifest = pd.concat(manifests, ignore_index=True)
    validate_no_disallowed_feature_columns(manifest.columns)
    return manifest


def feature_manifest_fieldnames(manifest: pd.DataFrame) -> list[str]:
    base = METADATA_MANIFEST_FIELDNAMES.copy()
    extras = [column for column in manifest.columns if column not in base]
    return base + extras


def select_model_feature_columns(task_table: pd.DataFrame) -> tuple[list[str], list[str]]:
    validate_no_disallowed_feature_columns(task_table.columns)

    numeric_columns = []
    categorical_columns = []
    for column in task_table.columns:
        if column in ADMIN_COLUMNS:
            continue
        if column == "age" or column == "n_cells" or column.startswith("cell_type_prop_") or column.startswith("tech_count_"):
            numeric_columns.append(column)
        elif column == "sex":
            categorical_columns.append(column)

    if not numeric_columns and not categorical_columns:
        raise Stage7MetadataBaselineError("No allowed metadata-only feature columns were found.")
    return numeric_columns, categorical_columns


def _one_hot_encoder() -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def run_task_loocv_baseline(
    task_table: pd.DataFrame,
    *,
    task: str,
    c_value: float = 0.1,
    max_iter: int = 1000,
    random_state: int = 42,
    return_debug: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[FoldDebug]]:
    if task_table["patient_id"].duplicated().any():
        raise Stage7MetadataBaselineError(f"{task} task manifest has duplicate patient rows.")

    numeric_columns, categorical_columns = select_model_feature_columns(task_table)
    X = task_table[numeric_columns + categorical_columns].copy()
    y = task_table["label"].astype(int).to_numpy()
    patient_ids = task_table["patient_id"].astype(str).tolist()
    groups = task_table["group"].astype(str).tolist()

    if len(np.unique(y)) != 2:
        raise Stage7MetadataBaselineError(f"{task} requires exactly two classes.")

    transformers: list[tuple[str, Any, list[str]]] = []
    if numeric_columns:
        transformers.append(
            (
                "numeric",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_columns,
            )
        )
    if categorical_columns:
        transformers.append(
            (
                "categorical",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", _one_hot_encoder()),
                    ]
                ),
                categorical_columns,
            )
        )

    preprocessor = ColumnTransformer(transformers=transformers, remainder="drop")
    loo = LeaveOneOut()

    rows: list[dict[str, Any]] = []
    debug_rows: list[FoldDebug] = []
    y_true: list[int] = []
    y_score: list[float] = []
    y_pred: list[int] = []

    for fold_index, (train_idx, test_idx) in enumerate(loo.split(X), start=1):
        X_train = X.iloc[train_idx]
        X_test = X.iloc[test_idx]
        y_train = y[train_idx]

        if len(np.unique(y_train)) != 2:
            raise Stage7MetadataBaselineError(
                f"{task} fold {fold_index} has only one class in training."
            )

        fitted = preprocessor.fit(X_train)
        X_train_transformed = fitted.transform(X_train)
        X_test_transformed = fitted.transform(X_test)

        model = LogisticRegression(
            class_weight="balanced",
            C=c_value,
            max_iter=max_iter,
            random_state=random_state,
        )
        model.fit(X_train_transformed, y_train)
        score = float(model.predict_proba(X_test_transformed)[0][1])
        predicted = int(score >= 0.5)

        held_out_index = int(test_idx[0])
        y_true.append(int(y[held_out_index]))
        y_score.append(score)
        y_pred.append(predicted)

        rows.append(
            {
                "run_id": f"stage7_metadata_{task}_loocv",
                "dataset_id": DATASET_ID,
                "task": task,
                "model_family": MODEL_FAMILY,
                "split_policy": SPLIT_POLICY,
                "evaluation_unit": EVALUATION_UNIT,
                "fold_id": f"loocv_{fold_index:03d}",
                "patient_id": patient_ids[held_out_index],
                "true_group": groups[held_out_index],
                "label": int(y[held_out_index]),
                "positive_label_score": score,
                "predicted_group": POSITIVE_LABEL if predicted == 1 else next(
                    item for item in sorted(set(groups)) if item != POSITIVE_LABEL
                ),
                "predicted_label": predicted,
                "n_train": int(len(train_idx)),
                "n_train_cases": int(y_train.sum()),
                "n_train_controls": int(len(train_idx) - y_train.sum()),
                "feature_policy": "patient_level_metadata_and_cell_composition_only",
                "numeric_preprocessing_scope": "train_fold_only",
                "categorical_preprocessing_scope": "train_fold_only",
                "scaler_fit_scope": "train_fold_only",
                "model_fit_scope": "train_fold_only",
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )

        if return_debug:
            numeric_stats: dict[str, float] = {}
            one_hot_categories: dict[str, tuple[str, ...]] = {}
            if numeric_columns:
                numeric_pipeline = fitted.named_transformers_["numeric"]
                stats = numeric_pipeline.named_steps["imputer"].statistics_
                numeric_stats = {
                    column: float(value)
                    for column, value in zip(numeric_columns, stats, strict=True)
                }
            if categorical_columns:
                categorical_pipeline = fitted.named_transformers_["categorical"]
                categories = categorical_pipeline.named_steps["onehot"].categories_
                one_hot_categories = {
                    column: tuple(str(item) for item in values)
                    for column, values in zip(categorical_columns, categories, strict=True)
                }
            debug_rows.append(
                FoldDebug(
                    task=task,
                    fold_id=f"loocv_{fold_index:03d}",
                    test_patient_id=patient_ids[held_out_index],
                    train_patient_ids=tuple(patient_ids[idx] for idx in train_idx),
                    numeric_columns=tuple(numeric_columns),
                    categorical_columns=tuple(categorical_columns),
                    numeric_imputer_statistics=numeric_stats,
                    one_hot_categories=one_hot_categories,
                )
            )

    metrics = {
        "run_id": f"stage7_metadata_{task}_loocv",
        "dataset_id": DATASET_ID,
        "model_family": MODEL_FAMILY,
        "task": task,
        "split_policy": SPLIT_POLICY,
        "evaluation_unit": EVALUATION_UNIT,
        "n_patients": int(len(task_table)),
        "n_cases": int(sum(y_true)),
        "n_controls": int(len(y_true) - sum(y_true)),
        "auroc": float(roc_auc_score(y_true, y_score)),
        "auprc": float(average_precision_score(y_true, y_score)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "status": "completed",
        "audit_status": "internal_metadata_only_control",
        "notes": (
            "This baseline uses only patient-level metadata and cell-composition "
            "features. Internal confounding-control only."
        ),
    }
    return rows, metrics, debug_rows


def write_readme(
    path: Path,
    *,
    status: str,
    output_dir: Path,
    artifact_path: Path,
    availability: MetadataAvailability,
    metric_rows: Sequence[Mapping[str, Any]],
    blocker: str | None = None,
) -> None:
    lines = [
        "# Stage 7 metadata-only baseline",
        "",
        CLAIM_BOUNDARY,
        "",
        "This baseline uses only patient-level metadata and cell-composition features.",
        "This control assesses whether simple metadata features can reproduce the internal LOOCV signal.",
        "Internal confounding-control only.",
        "",
        f"- Status: {status}",
        f"- Metadata artifact: `{availability.artifact_path}`",
        f"- Output directory: `{render_report_path(output_dir)}`",
        f"- Age available: {str(availability.age_available).lower()}",
        f"- Sex available: {str(availability.sex_available).lower()}",
        f"- Cell-type annotations available: {str(availability.cell_type_available).lower()}",
        f"- Cell counts available: {str(availability.cell_count_available).lower()}",
        "- Geneformer execution: not run",
        "- Geneformer embeddings: not used",
        "- Evaluation unit: patient",
        "- Split policy: leave-one-patient-out",
    ]
    if blocker:
        lines.extend(
            [
                "",
                "## TODO",
                "",
                blocker,
            ]
        )
    elif metric_rows:
        lines.extend(["", "## Metrics", "", "| task | auroc | auprc | balanced_accuracy | accuracy |", "| --- | ---: | ---: | ---: | ---: |"])
        for row in metric_rows:
            lines.append(
                "| {task} | {auroc:.6f} | {auprc:.6f} | {balanced_accuracy:.6f} | {accuracy:.6f} |".format(
                    **row
                )
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_blocked_outputs(
    *,
    output_dir: Path,
    artifact_path: Path,
    availability: MetadataAvailability,
    blocker: str,
    status: str,
) -> dict[str, Any]:
    feature_path = output_dir / "metadata_feature_manifest.csv"
    prediction_path = output_dir / "metadata_baseline_predictions.csv"
    metrics_path = output_dir / "metadata_baseline_metrics.csv"
    summary_path = output_dir / "run_summary.json"
    readme_path = output_dir / "README.md"

    write_csv(feature_path, [], METADATA_MANIFEST_FIELDNAMES)
    write_csv(prediction_path, [], PREDICTION_FIELDNAMES)
    write_csv(metrics_path, [], METRIC_FIELDNAMES)

    payload = {
        "status": status,
        "scope": "internal_metadata_only_control",
        "metadata_artifact": availability.artifact_path,
        "artifact_type": availability.artifact_type,
        "artifact_found": availability.artifact_found,
        "age_available": availability.age_available,
        "sex_available": availability.sex_available,
        "cell_type_available": availability.cell_type_available,
        "cell_count_available": availability.cell_count_available,
        "patient_id_available": availability.patient_id_available,
        "label_available": availability.label_available,
        "field_probe": list(availability.field_probe),
        "blocker": blocker,
        "metadata_feature_manifest": render_report_path(feature_path),
        "metadata_baseline_predictions": render_report_path(prediction_path),
        "metadata_baseline_metrics": render_report_path(metrics_path),
        "report": render_report_path(readme_path),
        "claim_boundary": CLAIM_BOUNDARY,
        "external_validation_performed": False,
        "clinical_validation_performed": False,
        "clinical_diagnostic_claim": False,
        "geneformer_run": False,
        "geneformer_embeddings_used": False,
    }
    write_json(summary_path, payload)
    write_readme(
        readme_path,
        status=status,
        output_dir=output_dir,
        artifact_path=artifact_path,
        availability=availability,
        metric_rows=[],
        blocker=blocker,
    )
    return payload


def run_metadata_baseline(
    *,
    metadata_artifact: Path | None = None,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    c_value: float = 0.1,
    max_iter: int = 1000,
    random_state: int = 42,
) -> dict[str, Any]:
    artifact_path = metadata_artifact or DEFAULT_METADATA_ARTIFACT
    availability = inspect_metadata_artifact(artifact_path)
    if not artifact_path.exists():
        return write_blocked_outputs(
            output_dir=output_dir,
            artifact_path=artifact_path,
            availability=availability,
            blocker=f"Required local metadata artifact was not found: {artifact_path.name}",
            status="blocked_missing_metadata_artifact",
        )

    try:
        cell_metadata = load_cell_metadata_frame(artifact_path)
        patient_table, runtime_availability = build_patient_metadata_feature_table(cell_metadata)
        availability = MetadataAvailability(
            artifact_found=True,
            artifact_path=availability.artifact_path,
            artifact_type=availability.artifact_type,
            patient_id_available=runtime_availability.patient_id_available,
            label_available=runtime_availability.label_available,
            age_available=runtime_availability.age_available,
            sex_available=runtime_availability.sex_available,
            cell_type_available=runtime_availability.cell_type_available,
            cell_count_available=runtime_availability.cell_count_available,
            field_probe=availability.field_probe or runtime_availability.field_probe,
        )
        manifest = build_task_feature_manifest(patient_table)
    except Stage7MetadataBaselineError as exc:
        return write_blocked_outputs(
            output_dir=output_dir,
            artifact_path=artifact_path,
            availability=availability,
            blocker=str(exc),
            status="blocked_metadata_extraction",
        )

    prediction_rows: list[dict[str, Any]] = []
    metric_rows: list[dict[str, Any]] = []
    for task_config in TASKS:
        task_table = manifest[manifest["task"] == task_config["task"]].reset_index(drop=True)
        rows, metrics, _debug = run_task_loocv_baseline(
            task_table,
            task=task_config["task"],
            c_value=c_value,
            max_iter=max_iter,
            random_state=random_state,
            return_debug=False,
        )
        prediction_rows.extend(rows)
        metric_rows.append(metrics)

    feature_path = output_dir / "metadata_feature_manifest.csv"
    prediction_path = output_dir / "metadata_baseline_predictions.csv"
    metrics_path = output_dir / "metadata_baseline_metrics.csv"
    summary_path = output_dir / "run_summary.json"
    readme_path = output_dir / "README.md"

    write_csv(
        feature_path,
        manifest.to_dict(orient="records"),
        feature_manifest_fieldnames(manifest),
    )
    write_csv(prediction_path, prediction_rows, PREDICTION_FIELDNAMES)
    write_csv(metrics_path, metric_rows, METRIC_FIELDNAMES)

    payload = {
        "status": "completed",
        "scope": "internal_metadata_only_control",
        "dataset_id": DATASET_ID,
        "model_family": MODEL_FAMILY,
        "split_policy": SPLIT_POLICY,
        "evaluation_unit": EVALUATION_UNIT,
        "metadata_artifact": availability.artifact_path,
        "artifact_type": availability.artifact_type,
        "artifact_found": availability.artifact_found,
        "age_available": availability.age_available,
        "sex_available": availability.sex_available,
        "cell_type_available": availability.cell_type_available,
        "cell_count_available": availability.cell_count_available,
        "field_probe": list(availability.field_probe),
        "tasks": [row["task"] for row in metric_rows],
        "metadata_feature_manifest": render_report_path(feature_path),
        "metadata_baseline_predictions": render_report_path(prediction_path),
        "metadata_baseline_metrics": render_report_path(metrics_path),
        "report": render_report_path(readme_path),
        "claim_boundary": CLAIM_BOUNDARY,
        "external_validation_performed": False,
        "clinical_validation_performed": False,
        "clinical_diagnostic_claim": False,
        "geneformer_run": False,
        "geneformer_embeddings_used": False,
        "summary": metric_rows,
    }
    write_json(summary_path, payload)
    write_readme(
        readme_path,
        status="completed",
        output_dir=output_dir,
        artifact_path=artifact_path,
        availability=availability,
        metric_rows=metric_rows,
    )
    return payload
