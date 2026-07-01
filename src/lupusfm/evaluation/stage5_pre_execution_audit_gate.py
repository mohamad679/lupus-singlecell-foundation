"""Stage 5 pre-execution audit gate.

This module validates a metadata-only pre-execution audit gate for Stage 5. It
checks that Stage 5 planning and donor-level contract gates are complete and
that all runtime, modeling, metric, training, external validation, and
performance-claim actions remain blocked.

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

STAGE5_CURRENT_FEATURE = "STAGE5-F004"
STAGE5_PREVIOUS_FEATURES = ("STAGE5-F001", "STAGE5-F002", "STAGE5-F003")
STAGE5_NEXT_FEATURE = "STAGE5-F005"
STAGE5_NAME = "Stage 5 - Modeling stage approval and execution planning"
STAGE5_FEATURE_NAME = "Pre-execution audit gate"
STAGE5_NEXT_FEATURE_NAME = "Final Stage 5 modeling handoff decision"

REVIEW_REQUIRED = "review_required"
BLOCKED_PENDING_REVIEW = "blocked_pending_review"
NOT_GRANTED = "not_granted"

DONOR_LEVEL = "donor"
DONOR_LEVEL_ONLY = "donor_level_only"
CELL_LEVEL_SPLIT_FORBIDDEN = "cell_level_split_forbidden"
AUDIT_ONLY_NO_EXECUTION = "audit_only_no_execution"
PROHIBITED_UNTIL_EXPLICIT_GATE = "prohibited_until_explicit_gate"
FUTURE_ONLY_NO_COMPUTATION = "future_only_no_computation"

ALLOWED_STAGE5_STATUSES = (IN_PROGRESS, BLOCKED)
ALLOWED_AUDIT_STATUSES = (PENDING, IN_PROGRESS, BLOCKED)
ALLOWED_AUDIT_OUTCOMES = (REVIEW_REQUIRED, BLOCKED_PENDING_REVIEW, BLOCKED)
ALLOWED_MODELING_AUTHORIZATION_STATUSES = (NOT_GRANTED, BLOCKED_PENDING_REVIEW)
ALLOWED_RECORD_LEVELS = (DONOR_LEVEL,)
ALLOWED_AUDIT_POLICIES = (
    DONOR_LEVEL_ONLY,
    CELL_LEVEL_SPLIT_FORBIDDEN,
    AUDIT_ONLY_NO_EXECUTION,
    PROHIBITED_UNTIL_EXPLICIT_GATE,
    FUTURE_ONLY_NO_COMPUTATION,
)


class Stage5PreExecutionAuditGateError(ValueError):
    """Raised when the Stage 5 pre-execution audit gate is unsafe."""


@dataclass(frozen=True)
class Stage5PreExecutionAuditGate:
    """Metadata-only Stage 5-F004 pre-execution audit gate.

    This audit confirms readiness metadata only. It does not grant modeling
    authorization or permit runtime execution.
    """

    current_stage: str = "Stage 5"
    stage_name: str = STAGE5_NAME
    current_feature: str = STAGE5_CURRENT_FEATURE
    feature_name: str = STAGE5_FEATURE_NAME
    stage5_status: str = IN_PROGRESS
    audit_status: str = IN_PROGRESS
    audit_outcome: str = REVIEW_REQUIRED
    modeling_authorization_status: str = NOT_GRANTED
    completed_stage5_features: tuple[str, ...] = STAGE5_PREVIOUS_FEATURES
    previous_contract_feature: str = "STAGE5-F003"
    previous_contract_status: str = COMPLETED
    next_feature: str = STAGE5_NEXT_FEATURE
    next_feature_name: str = STAGE5_NEXT_FEATURE_NAME
    scope: str = "pre_execution_audit_only_no_execution"
    audit_record_level: str = DONOR_LEVEL
    split_policy: str = DONOR_LEVEL_ONLY
    leakage_policy: str = CELL_LEVEL_SPLIT_FORBIDDEN
    audit_scope_policy: str = AUDIT_ONLY_NO_EXECUTION
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
    requires_final_stage5_handoff_decision: bool = True
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
        raise Stage5PreExecutionAuditGateError(f"{field_name} must not be empty.")
    if "\x00" in normalized:
        raise Stage5PreExecutionAuditGateError(
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
        raise Stage5PreExecutionAuditGateError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _normalize_completed_stage5_features(values: Sequence[object]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise Stage5PreExecutionAuditGateError(
            "completed_stage5_features must be a sequence."
        )

    normalized = tuple(
        _clean_required_string(value, "completed_stage5_features item")
        for value in values
    )
    if normalized != STAGE5_PREVIOUS_FEATURES:
        expected = ", ".join(STAGE5_PREVIOUS_FEATURES)
        got = ", ".join(normalized)
        raise Stage5PreExecutionAuditGateError(
            f"completed_stage5_features must exactly equal: {expected}; got: {got}."
        )

    return normalized


def validate_stage5_pre_execution_audit_gate(
    gate: Stage5PreExecutionAuditGate,
) -> Stage5PreExecutionAuditGate:
    """Validate the metadata-only Stage 5-F004 pre-execution audit gate."""

    current_stage = _validate_choice(gate.current_stage, ("Stage 5",), "current_stage")
    current_feature = _validate_choice(
        gate.current_feature,
        (STAGE5_CURRENT_FEATURE,),
        "current_feature",
    )
    stage5_status = _validate_choice(
        gate.stage5_status,
        ALLOWED_STAGE5_STATUSES,
        "stage5_status",
    )
    audit_status = _validate_choice(
        gate.audit_status,
        ALLOWED_AUDIT_STATUSES,
        "audit_status",
    )
    audit_outcome = _validate_choice(
        gate.audit_outcome,
        ALLOWED_AUDIT_OUTCOMES,
        "audit_outcome",
    )
    modeling_authorization_status = _validate_choice(
        gate.modeling_authorization_status,
        ALLOWED_MODELING_AUTHORIZATION_STATUSES,
        "modeling_authorization_status",
    )
    completed_stage5_features = _normalize_completed_stage5_features(
        gate.completed_stage5_features
    )
    previous_contract_feature = _validate_choice(
        gate.previous_contract_feature,
        ("STAGE5-F003",),
        "previous_contract_feature",
    )
    previous_contract_status = _validate_choice(
        gate.previous_contract_status,
        (COMPLETED,),
        "previous_contract_status",
    )
    next_feature = _validate_choice(
        gate.next_feature,
        (STAGE5_NEXT_FEATURE,),
        "next_feature",
    )
    audit_record_level = _validate_choice(
        gate.audit_record_level,
        ALLOWED_RECORD_LEVELS,
        "audit_record_level",
    )

    required_policy_values = {
        "split_policy": (gate.split_policy, DONOR_LEVEL_ONLY),
        "leakage_policy": (gate.leakage_policy, CELL_LEVEL_SPLIT_FORBIDDEN),
        "audit_scope_policy": (gate.audit_scope_policy, AUDIT_ONLY_NO_EXECUTION),
        "artifact_loading_policy": (
            gate.artifact_loading_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "input_materialization_policy": (
            gate.input_materialization_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "label_creation_policy": (
            gate.label_creation_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "split_execution_policy": (
            gate.split_execution_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "aggregation_execution_policy": (
            gate.aggregation_execution_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "modeling_execution_policy": (
            gate.modeling_execution_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "prediction_generation_policy": (
            gate.prediction_generation_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "metric_computation_policy": (
            gate.metric_computation_policy,
            FUTURE_ONLY_NO_COMPUTATION,
        ),
        "external_validation_policy": (
            gate.external_validation_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "performance_claim_policy": (
            gate.performance_claim_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
    }
    for field_name, (value, expected) in required_policy_values.items():
        _validate_choice(value, ALLOWED_AUDIT_POLICIES, field_name)
        if value != expected:
            raise Stage5PreExecutionAuditGateError(
                f"{field_name} must remain {expected}."
            )

    required_true_flags = {
        "requires_explicit_modeling_approval": gate.requires_explicit_modeling_approval,
        "requires_human_review_before_modeling": gate.requires_human_review_before_modeling,
        "requires_reproducibility_review": gate.requires_reproducibility_review,
        "requires_leakage_review": gate.requires_leakage_review,
        "requires_artifact_integrity_review": gate.requires_artifact_integrity_review,
        "requires_scope_review": gate.requires_scope_review,
        "requires_donor_level_only": gate.requires_donor_level_only,
        "forbids_cell_level_split": gate.forbids_cell_level_split,
        "requires_no_large_artifact_commit": gate.requires_no_large_artifact_commit,
        "requires_protocol_before_execution": gate.requires_protocol_before_execution,
        "requires_separate_execution_gate": gate.requires_separate_execution_gate,
        "requires_final_stage5_handoff_decision": (
            gate.requires_final_stage5_handoff_decision
        ),
    }
    disabled_required = sorted(
        name for name, value in required_true_flags.items() if not _as_bool(value)
    )
    if disabled_required:
        raise Stage5PreExecutionAuditGateError(
            "required Stage 5 pre-execution audit gates must remain enabled; "
            "disabled: " + ", ".join(disabled_required)
        )

    forbidden_flags = {
        "allow_real_artifact_loading": gate.allow_real_artifact_loading,
        "allow_npy_payload_loading": gate.allow_npy_payload_loading,
        "allow_embedding_vector_parsing": gate.allow_embedding_vector_parsing,
        "allow_input_materialization": gate.allow_input_materialization,
        "allow_label_array_creation": gate.allow_label_array_creation,
        "allow_split_execution": gate.allow_split_execution,
        "allow_real_aggregation_execution": gate.allow_real_aggregation_execution,
        "allow_anndata_loading": gate.allow_anndata_loading,
        "allow_geneformer_execution": gate.allow_geneformer_execution,
        "allow_tokenizer_execution": gate.allow_tokenizer_execution,
        "allow_embedding_extraction": gate.allow_embedding_extraction,
        "allow_feature_extraction": gate.allow_feature_extraction,
        "allow_global_preprocessing": gate.allow_global_preprocessing,
        "allow_scaler_outside_fold": gate.allow_scaler_outside_fold,
        "allow_model_fitting": gate.allow_model_fitting,
        "allow_prediction_generation": gate.allow_prediction_generation,
        "allow_metric_computation": gate.allow_metric_computation,
        "allow_modeling": gate.allow_modeling,
        "modeling_authorization_granted": gate.modeling_authorization_granted,
        "modeling_allowed": gate.modeling_allowed,
        "training_allowed": gate.training_allowed,
        "external_validation_allowed": gate.external_validation_allowed,
        "performance_claims_allowed": gate.performance_claims_allowed,
        "performance_claims_added": gate.performance_claims_added,
    }
    enabled = sorted(name for name, value in forbidden_flags.items() if _as_bool(value))
    if enabled:
        raise Stage5PreExecutionAuditGateError(
            "Stage 5-F004 does not grant artifact loading, input materialization, "
            "split execution, modeling, metrics, training, external validation, "
            "or performance claims; enabled: " + ", ".join(enabled)
        )

    return Stage5PreExecutionAuditGate(
        current_stage=current_stage,
        stage_name=_clean_required_string(gate.stage_name, "stage_name"),
        current_feature=current_feature,
        feature_name=_clean_required_string(gate.feature_name, "feature_name"),
        stage5_status=stage5_status,
        audit_status=audit_status,
        audit_outcome=audit_outcome,
        modeling_authorization_status=modeling_authorization_status,
        completed_stage5_features=completed_stage5_features,
        previous_contract_feature=previous_contract_feature,
        previous_contract_status=previous_contract_status,
        next_feature=next_feature,
        next_feature_name=_clean_required_string(
            gate.next_feature_name,
            "next_feature_name",
        ),
        scope=_clean_required_string(gate.scope, "scope"),
        audit_record_level=audit_record_level,
        split_policy=DONOR_LEVEL_ONLY,
        leakage_policy=CELL_LEVEL_SPLIT_FORBIDDEN,
        audit_scope_policy=AUDIT_ONLY_NO_EXECUTION,
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
        requires_final_stage5_handoff_decision=True,
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
        notes=str(gate.notes).strip(),
    )


def stage5_pre_execution_audit_gate_from_mapping(
    values: Mapping[str, Any],
) -> Stage5PreExecutionAuditGate:
    """Build and validate a Stage 5-F004 pre-execution audit gate from a mapping."""

    data = stage5_pre_execution_audit_gate_to_dict(Stage5PreExecutionAuditGate())
    data.update(values)
    return validate_stage5_pre_execution_audit_gate(
        Stage5PreExecutionAuditGate(**data)
    )


def stage5_pre_execution_audit_gate_to_dict(
    gate: Stage5PreExecutionAuditGate,
) -> dict[str, Any]:
    """Serialize a validated Stage 5-F004 pre-execution audit gate."""

    validated = validate_stage5_pre_execution_audit_gate(gate)
    serialized = asdict(validated)
    serialized["completed_stage5_features"] = list(validated.completed_stage5_features)
    return serialized


def stage5_pre_execution_audit_summary(
    gate: Stage5PreExecutionAuditGate,
) -> dict[str, Any]:
    """Return a compact summary of the Stage 5-F004 audit gate."""

    validated = validate_stage5_pre_execution_audit_gate(gate)
    return {
        "current_stage": validated.current_stage,
        "current_feature": validated.current_feature,
        "audit_status": validated.audit_status,
        "audit_outcome": validated.audit_outcome,
        "modeling_authorization_status": validated.modeling_authorization_status,
        "previous_contract_feature": validated.previous_contract_feature,
        "next_feature": validated.next_feature,
        "audit_record_level": validated.audit_record_level,
        "split_policy": validated.split_policy,
        "leakage_policy": validated.leakage_policy,
        "requires_final_stage5_handoff_decision": True,
        "modeling_authorization_granted": False,
        "modeling_allowed": False,
        "training_allowed": False,
        "performance_claims_allowed": False,
        "performance_claims_added": False,
    }
