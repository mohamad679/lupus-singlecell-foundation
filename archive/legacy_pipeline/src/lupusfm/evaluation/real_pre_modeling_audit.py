"""Stage 4 real pre-modeling audit gate.

This module validates a metadata-only pre-modeling audit gate for the real
donor-level Stage 4 workflow. It checks that upstream Stage 4 metadata contracts
are complete and that modeling, training, metric computation, prediction
generation, and performance claims remain blocked. It does not load .npy
payloads, materialize evaluation arrays, fit models, compute metrics, train
models, perform external validation, or add performance claims.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

from lupusfm.evaluation.real_input_readiness import COMPLETED


STAGE4_CURRENT_FEATURE = "STAGE4-F005"

PENDING = "pending"
VALIDATED = "validated"
BLOCKED = "blocked"
ALLOWED_AUDIT_STATUSES = (PENDING, VALIDATED, BLOCKED)

F001 = "STAGE4-F001"
F002 = "STAGE4-F002"
F003 = "STAGE4-F003"
F004 = "STAGE4-F004"
REQUIRED_COMPLETED_FEATURES = (F001, F002, F003, F004)

F006 = "STAGE4-F006"
NEXT_STAGE4_FEATURE = F006

REVIEW_REQUIRED = "review_required"
ALLOWED_AUDIT_OUTCOMES = (REVIEW_REQUIRED, BLOCKED)


class RealPreModelingAuditGateError(ValueError):
    """Raised when the Stage 4-F005 pre-modeling audit gate is unsafe."""


@dataclass(frozen=True)
class RealPreModelingAuditGate:
    """Metadata-only pre-modeling audit gate.

    This gate does not grant modeling permission. It records whether the
    upstream metadata gates are complete and whether modeling-related actions
    remain blocked.
    """

    current_feature: str = STAGE4_CURRENT_FEATURE
    audit_status: str = PENDING
    audit_outcome: str = REVIEW_REQUIRED
    completed_features: tuple[str, ...] = REQUIRED_COMPLETED_FEATURES
    artifact_validation_status: str = COMPLETED
    aggregation_plan_status: str = COMPLETED
    split_manifest_validation_status: str = COMPLETED
    evaluation_input_readiness_status: str = COMPLETED
    next_feature: str = NEXT_STAGE4_FEATURE
    next_feature_name: str = "Stage 4 final closeout and modeling handoff decision"
    requires_human_review_before_modeling: bool = True
    requires_explicit_modeling_permission: bool = True
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
    allow_modeling: bool = False
    allow_training: bool = False
    allow_external_validation: bool = False
    performance_claims_added: bool = False
    notes: str = ""


def _clean_required_string(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise RealPreModelingAuditGateError(f"{field_name} must not be empty.")
    if "\x00" in normalized:
        raise RealPreModelingAuditGateError(
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
        raise RealPreModelingAuditGateError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _normalize_completed_features(values: Sequence[object]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise RealPreModelingAuditGateError("completed_features must be a sequence.")

    normalized = tuple(
        _clean_required_string(value, "completed_features item") for value in values
    )
    if normalized != REQUIRED_COMPLETED_FEATURES:
        expected = ", ".join(REQUIRED_COMPLETED_FEATURES)
        got = ", ".join(normalized)
        raise RealPreModelingAuditGateError(
            f"completed_features must exactly equal: {expected}; got: {got}."
        )

    return normalized


def validate_real_pre_modeling_audit_gate(
    gate: RealPreModelingAuditGate,
) -> RealPreModelingAuditGate:
    """Validate the metadata-only Stage 4-F005 pre-modeling audit gate."""

    current_feature = _validate_choice(
        gate.current_feature,
        (STAGE4_CURRENT_FEATURE,),
        "current_feature",
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
    next_feature = _validate_choice(
        gate.next_feature,
        (NEXT_STAGE4_FEATURE,),
        "next_feature",
    )

    completed_features = _normalize_completed_features(gate.completed_features)

    upstream_statuses = {
        "artifact_validation_status": gate.artifact_validation_status,
        "aggregation_plan_status": gate.aggregation_plan_status,
        "split_manifest_validation_status": gate.split_manifest_validation_status,
        "evaluation_input_readiness_status": gate.evaluation_input_readiness_status,
    }
    incomplete = sorted(
        name
        for name, value in upstream_statuses.items()
        if _validate_choice(value, (COMPLETED,), name) != COMPLETED
    )
    if incomplete:
        raise RealPreModelingAuditGateError(
            "upstream Stage 4 gates must be completed: " + ", ".join(incomplete)
        )

    required_true_flags = {
        "requires_human_review_before_modeling": gate.requires_human_review_before_modeling,
        "requires_explicit_modeling_permission": gate.requires_explicit_modeling_permission,
        "requires_reproducibility_review": gate.requires_reproducibility_review,
        "requires_leakage_review": gate.requires_leakage_review,
        "requires_artifact_integrity_review": gate.requires_artifact_integrity_review,
        "requires_scope_review": gate.requires_scope_review,
    }
    disabled_required = sorted(
        name for name, value in required_true_flags.items() if not _as_bool(value)
    )
    if disabled_required:
        raise RealPreModelingAuditGateError(
            "required pre-modeling audit gates must remain enabled; disabled: "
            + ", ".join(disabled_required)
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
        "allow_training": gate.allow_training,
        "allow_external_validation": gate.allow_external_validation,
        "performance_claims_added": gate.performance_claims_added,
    }
    enabled = sorted(name for name, value in forbidden_flags.items() if _as_bool(value))
    if enabled:
        raise RealPreModelingAuditGateError(
            "Stage 4-F005 keeps artifact loading, input materialization, split "
            "execution, modeling, metrics, training, external validation, and "
            "claims disabled; enabled: " + ", ".join(enabled)
        )

    return RealPreModelingAuditGate(
        current_feature=current_feature,
        audit_status=audit_status,
        audit_outcome=audit_outcome,
        completed_features=completed_features,
        artifact_validation_status=COMPLETED,
        aggregation_plan_status=COMPLETED,
        split_manifest_validation_status=COMPLETED,
        evaluation_input_readiness_status=COMPLETED,
        next_feature=next_feature,
        next_feature_name=_clean_required_string(
            gate.next_feature_name,
            "next_feature_name",
        ),
        requires_human_review_before_modeling=True,
        requires_explicit_modeling_permission=True,
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
        allow_modeling=False,
        allow_training=False,
        allow_external_validation=False,
        performance_claims_added=False,
        notes=str(gate.notes).strip(),
    )


def real_pre_modeling_audit_gate_from_mapping(
    data: Mapping[str, Any],
) -> RealPreModelingAuditGate:
    """Build and validate a Stage 4-F005 audit gate from mapping data."""

    return validate_real_pre_modeling_audit_gate(
        RealPreModelingAuditGate(
            current_feature=data.get("current_feature", STAGE4_CURRENT_FEATURE),
            audit_status=data.get("audit_status", PENDING),
            audit_outcome=data.get("audit_outcome", REVIEW_REQUIRED),
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
            next_feature=data.get("next_feature", NEXT_STAGE4_FEATURE),
            next_feature_name=data.get(
                "next_feature_name",
                "Stage 4 final closeout and modeling handoff decision",
            ),
            requires_human_review_before_modeling=data.get(
                "requires_human_review_before_modeling",
                True,
            ),
            requires_explicit_modeling_permission=data.get(
                "requires_explicit_modeling_permission",
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
            allow_modeling=data.get("allow_modeling", False),
            allow_training=data.get("allow_training", False),
            allow_external_validation=data.get("allow_external_validation", False),
            performance_claims_added=data.get("performance_claims_added", False),
            notes=data.get("notes", ""),
        )
    )


def real_pre_modeling_audit_gate_to_dict(
    gate: RealPreModelingAuditGate,
) -> dict[str, Any]:
    """Validate and serialize a Stage 4-F005 audit gate."""

    validated = validate_real_pre_modeling_audit_gate(gate)
    serialized = asdict(validated)
    serialized["completed_features"] = list(validated.completed_features)
    return serialized


def pre_modeling_audit_summary(gate: RealPreModelingAuditGate) -> dict[str, Any]:
    """Summarize audit gate status without granting modeling permission."""

    validated = validate_real_pre_modeling_audit_gate(gate)
    return {
        "current_feature": validated.current_feature,
        "audit_status": validated.audit_status,
        "audit_outcome": validated.audit_outcome,
        "completed_features": list(validated.completed_features),
        "requires_human_review_before_modeling": True,
        "requires_explicit_modeling_permission": True,
        "allow_modeling": False,
        "allow_metric_computation": False,
        "allow_training": False,
        "performance_claims_added": False,
        "next_feature": validated.next_feature,
    }
