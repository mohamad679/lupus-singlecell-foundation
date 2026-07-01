"""Stage 5 modeling execution protocol scaffold.

This module validates the metadata-only execution protocol scaffold for the
separate modeling stage. It defines protocol boundaries, required approvals,
donor-level controls, and prohibited runtime actions only.

It does not load real artifacts, load .npy payloads, parse vectors, materialize
inputs, create labels, execute splits, aggregate real embeddings, fit models,
generate predictions, compute metrics, train models, perform external
validation, or add performance claims.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any


COMPLETED = "completed"
IN_PROGRESS = "in_progress"
BLOCKED = "blocked"
PENDING = "pending"

STAGE5_CURRENT_FEATURE = "STAGE5-F002"
STAGE5_PREVIOUS_FEATURE = "STAGE5-F001"
STAGE5_NEXT_FEATURE = "STAGE5-F003"
STAGE5_NAME = "Stage 5 - Modeling stage approval and execution planning"
STAGE5_FEATURE_NAME = "Modeling execution protocol scaffold"
STAGE5_NEXT_FEATURE_NAME = "Donor-level execution contract approval"

REQUIRED_COMPLETED_STAGE5_FEATURES = (STAGE5_PREVIOUS_FEATURE,)

MODELING_AUTHORIZATION_NOT_GRANTED = "not_granted"
BLOCKED_PENDING_HUMAN_REVIEW = "blocked_pending_human_review"
BLOCKED_PENDING_REQUIRED_REVIEWS = "blocked_pending_required_reviews"

DONOR_LEVEL = "donor"
DONOR_LEVEL_ONLY = "donor_level_only"
CELL_LEVEL_SPLIT_FORBIDDEN = "cell_level_split_forbidden"
PROTOCOL_ONLY_NO_RUNTIME_EXECUTION = "protocol_only_no_runtime_execution"
PROHIBITED_UNTIL_EXPLICIT_GATE = "prohibited_until_explicit_gate"
FUTURE_ONLY_NO_COMPUTATION = "future_only_no_computation"

ALLOWED_STAGE5_STATUSES = (IN_PROGRESS, BLOCKED)
ALLOWED_PROTOCOL_STATUSES = (PENDING, IN_PROGRESS, BLOCKED)
ALLOWED_APPROVAL_STATUSES = (PENDING, BLOCKED)
ALLOWED_MODELING_AUTHORIZATION_STATUSES = (
    MODELING_AUTHORIZATION_NOT_GRANTED,
    BLOCKED_PENDING_HUMAN_REVIEW,
    BLOCKED_PENDING_REQUIRED_REVIEWS,
)
ALLOWED_RECORD_LEVELS = (DONOR_LEVEL,)
ALLOWED_PROTOCOL_POLICIES = (
    DONOR_LEVEL_ONLY,
    CELL_LEVEL_SPLIT_FORBIDDEN,
    PROTOCOL_ONLY_NO_RUNTIME_EXECUTION,
    PROHIBITED_UNTIL_EXPLICIT_GATE,
    FUTURE_ONLY_NO_COMPUTATION,
)


class Stage5ModelingExecutionProtocolScaffoldError(ValueError):
    """Raised when the Stage 5 modeling execution protocol scaffold is unsafe."""


@dataclass(frozen=True)
class Stage5ModelingExecutionProtocolScaffold:
    """Metadata-only Stage 5-F002 execution protocol scaffold.

    This scaffold defines how a later execution protocol must be reviewed before
    any runtime work can occur. It does not grant modeling authorization.
    """

    current_stage: str = "Stage 5"
    stage_name: str = STAGE5_NAME
    current_feature: str = STAGE5_CURRENT_FEATURE
    feature_name: str = STAGE5_FEATURE_NAME
    stage5_status: str = IN_PROGRESS
    protocol_status: str = IN_PROGRESS
    approval_status: str = PENDING
    modeling_authorization_status: str = MODELING_AUTHORIZATION_NOT_GRANTED
    previous_feature: str = STAGE5_PREVIOUS_FEATURE
    previous_feature_status: str = COMPLETED
    completed_stage5_features: tuple[str, ...] = REQUIRED_COMPLETED_STAGE5_FEATURES
    next_feature: str = STAGE5_NEXT_FEATURE
    next_feature_name: str = STAGE5_NEXT_FEATURE_NAME
    scope: str = "execution_protocol_scaffold_only_no_modeling_execution"
    protocol_record_level: str = DONOR_LEVEL
    split_policy: str = DONOR_LEVEL_ONLY
    leakage_policy: str = CELL_LEVEL_SPLIT_FORBIDDEN
    artifact_loading_policy: str = PROHIBITED_UNTIL_EXPLICIT_GATE
    input_materialization_policy: str = PROHIBITED_UNTIL_EXPLICIT_GATE
    label_creation_policy: str = PROHIBITED_UNTIL_EXPLICIT_GATE
    aggregation_execution_policy: str = PROHIBITED_UNTIL_EXPLICIT_GATE
    modeling_execution_policy: str = PROHIBITED_UNTIL_EXPLICIT_GATE
    prediction_generation_policy: str = PROHIBITED_UNTIL_EXPLICIT_GATE
    metric_computation_policy: str = FUTURE_ONLY_NO_COMPUTATION
    external_validation_policy: str = PROHIBITED_UNTIL_EXPLICIT_GATE
    performance_claim_policy: str = PROHIBITED_UNTIL_EXPLICIT_GATE
    requires_explicit_modeling_approval: bool = True
    requires_human_review_before_modeling: bool = True
    requires_reproducibility_review: bool = True
    requires_leakage_review: bool = True
    requires_artifact_integrity_review: bool = True
    requires_scope_review: bool = True
    requires_donor_level_only: bool = True
    forbids_cell_level_split: bool = True
    requires_no_large_artifact_commit: bool = True
    requires_protocol_before_execution: bool = True
    requires_separate_execution_gate: bool = True
    allow_real_artifact_loading: bool = False
    allow_npy_payload_loading: bool = False
    allow_embedding_vector_parsing: bool = False
    allow_input_materialization: bool = False
    allow_label_array_creation: bool = False
    allow_split_execution: bool = False
    allow_real_aggregation_execution: bool = False
    allow_anndata_loading: bool = False
    allow_geneformer_execution: bool = False
    allow_tokenizer_execution: bool = False
    allow_embedding_extraction: bool = False
    allow_feature_extraction: bool = False
    allow_global_preprocessing: bool = False
    allow_scaler_outside_fold: bool = False
    allow_model_fitting: bool = False
    allow_prediction_generation: bool = False
    allow_metric_computation: bool = False
    allow_modeling: bool = False
    modeling_authorization_granted: bool = False
    modeling_allowed: bool = False
    training_allowed: bool = False
    external_validation_allowed: bool = False
    performance_claims_allowed: bool = False
    performance_claims_added: bool = False
    notes: str = ""


def _clean_required_string(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise Stage5ModelingExecutionProtocolScaffoldError(
            f"{field_name} must not be empty."
        )
    if "\x00" in normalized:
        raise Stage5ModelingExecutionProtocolScaffoldError(
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
        raise Stage5ModelingExecutionProtocolScaffoldError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _normalize_completed_stage5_features(values: Sequence[object]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise Stage5ModelingExecutionProtocolScaffoldError(
            "completed_stage5_features must be a sequence."
        )

    normalized = tuple(
        _clean_required_string(value, "completed_stage5_features item")
        for value in values
    )
    if normalized != REQUIRED_COMPLETED_STAGE5_FEATURES:
        expected = ", ".join(REQUIRED_COMPLETED_STAGE5_FEATURES)
        got = ", ".join(normalized)
        raise Stage5ModelingExecutionProtocolScaffoldError(
            f"completed_stage5_features must exactly equal: {expected}; got: {got}."
        )

    return normalized


def validate_stage5_modeling_execution_protocol_scaffold(
    scaffold: Stage5ModelingExecutionProtocolScaffold,
) -> Stage5ModelingExecutionProtocolScaffold:
    """Validate the metadata-only Stage 5-F002 execution protocol scaffold."""

    current_stage = _validate_choice(scaffold.current_stage, ("Stage 5",), "current_stage")
    current_feature = _validate_choice(
        scaffold.current_feature,
        (STAGE5_CURRENT_FEATURE,),
        "current_feature",
    )
    stage5_status = _validate_choice(
        scaffold.stage5_status,
        ALLOWED_STAGE5_STATUSES,
        "stage5_status",
    )
    protocol_status = _validate_choice(
        scaffold.protocol_status,
        ALLOWED_PROTOCOL_STATUSES,
        "protocol_status",
    )
    approval_status = _validate_choice(
        scaffold.approval_status,
        ALLOWED_APPROVAL_STATUSES,
        "approval_status",
    )
    modeling_authorization_status = _validate_choice(
        scaffold.modeling_authorization_status,
        ALLOWED_MODELING_AUTHORIZATION_STATUSES,
        "modeling_authorization_status",
    )
    previous_feature = _validate_choice(
        scaffold.previous_feature,
        (STAGE5_PREVIOUS_FEATURE,),
        "previous_feature",
    )
    previous_feature_status = _validate_choice(
        scaffold.previous_feature_status,
        (COMPLETED,),
        "previous_feature_status",
    )
    completed_stage5_features = _normalize_completed_stage5_features(
        scaffold.completed_stage5_features
    )
    next_feature = _validate_choice(
        scaffold.next_feature,
        (STAGE5_NEXT_FEATURE,),
        "next_feature",
    )
    protocol_record_level = _validate_choice(
        scaffold.protocol_record_level,
        ALLOWED_RECORD_LEVELS,
        "protocol_record_level",
    )

    required_policy_values = {
        "split_policy": (scaffold.split_policy, DONOR_LEVEL_ONLY),
        "leakage_policy": (scaffold.leakage_policy, CELL_LEVEL_SPLIT_FORBIDDEN),
        "artifact_loading_policy": (
            scaffold.artifact_loading_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "input_materialization_policy": (
            scaffold.input_materialization_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "label_creation_policy": (
            scaffold.label_creation_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "aggregation_execution_policy": (
            scaffold.aggregation_execution_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "modeling_execution_policy": (
            scaffold.modeling_execution_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "prediction_generation_policy": (
            scaffold.prediction_generation_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "metric_computation_policy": (
            scaffold.metric_computation_policy,
            FUTURE_ONLY_NO_COMPUTATION,
        ),
        "external_validation_policy": (
            scaffold.external_validation_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "performance_claim_policy": (
            scaffold.performance_claim_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
    }
    for field_name, (value, expected) in required_policy_values.items():
        _validate_choice(value, ALLOWED_PROTOCOL_POLICIES, field_name)
        if value != expected:
            raise Stage5ModelingExecutionProtocolScaffoldError(
                f"{field_name} must remain {expected}."
            )

    required_true_flags = {
        "requires_explicit_modeling_approval": scaffold.requires_explicit_modeling_approval,
        "requires_human_review_before_modeling": scaffold.requires_human_review_before_modeling,
        "requires_reproducibility_review": scaffold.requires_reproducibility_review,
        "requires_leakage_review": scaffold.requires_leakage_review,
        "requires_artifact_integrity_review": scaffold.requires_artifact_integrity_review,
        "requires_scope_review": scaffold.requires_scope_review,
        "requires_donor_level_only": scaffold.requires_donor_level_only,
        "forbids_cell_level_split": scaffold.forbids_cell_level_split,
        "requires_no_large_artifact_commit": scaffold.requires_no_large_artifact_commit,
        "requires_protocol_before_execution": scaffold.requires_protocol_before_execution,
        "requires_separate_execution_gate": scaffold.requires_separate_execution_gate,
    }
    disabled_required = sorted(
        name for name, value in required_true_flags.items() if not _as_bool(value)
    )
    if disabled_required:
        raise Stage5ModelingExecutionProtocolScaffoldError(
            "required Stage 5 execution protocol gates must remain enabled; disabled: "
            + ", ".join(disabled_required)
        )

    forbidden_flags = {
        "allow_real_artifact_loading": scaffold.allow_real_artifact_loading,
        "allow_npy_payload_loading": scaffold.allow_npy_payload_loading,
        "allow_embedding_vector_parsing": scaffold.allow_embedding_vector_parsing,
        "allow_input_materialization": scaffold.allow_input_materialization,
        "allow_label_array_creation": scaffold.allow_label_array_creation,
        "allow_split_execution": scaffold.allow_split_execution,
        "allow_real_aggregation_execution": scaffold.allow_real_aggregation_execution,
        "allow_anndata_loading": scaffold.allow_anndata_loading,
        "allow_geneformer_execution": scaffold.allow_geneformer_execution,
        "allow_tokenizer_execution": scaffold.allow_tokenizer_execution,
        "allow_embedding_extraction": scaffold.allow_embedding_extraction,
        "allow_feature_extraction": scaffold.allow_feature_extraction,
        "allow_global_preprocessing": scaffold.allow_global_preprocessing,
        "allow_scaler_outside_fold": scaffold.allow_scaler_outside_fold,
        "allow_model_fitting": scaffold.allow_model_fitting,
        "allow_prediction_generation": scaffold.allow_prediction_generation,
        "allow_metric_computation": scaffold.allow_metric_computation,
        "allow_modeling": scaffold.allow_modeling,
        "modeling_authorization_granted": scaffold.modeling_authorization_granted,
        "modeling_allowed": scaffold.modeling_allowed,
        "training_allowed": scaffold.training_allowed,
        "external_validation_allowed": scaffold.external_validation_allowed,
        "performance_claims_allowed": scaffold.performance_claims_allowed,
        "performance_claims_added": scaffold.performance_claims_added,
    }
    enabled = sorted(name for name, value in forbidden_flags.items() if _as_bool(value))
    if enabled:
        raise Stage5ModelingExecutionProtocolScaffoldError(
            "Stage 5-F002 does not grant artifact loading, input materialization, "
            "split execution, modeling, metrics, training, external validation, "
            "or performance claims; enabled: " + ", ".join(enabled)
        )

    return Stage5ModelingExecutionProtocolScaffold(
        current_stage=current_stage,
        stage_name=_clean_required_string(scaffold.stage_name, "stage_name"),
        current_feature=current_feature,
        feature_name=_clean_required_string(scaffold.feature_name, "feature_name"),
        stage5_status=stage5_status,
        protocol_status=protocol_status,
        approval_status=approval_status,
        modeling_authorization_status=modeling_authorization_status,
        previous_feature=previous_feature,
        previous_feature_status=previous_feature_status,
        completed_stage5_features=completed_stage5_features,
        next_feature=next_feature,
        next_feature_name=_clean_required_string(
            scaffold.next_feature_name,
            "next_feature_name",
        ),
        scope=_clean_required_string(scaffold.scope, "scope"),
        protocol_record_level=protocol_record_level,
        split_policy=DONOR_LEVEL_ONLY,
        leakage_policy=CELL_LEVEL_SPLIT_FORBIDDEN,
        artifact_loading_policy=PROHIBITED_UNTIL_EXPLICIT_GATE,
        input_materialization_policy=PROHIBITED_UNTIL_EXPLICIT_GATE,
        label_creation_policy=PROHIBITED_UNTIL_EXPLICIT_GATE,
        aggregation_execution_policy=PROHIBITED_UNTIL_EXPLICIT_GATE,
        modeling_execution_policy=PROHIBITED_UNTIL_EXPLICIT_GATE,
        prediction_generation_policy=PROHIBITED_UNTIL_EXPLICIT_GATE,
        metric_computation_policy=FUTURE_ONLY_NO_COMPUTATION,
        external_validation_policy=PROHIBITED_UNTIL_EXPLICIT_GATE,
        performance_claim_policy=PROHIBITED_UNTIL_EXPLICIT_GATE,
        requires_explicit_modeling_approval=True,
        requires_human_review_before_modeling=True,
        requires_reproducibility_review=True,
        requires_leakage_review=True,
        requires_artifact_integrity_review=True,
        requires_scope_review=True,
        requires_donor_level_only=True,
        forbids_cell_level_split=True,
        requires_no_large_artifact_commit=True,
        requires_protocol_before_execution=True,
        requires_separate_execution_gate=True,
        allow_real_artifact_loading=False,
        allow_npy_payload_loading=False,
        allow_embedding_vector_parsing=False,
        allow_input_materialization=False,
        allow_label_array_creation=False,
        allow_split_execution=False,
        allow_real_aggregation_execution=False,
        allow_anndata_loading=False,
        allow_geneformer_execution=False,
        allow_tokenizer_execution=False,
        allow_embedding_extraction=False,
        allow_feature_extraction=False,
        allow_global_preprocessing=False,
        allow_scaler_outside_fold=False,
        allow_model_fitting=False,
        allow_prediction_generation=False,
        allow_metric_computation=False,
        allow_modeling=False,
        modeling_authorization_granted=False,
        modeling_allowed=False,
        training_allowed=False,
        external_validation_allowed=False,
        performance_claims_allowed=False,
        performance_claims_added=False,
        notes=str(scaffold.notes).strip(),
    )


def stage5_modeling_execution_protocol_scaffold_from_mapping(
    values: Mapping[str, Any],
) -> Stage5ModelingExecutionProtocolScaffold:
    """Build and validate a Stage 5-F002 scaffold from a mapping."""

    data = stage5_modeling_execution_protocol_scaffold_to_dict(
        Stage5ModelingExecutionProtocolScaffold()
    )
    data.update(values)
    return validate_stage5_modeling_execution_protocol_scaffold(
        Stage5ModelingExecutionProtocolScaffold(**data)
    )


def stage5_modeling_execution_protocol_scaffold_to_dict(
    scaffold: Stage5ModelingExecutionProtocolScaffold,
) -> dict[str, Any]:
    """Serialize a validated Stage 5-F002 scaffold to plain Python values."""

    validated = validate_stage5_modeling_execution_protocol_scaffold(scaffold)
    serialized = asdict(validated)
    serialized["completed_stage5_features"] = list(validated.completed_stage5_features)
    return serialized


def stage5_modeling_execution_protocol_summary(
    scaffold: Stage5ModelingExecutionProtocolScaffold,
) -> dict[str, Any]:
    """Return a compact summary of the Stage 5-F002 execution protocol scaffold."""

    validated = validate_stage5_modeling_execution_protocol_scaffold(scaffold)
    return {
        "current_stage": validated.current_stage,
        "current_feature": validated.current_feature,
        "protocol_status": validated.protocol_status,
        "approval_status": validated.approval_status,
        "modeling_authorization_status": validated.modeling_authorization_status,
        "previous_feature": validated.previous_feature,
        "next_feature": validated.next_feature,
        "protocol_record_level": validated.protocol_record_level,
        "split_policy": validated.split_policy,
        "leakage_policy": validated.leakage_policy,
        "metric_computation_policy": validated.metric_computation_policy,
        "requires_separate_execution_gate": True,
        "modeling_authorization_granted": False,
        "modeling_allowed": False,
        "training_allowed": False,
        "performance_claims_allowed": False,
        "performance_claims_added": False,
    }
