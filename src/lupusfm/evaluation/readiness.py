"""Stage 3 modeling readiness gate.

This module defines the final metadata-only Stage 3 gate before any future
real-data validation or downstream modeling workflow can be considered. It does
not load real embedding artifacts, load AnnData files, execute Geneformer,
execute tokenizers, extract embeddings, extract baseline features, fit scalers,
train models, compute real metrics, evaluate model performance, perform external
validation, or add performance claims.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

from lupusfm.data.anndata_schema import DEFAULT_FORBIDDEN_SPLIT_VALUES


STAGE3_CURRENT_FEATURE = "STAGE3-F006"

EMBEDDING_ARTIFACT_SCHEMA = "embedding_artifact_schema"
PATIENT_AGGREGATION_DESIGN = "patient_aggregation_design"
LEAKAGE_SAFE_SPLITS = "leakage_safe_splits"
EVALUATION_PROTOCOL_SCAFFOLD = "evaluation_protocol_scaffold"
BASELINE_CONTROL_PLAN = "baseline_control_plan"

REQUIRED_STAGE3_COMPONENTS = (
    EMBEDDING_ARTIFACT_SCHEMA,
    PATIENT_AGGREGATION_DESIGN,
    LEAKAGE_SAFE_SPLITS,
    EVALUATION_PROTOCOL_SCAFFOLD,
    BASELINE_CONTROL_PLAN,
)

COMPLETED = "completed"
ALLOWED_COMPONENT_STATUSES = (
    COMPLETED,
    "in_progress",
    "blocked",
    "missing",
)

APPROVED_FOR_REAL_DATA_VALIDATION = "approved_for_real_data_validation"
BLOCKED_PENDING_STAGE3_COMPONENTS = "blocked_pending_stage3_components"

ALLOWED_READINESS_DECISIONS = (
    APPROVED_FOR_REAL_DATA_VALIDATION,
    BLOCKED_PENDING_STAGE3_COMPONENTS,
)

REAL_EMBEDDING_ARTIFACT_VALIDATION = "real_embedding_artifact_validation"
CONTROLLED_EMBEDDING_EXTRACTION = "controlled_embedding_extraction"
ALLOWED_NEXT_STEPS = (
    REAL_EMBEDDING_ARTIFACT_VALIDATION,
    CONTROLLED_EMBEDDING_EXTRACTION,
)

DEFAULT_SPLIT_LEVEL = "patient"
ALLOWED_READINESS_SPLIT_LEVELS = ("patient", "donor")


class ModelingReadinessGateError(ValueError):
    """Raised when the Stage 3 readiness gate violates the contract."""


@dataclass(frozen=True)
class ReadinessComponentStatus:
    """One Stage 3 prerequisite component status."""

    name: str
    status: str = COMPLETED
    evidence: str = "validated_by_tests"
    required: bool = True
    notes: str = ""


@dataclass(frozen=True)
class ModelingReadinessGate:
    """Metadata-only readiness decision for the future real-data path."""

    current_feature: str = STAGE3_CURRENT_FEATURE
    split_level: str = DEFAULT_SPLIT_LEVEL
    next_step: str = REAL_EMBEDDING_ARTIFACT_VALIDATION
    components: tuple[ReadinessComponentStatus, ...] = (
        ReadinessComponentStatus(EMBEDDING_ARTIFACT_SCHEMA),
        ReadinessComponentStatus(PATIENT_AGGREGATION_DESIGN),
        ReadinessComponentStatus(LEAKAGE_SAFE_SPLITS),
        ReadinessComponentStatus(EVALUATION_PROTOCOL_SCAFFOLD),
        ReadinessComponentStatus(BASELINE_CONTROL_PLAN),
    )
    require_embedding_artifact_schema: bool = True
    require_patient_aggregation_design: bool = True
    require_leakage_safe_splits: bool = True
    require_evaluation_protocol_scaffold: bool = True
    require_baseline_control_plan: bool = True
    require_patient_level_unit: bool = True
    require_same_splits_for_candidate_and_baselines: bool = True
    require_fold_internal_preprocessing: bool = True
    require_uncertainty_plan: bool = True
    require_permutation_plan: bool = True
    allow_real_data_validation_next_stage: bool = True
    allow_cell_level_split: bool = False
    allow_cell_level_features: bool = False
    allow_real_artifact_loading: bool = False
    allow_anndata_loading: bool = False
    allow_geneformer_execution: bool = False
    allow_tokenizer_execution: bool = False
    allow_embedding_extraction: bool = False
    allow_feature_extraction: bool = False
    allow_global_preprocessing: bool = False
    allow_scaler_outside_fold: bool = False
    allow_model_fitting: bool = False
    allow_metric_computation: bool = False
    allow_modeling: bool = False
    allow_training: bool = False
    allow_external_validation: bool = False
    performance_claims_added: bool = False
    readiness_decision: str = APPROVED_FOR_REAL_DATA_VALIDATION
    notes: str = ""


def _clean_required_string(value: object, field_name: str) -> str:
    """Return a non-empty normalized string or raise."""

    normalized = str(value).strip()
    if not normalized:
        raise ModelingReadinessGateError(f"{field_name} must not be empty.")
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
        raise ModelingReadinessGateError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _validate_patient_or_donor_level(value: object, field_name: str) -> str:
    """Validate patient/donor level and reject cell-level policy."""

    level = _validate_choice(value, ALLOWED_READINESS_SPLIT_LEVELS, field_name)
    forbidden_levels = {str(item) for item in DEFAULT_FORBIDDEN_SPLIT_VALUES}
    if level in forbidden_levels:
        raise ModelingReadinessGateError("cell-level assignments are not allowed.")

    return level


def validate_readiness_component_status(
    component: ReadinessComponentStatus | Mapping[str, Any],
) -> ReadinessComponentStatus:
    """Validate one Stage 3 prerequisite component."""

    if isinstance(component, Mapping):
        name = component.get("name", "")
        status = component.get("status", COMPLETED)
        evidence = component.get("evidence", "")
        required = component.get("required", True)
        notes = component.get("notes", "")
    else:
        name = component.name
        status = component.status
        evidence = component.evidence
        required = component.required
        notes = component.notes

    return ReadinessComponentStatus(
        name=_validate_choice(name, REQUIRED_STAGE3_COMPONENTS, "component.name"),
        status=_validate_choice(
            status,
            ALLOWED_COMPONENT_STATUSES,
            "component.status",
        ),
        evidence=_clean_required_string(evidence, "component.evidence"),
        required=_as_bool(required),
        notes=str(notes).strip(),
    )


def validate_readiness_components(
    components: Sequence[ReadinessComponentStatus | Mapping[str, Any]],
) -> tuple[ReadinessComponentStatus, ...]:
    """Validate Stage 3 prerequisite component coverage."""

    if isinstance(components, (str, bytes)) or not isinstance(components, Sequence):
        raise ModelingReadinessGateError("components must be a sequence.")
    if not components:
        raise ModelingReadinessGateError("components must not be empty.")

    validated = tuple(validate_readiness_component_status(item) for item in components)

    names = [component.name for component in validated]
    duplicate_names = sorted(name for name, count in Counter(names).items() if count > 1)
    if duplicate_names:
        raise ModelingReadinessGateError("component names must be unique.")

    missing_required = sorted(set(REQUIRED_STAGE3_COMPONENTS).difference(names))
    if missing_required:
        raise ModelingReadinessGateError(
            "readiness gate must include all required Stage 3 components."
        )

    incomplete = sorted(
        component.name
        for component in validated
        if component.required and component.status != COMPLETED
    )
    if incomplete:
        raise ModelingReadinessGateError(
            "all required Stage 3 components must be completed."
        )

    return tuple(sorted(validated, key=lambda component: component.name))


def validate_modeling_readiness_gate(
    gate: ModelingReadinessGate,
) -> ModelingReadinessGate:
    """Validate the final metadata-only Stage 3 readiness gate."""

    current_feature = _validate_choice(
        gate.current_feature,
        (STAGE3_CURRENT_FEATURE,),
        "current_feature",
    )
    split_level = _validate_patient_or_donor_level(gate.split_level, "split_level")
    next_step = _validate_choice(gate.next_step, ALLOWED_NEXT_STEPS, "next_step")
    readiness_decision = _validate_choice(
        gate.readiness_decision,
        ALLOWED_READINESS_DECISIONS,
        "readiness_decision",
    )
    components = validate_readiness_components(gate.components)

    if readiness_decision != APPROVED_FOR_REAL_DATA_VALIDATION:
        raise ModelingReadinessGateError(
            "readiness decision must approve real-data validation after Stage 3."
        )

    if not _as_bool(gate.require_embedding_artifact_schema):
        raise ModelingReadinessGateError("embedding artifact schema is required.")
    if not _as_bool(gate.require_patient_aggregation_design):
        raise ModelingReadinessGateError("patient aggregation design is required.")
    if not _as_bool(gate.require_leakage_safe_splits):
        raise ModelingReadinessGateError("leakage-safe splits are required.")
    if not _as_bool(gate.require_evaluation_protocol_scaffold):
        raise ModelingReadinessGateError("evaluation protocol scaffold is required.")
    if not _as_bool(gate.require_baseline_control_plan):
        raise ModelingReadinessGateError("baseline/control plan is required.")
    if not _as_bool(gate.require_patient_level_unit):
        raise ModelingReadinessGateError("patient/donor-level unit is required.")
    if not _as_bool(gate.require_same_splits_for_candidate_and_baselines):
        raise ModelingReadinessGateError(
            "candidate and baselines must use the same splits."
        )
    if not _as_bool(gate.require_fold_internal_preprocessing):
        raise ModelingReadinessGateError("fold-internal preprocessing is required.")
    if not _as_bool(gate.require_uncertainty_plan):
        raise ModelingReadinessGateError("uncertainty plan is required.")
    if not _as_bool(gate.require_permutation_plan):
        raise ModelingReadinessGateError("permutation plan is required.")
    if not _as_bool(gate.allow_real_data_validation_next_stage):
        raise ModelingReadinessGateError(
            "next-stage real-data validation must be explicitly allowed by the gate."
        )

    if _as_bool(gate.allow_cell_level_split):
        raise ModelingReadinessGateError("cell-level split assignments are not allowed.")
    if _as_bool(gate.allow_cell_level_features):
        raise ModelingReadinessGateError("cell-level features are not allowed.")
    if _as_bool(gate.allow_real_artifact_loading):
        raise ModelingReadinessGateError(
            "the readiness gate must not load real artifacts."
        )
    if _as_bool(gate.allow_anndata_loading):
        raise ModelingReadinessGateError("the readiness gate must not load AnnData.")
    if _as_bool(gate.allow_geneformer_execution):
        raise ModelingReadinessGateError(
            "the readiness gate must not execute Geneformer."
        )
    if _as_bool(gate.allow_tokenizer_execution):
        raise ModelingReadinessGateError(
            "the readiness gate must not execute tokenizers."
        )
    if _as_bool(gate.allow_embedding_extraction):
        raise ModelingReadinessGateError(
            "the readiness gate must not extract embeddings."
        )
    if _as_bool(gate.allow_feature_extraction):
        raise ModelingReadinessGateError(
            "the readiness gate must not extract baseline features."
        )
    if _as_bool(gate.allow_global_preprocessing):
        raise ModelingReadinessGateError(
            "global preprocessing across folds is not allowed."
        )
    if _as_bool(gate.allow_scaler_outside_fold):
        raise ModelingReadinessGateError(
            "scaler fitting outside the training fold is not allowed."
        )
    if _as_bool(gate.allow_model_fitting):
        raise ModelingReadinessGateError(
            "model fitting is not allowed in the readiness gate."
        )
    if _as_bool(gate.allow_metric_computation):
        raise ModelingReadinessGateError(
            "metric computation is not allowed in the readiness gate."
        )
    if _as_bool(gate.allow_modeling):
        raise ModelingReadinessGateError("Stage 3 readiness keeps modeling disabled.")
    if _as_bool(gate.allow_training):
        raise ModelingReadinessGateError("Stage 3 readiness keeps training disabled.")
    if _as_bool(gate.allow_external_validation):
        raise ModelingReadinessGateError(
            "Stage 3 readiness keeps external validation disabled."
        )
    if _as_bool(gate.performance_claims_added):
        raise ModelingReadinessGateError(
            "Stage 3 readiness must not add performance claims."
        )

    return ModelingReadinessGate(
        current_feature=current_feature,
        split_level=split_level,
        next_step=next_step,
        components=components,
        require_embedding_artifact_schema=True,
        require_patient_aggregation_design=True,
        require_leakage_safe_splits=True,
        require_evaluation_protocol_scaffold=True,
        require_baseline_control_plan=True,
        require_patient_level_unit=True,
        require_same_splits_for_candidate_and_baselines=True,
        require_fold_internal_preprocessing=True,
        require_uncertainty_plan=True,
        require_permutation_plan=True,
        allow_real_data_validation_next_stage=True,
        allow_cell_level_split=False,
        allow_cell_level_features=False,
        allow_real_artifact_loading=False,
        allow_anndata_loading=False,
        allow_geneformer_execution=False,
        allow_tokenizer_execution=False,
        allow_embedding_extraction=False,
        allow_feature_extraction=False,
        allow_global_preprocessing=False,
        allow_scaler_outside_fold=False,
        allow_model_fitting=False,
        allow_metric_computation=False,
        allow_modeling=False,
        allow_training=False,
        allow_external_validation=False,
        performance_claims_added=False,
        readiness_decision=APPROVED_FOR_REAL_DATA_VALIDATION,
        notes=str(gate.notes).strip(),
    )


def modeling_readiness_gate_from_mapping(data: Mapping[str, Any]) -> ModelingReadinessGate:
    """Build and validate a readiness gate from a mapping."""

    components_data = data.get("components")
    if components_data is None:
        components = ModelingReadinessGate().components
    elif isinstance(components_data, (str, bytes)) or not isinstance(
        components_data,
        Sequence,
    ):
        raise ModelingReadinessGateError("components must be a sequence.")
    else:
        components = tuple(
            validate_readiness_component_status(component)
            for component in components_data
        )

    return validate_modeling_readiness_gate(
        ModelingReadinessGate(
            current_feature=data.get("current_feature", STAGE3_CURRENT_FEATURE),
            split_level=data.get("split_level", DEFAULT_SPLIT_LEVEL),
            next_step=data.get("next_step", REAL_EMBEDDING_ARTIFACT_VALIDATION),
            components=components,
            require_embedding_artifact_schema=data.get(
                "require_embedding_artifact_schema",
                True,
            ),
            require_patient_aggregation_design=data.get(
                "require_patient_aggregation_design",
                True,
            ),
            require_leakage_safe_splits=data.get(
                "require_leakage_safe_splits",
                True,
            ),
            require_evaluation_protocol_scaffold=data.get(
                "require_evaluation_protocol_scaffold",
                True,
            ),
            require_baseline_control_plan=data.get(
                "require_baseline_control_plan",
                True,
            ),
            require_patient_level_unit=data.get("require_patient_level_unit", True),
            require_same_splits_for_candidate_and_baselines=data.get(
                "require_same_splits_for_candidate_and_baselines",
                True,
            ),
            require_fold_internal_preprocessing=data.get(
                "require_fold_internal_preprocessing",
                True,
            ),
            require_uncertainty_plan=data.get("require_uncertainty_plan", True),
            require_permutation_plan=data.get("require_permutation_plan", True),
            allow_real_data_validation_next_stage=data.get(
                "allow_real_data_validation_next_stage",
                True,
            ),
            allow_cell_level_split=data.get("allow_cell_level_split", False),
            allow_cell_level_features=data.get("allow_cell_level_features", False),
            allow_real_artifact_loading=data.get("allow_real_artifact_loading", False),
            allow_anndata_loading=data.get("allow_anndata_loading", False),
            allow_geneformer_execution=data.get("allow_geneformer_execution", False),
            allow_tokenizer_execution=data.get("allow_tokenizer_execution", False),
            allow_embedding_extraction=data.get("allow_embedding_extraction", False),
            allow_feature_extraction=data.get("allow_feature_extraction", False),
            allow_global_preprocessing=data.get("allow_global_preprocessing", False),
            allow_scaler_outside_fold=data.get("allow_scaler_outside_fold", False),
            allow_model_fitting=data.get("allow_model_fitting", False),
            allow_metric_computation=data.get("allow_metric_computation", False),
            allow_modeling=data.get("allow_modeling", False),
            allow_training=data.get("allow_training", False),
            allow_external_validation=data.get("allow_external_validation", False),
            performance_claims_added=data.get("performance_claims_added", False),
            readiness_decision=data.get(
                "readiness_decision",
                APPROVED_FOR_REAL_DATA_VALIDATION,
            ),
            notes=data.get("notes", ""),
        )
    )


def modeling_readiness_gate_to_dict(gate: ModelingReadinessGate) -> dict[str, Any]:
    """Serialize a validated readiness gate to a plain dictionary."""

    return asdict(validate_modeling_readiness_gate(gate))
