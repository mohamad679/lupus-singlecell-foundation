"""Stage 3 evaluation protocol scaffold.

This module defines metadata-only contracts for future patient-level evaluation.
It does not load real embedding artifacts, load AnnData files, execute
Geneformer, execute tokenizers, extract embeddings, fit scalers, train models,
compute real metrics, evaluate model performance, perform external validation,
or add performance claims.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

from lupusfm.data.anndata_schema import DEFAULT_FORBIDDEN_SPLIT_VALUES


ALLOWED_EVALUATION_TASKS = (
    "flare_vs_managed",
    "flare_vs_healthy",
    "flare_vs_nonflare",
)

ALLOWED_METRICS = (
    "auroc",
    "auprc",
    "balanced_accuracy",
    "sensitivity",
    "specificity",
)

REQUIRED_PRIMARY_METRICS = ("auroc", "auprc", "balanced_accuracy")

ALLOWED_UNCERTAINTY_METHODS = (
    "bootstrap_ci",
    "exact_binomial_ci",
    "cross_validation_interval",
)

ALLOWED_PERMUTATION_METHODS = (
    "label_permutation",
    "finite_label_permutation",
)

DEFAULT_SPLIT_LEVEL = "patient"
ALLOWED_PROTOCOL_SPLIT_LEVELS = ("patient", "donor")


class EvaluationProtocolError(ValueError):
    """Raised when a Stage 3 evaluation protocol violates the contract."""


@dataclass(frozen=True)
class MetricSpec:
    """One metric planned for future patient-level evaluation."""

    name: str
    required: bool = True
    requires_probabilities: bool = False
    notes: str = ""


@dataclass(frozen=True)
class UncertaintySpec:
    """Planned uncertainty reporting for future evaluation."""

    method: str
    n_resamples: int | None = None
    confidence_level: float = 0.95
    required: bool = True


@dataclass(frozen=True)
class PermutationSpec:
    """Planned permutation control for future evaluation."""

    method: str
    n_permutations: int
    finite_sample_correction: bool = True
    required: bool = True


@dataclass(frozen=True)
class EvaluationProtocol:
    """Metadata-only future evaluation protocol contract."""

    task: str
    split_level: str = DEFAULT_SPLIT_LEVEL
    metrics: tuple[MetricSpec, ...] = (
        MetricSpec("auroc", requires_probabilities=True),
        MetricSpec("auprc", requires_probabilities=True),
        MetricSpec("balanced_accuracy"),
    )
    uncertainty: UncertaintySpec | None = UncertaintySpec(
        method="bootstrap_ci",
        n_resamples=1000,
    )
    permutation: PermutationSpec | None = PermutationSpec(
        method="label_permutation",
        n_permutations=1000,
    )
    require_baseline_comparison: bool = True
    require_confounder_controls: bool = True
    allow_cell_level_split: bool = False
    allow_real_artifact_loading: bool = False
    allow_anndata_loading: bool = False
    allow_global_preprocessing: bool = False
    allow_scaler_outside_fold: bool = False
    allow_model_fitting: bool = False
    allow_metric_computation: bool = False
    allow_modeling: bool = False
    allow_training: bool = False
    allow_external_validation: bool = False
    performance_claims_added: bool = False
    notes: str = ""


def _clean_required_string(value: object, field_name: str) -> str:
    """Return a non-empty normalized string or raise."""

    normalized = str(value).strip()
    if not normalized:
        raise EvaluationProtocolError(f"{field_name} must not be empty.")
    return normalized


def _as_bool(value: object) -> bool:
    """Parse common bool-like values."""

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {"1", "true", "yes"}


def _validate_choice(value: object, allowed: tuple[str, ...], field_name: str) -> str:
    """Validate a normalized string against an allowed set."""

    normalized = _clean_required_string(value, field_name)
    if normalized not in allowed:
        allowed_text = ", ".join(allowed)
        raise EvaluationProtocolError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _optional_positive_int(value: object, field_name: str) -> int | None:
    """Return None or a positive integer."""

    if value is None:
        return None
    if isinstance(value, bool):
        raise EvaluationProtocolError(f"{field_name} must be an integer, not bool.")

    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise EvaluationProtocolError(f"{field_name} must be an integer.") from exc

    if parsed <= 0:
        raise EvaluationProtocolError(f"{field_name} must be positive.")

    return parsed


def _positive_int(value: object, field_name: str) -> int:
    """Return a positive integer."""

    parsed = _optional_positive_int(value, field_name)
    if parsed is None:
        raise EvaluationProtocolError(f"{field_name} is required.")

    return parsed


def _confidence_level(value: object) -> float:
    """Validate a confidence level in the open interval (0, 1)."""

    if isinstance(value, bool):
        raise EvaluationProtocolError("confidence_level must be numeric, not bool.")

    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise EvaluationProtocolError("confidence_level must be numeric.") from exc

    if not 0.0 < parsed < 1.0:
        raise EvaluationProtocolError("confidence_level must be between 0 and 1.")

    return parsed


def validate_metric_spec(spec: MetricSpec | Mapping[str, Any]) -> MetricSpec:
    """Validate one planned metric specification."""

    if isinstance(spec, Mapping):
        name = spec.get("name", "")
        required = spec.get("required", True)
        requires_probabilities = spec.get("requires_probabilities", False)
        notes = spec.get("notes", "")
    else:
        name = spec.name
        required = spec.required
        requires_probabilities = spec.requires_probabilities
        notes = spec.notes

    return MetricSpec(
        name=_validate_choice(name, ALLOWED_METRICS, "metric.name"),
        required=_as_bool(required),
        requires_probabilities=_as_bool(requires_probabilities),
        notes=str(notes).strip(),
    )


def validate_uncertainty_spec(
    spec: UncertaintySpec | Mapping[str, Any] | None,
) -> UncertaintySpec:
    """Validate planned uncertainty reporting."""

    if spec is None:
        raise EvaluationProtocolError("uncertainty reporting is required.")

    if isinstance(spec, Mapping):
        method = spec.get("method", "")
        n_resamples = spec.get("n_resamples")
        confidence_level = spec.get("confidence_level", 0.95)
        required = spec.get("required", True)
    else:
        method = spec.method
        n_resamples = spec.n_resamples
        confidence_level = spec.confidence_level
        required = spec.required

    method = _validate_choice(method, ALLOWED_UNCERTAINTY_METHODS, "uncertainty.method")
    parsed_n_resamples = _optional_positive_int(n_resamples, "uncertainty.n_resamples")

    if method in {"bootstrap_ci", "cross_validation_interval"} and parsed_n_resamples is None:
        raise EvaluationProtocolError(
            "uncertainty.n_resamples is required for resampling-based uncertainty."
        )

    return UncertaintySpec(
        method=method,
        n_resamples=parsed_n_resamples,
        confidence_level=_confidence_level(confidence_level),
        required=_as_bool(required),
    )


def validate_permutation_spec(
    spec: PermutationSpec | Mapping[str, Any] | None,
) -> PermutationSpec:
    """Validate planned permutation control."""

    if spec is None:
        raise EvaluationProtocolError("permutation control is required.")

    if isinstance(spec, Mapping):
        method = spec.get("method", "")
        n_permutations = spec.get("n_permutations")
        finite_sample_correction = spec.get("finite_sample_correction", True)
        required = spec.get("required", True)
    else:
        method = spec.method
        n_permutations = spec.n_permutations
        finite_sample_correction = spec.finite_sample_correction
        required = spec.required

    return PermutationSpec(
        method=_validate_choice(
            method,
            ALLOWED_PERMUTATION_METHODS,
            "permutation.method",
        ),
        n_permutations=_positive_int(
            n_permutations,
            "permutation.n_permutations",
        ),
        finite_sample_correction=_as_bool(finite_sample_correction),
        required=_as_bool(required),
    )


def validate_evaluation_protocol(
    protocol: EvaluationProtocol,
) -> EvaluationProtocol:
    """Validate a metadata-only future evaluation protocol."""

    task = _validate_choice(protocol.task, ALLOWED_EVALUATION_TASKS, "task")
    split_level = _validate_choice(
        protocol.split_level,
        ALLOWED_PROTOCOL_SPLIT_LEVELS,
        "split_level",
    )

    forbidden_split_levels = {str(value) for value in DEFAULT_FORBIDDEN_SPLIT_VALUES}
    if split_level in forbidden_split_levels:
        raise EvaluationProtocolError("cell-level split assignments are not allowed.")

    metrics = tuple(validate_metric_spec(metric) for metric in protocol.metrics)
    if not metrics:
        raise EvaluationProtocolError("at least one metric is required.")

    metric_names = [metric.name for metric in metrics]
    duplicate_metrics = sorted(
        name for name, count in Counter(metric_names).items() if count > 1
    )
    if duplicate_metrics:
        raise EvaluationProtocolError("metric names must be unique.")

    missing_primary = sorted(set(REQUIRED_PRIMARY_METRICS).difference(metric_names))
    if missing_primary:
        raise EvaluationProtocolError(
            "evaluation protocol must include all required primary metrics."
        )

    if _as_bool(protocol.allow_cell_level_split):
        raise EvaluationProtocolError("cell-level split assignments are not allowed.")
    if _as_bool(protocol.allow_real_artifact_loading):
        raise EvaluationProtocolError("evaluation protocol must not load real artifacts.")
    if _as_bool(protocol.allow_anndata_loading):
        raise EvaluationProtocolError("evaluation protocol must not load AnnData.")
    if _as_bool(protocol.allow_global_preprocessing):
        raise EvaluationProtocolError(
            "global preprocessing across folds is not allowed."
        )
    if _as_bool(protocol.allow_scaler_outside_fold):
        raise EvaluationProtocolError(
            "scaler fitting outside the training fold is not allowed."
        )
    if _as_bool(protocol.allow_model_fitting):
        raise EvaluationProtocolError(
            "model fitting is not allowed in the protocol scaffold."
        )
    if _as_bool(protocol.allow_metric_computation):
        raise EvaluationProtocolError(
            "metric computation is not allowed in the protocol scaffold."
        )
    if _as_bool(protocol.allow_modeling):
        raise EvaluationProtocolError("Stage 3 protocol keeps modeling disabled.")
    if _as_bool(protocol.allow_training):
        raise EvaluationProtocolError("Stage 3 protocol keeps training disabled.")
    if _as_bool(protocol.allow_external_validation):
        raise EvaluationProtocolError(
            "Stage 3 protocol keeps external validation disabled."
        )
    if _as_bool(protocol.performance_claims_added):
        raise EvaluationProtocolError(
            "Stage 3 protocol must not add performance claims."
        )

    if not _as_bool(protocol.require_baseline_comparison):
        raise EvaluationProtocolError("baseline comparison is required.")
    if not _as_bool(protocol.require_confounder_controls):
        raise EvaluationProtocolError("confounder controls are required.")

    return EvaluationProtocol(
        task=task,
        split_level=split_level,
        metrics=metrics,
        uncertainty=validate_uncertainty_spec(protocol.uncertainty),
        permutation=validate_permutation_spec(protocol.permutation),
        require_baseline_comparison=True,
        require_confounder_controls=True,
        allow_cell_level_split=False,
        allow_real_artifact_loading=False,
        allow_anndata_loading=False,
        allow_global_preprocessing=False,
        allow_scaler_outside_fold=False,
        allow_model_fitting=False,
        allow_metric_computation=False,
        allow_modeling=False,
        allow_training=False,
        allow_external_validation=False,
        performance_claims_added=False,
        notes=str(protocol.notes).strip(),
    )


def evaluation_protocol_from_mapping(data: Mapping[str, Any]) -> EvaluationProtocol:
    """Build and validate an evaluation protocol from a mapping."""

    metrics_data = data.get("metrics")
    if metrics_data is None:
        metrics = (
            MetricSpec("auroc", requires_probabilities=True),
            MetricSpec("auprc", requires_probabilities=True),
            MetricSpec("balanced_accuracy"),
        )
    elif isinstance(metrics_data, (str, bytes)) or not isinstance(metrics_data, Sequence):
        raise EvaluationProtocolError("metrics must be a sequence.")
    else:
        metrics = tuple(validate_metric_spec(metric) for metric in metrics_data)

    return validate_evaluation_protocol(
        EvaluationProtocol(
            task=data.get("task", ""),
            split_level=data.get("split_level", DEFAULT_SPLIT_LEVEL),
            metrics=metrics,
            uncertainty=data.get(
                "uncertainty",
                {"method": "bootstrap_ci", "n_resamples": 1000},
            ),
            permutation=data.get(
                "permutation",
                {"method": "label_permutation", "n_permutations": 1000},
            ),
            require_baseline_comparison=data.get(
                "require_baseline_comparison",
                True,
            ),
            require_confounder_controls=data.get(
                "require_confounder_controls",
                True,
            ),
            allow_cell_level_split=data.get("allow_cell_level_split", False),
            allow_real_artifact_loading=data.get("allow_real_artifact_loading", False),
            allow_anndata_loading=data.get("allow_anndata_loading", False),
            allow_global_preprocessing=data.get("allow_global_preprocessing", False),
            allow_scaler_outside_fold=data.get("allow_scaler_outside_fold", False),
            allow_model_fitting=data.get("allow_model_fitting", False),
            allow_metric_computation=data.get("allow_metric_computation", False),
            allow_modeling=data.get("allow_modeling", False),
            allow_training=data.get("allow_training", False),
            allow_external_validation=data.get("allow_external_validation", False),
            performance_claims_added=data.get("performance_claims_added", False),
            notes=data.get("notes", ""),
        )
    )


def evaluation_protocol_to_dict(protocol: EvaluationProtocol) -> dict[str, Any]:
    """Serialize a validated evaluation protocol to a plain dictionary."""

    return asdict(validate_evaluation_protocol(protocol))
