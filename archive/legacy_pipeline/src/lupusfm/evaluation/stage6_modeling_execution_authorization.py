"""Stage 6 controlled donor-level modeling execution authorization.

This module validates the metadata-only authorization record that opens
Stage 6 as the controlled donor-level modeling execution stage.

Stage 6-F001 authorizes the Stage 6 execution path itself, but it does not
perform runtime execution and does not grant immediate permission to load
real artifacts, load .npy payloads, parse vectors, materialize inputs,
create labels from real data, execute splits, aggregate embeddings, fit
models, generate predictions, compute metrics, train models, perform
external validation, or add performance claims.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, fields
from typing import Any


COMPLETED = "completed"
IN_PROGRESS = "in_progress"
BLOCKED = "blocked"

STAGE6_CURRENT_FEATURE = "STAGE6-F001"
STAGE6_NAME = "Stage 6 - Controlled donor-level modeling execution"
STAGE6_FEATURE_NAME = "Modeling execution authorization"

STAGE5_COMPLETED_FEATURES = (
    "STAGE5-F001",
    "STAGE5-F002",
    "STAGE5-F003",
    "STAGE5-F004",
    "STAGE5-F005",
)
STAGE6_REMAINING_FEATURES = (
    "STAGE6-F002",
    "STAGE6-F003",
    "STAGE6-F004",
    "STAGE6-F005",
    "STAGE6-F006",
    "STAGE6-F007",
)

SEPARATE_EXECUTION_STAGE_REQUIRED = "separate_modeling_execution_stage_required"
STAGE6_CONTROLLED_EXECUTION_PATH_AUTHORIZED = (
    "stage6_controlled_execution_path_authorized"
)
STAGE6_OPENED_NO_RUNTIME_EXECUTION = "stage6_opened_no_runtime_execution"
CONTROLLED_DONOR_LEVEL_EXECUTION_IN_STAGE6 = (
    "controlled_donor_level_execution_in_stage6"
)
NO_ADDITIONAL_EXECUTION_STAGE_REQUIRED = "no_additional_execution_stage_required"
DONOR_LEVEL = "donor"
DONOR_LEVEL_ONLY = "donor_level_only"
CELL_LEVEL_SPLIT_FORBIDDEN = "cell_level_split_forbidden"
PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE = "prohibited_until_explicit_stage6_gate"
NOT_APPLICABLE = "not_applicable"

ALLOWED_STAGE6_STATUSES = (IN_PROGRESS, BLOCKED)
ALLOWED_AUTHORIZATION_STATUSES = (IN_PROGRESS, BLOCKED)
ALLOWED_AUTHORIZATION_DECISIONS = (STAGE6_CONTROLLED_EXECUTION_PATH_AUTHORIZED,)
ALLOWED_MODELING_AUTHORIZATION_STATUSES = (STAGE6_OPENED_NO_RUNTIME_EXECUTION,)
ALLOWED_EXECUTION_POLICIES = (CONTROLLED_DONOR_LEVEL_EXECUTION_IN_STAGE6,)
ALLOWED_ADDITIONAL_STAGE_POLICIES = (NO_ADDITIONAL_EXECUTION_STAGE_REQUIRED,)
ALLOWED_RECORD_LEVELS = (DONOR_LEVEL,)
ALLOWED_POLICIES = (
    DONOR_LEVEL_ONLY,
    CELL_LEVEL_SPLIT_FORBIDDEN,
    PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
    NOT_APPLICABLE,
)


class Stage6ModelingExecutionAuthorizationError(ValueError):
    """Raised when Stage 6-F001 authorization metadata is unsafe."""


@dataclass(frozen=True)
class Stage6ModelingExecutionAuthorization:
    """Metadata-only Stage 6-F001 authorization record.

    This record starts the single controlled execution stage requested after
    Stage 5. It does not execute modeling yet; it fixes the rule that real
    execution must occur inside Stage 6 rather than being deferred to a
    separate Stage 7.
    """

    current_stage: str = "Stage 6"
    stage_name: str = STAGE6_NAME
    current_feature: str = STAGE6_CURRENT_FEATURE
    feature_name: str = STAGE6_FEATURE_NAME
    stage6_status: str = IN_PROGRESS
    authorization_status: str = IN_PROGRESS
    authorization_decision: str = STAGE6_CONTROLLED_EXECUTION_PATH_AUTHORIZED
    modeling_authorization_status: str = STAGE6_OPENED_NO_RUNTIME_EXECUTION
    upstream_stage5_status: str = COMPLETED
    upstream_handoff_decision: str = SEPARATE_EXECUTION_STAGE_REQUIRED
    completed_stage5_features: tuple[str, ...] = STAGE5_COMPLETED_FEATURES
    previous_stage5_feature: str = "STAGE5-F005"
    previous_stage5_closeout_status: str = COMPLETED
    stage6_execution_policy: str = CONTROLLED_DONOR_LEVEL_EXECUTION_IN_STAGE6
    additional_execution_stage_policy: str = NO_ADDITIONAL_EXECUTION_STAGE_REQUIRED
    scope: str = "authorization_only_no_runtime_execution"
    first_runtime_execution_feature: str = "STAGE6-F005"
    next_feature: str = "STAGE6-F002"
    next_feature_name: str = "Real artifact access and integrity gate"
    remaining_stage6_features: tuple[str, ...] = STAGE6_REMAINING_FEATURES
    handoff_record_level: str = DONOR_LEVEL
    split_policy: str = DONOR_LEVEL_ONLY
    leakage_policy: str = CELL_LEVEL_SPLIT_FORBIDDEN
    artifact_loading_policy: str = PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE
    input_materialization_policy: str = PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE
    label_creation_policy: str = PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE
    split_execution_policy: str = PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE
    aggregation_execution_policy: str = PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE
    modeling_execution_policy: str = PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE
    prediction_generation_policy: str = PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE
    metric_computation_policy: str = PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE
    external_validation_policy: str = PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE
    performance_claim_policy: str = PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE
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
    requires_no_additional_execution_stage: bool = True
    permits_stage6_controlled_execution_path: bool = True
    stage7_required: bool = False
    separate_stage7_required: bool = False
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
        raise Stage6ModelingExecutionAuthorizationError(
            f"{field_name} must not be empty."
        )
    if "\x00" in normalized:
        raise Stage6ModelingExecutionAuthorizationError(
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
        raise Stage6ModelingExecutionAuthorizationError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _normalize_exact_sequence(
    values: Sequence[object],
    expected: tuple[str, ...],
    field_name: str,
) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise Stage6ModelingExecutionAuthorizationError(
            f"{field_name} must be a sequence."
        )

    normalized = tuple(
        _clean_required_string(value, f"{field_name} item") for value in values
    )
    if normalized != expected:
        expected_text = ", ".join(expected)
        got = ", ".join(normalized)
        raise Stage6ModelingExecutionAuthorizationError(
            f"{field_name} must exactly equal: {expected_text}; got: {got}."
        )

    return normalized


def validate_stage6_modeling_execution_authorization(
    authorization: Stage6ModelingExecutionAuthorization,
) -> Stage6ModelingExecutionAuthorization:
    """Validate the metadata-only Stage 6-F001 authorization record."""

    current_stage = _validate_choice(
        authorization.current_stage,
        ("Stage 6",),
        "current_stage",
    )
    current_feature = _validate_choice(
        authorization.current_feature,
        (STAGE6_CURRENT_FEATURE,),
        "current_feature",
    )
    stage6_status = _validate_choice(
        authorization.stage6_status,
        ALLOWED_STAGE6_STATUSES,
        "stage6_status",
    )
    authorization_status = _validate_choice(
        authorization.authorization_status,
        ALLOWED_AUTHORIZATION_STATUSES,
        "authorization_status",
    )
    authorization_decision = _validate_choice(
        authorization.authorization_decision,
        ALLOWED_AUTHORIZATION_DECISIONS,
        "authorization_decision",
    )
    modeling_authorization_status = _validate_choice(
        authorization.modeling_authorization_status,
        ALLOWED_MODELING_AUTHORIZATION_STATUSES,
        "modeling_authorization_status",
    )
    upstream_stage5_status = _validate_choice(
        authorization.upstream_stage5_status,
        (COMPLETED,),
        "upstream_stage5_status",
    )
    upstream_handoff_decision = _validate_choice(
        authorization.upstream_handoff_decision,
        (SEPARATE_EXECUTION_STAGE_REQUIRED,),
        "upstream_handoff_decision",
    )
    completed_stage5_features = _normalize_exact_sequence(
        authorization.completed_stage5_features,
        STAGE5_COMPLETED_FEATURES,
        "completed_stage5_features",
    )
    previous_stage5_feature = _validate_choice(
        authorization.previous_stage5_feature,
        ("STAGE5-F005",),
        "previous_stage5_feature",
    )
    previous_stage5_closeout_status = _validate_choice(
        authorization.previous_stage5_closeout_status,
        (COMPLETED,),
        "previous_stage5_closeout_status",
    )
    stage6_execution_policy = _validate_choice(
        authorization.stage6_execution_policy,
        ALLOWED_EXECUTION_POLICIES,
        "stage6_execution_policy",
    )
    additional_execution_stage_policy = _validate_choice(
        authorization.additional_execution_stage_policy,
        ALLOWED_ADDITIONAL_STAGE_POLICIES,
        "additional_execution_stage_policy",
    )
    first_runtime_execution_feature = _validate_choice(
        authorization.first_runtime_execution_feature,
        ("STAGE6-F005",),
        "first_runtime_execution_feature",
    )
    next_feature = _validate_choice(
        authorization.next_feature,
        ("STAGE6-F002",),
        "next_feature",
    )
    remaining_stage6_features = _normalize_exact_sequence(
        authorization.remaining_stage6_features,
        STAGE6_REMAINING_FEATURES,
        "remaining_stage6_features",
    )
    handoff_record_level = _validate_choice(
        authorization.handoff_record_level,
        ALLOWED_RECORD_LEVELS,
        "handoff_record_level",
    )

    required_policy_values = {
        "split_policy": (authorization.split_policy, DONOR_LEVEL_ONLY),
        "leakage_policy": (
            authorization.leakage_policy,
            CELL_LEVEL_SPLIT_FORBIDDEN,
        ),
        "artifact_loading_policy": (
            authorization.artifact_loading_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "input_materialization_policy": (
            authorization.input_materialization_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "label_creation_policy": (
            authorization.label_creation_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "split_execution_policy": (
            authorization.split_execution_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "aggregation_execution_policy": (
            authorization.aggregation_execution_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "modeling_execution_policy": (
            authorization.modeling_execution_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "prediction_generation_policy": (
            authorization.prediction_generation_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "metric_computation_policy": (
            authorization.metric_computation_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "external_validation_policy": (
            authorization.external_validation_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "performance_claim_policy": (
            authorization.performance_claim_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
    }
    for field_name, (value, expected) in required_policy_values.items():
        _validate_choice(value, ALLOWED_POLICIES, field_name)
        if value != expected:
            raise Stage6ModelingExecutionAuthorizationError(
                f"{field_name} must remain {expected}."
            )

    required_true_flags = {
        "requires_explicit_modeling_approval": (
            authorization.requires_explicit_modeling_approval
        ),
        "requires_human_review_before_modeling": (
            authorization.requires_human_review_before_modeling
        ),
        "requires_reproducibility_review": authorization.requires_reproducibility_review,
        "requires_leakage_review": authorization.requires_leakage_review,
        "requires_artifact_integrity_review": (
            authorization.requires_artifact_integrity_review
        ),
        "requires_scope_review": authorization.requires_scope_review,
        "requires_donor_level_only": authorization.requires_donor_level_only,
        "forbids_cell_level_split": authorization.forbids_cell_level_split,
        "requires_no_large_artifact_commit": (
            authorization.requires_no_large_artifact_commit
        ),
        "requires_protocol_before_execution": (
            authorization.requires_protocol_before_execution
        ),
        "requires_no_additional_execution_stage": (
            authorization.requires_no_additional_execution_stage
        ),
        "permits_stage6_controlled_execution_path": (
            authorization.permits_stage6_controlled_execution_path
        ),
    }
    disabled_required = sorted(
        name for name, value in required_true_flags.items() if not _as_bool(value)
    )
    if disabled_required:
        raise Stage6ModelingExecutionAuthorizationError(
            "required Stage 6 authorization gates must remain enabled; disabled: "
            + ", ".join(disabled_required)
        )

    stage7_flags = {
        "stage7_required": authorization.stage7_required,
        "separate_stage7_required": authorization.separate_stage7_required,
    }
    enabled_stage7_flags = sorted(
        name for name, value in stage7_flags.items() if _as_bool(value)
    )
    if enabled_stage7_flags:
        raise Stage6ModelingExecutionAuthorizationError(
            "Stage 6-F001 must not defer execution to Stage 7; enabled: "
            + ", ".join(enabled_stage7_flags)
        )

    forbidden_flags = {
        "allow_real_artifact_loading": authorization.allow_real_artifact_loading,
        "allow_npy_payload_loading": authorization.allow_npy_payload_loading,
        "allow_embedding_vector_parsing": authorization.allow_embedding_vector_parsing,
        "allow_input_materialization": authorization.allow_input_materialization,
        "allow_label_array_creation": authorization.allow_label_array_creation,
        "allow_split_execution": authorization.allow_split_execution,
        "allow_real_aggregation_execution": authorization.allow_real_aggregation_execution,
        "allow_anndata_loading": authorization.allow_anndata_loading,
        "allow_geneformer_execution": authorization.allow_geneformer_execution,
        "allow_tokenizer_execution": authorization.allow_tokenizer_execution,
        "allow_embedding_extraction": authorization.allow_embedding_extraction,
        "allow_feature_extraction": authorization.allow_feature_extraction,
        "allow_global_preprocessing": authorization.allow_global_preprocessing,
        "allow_scaler_outside_fold": authorization.allow_scaler_outside_fold,
        "allow_model_fitting": authorization.allow_model_fitting,
        "allow_prediction_generation": authorization.allow_prediction_generation,
        "allow_metric_computation": authorization.allow_metric_computation,
        "allow_modeling": authorization.allow_modeling,
        "modeling_authorization_granted": authorization.modeling_authorization_granted,
        "modeling_allowed": authorization.modeling_allowed,
        "training_allowed": authorization.training_allowed,
        "external_validation_allowed": authorization.external_validation_allowed,
        "performance_claims_allowed": authorization.performance_claims_allowed,
        "performance_claims_added": authorization.performance_claims_added,
    }
    enabled = sorted(name for name, value in forbidden_flags.items() if _as_bool(value))
    if enabled:
        raise Stage6ModelingExecutionAuthorizationError(
            "Stage 6-F001 opens only the controlled Stage 6 execution path; it "
            "does not grant artifact loading, input materialization, split "
            "execution, modeling, metrics, training, external validation, or "
            "performance claims; enabled: " + ", ".join(enabled)
        )

    return Stage6ModelingExecutionAuthorization(
        current_stage=current_stage,
        stage_name=_clean_required_string(authorization.stage_name, "stage_name"),
        current_feature=current_feature,
        feature_name=_clean_required_string(authorization.feature_name, "feature_name"),
        stage6_status=stage6_status,
        authorization_status=authorization_status,
        authorization_decision=authorization_decision,
        modeling_authorization_status=modeling_authorization_status,
        upstream_stage5_status=upstream_stage5_status,
        upstream_handoff_decision=upstream_handoff_decision,
        completed_stage5_features=completed_stage5_features,
        previous_stage5_feature=previous_stage5_feature,
        previous_stage5_closeout_status=previous_stage5_closeout_status,
        stage6_execution_policy=stage6_execution_policy,
        additional_execution_stage_policy=additional_execution_stage_policy,
        scope=_clean_required_string(authorization.scope, "scope"),
        first_runtime_execution_feature=first_runtime_execution_feature,
        next_feature=next_feature,
        next_feature_name=_clean_required_string(
            authorization.next_feature_name,
            "next_feature_name",
        ),
        remaining_stage6_features=remaining_stage6_features,
        handoff_record_level=handoff_record_level,
        split_policy=DONOR_LEVEL_ONLY,
        leakage_policy=CELL_LEVEL_SPLIT_FORBIDDEN,
        artifact_loading_policy=PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        input_materialization_policy=PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        label_creation_policy=PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        split_execution_policy=PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        aggregation_execution_policy=PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        modeling_execution_policy=PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        prediction_generation_policy=PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        metric_computation_policy=PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        external_validation_policy=PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        performance_claim_policy=PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
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
        requires_no_additional_execution_stage=True,
        permits_stage6_controlled_execution_path=True,
        stage7_required=False,
        separate_stage7_required=False,
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
        notes=str(authorization.notes).strip(),
    )


def stage6_modeling_execution_authorization_from_mapping(
    values: Mapping[str, Any],
) -> Stage6ModelingExecutionAuthorization:
    """Build a Stage 6-F001 authorization record from a mapping."""

    defaults = {
        field.name: getattr(Stage6ModelingExecutionAuthorization(), field.name)
        for field in fields(Stage6ModelingExecutionAuthorization)
    }
    merged = {**defaults, **dict(values)}
    for sequence_field in ("completed_stage5_features", "remaining_stage6_features"):
        if sequence_field in merged and not isinstance(merged[sequence_field], tuple):
            merged[sequence_field] = tuple(merged[sequence_field])

    return validate_stage6_modeling_execution_authorization(
        Stage6ModelingExecutionAuthorization(**merged)
    )


def stage6_modeling_execution_authorization_to_dict(
    authorization: Stage6ModelingExecutionAuthorization,
) -> dict[str, Any]:
    """Serialize a validated Stage 6-F001 authorization record."""

    validated = validate_stage6_modeling_execution_authorization(authorization)
    serialized = asdict(validated)
    for sequence_field in ("completed_stage5_features", "remaining_stage6_features"):
        serialized[sequence_field] = list(serialized[sequence_field])

    return serialized


def stage6_modeling_execution_authorization_summary(
    authorization: Stage6ModelingExecutionAuthorization,
) -> dict[str, Any]:
    """Return the compact Stage 6-F001 authorization summary."""

    validated = validate_stage6_modeling_execution_authorization(authorization)
    return {
        "current_stage": validated.current_stage,
        "current_feature": validated.current_feature,
        "stage6_status": validated.stage6_status,
        "authorization_status": validated.authorization_status,
        "authorization_decision": validated.authorization_decision,
        "stage6_execution_policy": validated.stage6_execution_policy,
        "additional_execution_stage_policy": (
            validated.additional_execution_stage_policy
        ),
        "first_runtime_execution_feature": validated.first_runtime_execution_feature,
        "next_feature": validated.next_feature,
        "requires_donor_level_only": validated.requires_donor_level_only,
        "forbids_cell_level_split": validated.forbids_cell_level_split,
        "requires_no_additional_execution_stage": (
            validated.requires_no_additional_execution_stage
        ),
        "permits_stage6_controlled_execution_path": (
            validated.permits_stage6_controlled_execution_path
        ),
        "stage7_required": validated.stage7_required,
        "modeling_authorization_granted": validated.modeling_authorization_granted,
        "modeling_allowed": validated.modeling_allowed,
        "allow_model_fitting": validated.allow_model_fitting,
        "allow_prediction_generation": validated.allow_prediction_generation,
        "allow_metric_computation": validated.allow_metric_computation,
        "performance_claims_allowed": validated.performance_claims_allowed,
        "performance_claims_added": validated.performance_claims_added,
    }
