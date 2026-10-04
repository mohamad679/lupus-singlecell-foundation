"""Stage 6 controlled baseline execution.

This module implements the STAGE6-F005 controlled donor-level baseline
execution contract.

The execution path is intentionally narrow:
- caller-supplied in-memory donor-level records only
- donor IDs must be unique
- fitting uses train records only
- non-train records are held for later STAGE6-F006 prediction/metric work
- no filesystem artifact access
- no .npy loading
- no embedding vector parsing from disk
- no global preprocessing
- no model artifact writing
- no prediction generation
- no metric computation
- no external validation
- no performance claims

The baseline implemented here is dependency-free and deterministic: a
nearest-centroid-style fit that stores per-label feature centroids from
train donors only. It does not score or predict holdout donors in F005.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, fields
from math import isfinite
from typing import Any


COMPLETED = "completed"
IN_PROGRESS = "in_progress"
BLOCKED = "blocked"

STAGE6_CURRENT_FEATURE = "STAGE6-F005"
STAGE6_NAME = "Stage 6 - Controlled donor-level modeling execution"
STAGE6_FEATURE_NAME = "Controlled baseline execution"

REQUIRED_UPSTREAM_GATES = (
    "STAGE6-F001",
    "STAGE6-F002",
    "STAGE6-F003",
    "STAGE6-F004",
)
STAGE6_COMPLETED_FEATURES = REQUIRED_UPSTREAM_GATES

CONTROLLED_BASELINE_EXECUTION_COMPLETED = (
    "controlled_baseline_execution_completed"
)
IN_MEMORY_DONOR_BASELINE_FIT_ONLY = (
    "in_memory_donor_level_baseline_fit_only_no_predictions_metrics"
)
NEAREST_CENTROID_BASELINE = "nearest_centroid_baseline"
DONOR_LEVEL = "donor"
FOLD_LOCAL_ONLY = "fold_local_only"
TRAIN_SPLIT = "train"
VALIDATION_SPLIT = "validation"
TEST_SPLIT = "test"
HOLDOUT_SPLIT = "holdout"
ALLOWED_SPLITS = (TRAIN_SPLIT, VALIDATION_SPLIT, TEST_SPLIT, HOLDOUT_SPLIT)

REQUIRED_EXECUTION_CONTRACTS = (
    "donor_level_input_records",
    "unique_donor_ids",
    "train_only_fit",
    "holdout_prediction_deferred",
    "metric_computation_deferred",
    "no_cell_level_split",
    "no_global_preprocessing",
    "no_model_artifact_persistence",
    "no_performance_claims",
)

DEFERRED_F006_ACTIONS = (
    "generate_holdout_predictions",
    "compute_holdout_metrics",
    "write_prediction_manifest",
    "write_metric_tables",
    "calibrate_prediction_scores",
    "report_uncertainty_intervals",
)

ALLOWED_GATE_STATUSES = (COMPLETED, IN_PROGRESS, BLOCKED)
ALLOWED_GATE_DECISIONS = (CONTROLLED_BASELINE_EXECUTION_COMPLETED,)
ALLOWED_SCOPES = (IN_MEMORY_DONOR_BASELINE_FIT_ONLY,)
ALLOWED_BASELINE_FAMILIES = (NEAREST_CENTROID_BASELINE,)
ALLOWED_RECORD_LEVELS = (DONOR_LEVEL,)
ALLOWED_PREPROCESSING_SCOPES = (FOLD_LOCAL_ONLY,)


class Stage6ControlledBaselineExecutionError(ValueError):
    """Raised when STAGE6-F005 controlled baseline execution is unsafe."""


@dataclass(frozen=True)
class DonorFeatureRecord:
    """One donor-level feature record supplied by the caller in memory."""

    donor_id: str
    split: str
    label: str
    features: tuple[float, ...]


@dataclass(frozen=True)
class FittedCentroidBaseline:
    """F005 fitted baseline parameters without prediction or metric output."""

    model_family: str
    feature_count: int
    labels: tuple[str, ...]
    train_donor_ids: tuple[str, ...]
    centroids_by_label: Mapping[str, tuple[float, ...]]
    class_counts: Mapping[str, int]
    fitted_on_split: str = TRAIN_SPLIT
    prediction_generation_deferred_to: str = "STAGE6-F006"
    metric_computation_deferred_to: str = "STAGE6-F006"
    model_artifact_persisted: bool = False
    predictions_generated: bool = False
    metrics_computed: bool = False
    performance_claims_added: bool = False


@dataclass(frozen=True)
class ControlledBaselineExecutionResult:
    """Validated result of F005 baseline fitting only."""

    current_feature: str
    execution_status: str
    model_family: str
    record_level: str
    preprocessing_scope: str
    n_records: int
    n_train_records: int
    n_deferred_prediction_records: int
    fitted_model: FittedCentroidBaseline
    required_execution_contracts: tuple[str, ...] = REQUIRED_EXECUTION_CONTRACTS
    deferred_f006_actions: tuple[str, ...] = DEFERRED_F006_ACTIONS
    predictions_generated: bool = False
    metrics_computed: bool = False
    performance_claims_added: bool = False
    notes: str = ""


@dataclass(frozen=True)
class Stage6ControlledBaselineExecutionGate:
    """Metadata and safety flags for STAGE6-F005 controlled baseline execution."""

    current_stage: str = "Stage 6"
    stage_name: str = STAGE6_NAME
    current_feature: str = STAGE6_CURRENT_FEATURE
    feature_name: str = STAGE6_FEATURE_NAME
    gate_status: str = COMPLETED
    gate_decision: str = CONTROLLED_BASELINE_EXECUTION_COMPLETED
    branch: str = "feat/stage6-f005-controlled-baseline-execution"
    previous_feature: str = "STAGE6-F004"
    previous_feature_status: str = COMPLETED
    completed_stage6_features: tuple[str, ...] = STAGE6_COMPLETED_FEATURES
    required_upstream_gates: tuple[str, ...] = REQUIRED_UPSTREAM_GATES
    scope: str = IN_MEMORY_DONOR_BASELINE_FIT_ONLY
    baseline_family: str = NEAREST_CENTROID_BASELINE
    expected_record_level: str = DONOR_LEVEL
    expected_split_level: str = DONOR_LEVEL
    preprocessing_scope: str = FOLD_LOCAL_ONLY
    required_execution_contracts: tuple[str, ...] = REQUIRED_EXECUTION_CONTRACTS
    deferred_f006_actions: tuple[str, ...] = DEFERRED_F006_ACTIONS
    next_feature: str = "STAGE6-F006"
    next_feature_name: str = "Prediction and metric computation"
    closeout_feature: str = "STAGE6-F005-CLOSEOUT"
    closeout_status: str = COMPLETED
    closeout_scope: str = "feature_and_closeout_combined_controlled_fit_only"
    require_completed_stage6_f001: bool = True
    require_completed_stage6_f002: bool = True
    require_completed_stage6_f003: bool = True
    require_completed_stage6_f004: bool = True
    require_donor_level_records: bool = True
    require_unique_donor_ids: bool = True
    require_train_only_fit: bool = True
    require_holdout_predictions_deferred: bool = True
    require_metric_computation_deferred: bool = True
    require_no_cell_level_split: bool = True
    require_no_global_preprocessing: bool = True
    require_no_model_artifact_persistence: bool = True
    allow_in_memory_donor_records: bool = True
    allow_controlled_baseline_fitting: bool = True
    allow_model_fitting: bool = True
    modeling_authorization_granted: bool = True
    modeling_allowed: bool = True
    allow_filesystem_artifact_access: bool = False
    allow_real_artifact_loading: bool = False
    allow_npy_payload_loading: bool = False
    allow_embedding_vector_parsing_from_disk: bool = False
    allow_input_file_materialization: bool = False
    allow_label_file_materialization: bool = False
    allow_split_execution_from_file: bool = False
    allow_global_preprocessing: bool = False
    allow_scaler_outside_fold: bool = False
    allow_model_artifact_persistence: bool = False
    allow_prediction_generation: bool = False
    allow_metric_computation: bool = False
    allow_training_beyond_controlled_baseline_fit: bool = False
    training_allowed: bool = False
    external_validation_allowed: bool = False
    performance_claims_allowed: bool = False
    performance_claims_added: bool = False
    notes: str = ""


def _clean_required_string(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise Stage6ControlledBaselineExecutionError(
            f"{field_name} must not be empty."
        )
    if "\x00" in normalized:
        raise Stage6ControlledBaselineExecutionError(
            f"{field_name} must not contain null bytes."
        )
    return normalized


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _validate_choice(value: object, allowed: tuple[str, ...], field_name: str) -> str:
    normalized = _clean_required_string(value, field_name)
    if normalized not in allowed:
        allowed_text = ", ".join(allowed)
        raise Stage6ControlledBaselineExecutionError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )
    return normalized


def _normalize_exact_sequence(
    values: Sequence[object],
    expected: tuple[str, ...],
    field_name: str,
) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise Stage6ControlledBaselineExecutionError(
            f"{field_name} must be a sequence."
        )
    normalized = tuple(
        _clean_required_string(value, f"{field_name} item") for value in values
    )
    if normalized != expected:
        raise Stage6ControlledBaselineExecutionError(
            f"{field_name} must exactly match the STAGE6-F005 contract."
        )
    return normalized


def _normalize_features(values: Sequence[object], field_name: str) -> tuple[float, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise Stage6ControlledBaselineExecutionError(
            f"{field_name} must be a numeric sequence."
        )
    features = tuple(float(value) for value in values)
    if not features:
        raise Stage6ControlledBaselineExecutionError(
            f"{field_name} must not be empty."
        )
    if not all(isfinite(value) for value in features):
        raise Stage6ControlledBaselineExecutionError(
            f"{field_name} must contain finite values only."
        )
    return features


def _normalize_record(record: DonorFeatureRecord | Mapping[str, Any]) -> DonorFeatureRecord:
    if isinstance(record, Mapping):
        donor_id = record.get("donor_id", "")
        split = record.get("split", "")
        label = record.get("label", "")
        features = record.get("features", ())
    else:
        donor_id = record.donor_id
        split = record.split
        label = record.label
        features = record.features

    return DonorFeatureRecord(
        donor_id=_clean_required_string(donor_id, "donor_id"),
        split=_validate_choice(split, ALLOWED_SPLITS, "split"),
        label=_clean_required_string(label, "label"),
        features=_normalize_features(features, "features"),
    )


def validate_stage6_controlled_baseline_execution_gate(
    gate: Stage6ControlledBaselineExecutionGate,
) -> Stage6ControlledBaselineExecutionGate:
    """Validate STAGE6-F005 controlled baseline execution permissions."""

    current_stage = _validate_choice(gate.current_stage, ("Stage 6",), "current_stage")
    current_feature = _validate_choice(
        gate.current_feature,
        (STAGE6_CURRENT_FEATURE,),
        "current_feature",
    )
    gate_status = _validate_choice(
        gate.gate_status,
        ALLOWED_GATE_STATUSES,
        "gate_status",
    )
    gate_decision = _validate_choice(
        gate.gate_decision,
        ALLOWED_GATE_DECISIONS,
        "gate_decision",
    )
    previous_feature = _validate_choice(
        gate.previous_feature,
        ("STAGE6-F004",),
        "previous_feature",
    )
    previous_feature_status = _validate_choice(
        gate.previous_feature_status,
        (COMPLETED,),
        "previous_feature_status",
    )
    completed_stage6_features = _normalize_exact_sequence(
        gate.completed_stage6_features,
        STAGE6_COMPLETED_FEATURES,
        "completed_stage6_features",
    )
    required_upstream_gates = _normalize_exact_sequence(
        gate.required_upstream_gates,
        REQUIRED_UPSTREAM_GATES,
        "required_upstream_gates",
    )
    scope = _validate_choice(gate.scope, ALLOWED_SCOPES, "scope")
    baseline_family = _validate_choice(
        gate.baseline_family,
        ALLOWED_BASELINE_FAMILIES,
        "baseline_family",
    )
    expected_record_level = _validate_choice(
        gate.expected_record_level,
        ALLOWED_RECORD_LEVELS,
        "expected_record_level",
    )
    expected_split_level = _validate_choice(
        gate.expected_split_level,
        ALLOWED_RECORD_LEVELS,
        "expected_split_level",
    )
    preprocessing_scope = _validate_choice(
        gate.preprocessing_scope,
        ALLOWED_PREPROCESSING_SCOPES,
        "preprocessing_scope",
    )
    required_execution_contracts = _normalize_exact_sequence(
        gate.required_execution_contracts,
        REQUIRED_EXECUTION_CONTRACTS,
        "required_execution_contracts",
    )
    deferred_f006_actions = _normalize_exact_sequence(
        gate.deferred_f006_actions,
        DEFERRED_F006_ACTIONS,
        "deferred_f006_actions",
    )
    next_feature = _validate_choice(gate.next_feature, ("STAGE6-F006",), "next_feature")
    closeout_feature = _validate_choice(
        gate.closeout_feature,
        ("STAGE6-F005-CLOSEOUT",),
        "closeout_feature",
    )

    required_true = {
        "require_completed_stage6_f001": gate.require_completed_stage6_f001,
        "require_completed_stage6_f002": gate.require_completed_stage6_f002,
        "require_completed_stage6_f003": gate.require_completed_stage6_f003,
        "require_completed_stage6_f004": gate.require_completed_stage6_f004,
        "require_donor_level_records": gate.require_donor_level_records,
        "require_unique_donor_ids": gate.require_unique_donor_ids,
        "require_train_only_fit": gate.require_train_only_fit,
        "require_holdout_predictions_deferred": (
            gate.require_holdout_predictions_deferred
        ),
        "require_metric_computation_deferred": gate.require_metric_computation_deferred,
        "require_no_cell_level_split": gate.require_no_cell_level_split,
        "require_no_global_preprocessing": gate.require_no_global_preprocessing,
        "require_no_model_artifact_persistence": (
            gate.require_no_model_artifact_persistence
        ),
        "allow_in_memory_donor_records": gate.allow_in_memory_donor_records,
        "allow_controlled_baseline_fitting": gate.allow_controlled_baseline_fitting,
        "allow_model_fitting": gate.allow_model_fitting,
        "modeling_authorization_granted": gate.modeling_authorization_granted,
        "modeling_allowed": gate.modeling_allowed,
    }
    disabled = sorted(name for name, value in required_true.items() if not _as_bool(value))
    if disabled:
        raise Stage6ControlledBaselineExecutionError(
            "STAGE6-F005 controlled baseline fitting requires enabled controls: "
            + ", ".join(disabled)
        )

    forbidden_true = {
        "allow_filesystem_artifact_access": gate.allow_filesystem_artifact_access,
        "allow_real_artifact_loading": gate.allow_real_artifact_loading,
        "allow_npy_payload_loading": gate.allow_npy_payload_loading,
        "allow_embedding_vector_parsing_from_disk": (
            gate.allow_embedding_vector_parsing_from_disk
        ),
        "allow_input_file_materialization": gate.allow_input_file_materialization,
        "allow_label_file_materialization": gate.allow_label_file_materialization,
        "allow_split_execution_from_file": gate.allow_split_execution_from_file,
        "allow_global_preprocessing": gate.allow_global_preprocessing,
        "allow_scaler_outside_fold": gate.allow_scaler_outside_fold,
        "allow_model_artifact_persistence": gate.allow_model_artifact_persistence,
        "allow_prediction_generation": gate.allow_prediction_generation,
        "allow_metric_computation": gate.allow_metric_computation,
        "allow_training_beyond_controlled_baseline_fit": (
            gate.allow_training_beyond_controlled_baseline_fit
        ),
        "training_allowed": gate.training_allowed,
        "external_validation_allowed": gate.external_validation_allowed,
        "performance_claims_allowed": gate.performance_claims_allowed,
        "performance_claims_added": gate.performance_claims_added,
    }
    enabled = sorted(name for name, value in forbidden_true.items() if _as_bool(value))
    if enabled:
        raise Stage6ControlledBaselineExecutionError(
            "STAGE6-F005 fits a controlled in-memory baseline only and must "
            "not load files, predict, compute metrics, persist artifacts, train "
            "beyond the controlled baseline fit, externally validate, or add "
            "claims; enabled: " + ", ".join(enabled)
        )

    return Stage6ControlledBaselineExecutionGate(
        current_stage=current_stage,
        stage_name=_clean_required_string(gate.stage_name, "stage_name"),
        current_feature=current_feature,
        feature_name=_clean_required_string(gate.feature_name, "feature_name"),
        gate_status=gate_status,
        gate_decision=gate_decision,
        branch=_clean_required_string(gate.branch, "branch"),
        previous_feature=previous_feature,
        previous_feature_status=previous_feature_status,
        completed_stage6_features=completed_stage6_features,
        required_upstream_gates=required_upstream_gates,
        scope=scope,
        baseline_family=baseline_family,
        expected_record_level=expected_record_level,
        expected_split_level=expected_split_level,
        preprocessing_scope=preprocessing_scope,
        required_execution_contracts=required_execution_contracts,
        deferred_f006_actions=deferred_f006_actions,
        next_feature=next_feature,
        next_feature_name=_clean_required_string(
            gate.next_feature_name,
            "next_feature_name",
        ),
        closeout_feature=closeout_feature,
        closeout_status=COMPLETED,
        closeout_scope=_clean_required_string(gate.closeout_scope, "closeout_scope"),
        require_completed_stage6_f001=True,
        require_completed_stage6_f002=True,
        require_completed_stage6_f003=True,
        require_completed_stage6_f004=True,
        require_donor_level_records=True,
        require_unique_donor_ids=True,
        require_train_only_fit=True,
        require_holdout_predictions_deferred=True,
        require_metric_computation_deferred=True,
        require_no_cell_level_split=True,
        require_no_global_preprocessing=True,
        require_no_model_artifact_persistence=True,
        allow_in_memory_donor_records=True,
        allow_controlled_baseline_fitting=True,
        allow_model_fitting=True,
        modeling_authorization_granted=True,
        modeling_allowed=True,
        allow_filesystem_artifact_access=False,
        allow_real_artifact_loading=False,
        allow_npy_payload_loading=False,
        allow_embedding_vector_parsing_from_disk=False,
        allow_input_file_materialization=False,
        allow_label_file_materialization=False,
        allow_split_execution_from_file=False,
        allow_global_preprocessing=False,
        allow_scaler_outside_fold=False,
        allow_model_artifact_persistence=False,
        allow_prediction_generation=False,
        allow_metric_computation=False,
        allow_training_beyond_controlled_baseline_fit=False,
        training_allowed=False,
        external_validation_allowed=False,
        performance_claims_allowed=False,
        performance_claims_added=False,
        notes=str(gate.notes).strip(),
    )


def normalize_donor_feature_records(
    records: Sequence[DonorFeatureRecord | Mapping[str, Any]],
) -> tuple[DonorFeatureRecord, ...]:
    """Validate caller-supplied donor-level records without file access."""

    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise Stage6ControlledBaselineExecutionError("records must be a sequence.")
    normalized = tuple(_normalize_record(record) for record in records)
    if len(normalized) < 3:
        raise Stage6ControlledBaselineExecutionError(
            "controlled baseline execution requires at least three donor records."
        )

    donor_ids = [record.donor_id for record in normalized]
    duplicates = sorted(
        donor_id for donor_id, count in Counter(donor_ids).items() if count > 1
    )
    if duplicates:
        raise Stage6ControlledBaselineExecutionError(
            "donor IDs must be unique across splits: " + ", ".join(duplicates)
        )

    feature_lengths = {len(record.features) for record in normalized}
    if len(feature_lengths) != 1:
        raise Stage6ControlledBaselineExecutionError(
            "all donor feature vectors must have the same length."
        )

    train_records = [record for record in normalized if record.split == TRAIN_SPLIT]
    deferred_records = [record for record in normalized if record.split != TRAIN_SPLIT]
    if len(train_records) < 2:
        raise Stage6ControlledBaselineExecutionError(
            "controlled baseline execution requires at least two train donors."
        )
    if not deferred_records:
        raise Stage6ControlledBaselineExecutionError(
            "at least one non-train donor must be deferred to STAGE6-F006."
        )

    labels = {record.label for record in train_records}
    if len(labels) < 2:
        raise Stage6ControlledBaselineExecutionError(
            "train split requires at least two labels for baseline fitting."
        )

    return normalized


def fit_controlled_centroid_baseline(
    records: Sequence[DonorFeatureRecord | Mapping[str, Any]],
    gate: Stage6ControlledBaselineExecutionGate | None = None,
    *,
    notes: str = "",
) -> ControlledBaselineExecutionResult:
    """Fit the F005 controlled baseline on train donors only.

    This function returns fitted centroids only. It intentionally does not
    predict non-train donors and does not compute metrics.
    """

    validated_gate = validate_stage6_controlled_baseline_execution_gate(
        gate or Stage6ControlledBaselineExecutionGate()
    )
    normalized = normalize_donor_feature_records(records)

    train_records = tuple(record for record in normalized if record.split == TRAIN_SPLIT)
    deferred_records = tuple(record for record in normalized if record.split != TRAIN_SPLIT)
    feature_count = len(train_records[0].features)

    grouped: dict[str, list[tuple[float, ...]]] = defaultdict(list)
    for record in train_records:
        grouped[record.label].append(record.features)

    centroids = {}
    class_counts = {}
    for label in sorted(grouped):
        rows = grouped[label]
        class_counts[label] = len(rows)
        centroids[label] = tuple(
            sum(row[idx] for row in rows) / len(rows)
            for idx in range(feature_count)
        )

    fitted = FittedCentroidBaseline(
        model_family=validated_gate.baseline_family,
        feature_count=feature_count,
        labels=tuple(sorted(centroids)),
        train_donor_ids=tuple(record.donor_id for record in train_records),
        centroids_by_label=centroids,
        class_counts=class_counts,
    )

    return ControlledBaselineExecutionResult(
        current_feature=validated_gate.current_feature,
        execution_status=COMPLETED,
        model_family=validated_gate.baseline_family,
        record_level=validated_gate.expected_record_level,
        preprocessing_scope=validated_gate.preprocessing_scope,
        n_records=len(normalized),
        n_train_records=len(train_records),
        n_deferred_prediction_records=len(deferred_records),
        fitted_model=fitted,
        predictions_generated=False,
        metrics_computed=False,
        performance_claims_added=False,
        notes=str(notes).strip(),
    )


def stage6_controlled_baseline_execution_gate_from_mapping(
    values: Mapping[str, Any],
) -> Stage6ControlledBaselineExecutionGate:
    """Build and validate F005 gate metadata from a mapping."""

    defaults = {
        field.name: getattr(Stage6ControlledBaselineExecutionGate(), field.name)
        for field in fields(Stage6ControlledBaselineExecutionGate)
    }
    merged = {**defaults, **dict(values)}
    for sequence_field in (
        "completed_stage6_features",
        "required_upstream_gates",
        "required_execution_contracts",
        "deferred_f006_actions",
    ):
        if sequence_field in merged and not isinstance(merged[sequence_field], tuple):
            merged[sequence_field] = tuple(merged[sequence_field])

    return validate_stage6_controlled_baseline_execution_gate(
        Stage6ControlledBaselineExecutionGate(**merged)
    )


def stage6_controlled_baseline_execution_gate_to_dict(
    gate: Stage6ControlledBaselineExecutionGate,
) -> dict[str, Any]:
    """Serialize F005 gate metadata to a plain dictionary."""

    validated = validate_stage6_controlled_baseline_execution_gate(gate)
    serialized = asdict(validated)
    for sequence_field in (
        "completed_stage6_features",
        "required_upstream_gates",
        "required_execution_contracts",
        "deferred_f006_actions",
    ):
        serialized[sequence_field] = list(serialized[sequence_field])
    return serialized


def controlled_baseline_execution_result_to_dict(
    result: ControlledBaselineExecutionResult,
) -> dict[str, Any]:
    """Serialize an F005 execution result without predictions or metrics."""

    serialized = asdict(result)
    serialized["required_execution_contracts"] = list(
        serialized["required_execution_contracts"]
    )
    serialized["deferred_f006_actions"] = list(serialized["deferred_f006_actions"])
    serialized["fitted_model"]["labels"] = list(serialized["fitted_model"]["labels"])
    serialized["fitted_model"]["train_donor_ids"] = list(
        serialized["fitted_model"]["train_donor_ids"]
    )
    serialized["fitted_model"]["centroids_by_label"] = {
        label: list(values)
        for label, values in serialized["fitted_model"]["centroids_by_label"].items()
    }
    serialized["fitted_model"]["class_counts"] = dict(
        serialized["fitted_model"]["class_counts"]
    )
    return serialized


def stage6_controlled_baseline_execution_summary(
    result: ControlledBaselineExecutionResult,
) -> dict[str, Any]:
    """Return compact F005 execution summary without performance claims."""

    return {
        "current_feature": result.current_feature,
        "execution_status": result.execution_status,
        "model_family": result.model_family,
        "record_level": result.record_level,
        "preprocessing_scope": result.preprocessing_scope,
        "n_records": result.n_records,
        "n_train_records": result.n_train_records,
        "n_deferred_prediction_records": result.n_deferred_prediction_records,
        "labels": result.fitted_model.labels,
        "predictions_generated": result.predictions_generated,
        "metrics_computed": result.metrics_computed,
        "performance_claims_added": result.performance_claims_added,
        "next_feature": "STAGE6-F006",
    }
