"""Stage 4 final closeout and modeling handoff decision.

This module records a metadata-only Stage 4 closeout decision. It confirms that
the real-artifact validation, donor-level aggregation planning, split-manifest
validation, evaluation-input readiness, and pre-modeling audit gates are
complete.

The handoff decision does not authorize modeling inside Stage 4. Modeling,
training, prediction generation, metric computation, external validation, and
performance claims remain blocked unless a separate modeling stage is explicitly
approved.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any


STAGE4_FINAL_FEATURE = "STAGE4-F006"
COMPLETED = "completed"

F001 = "STAGE4-F001"
F002 = "STAGE4-F002"
F003 = "STAGE4-F003"
F004 = "STAGE4-F004"
F005 = "STAGE4-F005"
REQUIRED_COMPLETED_FEATURES = (F001, F002, F003, F004, F005)

SEPARATE_MODELING_STAGE_REQUIRED = "separate_modeling_stage_required"
BLOCKED_PENDING_HUMAN_REVIEW = "blocked_pending_human_review"
BLOCKED = "blocked"
ALLOWED_HANDOFF_DECISIONS = (
    SEPARATE_MODELING_STAGE_REQUIRED,
    BLOCKED_PENDING_HUMAN_REVIEW,
    BLOCKED,
)


class Stage4ModelingHandoffDecisionError(ValueError):
    """Raised when the Stage 4 handoff decision is unsafe or incomplete."""


@dataclass(frozen=True)
class Stage4ModelingHandoffDecision:
    """Metadata-only final Stage 4 handoff decision.

    The default decision allows planning a separate modeling stage but does not
    grant modeling permission in Stage 4.
    """

    current_feature: str = STAGE4_FINAL_FEATURE
    stage4_status: str = COMPLETED
    decision_status: str = COMPLETED
    handoff_decision: str = SEPARATE_MODELING_STAGE_REQUIRED
    completed_features: tuple[str, ...] = REQUIRED_COMPLETED_FEATURES
    artifact_validation_status: str = COMPLETED
    aggregation_plan_status: str = COMPLETED
    split_manifest_validation_status: str = COMPLETED
    evaluation_input_readiness_status: str = COMPLETED
    pre_modeling_audit_status: str = COMPLETED
    next_phase: str = "separate_modeling_stage_requires_explicit_approval"
    next_phase_name: str = "Modeling stage planning requires explicit approval"
    requires_separate_modeling_stage: bool = True
    requires_new_branch_for_modeling: bool = True
    requires_explicit_modeling_approval: bool = True
    requires_human_review_before_modeling: bool = True
    requires_reproducibility_review: bool = True
    requires_leakage_review: bool = True
    requires_artifact_integrity_review: bool = True
    requires_scope_review: bool = True
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
        raise Stage4ModelingHandoffDecisionError(f"{field_name} must not be empty.")
    if "\x00" in normalized:
        raise Stage4ModelingHandoffDecisionError(
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
        raise Stage4ModelingHandoffDecisionError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _normalize_completed_features(values: Sequence[object]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise Stage4ModelingHandoffDecisionError(
            "completed_features must be a sequence."
        )

    normalized = tuple(
        _clean_required_string(value, "completed_features item") for value in values
    )
    if normalized != REQUIRED_COMPLETED_FEATURES:
        expected = ", ".join(REQUIRED_COMPLETED_FEATURES)
        got = ", ".join(normalized)
        raise Stage4ModelingHandoffDecisionError(
            f"completed_features must exactly equal: {expected}; got: {got}."
        )

    return normalized


def validate_stage4_modeling_handoff_decision(
    decision: Stage4ModelingHandoffDecision,
) -> Stage4ModelingHandoffDecision:
    """Validate the final Stage 4 metadata-only handoff decision."""

    current_feature = _validate_choice(
        decision.current_feature,
        (STAGE4_FINAL_FEATURE,),
        "current_feature",
    )
    stage4_status = _validate_choice(
        decision.stage4_status,
        (COMPLETED,),
        "stage4_status",
    )
    decision_status = _validate_choice(
        decision.decision_status,
        (COMPLETED,),
        "decision_status",
    )
    handoff_decision = _validate_choice(
        decision.handoff_decision,
        ALLOWED_HANDOFF_DECISIONS,
        "handoff_decision",
    )

    completed_features = _normalize_completed_features(decision.completed_features)

    upstream_statuses = {
        "artifact_validation_status": decision.artifact_validation_status,
        "aggregation_plan_status": decision.aggregation_plan_status,
        "split_manifest_validation_status": decision.split_manifest_validation_status,
        "evaluation_input_readiness_status": (
            decision.evaluation_input_readiness_status
        ),
        "pre_modeling_audit_status": decision.pre_modeling_audit_status,
    }
    for field_name, status in upstream_statuses.items():
        _validate_choice(status, (COMPLETED,), field_name)

    required_true_flags = {
        "requires_separate_modeling_stage": decision.requires_separate_modeling_stage,
        "requires_new_branch_for_modeling": decision.requires_new_branch_for_modeling,
        "requires_explicit_modeling_approval": (
            decision.requires_explicit_modeling_approval
        ),
        "requires_human_review_before_modeling": (
            decision.requires_human_review_before_modeling
        ),
        "requires_reproducibility_review": decision.requires_reproducibility_review,
        "requires_leakage_review": decision.requires_leakage_review,
        "requires_artifact_integrity_review": (
            decision.requires_artifact_integrity_review
        ),
        "requires_scope_review": decision.requires_scope_review,
    }
    disabled_required = sorted(
        name for name, value in required_true_flags.items() if not _as_bool(value)
    )
    if disabled_required:
        raise Stage4ModelingHandoffDecisionError(
            "required Stage 4 handoff gates must remain enabled; disabled: "
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
        "modeling_authorization_granted": decision.modeling_authorization_granted,
        "modeling_allowed": decision.modeling_allowed,
        "training_allowed": decision.training_allowed,
        "external_validation_allowed": decision.external_validation_allowed,
        "performance_claims_allowed": decision.performance_claims_allowed,
        "performance_claims_added": decision.performance_claims_added,
    }
    enabled = sorted(name for name, value in forbidden_flags.items() if _as_bool(value))
    if enabled:
        raise Stage4ModelingHandoffDecisionError(
            "Stage 4 final closeout does not grant artifact loading, input "
            "materialization, split execution, modeling, metrics, training, "
            "external validation, or performance claims; enabled: "
            + ", ".join(enabled)
        )

    return Stage4ModelingHandoffDecision(
        current_feature=current_feature,
        stage4_status=stage4_status,
        decision_status=decision_status,
        handoff_decision=handoff_decision,
        completed_features=completed_features,
        artifact_validation_status=COMPLETED,
        aggregation_plan_status=COMPLETED,
        split_manifest_validation_status=COMPLETED,
        evaluation_input_readiness_status=COMPLETED,
        pre_modeling_audit_status=COMPLETED,
        next_phase=_clean_required_string(decision.next_phase, "next_phase"),
        next_phase_name=_clean_required_string(
            decision.next_phase_name,
            "next_phase_name",
        ),
        requires_separate_modeling_stage=True,
        requires_new_branch_for_modeling=True,
        requires_explicit_modeling_approval=True,
        requires_human_review_before_modeling=True,
        requires_reproducibility_review=True,
        requires_leakage_review=True,
        requires_artifact_integrity_review=True,
        requires_scope_review=True,
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
        modeling_authorization_granted=False,
        modeling_allowed=False,
        training_allowed=False,
        external_validation_allowed=False,
        performance_claims_allowed=False,
        performance_claims_added=False,
        notes=str(decision.notes).strip(),
    )


def stage4_modeling_handoff_decision_from_mapping(
    data: Mapping[str, Any],
) -> Stage4ModelingHandoffDecision:
    """Build and validate a Stage 4 handoff decision from mapping data."""

    return validate_stage4_modeling_handoff_decision(
        Stage4ModelingHandoffDecision(
            current_feature=data.get("current_feature", STAGE4_FINAL_FEATURE),
            stage4_status=data.get("stage4_status", COMPLETED),
            decision_status=data.get("decision_status", COMPLETED),
            handoff_decision=data.get(
                "handoff_decision",
                SEPARATE_MODELING_STAGE_REQUIRED,
            ),
            completed_features=tuple(
                data.get("completed_features", REQUIRED_COMPLETED_FEATURES)
            ),
            artifact_validation_status=data.get(
                "artifact_validation_status",
                COMPLETED,
            ),
            aggregation_plan_status=data.get("aggregation_plan_status", COMPLETED),
            split_manifest_validation_status=data.get(
                "split_manifest_validation_status",
                COMPLETED,
            ),
            evaluation_input_readiness_status=data.get(
                "evaluation_input_readiness_status",
                COMPLETED,
            ),
            pre_modeling_audit_status=data.get(
                "pre_modeling_audit_status",
                COMPLETED,
            ),
            next_phase=data.get(
                "next_phase",
                "separate_modeling_stage_requires_explicit_approval",
            ),
            next_phase_name=data.get(
                "next_phase_name",
                "Modeling stage planning requires explicit approval",
            ),
            requires_separate_modeling_stage=data.get(
                "requires_separate_modeling_stage",
                True,
            ),
            requires_new_branch_for_modeling=data.get(
                "requires_new_branch_for_modeling",
                True,
            ),
            requires_explicit_modeling_approval=data.get(
                "requires_explicit_modeling_approval",
                True,
            ),
            requires_human_review_before_modeling=data.get(
                "requires_human_review_before_modeling",
                True,
            ),
            requires_reproducibility_review=data.get(
                "requires_reproducibility_review",
                True,
            ),
            requires_leakage_review=data.get("requires_leakage_review", True),
            requires_artifact_integrity_review=data.get(
                "requires_artifact_integrity_review",
                True,
            ),
            requires_scope_review=data.get("requires_scope_review", True),
            allow_real_artifact_loading=data.get("allow_real_artifact_loading", False),
            allow_npy_payload_loading=data.get("allow_npy_payload_loading", False),
            allow_embedding_vector_parsing=data.get(
                "allow_embedding_vector_parsing",
                False,
            ),
            allow_input_materialization=data.get("allow_input_materialization", False),
            allow_label_array_creation=data.get("allow_label_array_creation", False),
            allow_split_execution=data.get("allow_split_execution", False),
            allow_real_aggregation_execution=data.get(
                "allow_real_aggregation_execution",
                False,
            ),
            allow_anndata_loading=data.get("allow_anndata_loading", False),
            allow_geneformer_execution=data.get("allow_geneformer_execution", False),
            allow_tokenizer_execution=data.get("allow_tokenizer_execution", False),
            allow_embedding_extraction=data.get("allow_embedding_extraction", False),
            allow_feature_extraction=data.get("allow_feature_extraction", False),
            allow_global_preprocessing=data.get("allow_global_preprocessing", False),
            allow_scaler_outside_fold=data.get("allow_scaler_outside_fold", False),
            allow_model_fitting=data.get("allow_model_fitting", False),
            allow_prediction_generation=data.get("allow_prediction_generation", False),
            allow_metric_computation=data.get("allow_metric_computation", False),
            modeling_authorization_granted=data.get(
                "modeling_authorization_granted",
                False,
            ),
            modeling_allowed=data.get("modeling_allowed", False),
            training_allowed=data.get("training_allowed", False),
            external_validation_allowed=data.get("external_validation_allowed", False),
            performance_claims_allowed=data.get(
                "performance_claims_allowed",
                False,
            ),
            performance_claims_added=data.get("performance_claims_added", False),
            notes=data.get("notes", ""),
        )
    )


def stage4_modeling_handoff_decision_to_dict(
    decision: Stage4ModelingHandoffDecision,
) -> dict[str, Any]:
    """Validate and serialize a Stage 4 handoff decision."""

    validated = validate_stage4_modeling_handoff_decision(decision)
    serialized = asdict(validated)
    serialized["completed_features"] = list(validated.completed_features)
    return serialized


def stage4_handoff_summary(
    decision: Stage4ModelingHandoffDecision,
) -> dict[str, Any]:
    """Summarize Stage 4 closeout without granting modeling permission."""

    validated = validate_stage4_modeling_handoff_decision(decision)
    return {
        "current_feature": validated.current_feature,
        "stage4_status": validated.stage4_status,
        "decision_status": validated.decision_status,
        "handoff_decision": validated.handoff_decision,
        "completed_features": list(validated.completed_features),
        "requires_separate_modeling_stage": True,
        "requires_explicit_modeling_approval": True,
        "modeling_authorization_granted": False,
        "modeling_allowed": False,
        "training_allowed": False,
        "performance_claims_allowed": False,
        "performance_claims_added": False,
        "next_phase": validated.next_phase,
    }
