"""Stage 5 donor-level execution contract approval.

This module validates a metadata-only donor-level execution contract approval
gate for Stage 5. It records the required donor-level contract constraints and
approval requirements only.

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

STAGE5_CURRENT_FEATURE = "STAGE5-F003"
STAGE5_PREVIOUS_FEATURES = ("STAGE5-F001", "STAGE5-F002")
STAGE5_NEXT_FEATURE = "STAGE5-F004"
STAGE5_NAME = "Stage 5 - Modeling stage approval and execution planning"
STAGE5_FEATURE_NAME = "Donor-level execution contract approval"
STAGE5_NEXT_FEATURE_NAME = "Pre-execution audit gate"

DONOR_LEVEL = "donor"
DONOR_LEVEL_ONLY = "donor_level_only"
CELL_LEVEL_SPLIT_FORBIDDEN = "cell_level_split_forbidden"
CONTRACT_REVIEW_ONLY_NO_EXECUTION = "contract_review_only_no_execution"
PROHIBITED_UNTIL_EXPLICIT_GATE = "prohibited_until_explicit_gate"
FUTURE_ONLY_NO_COMPUTATION = "future_only_no_computation"
NOT_GRANTED = "not_granted"
PENDING_CONTRACT_REVIEW = "pending_contract_review"
BLOCKED_PENDING_REVIEW = "blocked_pending_review"

ALLOWED_STAGE5_STATUSES = (IN_PROGRESS, BLOCKED)
ALLOWED_CONTRACT_STATUSES = (PENDING, IN_PROGRESS, BLOCKED)
ALLOWED_APPROVAL_DECISIONS = (
    NOT_GRANTED,
    PENDING_CONTRACT_REVIEW,
    BLOCKED_PENDING_REVIEW,
)
ALLOWED_RECORD_LEVELS = (DONOR_LEVEL,)
ALLOWED_CONTRACT_POLICIES = (
    DONOR_LEVEL_ONLY,
    CELL_LEVEL_SPLIT_FORBIDDEN,
    CONTRACT_REVIEW_ONLY_NO_EXECUTION,
    PROHIBITED_UNTIL_EXPLICIT_GATE,
    FUTURE_ONLY_NO_COMPUTATION,
)


class Stage5DonorLevelExecutionContractApprovalError(ValueError):
    """Raised when the Stage 5 donor-level execution contract is unsafe."""


@dataclass(frozen=True)
class Stage5DonorLevelExecutionContractApproval:
    """Metadata-only Stage 5-F003 donor-level execution contract approval.

    This gate reviews contract constraints only. It does not authorize runtime
    execution, model fitting, prediction generation, metric computation,
    training, external validation, or performance claims.
    """

    current_stage: str = "Stage 5"
    stage_name: str = STAGE5_NAME
    current_feature: str = STAGE5_CURRENT_FEATURE
    feature_name: str = STAGE5_FEATURE_NAME
    stage5_status: str = IN_PROGRESS
    contract_status: str = IN_PROGRESS
    contract_approval_decision: str = PENDING_CONTRACT_REVIEW
    completed_stage5_features: tuple[str, ...] = STAGE5_PREVIOUS_FEATURES
    previous_protocol_feature: str = "STAGE5-F002"
    previous_protocol_status: str = COMPLETED
    next_feature: str = STAGE5_NEXT_FEATURE
    next_feature_name: str = STAGE5_NEXT_FEATURE_NAME
    scope: str = "donor_level_contract_approval_only_no_execution"
    contract_record_level: str = DONOR_LEVEL
    contract_split_level: str = DONOR_LEVEL
    contract_label_level: str = DONOR_LEVEL
    contract_prediction_level: str = DONOR_LEVEL
    split_policy: str = DONOR_LEVEL_ONLY
    leakage_policy: str = CELL_LEVEL_SPLIT_FORBIDDEN
    contract_scope_policy: str = CONTRACT_REVIEW_ONLY_NO_EXECUTION
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
    requires_pre_execution_audit: bool = True
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
        raise Stage5DonorLevelExecutionContractApprovalError(
            f"{field_name} must not be empty."
        )
    if "\x00" in normalized:
        raise Stage5DonorLevelExecutionContractApprovalError(
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
        raise Stage5DonorLevelExecutionContractApprovalError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _normalize_completed_stage5_features(values: Sequence[object]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise Stage5DonorLevelExecutionContractApprovalError(
            "completed_stage5_features must be a sequence."
        )

    normalized = tuple(
        _clean_required_string(value, "completed_stage5_features item")
        for value in values
    )
    if normalized != STAGE5_PREVIOUS_FEATURES:
        expected = ", ".join(STAGE5_PREVIOUS_FEATURES)
        got = ", ".join(normalized)
        raise Stage5DonorLevelExecutionContractApprovalError(
            f"completed_stage5_features must exactly equal: {expected}; got: {got}."
        )

    return normalized


def validate_stage5_donor_level_execution_contract_approval(
    contract: Stage5DonorLevelExecutionContractApproval,
) -> Stage5DonorLevelExecutionContractApproval:
    """Validate the metadata-only Stage 5-F003 donor-level contract approval."""

    current_stage = _validate_choice(contract.current_stage, ("Stage 5",), "current_stage")
    current_feature = _validate_choice(
        contract.current_feature,
        (STAGE5_CURRENT_FEATURE,),
        "current_feature",
    )
    stage5_status = _validate_choice(
        contract.stage5_status,
        ALLOWED_STAGE5_STATUSES,
        "stage5_status",
    )
    contract_status = _validate_choice(
        contract.contract_status,
        ALLOWED_CONTRACT_STATUSES,
        "contract_status",
    )
    contract_approval_decision = _validate_choice(
        contract.contract_approval_decision,
        ALLOWED_APPROVAL_DECISIONS,
        "contract_approval_decision",
    )
    completed_stage5_features = _normalize_completed_stage5_features(
        contract.completed_stage5_features
    )
    previous_protocol_feature = _validate_choice(
        contract.previous_protocol_feature,
        ("STAGE5-F002",),
        "previous_protocol_feature",
    )
    previous_protocol_status = _validate_choice(
        contract.previous_protocol_status,
        (COMPLETED,),
        "previous_protocol_status",
    )
    next_feature = _validate_choice(
        contract.next_feature,
        (STAGE5_NEXT_FEATURE,),
        "next_feature",
    )

    record_level_fields = {
        "contract_record_level": contract.contract_record_level,
        "contract_split_level": contract.contract_split_level,
        "contract_label_level": contract.contract_label_level,
        "contract_prediction_level": contract.contract_prediction_level,
    }
    normalized_record_levels = {
        name: _validate_choice(value, ALLOWED_RECORD_LEVELS, name)
        for name, value in record_level_fields.items()
    }

    required_policy_values = {
        "split_policy": (contract.split_policy, DONOR_LEVEL_ONLY),
        "leakage_policy": (contract.leakage_policy, CELL_LEVEL_SPLIT_FORBIDDEN),
        "contract_scope_policy": (
            contract.contract_scope_policy,
            CONTRACT_REVIEW_ONLY_NO_EXECUTION,
        ),
        "artifact_loading_policy": (
            contract.artifact_loading_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "input_materialization_policy": (
            contract.input_materialization_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "label_creation_policy": (
            contract.label_creation_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "split_execution_policy": (
            contract.split_execution_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "aggregation_execution_policy": (
            contract.aggregation_execution_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "modeling_execution_policy": (
            contract.modeling_execution_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "prediction_generation_policy": (
            contract.prediction_generation_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "metric_computation_policy": (
            contract.metric_computation_policy,
            FUTURE_ONLY_NO_COMPUTATION,
        ),
        "external_validation_policy": (
            contract.external_validation_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
        "performance_claim_policy": (
            contract.performance_claim_policy,
            PROHIBITED_UNTIL_EXPLICIT_GATE,
        ),
    }
    for field_name, (value, expected) in required_policy_values.items():
        _validate_choice(value, ALLOWED_CONTRACT_POLICIES, field_name)
        if value != expected:
            raise Stage5DonorLevelExecutionContractApprovalError(
                f"{field_name} must remain {expected}."
            )

    required_true_flags = {
        "requires_explicit_modeling_approval": contract.requires_explicit_modeling_approval,
        "requires_human_review_before_modeling": contract.requires_human_review_before_modeling,
        "requires_reproducibility_review": contract.requires_reproducibility_review,
        "requires_leakage_review": contract.requires_leakage_review,
        "requires_artifact_integrity_review": contract.requires_artifact_integrity_review,
        "requires_scope_review": contract.requires_scope_review,
        "requires_donor_level_only": contract.requires_donor_level_only,
        "forbids_cell_level_split": contract.forbids_cell_level_split,
        "requires_no_large_artifact_commit": contract.requires_no_large_artifact_commit,
        "requires_protocol_before_execution": contract.requires_protocol_before_execution,
        "requires_separate_execution_gate": contract.requires_separate_execution_gate,
        "requires_pre_execution_audit": contract.requires_pre_execution_audit,
    }
    disabled_required = sorted(
        name for name, value in required_true_flags.items() if not _as_bool(value)
    )
    if disabled_required:
        raise Stage5DonorLevelExecutionContractApprovalError(
            "required Stage 5 donor-level execution contract gates must remain "
            "enabled; disabled: " + ", ".join(disabled_required)
        )

    forbidden_flags = {
        "allow_real_artifact_loading": contract.allow_real_artifact_loading,
        "allow_npy_payload_loading": contract.allow_npy_payload_loading,
        "allow_embedding_vector_parsing": contract.allow_embedding_vector_parsing,
        "allow_input_materialization": contract.allow_input_materialization,
        "allow_label_array_creation": contract.allow_label_array_creation,
        "allow_split_execution": contract.allow_split_execution,
        "allow_real_aggregation_execution": contract.allow_real_aggregation_execution,
        "allow_anndata_loading": contract.allow_anndata_loading,
        "allow_geneformer_execution": contract.allow_geneformer_execution,
        "allow_tokenizer_execution": contract.allow_tokenizer_execution,
        "allow_embedding_extraction": contract.allow_embedding_extraction,
        "allow_feature_extraction": contract.allow_feature_extraction,
        "allow_global_preprocessing": contract.allow_global_preprocessing,
        "allow_scaler_outside_fold": contract.allow_scaler_outside_fold,
        "allow_model_fitting": contract.allow_model_fitting,
        "allow_prediction_generation": contract.allow_prediction_generation,
        "allow_metric_computation": contract.allow_metric_computation,
        "allow_modeling": contract.allow_modeling,
        "modeling_authorization_granted": contract.modeling_authorization_granted,
        "modeling_allowed": contract.modeling_allowed,
        "training_allowed": contract.training_allowed,
        "external_validation_allowed": contract.external_validation_allowed,
        "performance_claims_allowed": contract.performance_claims_allowed,
        "performance_claims_added": contract.performance_claims_added,
    }
    enabled = sorted(name for name, value in forbidden_flags.items() if _as_bool(value))
    if enabled:
        raise Stage5DonorLevelExecutionContractApprovalError(
            "Stage 5-F003 does not grant artifact loading, input materialization, "
            "split execution, modeling, metrics, training, external validation, "
            "or performance claims; enabled: " + ", ".join(enabled)
        )

    return Stage5DonorLevelExecutionContractApproval(
        current_stage=current_stage,
        stage_name=_clean_required_string(contract.stage_name, "stage_name"),
        current_feature=current_feature,
        feature_name=_clean_required_string(contract.feature_name, "feature_name"),
        stage5_status=stage5_status,
        contract_status=contract_status,
        contract_approval_decision=contract_approval_decision,
        completed_stage5_features=completed_stage5_features,
        previous_protocol_feature=previous_protocol_feature,
        previous_protocol_status=previous_protocol_status,
        next_feature=next_feature,
        next_feature_name=_clean_required_string(
            contract.next_feature_name,
            "next_feature_name",
        ),
        scope=_clean_required_string(contract.scope, "scope"),
        contract_record_level=normalized_record_levels["contract_record_level"],
        contract_split_level=normalized_record_levels["contract_split_level"],
        contract_label_level=normalized_record_levels["contract_label_level"],
        contract_prediction_level=normalized_record_levels["contract_prediction_level"],
        split_policy=DONOR_LEVEL_ONLY,
        leakage_policy=CELL_LEVEL_SPLIT_FORBIDDEN,
        contract_scope_policy=CONTRACT_REVIEW_ONLY_NO_EXECUTION,
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
        requires_pre_execution_audit=True,
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
        notes=str(contract.notes).strip(),
    )


def stage5_donor_level_execution_contract_approval_from_mapping(
    values: Mapping[str, Any],
) -> Stage5DonorLevelExecutionContractApproval:
    """Build and validate a Stage 5-F003 donor-level contract from a mapping."""

    data = stage5_donor_level_execution_contract_approval_to_dict(
        Stage5DonorLevelExecutionContractApproval()
    )
    data.update(values)
    return validate_stage5_donor_level_execution_contract_approval(
        Stage5DonorLevelExecutionContractApproval(**data)
    )


def stage5_donor_level_execution_contract_approval_to_dict(
    contract: Stage5DonorLevelExecutionContractApproval,
) -> dict[str, Any]:
    """Serialize a validated Stage 5-F003 donor-level contract."""

    validated = validate_stage5_donor_level_execution_contract_approval(contract)
    serialized = asdict(validated)
    serialized["completed_stage5_features"] = list(validated.completed_stage5_features)
    return serialized


def stage5_donor_level_execution_contract_summary(
    contract: Stage5DonorLevelExecutionContractApproval,
) -> dict[str, Any]:
    """Return a compact summary of the Stage 5-F003 donor-level contract."""

    validated = validate_stage5_donor_level_execution_contract_approval(contract)
    return {
        "current_stage": validated.current_stage,
        "current_feature": validated.current_feature,
        "contract_status": validated.contract_status,
        "contract_approval_decision": validated.contract_approval_decision,
        "previous_protocol_feature": validated.previous_protocol_feature,
        "next_feature": validated.next_feature,
        "contract_record_level": validated.contract_record_level,
        "contract_split_level": validated.contract_split_level,
        "contract_label_level": validated.contract_label_level,
        "contract_prediction_level": validated.contract_prediction_level,
        "split_policy": validated.split_policy,
        "leakage_policy": validated.leakage_policy,
        "requires_pre_execution_audit": True,
        "modeling_authorization_granted": False,
        "modeling_allowed": False,
        "training_allowed": False,
        "performance_claims_allowed": False,
        "performance_claims_added": False,
    }
