"""Stage 7 internal confounding audit for technical and compositional variables."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import numpy as np
import pandas as pd

from lupusfm.evaluation.stage7_metadata_baseline import (
    DEFAULT_METADATA_ARTIFACT,
    REPO_ROOT,
    TASKS,
    MetadataAvailability,
    Stage7MetadataBaselineError,
    _collapse_patient_scalar,
    _find_column,
    load_cell_metadata_frame,
    render_report_path,
    sanitize_column_name,
    validate_no_disallowed_feature_columns,
    write_csv,
    write_json,
)


DEFAULT_OUTPUT_DIR = REPO_ROOT / "reports" / "post_stage7_confounding_audit"

CLAIM_BOUNDARY = (
    "Confounding audit is an internal dataset-structure analysis only. "
    "It does not constitute external validation, clinical validation, or "
    "evidence of clinical diagnostic utility."
)

DATASET_ID = "GSE174188_CELLxGENE_stage7_internal_confounding_audit"
AUDIT_SCOPE = "internal_dataset_structure_audit_only"
EVALUATION_UNIT = "patient"
MIXED_WITHIN_PATIENT = "__mixed_within_patient__"
MISSING_CATEGORY = "__missing__"

PATIENT_ID_CANDIDATES = ("patient_id", "donor_id", "donor", "sample_id")
LABEL_CANDIDATES = (
    "disease_group",
    "disease_label",
    "disease",
    "group",
    "condition",
)
CELL_TYPE_CANDIDATES = (
    "cell_type",
    "celltype",
    "cell_type_annotation",
    "annotation",
    "cell_label",
)
SOURCE_BATCH_CANDIDATES = (
    "source",
    "batch",
    "dataset",
    "sample_source",
    "library",
    "library_id",
    "library_batch",
    "chemistry",
    "platform",
    "center",
    "site",
    "sequencing_batch",
    "processing_batch",
    "study",
    "accession",
)
FIELD_PROBE_TOKENS = tuple(
    sorted(set(PATIENT_ID_CANDIDATES + LABEL_CANDIDATES + CELL_TYPE_CANDIDATES + SOURCE_BATCH_CANDIDATES))
)

PATIENT_MANIFEST_BASE_FIELDNAMES = [
    "patient_id",
    "group",
    "task",
    "label",
    "n_cells",
    "log1p_n_cells",
]
CELL_COUNT_AUDIT_FIELDNAMES = [
    "task",
    "case_group",
    "control_group",
    "n_patients",
    "n_cases",
    "n_controls",
    "mean_n_cells_case",
    "mean_n_cells_control",
    "median_n_cells_case",
    "median_n_cells_control",
    "mean_log1p_n_cells_case",
    "mean_log1p_n_cells_control",
    "log1p_n_cells_smd",
    "warning_flag",
]
CELL_TYPE_AUDIT_FIELDNAMES = [
    "task",
    "case_group",
    "control_group",
    "cell_type_feature",
    "mean_prop_case",
    "mean_prop_control",
    "abs_mean_prop_diff",
    "warning_flag",
]
SOURCE_BATCH_AUDIT_FIELDNAMES = [
    "task",
    "case_group",
    "control_group",
    "source_field",
    "source_column",
    "category",
    "n_patients",
    "n_cases",
    "n_controls",
    "case_class_proportion",
    "control_class_proportion",
    "abs_class_proportion_diff",
    "present_in_only_one_class",
    "warning_flag",
]
SUMMARY_FIELDNAMES = [
    "task",
    "case_group",
    "control_group",
    "n_patients",
    "n_cases",
    "n_controls",
    "cell_count_warning_flag",
    "top_cell_type_imbalances",
    "source_batch_warning_fields",
    "source_batch_categories_flagged",
    "warning_flag",
    "notes",
]


@dataclass(frozen=True)
class ConfoundingAvailability:
    artifact_found: bool
    artifact_path: str
    artifact_type: str
    patient_id_available: bool
    label_available: bool
    cell_type_available: bool
    cell_count_available: bool
    source_batch_fields_available: bool
    source_batch_fields: tuple[str, ...]
    field_probe: tuple[str, ...]


@dataclass(frozen=True)
class PatientAuditBuild:
    patient_table: pd.DataFrame
    availability: ConfoundingAvailability
    source_columns: tuple[str, ...]
    cell_type_columns: tuple[str, ...]


def _probe_metadata_fields(path: Path) -> tuple[str, ...]:
    if not path.exists():
        return ()

    found: set[str] = set()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            lowered = chunk.lower()
            for token in FIELD_PROBE_TOKENS:
                if token.encode("utf-8") in lowered:
                    found.add(token)
            if len(found) == len(FIELD_PROBE_TOKENS):
                break
    return tuple(sorted(found))


def inspect_confounding_metadata_artifact(path: Path) -> ConfoundingAvailability:
    suffix = path.suffix.lower()
    field_probe = _probe_metadata_fields(path) if suffix == ".h5ad" else ()
    source_fields = tuple(
        candidate for candidate in SOURCE_BATCH_CANDIDATES if candidate in field_probe
    )
    return ConfoundingAvailability(
        artifact_found=path.exists(),
        artifact_path=render_report_path(path),
        artifact_type=suffix.lstrip(".") or "unknown",
        patient_id_available=any(candidate in field_probe for candidate in PATIENT_ID_CANDIDATES),
        label_available=any(candidate in field_probe for candidate in LABEL_CANDIDATES),
        cell_type_available=any(candidate in field_probe for candidate in CELL_TYPE_CANDIDATES),
        cell_count_available=path.exists(),
        source_batch_fields_available=bool(source_fields),
        source_batch_fields=source_fields,
        field_probe=field_probe,
    )


def _collapse_patient_category(frame: pd.DataFrame, patient_col: str, value_col: str) -> pd.Series:
    def _category(series: pd.Series) -> Any:
        observed = [
            str(item).strip()
            for item in series.tolist()
            if pd.notna(item) and str(item).strip() != ""
        ]
        if not observed:
            return np.nan
        categories = sorted(set(observed))
        if len(categories) == 1:
            return categories[0]
        return MIXED_WITHIN_PATIENT

    return frame.groupby(patient_col, sort=True)[value_col].apply(_category)


def _feature_fieldnames(base: Sequence[str], frame: pd.DataFrame) -> list[str]:
    extras = [column for column in frame.columns if column not in base]
    return list(base) + extras


def _detect_source_batch_columns(
    columns: Iterable[str],
    *,
    excluded: Iterable[str],
) -> list[str]:
    excluded_set = {str(value) for value in excluded}
    lowered = {str(column).strip().lower(): str(column) for column in columns}
    selected: list[str] = []
    for candidate in SOURCE_BATCH_CANDIDATES:
        column = lowered.get(candidate)
        if column is None or column in excluded_set:
            continue
        selected.append(column)
    validate_no_disallowed_feature_columns(selected)
    return selected


def build_patient_confounding_table(cell_metadata: pd.DataFrame) -> PatientAuditBuild:
    if cell_metadata.empty:
        raise Stage7MetadataBaselineError("Cell metadata frame is empty.")

    validate_no_disallowed_feature_columns(cell_metadata.columns)

    patient_col = _find_column(cell_metadata.columns, PATIENT_ID_CANDIDATES)
    label_col = _find_column(cell_metadata.columns, LABEL_CANDIDATES)
    cell_type_col = _find_column(cell_metadata.columns, CELL_TYPE_CANDIDATES)
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
            "n_cells": n_cells.reindex(label_by_patient.index).astype(int).values,
        }
    )
    patient_table["log1p_n_cells"] = patient_table["n_cells"].astype(float).map(np.log1p)

    source_columns = _detect_source_batch_columns(
        normalized.columns,
        excluded=(patient_col, label_col, cell_type_col),
    )
    for source_column in source_columns:
        manifest_column = f"source_field_{sanitize_column_name(source_column)}"
        patient_table[manifest_column] = (
            _collapse_patient_category(normalized, patient_col, source_column)
            .reindex(label_by_patient.index)
            .values
        )

    cell_type_columns: list[str] = []
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
        cell_type_columns = [str(column) for column in proportions.columns]
        patient_table = patient_table.merge(
            proportions.reset_index().rename(columns={patient_col: "patient_id"}),
            on="patient_id",
            how="left",
        )

    patient_table = patient_table.sort_values("patient_id").reset_index(drop=True)
    validate_no_disallowed_feature_columns(patient_table.columns)

    availability = ConfoundingAvailability(
        artifact_found=True,
        artifact_path="<in_memory>",
        artifact_type="dataframe",
        patient_id_available=True,
        label_available=True,
        cell_type_available=cell_type_col is not None,
        cell_count_available=True,
        source_batch_fields_available=bool(source_columns),
        source_batch_fields=tuple(source_columns),
        field_probe=tuple(
            item
            for item, present in (
                ("patient_id", True),
                ("disease_group", True),
                ("cell_type", cell_type_col is not None),
                *[(column, True) for column in source_columns],
            )
            if present
        ),
    )
    return PatientAuditBuild(
        patient_table=patient_table,
        availability=availability,
        source_columns=tuple(f"source_field_{sanitize_column_name(column)}" for column in source_columns),
        cell_type_columns=tuple(cell_type_columns),
    )


def build_task_confounding_manifest(patient_table: pd.DataFrame) -> pd.DataFrame:
    manifests: list[pd.DataFrame] = []
    for task_config in TASKS:
        task_table = patient_table[
            patient_table["group"].isin(
                [task_config["case_group"], task_config["control_group"]]
            )
        ].copy()
        task_table.insert(2, "task", task_config["task"])
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


def _task_groups(task: str) -> tuple[str, str]:
    for task_config in TASKS:
        if task_config["task"] == task:
            return task_config["case_group"], task_config["control_group"]
    raise Stage7MetadataBaselineError(f"Unknown task: {task}")


def _standardized_mean_difference(case_values: pd.Series, control_values: pd.Series) -> float:
    case = pd.to_numeric(case_values, errors="coerce").dropna().astype(float)
    control = pd.to_numeric(control_values, errors="coerce").dropna().astype(float)
    if case.empty or control.empty:
        return float("nan")

    case_mean = float(case.mean())
    control_mean = float(control.mean())
    if len(case) < 2 and len(control) < 2:
        return 0.0 if math.isclose(case_mean, control_mean) else float("nan")

    case_var = float(case.var(ddof=1)) if len(case) > 1 else 0.0
    control_var = float(control.var(ddof=1)) if len(control) > 1 else 0.0
    denominator = len(case) + len(control) - 2
    pooled_variance = (
        ((len(case) - 1) * case_var + (len(control) - 1) * control_var) / denominator
        if denominator > 0
        else 0.0
    )
    pooled_sd = math.sqrt(max(pooled_variance, 0.0))
    if pooled_sd == 0.0:
        return 0.0 if math.isclose(case_mean, control_mean) else float("inf")
    return (case_mean - control_mean) / pooled_sd


def _warning_flag(value: float, *, moderate: float, strong: float) -> str:
    if not math.isfinite(value):
        return "not_estimable"
    absolute = abs(value)
    if absolute >= strong:
        return "strong"
    if absolute >= moderate:
        return "flag"
    return "none"


def audit_cell_counts(manifest: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task_config in TASKS:
        task = task_config["task"]
        task_table = manifest[manifest["task"] == task].copy()
        case_table = task_table[task_table["label"] == 1]
        control_table = task_table[task_table["label"] == 0]
        smd = _standardized_mean_difference(
            case_table["log1p_n_cells"],
            control_table["log1p_n_cells"],
        )
        rows.append(
            {
                "task": task,
                "case_group": task_config["case_group"],
                "control_group": task_config["control_group"],
                "n_patients": int(len(task_table)),
                "n_cases": int(len(case_table)),
                "n_controls": int(len(control_table)),
                "mean_n_cells_case": float(case_table["n_cells"].mean()),
                "mean_n_cells_control": float(control_table["n_cells"].mean()),
                "median_n_cells_case": float(case_table["n_cells"].median()),
                "median_n_cells_control": float(control_table["n_cells"].median()),
                "mean_log1p_n_cells_case": float(case_table["log1p_n_cells"].mean()),
                "mean_log1p_n_cells_control": float(control_table["log1p_n_cells"].mean()),
                "log1p_n_cells_smd": float(smd),
                "warning_flag": _warning_flag(smd, moderate=0.5, strong=1.0),
            }
        )
    return rows


def audit_cell_type_composition(
    manifest: pd.DataFrame,
    *,
    cell_type_columns: Sequence[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task_config in TASKS:
        task = task_config["task"]
        task_table = manifest[manifest["task"] == task].copy()
        case_table = task_table[task_table["label"] == 1]
        control_table = task_table[task_table["label"] == 0]
        for column in cell_type_columns:
            case_mean = float(case_table[column].mean())
            control_mean = float(control_table[column].mean())
            diff = abs(case_mean - control_mean)
            rows.append(
                {
                    "task": task,
                    "case_group": task_config["case_group"],
                    "control_group": task_config["control_group"],
                    "cell_type_feature": column,
                    "mean_prop_case": case_mean,
                    "mean_prop_control": control_mean,
                    "abs_mean_prop_diff": diff,
                    "warning_flag": _warning_flag(diff, moderate=0.10, strong=0.20),
                }
            )
    return rows


def audit_source_batch_fields(
    manifest: pd.DataFrame,
    *,
    source_columns: Sequence[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task_config in TASKS:
        task = task_config["task"]
        task_table = manifest[manifest["task"] == task].copy()
        case_table = task_table[task_table["label"] == 1]
        control_table = task_table[task_table["label"] == 0]
        n_cases = max(len(case_table), 1)
        n_controls = max(len(control_table), 1)
        for column in source_columns:
            field_name = column.removeprefix("source_field_")
            series = task_table[column].fillna(MISSING_CATEGORY).astype(str)
            for category in sorted(series.unique()):
                case_count = int((case_table[column].fillna(MISSING_CATEGORY).astype(str) == category).sum())
                control_count = int(
                    (control_table[column].fillna(MISSING_CATEGORY).astype(str) == category).sum()
                )
                case_prop = case_count / n_cases
                control_prop = control_count / n_controls
                abs_diff = abs(case_prop - control_prop)
                present_in_only_one_class = (
                    (case_count == 0) != (control_count == 0)
                    and (case_count + control_count) >= 2
                )
                warning_value = 1.0 if present_in_only_one_class else abs_diff
                rows.append(
                    {
                        "task": task,
                        "case_group": task_config["case_group"],
                        "control_group": task_config["control_group"],
                        "source_field": field_name,
                        "source_column": column,
                        "category": category,
                        "n_patients": int(case_count + control_count),
                        "n_cases": case_count,
                        "n_controls": control_count,
                        "case_class_proportion": float(case_prop),
                        "control_class_proportion": float(control_prop),
                        "abs_class_proportion_diff": float(abs_diff),
                        "present_in_only_one_class": bool(present_in_only_one_class),
                        "warning_flag": _warning_flag(warning_value, moderate=0.25, strong=1.0),
                    }
                )
    return rows


def build_confounding_summary(
    cell_count_rows: Sequence[Mapping[str, Any]],
    cell_type_rows: Sequence[Mapping[str, Any]],
    source_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    summary_rows: list[dict[str, Any]] = []
    for task_config in TASKS:
        task = task_config["task"]
        count_row = next(row for row in cell_count_rows if row["task"] == task)
        task_cell_types = [row for row in cell_type_rows if row["task"] == task]
        task_sources = [row for row in source_rows if row["task"] == task]

        top_cell_types = sorted(
            task_cell_types,
            key=lambda row: float(row["abs_mean_prop_diff"]),
            reverse=True,
        )[:3]
        top_cell_type_summary = "; ".join(
            f"{row['cell_type_feature']}={row['abs_mean_prop_diff']:.3f}"
            for row in top_cell_types
            if float(row["abs_mean_prop_diff"]) > 0.0
        )

        flagged_source_rows = [row for row in task_sources if row["warning_flag"] != "none"]
        flagged_fields = "; ".join(sorted({str(row["source_field"]) for row in flagged_source_rows}))

        warning_levels = [str(count_row["warning_flag"])]
        warning_levels.extend(str(row["warning_flag"]) for row in task_cell_types)
        warning_levels.extend(str(row["warning_flag"]) for row in task_sources)
        if "strong" in warning_levels:
            overall_flag = "strong"
        elif "flag" in warning_levels:
            overall_flag = "flag"
        elif "not_estimable" in warning_levels:
            overall_flag = "not_estimable"
        else:
            overall_flag = "none"

        summary_rows.append(
            {
                "task": task,
                "case_group": task_config["case_group"],
                "control_group": task_config["control_group"],
                "n_patients": count_row["n_patients"],
                "n_cases": count_row["n_cases"],
                "n_controls": count_row["n_controls"],
                "cell_count_warning_flag": count_row["warning_flag"],
                "top_cell_type_imbalances": top_cell_type_summary,
                "source_batch_warning_fields": flagged_fields,
                "source_batch_categories_flagged": int(len(flagged_source_rows)),
                "warning_flag": overall_flag,
                "notes": (
                    "Detected imbalance indicates confounding risk, not causal explanation. "
                    "Lack of detected imbalance does not prove absence of confounding."
                ),
            }
        )
    return summary_rows


def write_readme(
    path: Path,
    *,
    status: str,
    output_dir: Path,
    availability: ConfoundingAvailability,
    summary_rows: Sequence[Mapping[str, Any]],
    blocker: str | None = None,
) -> None:
    lines = [
        "# Stage 7 confounding audit",
        "",
        CLAIM_BOUNDARY,
        "",
        "This audit evaluates whether labels are associated with simple technical or compositional variables.",
        "Detected imbalance indicates confounding risk, not causal explanation.",
        "Lack of detected imbalance does not prove absence of confounding.",
        "Internal dataset-structure audit only.",
        "",
        f"- Status: {status}",
        f"- Metadata artifact: `{availability.artifact_path}`",
        f"- Output directory: `{render_report_path(output_dir)}`",
        f"- Patient identifier available: {str(availability.patient_id_available).lower()}",
        f"- Label available: {str(availability.label_available).lower()}",
        f"- Cell counts available: {str(availability.cell_count_available).lower()}",
        f"- Cell-type annotations available: {str(availability.cell_type_available).lower()}",
        f"- Source/batch-like fields available: {str(availability.source_batch_fields_available).lower()}",
        f"- Detected source/batch-like fields: {', '.join(availability.source_batch_fields) or 'none'}",
        "- Geneformer execution: not run",
        "- Geneformer embeddings: not used",
        "- Evaluation unit: patient",
        "- Split policy: no train/test split; internal audit summary only",
    ]
    if blocker:
        lines.extend(["", "## TODO", "", blocker])
    elif summary_rows:
        lines.extend(
            [
                "",
                "## Warning Summary",
                "",
                "| task | n_patients | cell_count_warning | source_batch_categories_flagged | warning_flag |",
                "| --- | ---: | --- | ---: | --- |",
            ]
        )
        for row in summary_rows:
            lines.append(
                "| {task} | {n_patients} | {cell_count_warning_flag} | {source_batch_categories_flagged} | {warning_flag} |".format(
                    **row
                )
            )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_blocked_outputs(
    *,
    output_dir: Path,
    availability: ConfoundingAvailability,
    blocker: str,
    status: str,
) -> dict[str, Any]:
    manifest_path = output_dir / "patient_confounding_manifest.csv"
    cell_count_path = output_dir / "cell_count_audit.csv"
    cell_type_path = output_dir / "cell_type_composition_audit.csv"
    source_path = output_dir / "source_batch_audit.csv"
    summary_csv_path = output_dir / "confounding_audit_summary.csv"
    summary_json_path = output_dir / "run_summary.json"
    readme_path = output_dir / "README.md"

    write_csv(manifest_path, [], PATIENT_MANIFEST_BASE_FIELDNAMES)
    write_csv(cell_count_path, [], CELL_COUNT_AUDIT_FIELDNAMES)
    write_csv(cell_type_path, [], CELL_TYPE_AUDIT_FIELDNAMES)
    write_csv(source_path, [], SOURCE_BATCH_AUDIT_FIELDNAMES)
    write_csv(summary_csv_path, [], SUMMARY_FIELDNAMES)

    payload = {
        "status": status,
        "scope": AUDIT_SCOPE,
        "dataset_id": DATASET_ID,
        "metadata_artifact": availability.artifact_path,
        "artifact_type": availability.artifact_type,
        "artifact_found": availability.artifact_found,
        "patient_id_available": availability.patient_id_available,
        "label_available": availability.label_available,
        "cell_type_available": availability.cell_type_available,
        "cell_count_available": availability.cell_count_available,
        "source_batch_fields_available": availability.source_batch_fields_available,
        "source_batch_fields": list(availability.source_batch_fields),
        "field_probe": list(availability.field_probe),
        "blocker": blocker,
        "patient_confounding_manifest": render_report_path(manifest_path),
        "cell_count_audit": render_report_path(cell_count_path),
        "cell_type_composition_audit": render_report_path(cell_type_path),
        "source_batch_audit": render_report_path(source_path),
        "confounding_audit_summary": render_report_path(summary_csv_path),
        "report": render_report_path(readme_path),
        "claim_boundary": CLAIM_BOUNDARY,
        "external_validation_performed": False,
        "clinical_validation_performed": False,
        "clinical_diagnostic_claim": False,
        "geneformer_run": False,
        "geneformer_embeddings_used": False,
        "real_audit_metrics_generated": False,
    }
    write_json(summary_json_path, payload)
    write_readme(
        readme_path,
        status=status,
        output_dir=output_dir,
        availability=availability,
        summary_rows=[],
        blocker=blocker,
    )
    return payload


def run_confounding_audit(
    *,
    metadata_artifact: Path | None = None,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    artifact_path = metadata_artifact or DEFAULT_METADATA_ARTIFACT
    availability = inspect_confounding_metadata_artifact(artifact_path)
    if not artifact_path.exists():
        return write_blocked_outputs(
            output_dir=output_dir,
            availability=availability,
            blocker=f"Required local metadata artifact was not found: {artifact_path.name}",
            status="blocked_missing_metadata_artifact",
        )

    try:
        cell_metadata = load_cell_metadata_frame(artifact_path)
        build = build_patient_confounding_table(cell_metadata)
        availability = ConfoundingAvailability(
            artifact_found=True,
            artifact_path=availability.artifact_path,
            artifact_type=availability.artifact_type,
            patient_id_available=build.availability.patient_id_available,
            label_available=build.availability.label_available,
            cell_type_available=build.availability.cell_type_available,
            cell_count_available=build.availability.cell_count_available,
            source_batch_fields_available=build.availability.source_batch_fields_available,
            source_batch_fields=build.availability.source_batch_fields,
            field_probe=availability.field_probe or build.availability.field_probe,
        )
        manifest = build_task_confounding_manifest(build.patient_table)
    except Stage7MetadataBaselineError as exc:
        return write_blocked_outputs(
            output_dir=output_dir,
            availability=availability,
            blocker=str(exc),
            status="blocked_metadata_extraction",
        )

    cell_count_rows = audit_cell_counts(manifest)
    cell_type_rows = audit_cell_type_composition(
        manifest,
        cell_type_columns=build.cell_type_columns,
    )
    source_rows = audit_source_batch_fields(
        manifest,
        source_columns=build.source_columns,
    )
    summary_rows = build_confounding_summary(cell_count_rows, cell_type_rows, source_rows)

    manifest_path = output_dir / "patient_confounding_manifest.csv"
    cell_count_path = output_dir / "cell_count_audit.csv"
    cell_type_path = output_dir / "cell_type_composition_audit.csv"
    source_path = output_dir / "source_batch_audit.csv"
    summary_csv_path = output_dir / "confounding_audit_summary.csv"
    summary_json_path = output_dir / "run_summary.json"
    readme_path = output_dir / "README.md"

    write_csv(
        manifest_path,
        manifest.to_dict(orient="records"),
        _feature_fieldnames(PATIENT_MANIFEST_BASE_FIELDNAMES, manifest),
    )
    write_csv(cell_count_path, cell_count_rows, CELL_COUNT_AUDIT_FIELDNAMES)
    write_csv(cell_type_path, cell_type_rows, CELL_TYPE_AUDIT_FIELDNAMES)
    write_csv(source_path, source_rows, SOURCE_BATCH_AUDIT_FIELDNAMES)
    write_csv(summary_csv_path, summary_rows, SUMMARY_FIELDNAMES)

    payload = {
        "status": "completed",
        "scope": AUDIT_SCOPE,
        "dataset_id": DATASET_ID,
        "evaluation_unit": EVALUATION_UNIT,
        "metadata_artifact": availability.artifact_path,
        "artifact_type": availability.artifact_type,
        "artifact_found": availability.artifact_found,
        "patient_id_available": availability.patient_id_available,
        "label_available": availability.label_available,
        "cell_type_available": availability.cell_type_available,
        "cell_count_available": availability.cell_count_available,
        "source_batch_fields_available": availability.source_batch_fields_available,
        "source_batch_fields": list(availability.source_batch_fields),
        "field_probe": list(availability.field_probe),
        "patient_confounding_manifest": render_report_path(manifest_path),
        "cell_count_audit": render_report_path(cell_count_path),
        "cell_type_composition_audit": render_report_path(cell_type_path),
        "source_batch_audit": render_report_path(source_path),
        "confounding_audit_summary": render_report_path(summary_csv_path),
        "report": render_report_path(readme_path),
        "claim_boundary": CLAIM_BOUNDARY,
        "external_validation_performed": False,
        "clinical_validation_performed": False,
        "clinical_diagnostic_claim": False,
        "geneformer_run": False,
        "geneformer_embeddings_used": False,
        "real_audit_metrics_generated": True,
        "tasks": [row["task"] for row in summary_rows],
        "summary": summary_rows,
    }
    write_json(summary_json_path, payload)
    write_readme(
        readme_path,
        status="completed",
        output_dir=output_dir,
        availability=availability,
        summary_rows=summary_rows,
    )
    return payload


__all__ = [
    "CLAIM_BOUNDARY",
    "DEFAULT_METADATA_ARTIFACT",
    "DEFAULT_OUTPUT_DIR",
    "build_patient_confounding_table",
    "build_task_confounding_manifest",
    "audit_cell_counts",
    "audit_cell_type_composition",
    "audit_source_batch_fields",
    "run_confounding_audit",
]
