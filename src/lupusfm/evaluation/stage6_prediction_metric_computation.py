"""Stage 6 controlled prediction and metric computation.

This module implements STAGE6-F006 for in-memory donor-level prediction and
metric computation using the fitted F005 controlled baseline object.

Allowed in F006:
- caller-supplied in-memory donor-level records
- prediction for non-train donor records
- metric computation on those in-memory records
- no performance claims

Still forbidden:
- filesystem artifact access
- .npy loading
- embedding vector parsing from disk
- split execution from files
- model artifact persistence
- training or refitting
- external validation
- scientific performance claims
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, fields
from math import isfinite, sqrt
from typing import Any

from lupusfm.evaluation.stage6_controlled_baseline_execution import (
    DONOR_LEVEL,
    FOLD_LOCAL_ONLY,
    NEAREST_CENTROID_BASELINE,
    STAGE6_CURRENT_FEATURE as STAGE6_F005_FEATURE,
    DonorFeatureRecord,
    FittedCentroidBaseline,
    normalize_donor_feature_records,
)


COMPLETED = "completed"
IN_PROGRESS = "in_progress"
BLOCKED = "blocked"

STAGE6_CURRENT_FEATURE = "STAGE6-F006"
STAGE6_NAME = "Stage 6 - Controlled donor-level modeling execution"
STAGE6_FEATURE_NAME = "Prediction and metric computation"

REQUIRED_UPSTREAM_GATES = (
    "STAGE6-F001",
    "STAGE6-F002",
    "STAGE6-F003",
    "STAGE6-F004",
    "STAGE6-F005",
)
STAGE6_COMPLETED_FEATURES = REQUIRED_UPSTREAM_GATES

PREDICTION_METRIC_COMPUTATION_COMPLETED = (
    "prediction_metric_computation_completed"
)
IN_MEMORY_DONOR_PREDICTION_METRIC_ONLY = (
    "in_memory_donor_level_prediction_metric_only_no_artifacts_claims"
)

POSITIVE_LABEL_DEFAULT = "flare"

REQUIRED_F006_CONTRACTS = (
    "f005_fitted_baseline_required",
    "in_memory_donor_records_only",
    "predict_non_train_records_only",
    "metric_computation_on_in_memory_predictions_only",
    "no_file_or_artifact_outputs",
    "no_refit_or_training",
    "no_external_validation",
    "no_performance_claims",
)

DEFERRED_F007_ACTIONS = (
    "write_final_result_report",
    "summarize_stage6_controls",
    "document_metric_scope",
    "close_stage6",
)

METRIC_NAMES = (
    "accuracy",
    "balanced_accuracy",
    "sensitivity",
    "specificity",
    "precision",
    "f1",
    "brier_score",
)

ALLOWED_GATE_STATUSES = (COMPLETED, IN_PROGRESS, BLOCKED)
ALLOWED_GATE_DECISIONS = (PREDICTION_METRIC_COMPUTATION_COMPLETED,)
ALLOWED_SCOPES = (IN_MEMORY_DONOR_PREDICTION_METRIC_ONLY,)
ALLOWED_BASELINE_FAMILIES = (NEAREST_CENTROID_BASELINE,)
ALLOWED_RECORD_LEVELS = (DONOR_LEVEL,)
ALLOWED_PREPROCESSING_SCOPES = (FOLD_LOCAL_ONLY,)


class Stage6PredictionMetricComputationError(ValueError):
    """Raised when F006 prediction/metric computation is unsafe."""


@dataclass(frozen=True)
class DonorPredictionRecord:
    """One in-memory donor-level prediction record."""

    donor_id: str
    split: str
    true_label: str
    predicted_label: str
    positive_label_score: float
    prediction_unit: str = DONOR_LEVEL


@dataclass(frozen=True)
class BinaryMetricSummary:
    """Binary metrics from in-memory donor-level predictions only."""

    positive_label: str
    n_predictions: int
    true_positive: int
    true_negative: int
    false_positive: int
    false_negative: int
    accuracy: float
    balanced_accuracy: float
    sensitivity: float
    specificity: float
    precision: float
    f1: float
    brier_score: float
    metric_scope: str = "in_memory_donor_level_predictions_only"
    performance_claims_added: bool = False


@dataclass(frozen=True)
class PredictionMetricComputationResult:
    """F006 prediction and metric result without artifact persistence."""

    current_feature: str
    computation_status: str
    model_family: str
    record_level: str
    preprocessing_scope: str
    positive_label: str
    predictions: tuple[DonorPredictionRecord, ...]
    metrics: BinaryMetricSummary
    required_f006_contracts: tuple[str, ...] = REQUIRED_F006_CONTRACTS
    deferred_f007_actions: tuple[str, ...] = DEFERRED_F007_ACTIONS
    artifacts_written: bool = False
    model_refit_performed: bool = False
    external_validation_performed: bool = False
    performance_claims_added: bool = False
    notes: str = ""


@dataclass(frozen=True)
class Stage6PredictionMetricComputationGate:
    """Metadata and safety flags for STAGE6-F006."""

    current_stage: str = "Stage 6"
    stage_name: str = STAGE6_NAME
    current_feature: str = STAGE6_CURRENT_FEATURE
    feature_name: str = STAGE6_FEATURE_NAME
    gate_status: str = COMPLETED
    gate_decision: str = PREDICTION_METRIC_COMPUTATION_COMPLETED
    branch: str = "feat/stage6-f006-prediction-metric-computation"
    previous_feature: str = "STAGE6-F005"
    previous_feature_status: str = COMPLETED
    completed_stage6_features: tuple[str, ...] = STAGE6_COMPLETED_FEATURES
    required_upstream_gates: tuple[str, ...] = REQUIRED_UPSTREAM_GATES
    scope: str = IN_MEMORY_DONOR_PREDICTION_METRIC_ONLY
    baseline_family: str = NEAREST_CENTROID_BASELINE
    expected_record_level: str = DONOR_LEVEL
    preprocessing_scope: str = FOLD_LOCAL_ONLY
    required_f006_contracts: tuple[str, ...] = REQUIRED_F006_CONTRACTS
    deferred_f007_actions: tuple[str, ...] = DEFERRED_F007_ACTIONS
    metric_names: tuple[str, ...] = METRIC_NAMES
    next_feature: str = "STAGE6-F007"
    next_feature_name: str = "Stage 6 final result report and closeout"
    closeout_feature: str = "STAGE6-F006-CLOSEOUT"
    closeout_status: str = COMPLETED
    closeout_scope: str = "feature_and_closeout_combined_prediction_metric_only"
    require_completed_stage6_f001: bool = True
    require_completed_stage6_f002: bool = True
    require_completed_stage6_f003: bool = True
    require_completed_stage6_f004: bool = True
    require_completed_stage6_f005: bool = True
    require_f005_fitted_baseline: bool = True
    require_in_memory_records_only: bool = True
    require_non_train_predictions_only: bool = True
    require_metric_scope_limited_to_in_memory_predictions: bool = True
    require_no_file_or_artifact_outputs: bool = True
    require_no_refit_or_training: bool = True
    require_no_external_validation: bool = True
    require_no_performance_claims: bool = True
    allow_in_memory_prediction_generation: bool = True
    allow_in_memory_metric_computation: bool = True
    allow_prediction_generation: bool = True
    allow_metric_computation: bool = True
    allow_filesystem_artifact_access: bool = False
    allow_real_artifact_loading: bool = False
    allow_npy_payload_loading: bool = False
    allow_embedding_vector_parsing_from_disk: bool = False
    allow_split_execution_from_file: bool = False
    allow_model_refit: bool = False
    allow_training: bool = False
    training_allowed: bool = False
    allow_model_artifact_persistence: bool = False
    allow_prediction_manifest_write: bool = False
    allow_metric_table_write: bool = False
    external_validation_allowed: bool = False
    allow_external_validation: bool = False
    performance_claims_allowed: bool = False
    performance_claims_added: bool = False
    notes: str = ""


def _clean_required_string(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise Stage6PredictionMetricComputationError(
            f"{field_name} must not be empty."
        )
    if "\x00" in normalized:
        raise Stage6PredictionMetricComputationError(
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
        raise Stage6PredictionMetricComputationError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )
    return normalized


def _normalize_exact_sequence(
    values: Sequence[object],
    expected: tuple[str, ...],
    field_name: str,
) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise Stage6PredictionMetricComputationError(
            f"{field_name} must be a sequence."
        )
    normalized = tuple(
        _clean_required_string(value, f"{field_name} item") for value in values
    )
    if normalized != expected:
        raise Stage6PredictionMetricComputationError(
            f"{field_name} must exactly match the STAGE6-F006 contract."
        )
    return normalized


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _euclidean_distance(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return sqrt(sum((a - b) ** 2 for a, b in zip(left, right)))


def _validate_fitted_baseline(model: FittedCentroidBaseline) -> FittedCentroidBaseline:
    if model.model_family != NEAREST_CENTROID_BASELINE:
        raise Stage6PredictionMetricComputationError(
            "F006 requires the F005 nearest-centroid baseline."
        )
    if model.predictions_generated:
        raise Stage6PredictionMetricComputationError(
            "F005 fitted model must not already contain predictions."
        )
    if model.metrics_computed:
        raise Stage6PredictionMetricComputationError(
            "F005 fitted model must not already contain metrics."
        )
    if model.model_artifact_persisted:
        raise Stage6PredictionMetricComputationError(
            "F005 fitted model must not be persisted as an artifact."
        )
    if model.performance_claims_added:
        raise Stage6PredictionMetricComputationError(
            "F005 fitted model must not contain performance claims."
        )
    if not model.labels or len(model.labels) < 2:
        raise Stage6PredictionMetricComputationError(
            "F006 requires at least two fitted labels."
        )
    if model.feature_count <= 0:
        raise Stage6PredictionMetricComputationError(
            "fitted model feature_count must be positive."
        )
    if set(model.labels) != set(model.centroids_by_label):
        raise Stage6PredictionMetricComputationError(
            "fitted labels and centroids must match."
        )
    for label, centroid in model.centroids_by_label.items():
        if len(centroid) != model.feature_count:
            raise Stage6PredictionMetricComputationError(
                f"centroid for {label!r} has the wrong feature count."
            )
        if not all(isfinite(value) for value in centroid):
            raise Stage6PredictionMetricComputationError(
                f"centroid for {label!r} must contain finite values only."
            )
    return model


def validate_stage6_prediction_metric_computation_gate(
    gate: Stage6PredictionMetricComputationGate,
) -> Stage6PredictionMetricComputationGate:
    """Validate F006 prediction/metric permissions."""

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
        ("STAGE6-F005",),
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
    preprocessing_scope = _validate_choice(
        gate.preprocessing_scope,
        ALLOWED_PREPROCESSING_SCOPES,
        "preprocessing_scope",
    )
    required_f006_contracts = _normalize_exact_sequence(
        gate.required_f006_contracts,
        REQUIRED_F006_CONTRACTS,
        "required_f006_contracts",
    )
    deferred_f007_actions = _normalize_exact_sequence(
        gate.deferred_f007_actions,
        DEFERRED_F007_ACTIONS,
        "deferred_f007_actions",
    )
    metric_names = _normalize_exact_sequence(
        gate.metric_names,
        METRIC_NAMES,
        "metric_names",
    )
    next_feature = _validate_choice(gate.next_feature, ("STAGE6-F007",), "next_feature")
    closeout_feature = _validate_choice(
        gate.closeout_feature,
        ("STAGE6-F006-CLOSEOUT",),
        "closeout_feature",
    )

    required_true = {
        "require_completed_stage6_f001": gate.require_completed_stage6_f001,
        "require_completed_stage6_f002": gate.require_completed_stage6_f002,
        "require_completed_stage6_f003": gate.require_completed_stage6_f003,
        "require_completed_stage6_f004": gate.require_completed_stage6_f004,
        "require_completed_stage6_f005": gate.require_completed_stage6_f005,
        "require_f005_fitted_baseline": gate.require_f005_fitted_baseline,
        "require_in_memory_records_only": gate.require_in_memory_records_only,
        "require_non_train_predictions_only": gate.require_non_train_predictions_only,
        "require_metric_scope_limited_to_in_memory_predictions": (
            gate.require_metric_scope_limited_to_in_memory_predictions
        ),
        "require_no_file_or_artifact_outputs": gate.require_no_file_or_artifact_outputs,
        "require_no_refit_or_training": gate.require_no_refit_or_training,
        "require_no_external_validation": gate.require_no_external_validation,
        "require_no_performance_claims": gate.require_no_performance_claims,
        "allow_in_memory_prediction_generation": (
            gate.allow_in_memory_prediction_generation
        ),
        "allow_in_memory_metric_computation": (
            gate.allow_in_memory_metric_computation
        ),
        "allow_prediction_generation": gate.allow_prediction_generation,
        "allow_metric_computation": gate.allow_metric_computation,
    }
    disabled = sorted(name for name, value in required_true.items() if not _as_bool(value))
    if disabled:
        raise Stage6PredictionMetricComputationError(
            "STAGE6-F006 requires enabled prediction/metric controls: "
            + ", ".join(disabled)
        )

    forbidden_true = {
        "allow_filesystem_artifact_access": gate.allow_filesystem_artifact_access,
        "allow_real_artifact_loading": gate.allow_real_artifact_loading,
        "allow_npy_payload_loading": gate.allow_npy_payload_loading,
        "allow_embedding_vector_parsing_from_disk": (
            gate.allow_embedding_vector_parsing_from_disk
        ),
        "allow_split_execution_from_file": gate.allow_split_execution_from_file,
        "allow_model_refit": gate.allow_model_refit,
        "allow_training": gate.allow_training,
        "training_allowed": gate.training_allowed,
        "allow_model_artifact_persistence": gate.allow_model_artifact_persistence,
        "allow_prediction_manifest_write": gate.allow_prediction_manifest_write,
        "allow_metric_table_write": gate.allow_metric_table_write,
        "external_validation_allowed": gate.external_validation_allowed,
        "allow_external_validation": gate.allow_external_validation,
        "performance_claims_allowed": gate.performance_claims_allowed,
        "performance_claims_added": gate.performance_claims_added,
    }
    enabled = sorted(name for name, value in forbidden_true.items() if _as_bool(value))
    if enabled:
        raise Stage6PredictionMetricComputationError(
            "STAGE6-F006 computes in-memory predictions and metrics only and "
            "must not access files, refit/train, persist artifacts, externally "
            "validate, or add claims; enabled: " + ", ".join(enabled)
        )

    return Stage6PredictionMetricComputationGate(
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
        preprocessing_scope=preprocessing_scope,
        required_f006_contracts=required_f006_contracts,
        deferred_f007_actions=deferred_f007_actions,
        metric_names=metric_names,
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
        require_completed_stage6_f005=True,
        require_f005_fitted_baseline=True,
        require_in_memory_records_only=True,
        require_non_train_predictions_only=True,
        require_metric_scope_limited_to_in_memory_predictions=True,
        require_no_file_or_artifact_outputs=True,
        require_no_refit_or_training=True,
        require_no_external_validation=True,
        require_no_performance_claims=True,
        allow_in_memory_prediction_generation=True,
        allow_in_memory_metric_computation=True,
        allow_prediction_generation=True,
        allow_metric_computation=True,
        allow_filesystem_artifact_access=False,
        allow_real_artifact_loading=False,
        allow_npy_payload_loading=False,
        allow_embedding_vector_parsing_from_disk=False,
        allow_split_execution_from_file=False,
        allow_model_refit=False,
        allow_training=False,
        training_allowed=False,
        allow_model_artifact_persistence=False,
        allow_prediction_manifest_write=False,
        allow_metric_table_write=False,
        external_validation_allowed=False,
        allow_external_validation=False,
        performance_claims_allowed=False,
        performance_claims_added=False,
        notes=str(gate.notes).strip(),
    )


def predict_with_f005_centroid_baseline(
    model: FittedCentroidBaseline,
    records: Sequence[DonorFeatureRecord | Mapping[str, Any]],
    *,
    positive_label: str = POSITIVE_LABEL_DEFAULT,
) -> tuple[DonorPredictionRecord, ...]:
    """Predict non-train donors in memory without metric computation."""

    validated_model = _validate_fitted_baseline(model)
    normalized = normalize_donor_feature_records(records)

    if positive_label not in validated_model.labels:
        raise Stage6PredictionMetricComputationError(
            "positive_label must be one of the fitted model labels."
        )

    train_ids = set(validated_model.train_donor_ids)
    prediction_records = []
    for record in normalized:
        if record.donor_id in train_ids or record.split == "train":
            continue
        if len(record.features) != validated_model.feature_count:
            raise Stage6PredictionMetricComputationError(
                "prediction record feature count must match fitted model."
            )

        distances = {
            label: _euclidean_distance(record.features, centroid)
            for label, centroid in validated_model.centroids_by_label.items()
        }
        predicted_label = min(distances, key=lambda label: (distances[label], label))

        positive_distance = distances[positive_label]
        inverse_distances = {
            label: 1.0 / (distance + 1.0) for label, distance in distances.items()
        }
        denominator = sum(inverse_distances.values())
        positive_score = inverse_distances[positive_label] / denominator
        if not isfinite(positive_score):
            raise Stage6PredictionMetricComputationError(
                "positive label score must be finite."
            )

        prediction_records.append(
            DonorPredictionRecord(
                donor_id=record.donor_id,
                split=record.split,
                true_label=record.label,
                predicted_label=predicted_label,
                positive_label_score=positive_score,
            )
        )

    if not prediction_records:
        raise Stage6PredictionMetricComputationError(
            "F006 requires at least one non-train prediction record."
        )
    return tuple(prediction_records)


def compute_binary_metrics(
    predictions: Sequence[DonorPredictionRecord],
    *,
    positive_label: str = POSITIVE_LABEL_DEFAULT,
) -> BinaryMetricSummary:
    """Compute binary metrics from in-memory predictions only."""

    if isinstance(predictions, (str, bytes)) or not isinstance(predictions, Sequence):
        raise Stage6PredictionMetricComputationError(
            "predictions must be a sequence."
        )
    normalized = tuple(predictions)
    if not normalized:
        raise Stage6PredictionMetricComputationError(
            "at least one prediction is required."
        )

    labels = {record.true_label for record in normalized} | {
        record.predicted_label for record in normalized
    }
    if len(labels) != 2:
        raise Stage6PredictionMetricComputationError(
            "binary metrics require exactly two labels."
        )
    if positive_label not in labels:
        raise Stage6PredictionMetricComputationError(
            "positive_label must appear in prediction labels."
        )

    for record in normalized:
        if record.prediction_unit != DONOR_LEVEL:
            raise Stage6PredictionMetricComputationError(
                "prediction_unit must remain donor."
            )
        if not 0.0 <= record.positive_label_score <= 1.0:
            raise Stage6PredictionMetricComputationError(
                "positive_label_score must be in [0, 1]."
            )

    tp = sum(
        record.true_label == positive_label and record.predicted_label == positive_label
        for record in normalized
    )
    tn = sum(
        record.true_label != positive_label and record.predicted_label != positive_label
        for record in normalized
    )
    fp = sum(
        record.true_label != positive_label and record.predicted_label == positive_label
        for record in normalized
    )
    fn = sum(
        record.true_label == positive_label and record.predicted_label != positive_label
        for record in normalized
    )
    n_predictions = len(normalized)

    sensitivity = _safe_divide(tp, tp + fn)
    specificity = _safe_divide(tn, tn + fp)
    precision = _safe_divide(tp, tp + fp)
    accuracy = _safe_divide(tp + tn, n_predictions)
    balanced_accuracy = (sensitivity + specificity) / 2.0
    f1 = _safe_divide(2.0 * precision * sensitivity, precision + sensitivity)
    brier_score = sum(
        (
            record.positive_label_score
            - (1.0 if record.true_label == positive_label else 0.0)
        )
        ** 2
        for record in normalized
    ) / n_predictions

    return BinaryMetricSummary(
        positive_label=positive_label,
        n_predictions=n_predictions,
        true_positive=int(tp),
        true_negative=int(tn),
        false_positive=int(fp),
        false_negative=int(fn),
        accuracy=accuracy,
        balanced_accuracy=balanced_accuracy,
        sensitivity=sensitivity,
        specificity=specificity,
        precision=precision,
        f1=f1,
        brier_score=brier_score,
        performance_claims_added=False,
    )


def compute_stage6_prediction_metrics(
    model: FittedCentroidBaseline,
    records: Sequence[DonorFeatureRecord | Mapping[str, Any]],
    gate: Stage6PredictionMetricComputationGate | None = None,
    *,
    positive_label: str = POSITIVE_LABEL_DEFAULT,
    notes: str = "",
) -> PredictionMetricComputationResult:
    """Run F006 in-memory prediction and metric computation."""

    validated_gate = validate_stage6_prediction_metric_computation_gate(
        gate or Stage6PredictionMetricComputationGate()
    )
    if validated_gate.baseline_family != model.model_family:
        raise Stage6PredictionMetricComputationError(
            "gate baseline family must match fitted model family."
        )

    predictions = predict_with_f005_centroid_baseline(
        model,
        records,
        positive_label=positive_label,
    )
    metrics = compute_binary_metrics(predictions, positive_label=positive_label)

    return PredictionMetricComputationResult(
        current_feature=validated_gate.current_feature,
        computation_status=COMPLETED,
        model_family=validated_gate.baseline_family,
        record_level=validated_gate.expected_record_level,
        preprocessing_scope=validated_gate.preprocessing_scope,
        positive_label=positive_label,
        predictions=predictions,
        metrics=metrics,
        artifacts_written=False,
        model_refit_performed=False,
        external_validation_performed=False,
        performance_claims_added=False,
        notes=str(notes).strip(),
    )


def stage6_prediction_metric_computation_gate_from_mapping(
    values: Mapping[str, Any],
) -> Stage6PredictionMetricComputationGate:
    """Build and validate F006 gate metadata from mapping."""

    defaults = {
        field.name: getattr(Stage6PredictionMetricComputationGate(), field.name)
        for field in fields(Stage6PredictionMetricComputationGate)
    }
    merged = {**defaults, **dict(values)}
    for sequence_field in (
        "completed_stage6_features",
        "required_upstream_gates",
        "required_f006_contracts",
        "deferred_f007_actions",
        "metric_names",
    ):
        if sequence_field in merged and not isinstance(merged[sequence_field], tuple):
            merged[sequence_field] = tuple(merged[sequence_field])

    return validate_stage6_prediction_metric_computation_gate(
        Stage6PredictionMetricComputationGate(**merged)
    )


def stage6_prediction_metric_computation_gate_to_dict(
    gate: Stage6PredictionMetricComputationGate,
) -> dict[str, Any]:
    """Serialize F006 gate metadata."""

    validated = validate_stage6_prediction_metric_computation_gate(gate)
    serialized = asdict(validated)
    for sequence_field in (
        "completed_stage6_features",
        "required_upstream_gates",
        "required_f006_contracts",
        "deferred_f007_actions",
        "metric_names",
    ):
        serialized[sequence_field] = list(serialized[sequence_field])
    return serialized


def prediction_metric_computation_result_to_dict(
    result: PredictionMetricComputationResult,
) -> dict[str, Any]:
    """Serialize F006 result without writing artifacts."""

    serialized = asdict(result)
    serialized["required_f006_contracts"] = list(
        serialized["required_f006_contracts"]
    )
    serialized["deferred_f007_actions"] = list(serialized["deferred_f007_actions"])
    return serialized


def stage6_prediction_metric_computation_summary(
    result: PredictionMetricComputationResult,
) -> dict[str, Any]:
    """Return compact metric summary without performance claims."""

    metric_values = {
        metric_name: getattr(result.metrics, metric_name)
        for metric_name in METRIC_NAMES
    }
    return {
        "current_feature": result.current_feature,
        "computation_status": result.computation_status,
        "model_family": result.model_family,
        "record_level": result.record_level,
        "positive_label": result.positive_label,
        "n_predictions": result.metrics.n_predictions,
        "metrics": metric_values,
        "artifacts_written": result.artifacts_written,
        "model_refit_performed": result.model_refit_performed,
        "external_validation_performed": result.external_validation_performed,
        "performance_claims_added": result.performance_claims_added,
        "next_feature": "STAGE6-F007",
    }
