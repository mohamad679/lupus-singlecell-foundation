"""Stage 5 final modeling handoff decision.

This module records the final metadata-only Stage 5 handoff decision. Stage 5
does not execute modeling. The only safe handoff outcome is that any future
modeling must happen in a separate explicitly approved execution stage.

It does not load artifacts, load .npy payloads, parse vectors, materialize
inputs, create labels, execute splits, aggregate embeddings, fit models,
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

STAGE5_CURRENT_FEATURE = "STAGE5-F005"
STAGE5_PREVIOUS_FEATURES = (
    "STAGE5-F001",
    "STAGE5-F002",
    "STAGE5-F003",
    "STAGE5-F004",
)
STAGE5_NAME = "Stage 5 - Modeling stage approval and execution planning"
STAGE5_FEATURE_NAME = "Final Stage 5 modeling handoff decision"

SEPARATE_EXECUTION_STAGE_REQUIRED = "separate_modeling_execution_stage_required"
STAGE5_DOES_NOT_AUTHORIZE_MODELING = "stage5_does_not_authorize_modeling"
FUTURE_ONLY_EXPLICIT_STAGE = "future_only_explicit_execution_stage"
NOT_GRANTED = "not_granted"

DONOR_LEVEL = "donor"
DONOR_LEVEL_ONLY = "donor_level_only"
CELL_LEVEL_SPLIT_FORBIDDEN = "cell_level_split_forbidden"
HANDOFF_ONLY_NO_EXECUTION = "handoff_only_no_execution"
PROHIBITED_UNTIL_EXPLICIT_GATE = "prohibited_until_explicit_gate"
FUTURE_ONLY_NO_COMPUTATION = "future_only_no_computation"

ALLOWED_STAGE5_STATUSES = (IN_PROGRESS, BLOCKED)
ALLOWED_HANDOFF_STATUSES = (IN_PROGRESS, BLOCKED)
ALLOWED_HANDOFF_DECISIONS = (SEPARATE_EXECUTION_STAGE_REQUIRED,)
ALLOWED_MODELING_AUTHORIZATION_STATUSES = (
    NOT_GRANTED,
    STAGE5_DOES_NOT_AUTHORIZE_MODELING,
)
ALLOWED_FUTURE_MODELING_POLICIES = (FUTURE_ONLY_EXPLICIT_STAGE,)
ALLOWED_RECORD_LEVELS = (DONOR_LEVEL,)
ALLOWED_POLICIES = (
    DONOR_LEVEL_ONLY,
    CELL_LEVEL_SPLIT_FORBIDDEN,
    HANDOFF_ONLY_NO_EXECUTION,
    PROHIBITED_UNTIL_EXPLICIT_GATE,
    FUTURE_ONLY_NO_COMPUTATION,
)


class Stage5FinalModelingHandoffDecisionError(ValueError):
    """Raised when the Stage 5 final handoff decision is unsafe."""


@dataclass(frozen=True)
class Stage5FinalModelingHandoffDecision:
    """Metadata-only Stage 5-F005 final handoff decision."""

    current_stage: str = "Stage 5"
    stage_name: str = STAGE5_NAME
    current_feature: str = STAGE5_CURRENT_FEATURE
    feature_name: str = STAGE5_FEATURE_NAME
    stage5_status: str = IN_PROGRESS
    handoff_status: str = IN_PROGRESS
    handoff_decision: str = SEPARATE_EXECUTION_STAGE_REQUIRED
    modeling_authorization_status: str = STAGE5_DOES_NOT_AUTHORIZE_MODELING
    future_modeling_policy: str = FUTURE_ONLY_EXPLICIT_STAGE
    completed_stage5_features: tuple[str, ...] = STAGE5_PREVIOUS_FEATURES
    previous_audit_feature: str = "STAGE5-F004"
    previous_audit_status: str = COMPLETED
    scope: str = "final_handoff_decision_only_no_execution"
    handoff_record_level: str = DONOR_LEVEL
    split_policy: str = DONOR_LEVEL_ONLY
    leakage_policy: str = CELL_LEVEL_SPLIT_FORBIDDEN
    handoff_scope_policy: str = HANDOFF_ONLY_NO_EXECUTION
    artifact_loading_policy: str = PROHIBITED_UNTIL_EXPLICIT_GATE
    input_materialization_policy: str = PROHIBITED_UNTIL_EXPLICIT_GATE
    label_creation_policy: str = PROHIBITED_UNTIL_EXPLICIT_GATE
    split_execution_policy: str = PROHIBITED_UNTIL_EXPLICIT_GATE
    aggregation_execution_policy: str = PROHIBITED_UNTIL_EXPLICIT_GATE
    modeling_execution_policy: str = PROHIBITED_UNTIL_EXPLICIT_GATE
    prediction_generation_policy: str = PROHIBITED_UNTIL_EXPLICIT_GATE
    metric_computation_policy: str = FUTURE_ONLY_NO_COMPUTATION
    external_validation_policy: str = PROHIBITED_UNTIL_EXPLICIT_GATE
    performance_claim_policy: str = PROHIBITED_UNTIL_EXPLICIT_GATE
    requires_explicit_modeling_approval: bool = True
    requires_separate_execution_stage: bool = True
    requires_human_review_before_modeling: bool = True
    requires_reproducibility_review: bool = True
    requires_leakage_review: bool = True
    requires_artifact_integrity_review: bool = True
    requires_scope_review: bool = True
    requires_donor_level_only: bool = True
    forbids_cell_level_split: bool = True
    requires_no_large_artifact_commit: bool = True
    requires_protocol_before_execution: bool = True
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
        raise Stage5FinalModelingHandoffDecisionError(
            f"{field_name} must not be empty."
        )
    if "\x00" in normalized:
        raise Stage5FinalModelingHandoffDecisionError(
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
        raise Stage5FinalModelingHandoffDecisionError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _normalize_completed_stage5_features(values: Sequence[object]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise Stage5FinalModelingHandoffDecisionError(
            "completed_stage5_features must be a sequence."
        )

    normalized = tuple(
        _clean_required_string(value, "completed_stage5_features item")
        for value in values
    )
    if normalized != STAGE5_PREVIOUS_FEATURES:
        expected = ", ".join(STAGE5_PREVIOUS_FEATURES)
        got = ", ".join(normalized)
        raise Stage5FinalModelingHandoffDecisionError(
            f"completed_stage5_features must exactly equal: {expected}; got: {got}."
        )

    return normalized


def validate_stage5_final_modeling_handoff_decision(
    decision: Stage5FinalModelingHandoffDecision,
) -> Stage5FinalModelingHandoffDecision:
    """Validate the metadata-only Stage 5-F005 final handoff decision."""

    current_stage = _validate_choice(decision.current_stage, ("Stage 5",), "current_stage")
    current_feature = _validate_choice(
        decision.current_feature,
        (STAGE5_CURRENT_FEATURE,),
        "current_feature",
    )
    stage5_status = _validate_choice(
        decision.stage5_status,
        ALLOWED_STAGE5_STATUSES,
        "stage5_status",
    )
    handoff_status = _validate_choice(
        decision.handoff_status,
        ALLOWED_HANDOFF_STATUSES,
        "handoff_status",
    )
    handoff_decision = _validate_choice(
        decision.handoff_decision,
        ALLOWED_HANDOFF_DECISIONS,
        "handoff_decision",
    )
    modeling_authorization_status = _validate_choice(
        decision.modeling_authorization_status,
        ALLOWED_MODELING_AUTHORIZATION_STATUSES,
        "modeling_authorization_status",
    )
    future_modeling_policy = _validate_choice(
        decision.future_modeling_policy,
        ALLOWED_FUTURE_MODELING_POLICIES,
        "future_modeling_policy",
    )
    completed_stage5_features = _normalize_completed_stage5_features(
        decision.completed_stage5_features
    )
    previous_audit_feature = _validate_choice(
        decision.previous_audit_feature,
        ("STAGE5-F004",),
        "previous_audit_feature",
    )
    previous_audit_status = _validate_choice(
        decision.previous_audit_status,
        (COMPLETED,),
        "previous_audit_status",
    )
    handoff_record_level = _validate_choice(
        decision.handoff_record_level,
        ALLOWED_RECORD_LEVELS,
        "handoff_record_level",
    )

    required_policy_values = {
        "split_policy": (decision.split_policy, DONOR_LEVEL_ONLY),
        "leakage_policy": (decision.leakage_policy, CELL_LEVEL_SPLIT_FORBIDDEN),
        "handoff_scope_policy": (decision.handoff_scope_policy, HANDOFF_ONLY_NO_EXECUTION),
        "artifact_loading_policy": (
            decision.artifact_loading_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "input_materialization_policy": (
            decision.input_materialization_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "label_creation_policy": (
            decision.label_creation_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "split_execution_policy": (
            decision.split_execution_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "aggregation_execution_policy": (
            decision.aggregation_execution_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "modeling_execution_policy": (
            decision.modeling_execution_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "prediction_generation_policy": (
            decision.prediction_generation_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "metric_computation_policy": (
            decision.metric_computation_policy,
            FUTURE_ONLY_NO_COMPUTATION,
        ),
        "external_validation_policy": (
            decision.external_validation_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "performance_claim_policy": (
            decision.performance_claim_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
    }
    for field_name, (value, expected) in required_policy_values.items():
        _validate_choice(value, ALLOWED_POLICIES, field_name)
        if value != expected:
            raise Stage5FinalModelingHandoffDecisionError(
                f"{field_name} must remain {expected}."
            )

    required_true_flags = {
        "requires_explicit_modeling_approval": decision.requires_explicit_modeling_approval,
        "requires_separate_execution_stage": decision.requires_separate_execution_stage,
        "requires_human_review_before_modeling": (
            decision.requires_human_review_before_modeling
        ),
        "requires_reproducibility_review": decision.requires_reproducibility_review,
        "requires_leakage_review": decision.requires_leakage_review,
        "requires_artifact_integrity_review": decision.requires_artifact_integrity_review,
        "requires_scope_review": decision.requires_scope_review,
        "requires_donor_level_only": decision.requires_donor_level_only,
        "forbids_cell_level_split": decision.forbids_cell_level_split,
        "requires_no_large_artifact_commit": decision.requires_no_large_artifact_commit,
        "requires_protocol_before_execution": decision.requires_protocol_before_execution,
    }
    disabled_required = sorted(
        name for name, value in required_true_flags.items() if not _as_bool(value)
    )
    if disabled_required:
        raise Stage5FinalModelingHandoffDecisionError(
            "required Stage 5 final handoff gates must remain enabled; disabled: "
            + ", ".join(disabled_required)
        )

    forbidden_flags = {
        "allow_real_artifact_loading": decision.allow_real_artifact_loading,
        "allow_npy_payload_loading": decision.allow_npy_payload_loading,
        "allow_embedding_vector_parsing": decision.allow_embedding_vector_parsing,
        "allow_input_materialization": decision.allow_input_materialization,
        "allow_label_array_creation": decision.allow_label_array_creation,
        "allow_split_execution": decision.allow_split_execution,
        "allow_real_aggregation_execution": decision.allow_real_aggregation_execution,
        "allow_anndata_loading": decision.allow_anndata_loading,
        "allow_geneformer_execution": decision.allow_geneformer_execution,
        "allow_tokenizer_execution": decision.allow_tokenizer_execution,
        "allow_embedding_extraction": decision.allow_embedding_extraction,
        "allow_feature_extraction": decision.allow_feature_extraction,
        "allow_global_preprocessing": decision.allow_global_preprocessing,
        "allow_scaler_outside_fold": decision.allow_scaler_outside_fold,
        "allow_model_fitting": decision.allow_model_fitting,
        "allow_prediction_generation": decision.allow_prediction_generation,
        "allow_metric_computation": decision.allow_metric_computation,
        "allow_modeling": decision.allow_modeling,
        "modeling_authorization_granted": decision.modeling_authorization_granted,
        "modeling_allowed": decision.modeling_allowed,
        "training_allowed": decision.training_allowed,
        "external_validation_allowed": decision.external_validation_allowed,
        "performance_claims_allowed": decision.performance_claims_allowed,
        "performance_claims_added": decision.performance_claims_added,
    }
    enabled = sorted(name for name, value in forbidden_flags.items() if _as_bool(value))
    if enabled:
        raise Stage5FinalModelingHandoffDecisionError(
            "Stage 5-F005 does not grant artifact loading, execution, modeling, "
            "metrics, training, external validation, or performance claims; enabled: "
            + ", ".join(enabled)
        )

    return Stage5FinalModelingHandoffDecision(
        current_stage=current_stage,
        stage_name=_clean_required_string(decision.stage_name, "stage_name"),
        current_feature=current_feature,
        feature_name=_clean_required_string(decision.feature_name, "feature_name"),
        stage5_status=stage5_status,
        handoff_status=handoff_status,
        handoff_decision=handoff_decision,
        modeling_authorization_status=modeling_authorization_status,
        future_modeling_policy=future_modeling_policy,
        completed_stage5_features=completed_stage5_features,
        previous_audit_feature=previous_audit_feature,
        previous_audit_status=previous_audit_status,
        scope=_clean_required_string(decision.scope, "scope"),
        handoff_record_level=handoff_record_level,
        split_policy=DONOR_LEVEL_ONLY,
        leakage_policy=CELL_LEVEL_SPLIT_FORBIDDEN,
        handoff_scope_policy=HANDOFF_ONLY_NO_EXECUTION,
        artifact_loading_policy=PROHIBITED_UNTIL_EXPLICIT_GATE,
        input_materialization_policy=PROHIBITED_UNTIL_EXPLICIT_GATE,
        label_creation_policy=PROHIBITED_UNTIL_EXPLICIT_GATE,
        split_execution_policy=PROHIBITED_UNTIL_EXPLICIT_GATE,
        aggregation_execution_policy=PROHIBITED_UNTIL_EXPLICIT_GATE,
        modeling_execution_policy=PROHIBITED_UNTIL_EXPLICIT_GATE,
        prediction_generation_policy=PROHIBITED_UNTIL_EXPLICIT_GATE,
        metric_computation_policy=FUTURE_ONLY_NO_COMPUTATION,
        external_validation_policy=PROHIBITED_UNTIL_EXPLICIT_GATE,
        performance_claim_policy=PROHIBITED_UNTIL_EXPLICIT_GATE,
        requires_explicit_modeling_approval=True,
        requires_separate_execution_stage=True,
        requires_human_review_before_modeling=True,
        requires_reproducibility_review=True,
        requires_leakage_review=True,
        requires_artifact_integrity_review=True,
        requires_scope_review=True,
        requires_donor_level_only=True,
        forbids_cell_level_split=True,
        requires_no_large_artifact_commit=True,
        requires_protocol_before_execution=True,
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
        notes=str(decision.notes).strip(),
    )


def stage5_final_modeling_handoff_decision_from_mapping(
    values: Mapping[str, Any],
) -> Stage5FinalModelingHandoffDecision:
    """Build and validate a Stage 5-F005 final handoff decision from a mapping."""

    data = stage5_final_modeling_handoff_decision_to_dict(
        Stage5FinalModelingHandoffDecision()
    )
    data.update(values)
    return validate_stage5_final_modeling_handoff_decision(
        Stage5FinalModelingHandoffDecision(**data)
    )


def stage5_final_modeling_handoff_decision_to_dict(
    decision: Stage5FinalModelingHandoffDecision,
) -> dict[str, Any]:
    """Serialize a validated Stage 5-F005 final handoff decision."""

    validated = validate_stage5_final_modeling_handoff_decision(decision)
    serialized = asdict(validated)
    serialized["completed_stage5_features"] = list(validated.completed_stage5_features)
    return serialized


def stage5_final_modeling_handoff_summary(
    decision: Stage5FinalModelingHandoffDecision,
) -> dict[str, Any]:
    """Return a compact summary of the Stage 5-F005 handoff decision."""

    validated = validate_stage5_final_modeling_handoff_decision(decision)
    return {
        "current_stage": validated.current_stage,
        "current_feature": validated.current_feature,
        "handoff_status": validated.handoff_status,
        "handoff_decision": validated.handoff_decision,
        "modeling_authorization_status": validated.modeling_authorization_status,
        "future_modeling_policy": validated.future_modeling_policy,
        "previous_audit_feature": validated.previous_audit_feature,
        "handoff_record_level": validated.handoff_record_level,
        "split_policy": validated.split_policy,
        "leakage_policy": validated.leakage_policy,
        "requires_separate_execution_stage": True,
        "modeling_authorization_granted": False,
        "modeling_allowed": False,
        "training_allowed": False,
        "performance_claims_allowed": False,
        "performance_claims_added": False,
    }
