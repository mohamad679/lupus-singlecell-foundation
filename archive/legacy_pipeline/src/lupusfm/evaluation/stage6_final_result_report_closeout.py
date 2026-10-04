"""Stage 6 final result report and closeout.

This module validates the STAGE6-F007 final closeout contract.

It records what Stage 6 completed:
- controlled donor-level authorization
- real artifact access/integrity gate
- donor-level input materialization contract
- split/leakage-control contract
- controlled in-memory baseline fitting
- controlled in-memory prediction and metric computation

It does not add real-cohort performance claims, write report artifacts, load
.npy payloads, parse embedding vectors from disk, train models, perform
external validation, or claim scientific validity beyond the explicitly
documented in-memory execution scope.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, fields
from typing import Any


COMPLETED = "completed"

STAGE6_CURRENT_FEATURE = "STAGE6-F007"
STAGE6_COMPLETE_FEATURE = "STAGE6-COMPLETE"
STAGE6_NAME = "Stage 6 - Controlled donor-level modeling execution"
STAGE6_FEATURE_NAME = "Stage 6 final result report and closeout"

STAGE6_COMPLETED_FEATURES = (
    "STAGE6-F001",
    "STAGE6-F002",
    "STAGE6-F003",
    "STAGE6-F004",
    "STAGE6-F005",
    "STAGE6-F006",
    "STAGE6-F007",
)
REQUIRED_PRIOR_FEATURES = (
    "STAGE6-F001",
    "STAGE6-F002",
    "STAGE6-F003",
    "STAGE6-F004",
    "STAGE6-F005",
    "STAGE6-F006",
)
REQUIRED_CLOSEOUT_SECTIONS = (
    "authorization_summary",
    "artifact_access_integrity_summary",
    "input_materialization_summary",
    "split_leakage_control_summary",
    "controlled_baseline_execution_summary",
    "prediction_metric_scope_summary",
    "safety_limitations_summary",
    "next_research_handoff_summary",
)
REQUIRED_FINAL_LIMITATIONS = (
    "no_real_cohort_performance_claim",
    "no_external_validation_performed",
    "no_prediction_or_metric_artifact_written",
    "no_npy_payload_loaded",
    "no_embedding_vector_parsed_from_disk",
    "no_model_artifact_persisted",
    "in_memory_execution_scope_only",
)

FINAL_CLOSEOUT_COMPLETED = "stage6_final_result_report_closeout_completed"
FINAL_REPORT_SCOPE = "stage6_final_report_closeout_no_real_performance_claims"
DONOR_LEVEL = "donor"
IN_MEMORY_ONLY = "in_memory_only"
NO_STAGE7_REQUIRED = "no_stage7_required"


class Stage6FinalResultReportCloseoutError(ValueError):
    """Raised when Stage 6 final closeout metadata is unsafe."""


@dataclass(frozen=True)
class Stage6FinalResultReportCloseout:
    """Metadata-only final closeout for Stage 6."""

    current_stage: str = "Stage 6"
    stage_name: str = STAGE6_NAME
    current_feature: str = STAGE6_CURRENT_FEATURE
    feature_name: str = STAGE6_FEATURE_NAME
    closeout_feature: str = "STAGE6-F007-CLOSEOUT"
    closeout_status: str = COMPLETED
    closeout_decision: str = FINAL_CLOSEOUT_COMPLETED
    branch: str = "chore/stage6-final-result-report-closeout"
    previous_feature: str = "STAGE6-F006"
    previous_feature_status: str = COMPLETED
    completed_stage6_features: tuple[str, ...] = STAGE6_COMPLETED_FEATURES
    required_prior_features: tuple[str, ...] = REQUIRED_PRIOR_FEATURES
    required_closeout_sections: tuple[str, ...] = REQUIRED_CLOSEOUT_SECTIONS
    required_final_limitations: tuple[str, ...] = REQUIRED_FINAL_LIMITATIONS
    final_stage_status: str = COMPLETED
    final_current_feature: str = STAGE6_COMPLETE_FEATURE
    scope: str = FINAL_REPORT_SCOPE
    record_level: str = DONOR_LEVEL
    execution_scope: str = IN_MEMORY_ONLY
    stage7_policy: str = NO_STAGE7_REQUIRED
    prediction_metric_scope: str = "in_memory_donor_level_predictions_only"
    report_artifact_policy: str = "no_report_artifact_written"
    performance_claim_policy: str = "no_real_cohort_performance_claim"
    external_validation_policy: str = "not_performed"
    allow_final_report_metadata: bool = True
    allow_stage6_closeout: bool = True
    allow_next_research_handoff_summary: bool = True
    require_all_stage6_features_completed: bool = True
    require_metric_scope_documented: bool = True
    require_limitations_documented: bool = True
    require_no_stage7: bool = True
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
    allow_report_artifact_write: bool = False
    external_validation_allowed: bool = False
    allow_external_validation: bool = False
    performance_claims_allowed: bool = False
    performance_claims_added: bool = False
    notes: str = ""


def _clean_required_string(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise Stage6FinalResultReportCloseoutError(
            f"{field_name} must not be empty."
        )
    if "\x00" in normalized:
        raise Stage6FinalResultReportCloseoutError(
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
        raise Stage6FinalResultReportCloseoutError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )
    return normalized


def _normalize_exact_sequence(
    values: Sequence[object],
    expected: tuple[str, ...],
    field_name: str,
) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise Stage6FinalResultReportCloseoutError(
            f"{field_name} must be a sequence."
        )
    normalized = tuple(
        _clean_required_string(value, f"{field_name} item") for value in values
    )
    if normalized != expected:
        raise Stage6FinalResultReportCloseoutError(
            f"{field_name} must exactly match the Stage 6 final closeout contract."
        )
    return normalized


def validate_stage6_final_result_report_closeout(
    closeout: Stage6FinalResultReportCloseout,
) -> Stage6FinalResultReportCloseout:
    """Validate Stage 6 final closeout metadata and safety locks."""

    current_stage = _validate_choice(closeout.current_stage, ("Stage 6",), "current_stage")
    current_feature = _validate_choice(
        closeout.current_feature,
        (STAGE6_CURRENT_FEATURE,),
        "current_feature",
    )
    closeout_feature = _validate_choice(
        closeout.closeout_feature,
        ("STAGE6-F007-CLOSEOUT",),
        "closeout_feature",
    )
    closeout_status = _validate_choice(
        closeout.closeout_status,
        (COMPLETED,),
        "closeout_status",
    )
    closeout_decision = _validate_choice(
        closeout.closeout_decision,
        (FINAL_CLOSEOUT_COMPLETED,),
        "closeout_decision",
    )
    previous_feature = _validate_choice(
        closeout.previous_feature,
        ("STAGE6-F006",),
        "previous_feature",
    )
    previous_feature_status = _validate_choice(
        closeout.previous_feature_status,
        (COMPLETED,),
        "previous_feature_status",
    )
    completed_stage6_features = _normalize_exact_sequence(
        closeout.completed_stage6_features,
        STAGE6_COMPLETED_FEATURES,
        "completed_stage6_features",
    )
    required_prior_features = _normalize_exact_sequence(
        closeout.required_prior_features,
        REQUIRED_PRIOR_FEATURES,
        "required_prior_features",
    )
    required_closeout_sections = _normalize_exact_sequence(
        closeout.required_closeout_sections,
        REQUIRED_CLOSEOUT_SECTIONS,
        "required_closeout_sections",
    )
    required_final_limitations = _normalize_exact_sequence(
        closeout.required_final_limitations,
        REQUIRED_FINAL_LIMITATIONS,
        "required_final_limitations",
    )
    final_stage_status = _validate_choice(
        closeout.final_stage_status,
        (COMPLETED,),
        "final_stage_status",
    )
    final_current_feature = _validate_choice(
        closeout.final_current_feature,
        (STAGE6_COMPLETE_FEATURE,),
        "final_current_feature",
    )
    scope = _validate_choice(closeout.scope, (FINAL_REPORT_SCOPE,), "scope")
    record_level = _validate_choice(closeout.record_level, (DONOR_LEVEL,), "record_level")
    execution_scope = _validate_choice(
        closeout.execution_scope,
        (IN_MEMORY_ONLY,),
        "execution_scope",
    )
    stage7_policy = _validate_choice(
        closeout.stage7_policy,
        (NO_STAGE7_REQUIRED,),
        "stage7_policy",
    )

    required_true = {
        "allow_final_report_metadata": closeout.allow_final_report_metadata,
        "allow_stage6_closeout": closeout.allow_stage6_closeout,
        "allow_next_research_handoff_summary": (
            closeout.allow_next_research_handoff_summary
        ),
        "require_all_stage6_features_completed": (
            closeout.require_all_stage6_features_completed
        ),
        "require_metric_scope_documented": closeout.require_metric_scope_documented,
        "require_limitations_documented": closeout.require_limitations_documented,
        "require_no_stage7": closeout.require_no_stage7,
    }
    disabled = sorted(name for name, value in required_true.items() if not _as_bool(value))
    if disabled:
        raise Stage6FinalResultReportCloseoutError(
            "Stage 6 final closeout requires enabled documentation controls: "
            + ", ".join(disabled)
        )

    forbidden_true = {
        "allow_filesystem_artifact_access": closeout.allow_filesystem_artifact_access,
        "allow_real_artifact_loading": closeout.allow_real_artifact_loading,
        "allow_npy_payload_loading": closeout.allow_npy_payload_loading,
        "allow_embedding_vector_parsing_from_disk": (
            closeout.allow_embedding_vector_parsing_from_disk
        ),
        "allow_split_execution_from_file": closeout.allow_split_execution_from_file,
        "allow_model_refit": closeout.allow_model_refit,
        "allow_training": closeout.allow_training,
        "training_allowed": closeout.training_allowed,
        "allow_model_artifact_persistence": closeout.allow_model_artifact_persistence,
        "allow_prediction_manifest_write": closeout.allow_prediction_manifest_write,
        "allow_metric_table_write": closeout.allow_metric_table_write,
        "allow_report_artifact_write": closeout.allow_report_artifact_write,
        "external_validation_allowed": closeout.external_validation_allowed,
        "allow_external_validation": closeout.allow_external_validation,
        "performance_claims_allowed": closeout.performance_claims_allowed,
        "performance_claims_added": closeout.performance_claims_added,
    }
    enabled = sorted(name for name, value in forbidden_true.items() if _as_bool(value))
    if enabled:
        raise Stage6FinalResultReportCloseoutError(
            "Stage 6 final closeout must not access files, load artifacts, "
            "refit/train, persist outputs, externally validate, or add claims; "
            "enabled: " + ", ".join(enabled)
        )

    return Stage6FinalResultReportCloseout(
        current_stage=current_stage,
        stage_name=_clean_required_string(closeout.stage_name, "stage_name"),
        current_feature=current_feature,
        feature_name=_clean_required_string(closeout.feature_name, "feature_name"),
        closeout_feature=closeout_feature,
        closeout_status=closeout_status,
        closeout_decision=closeout_decision,
        branch=_clean_required_string(closeout.branch, "branch"),
        previous_feature=previous_feature,
        previous_feature_status=previous_feature_status,
        completed_stage6_features=completed_stage6_features,
        required_prior_features=required_prior_features,
        required_closeout_sections=required_closeout_sections,
        required_final_limitations=required_final_limitations,
        final_stage_status=final_stage_status,
        final_current_feature=final_current_feature,
        scope=scope,
        record_level=record_level,
        execution_scope=execution_scope,
        stage7_policy=stage7_policy,
        prediction_metric_scope=_clean_required_string(
            closeout.prediction_metric_scope,
            "prediction_metric_scope",
        ),
        report_artifact_policy=_clean_required_string(
            closeout.report_artifact_policy,
            "report_artifact_policy",
        ),
        performance_claim_policy=_clean_required_string(
            closeout.performance_claim_policy,
            "performance_claim_policy",
        ),
        external_validation_policy=_clean_required_string(
            closeout.external_validation_policy,
            "external_validation_policy",
        ),
        allow_final_report_metadata=True,
        allow_stage6_closeout=True,
        allow_next_research_handoff_summary=True,
        require_all_stage6_features_completed=True,
        require_metric_scope_documented=True,
        require_limitations_documented=True,
        require_no_stage7=True,
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
        allow_report_artifact_write=False,
        external_validation_allowed=False,
        allow_external_validation=False,
        performance_claims_allowed=False,
        performance_claims_added=False,
        notes=str(closeout.notes).strip(),
    )


def stage6_final_result_report_closeout_from_mapping(
    values: Mapping[str, Any],
) -> Stage6FinalResultReportCloseout:
    """Build and validate final closeout metadata from mapping."""

    defaults = {
        field.name: getattr(Stage6FinalResultReportCloseout(), field.name)
        for field in fields(Stage6FinalResultReportCloseout)
    }
    merged = {**defaults, **dict(values)}
    for sequence_field in (
        "completed_stage6_features",
        "required_prior_features",
        "required_closeout_sections",
        "required_final_limitations",
    ):
        if sequence_field in merged and not isinstance(merged[sequence_field], tuple):
            merged[sequence_field] = tuple(merged[sequence_field])

    return validate_stage6_final_result_report_closeout(
        Stage6FinalResultReportCloseout(**merged)
    )


def stage6_final_result_report_closeout_to_dict(
    closeout: Stage6FinalResultReportCloseout,
) -> dict[str, Any]:
    """Serialize validated Stage 6 final closeout metadata."""

    validated = validate_stage6_final_result_report_closeout(closeout)
    serialized = asdict(validated)
    for sequence_field in (
        "completed_stage6_features",
        "required_prior_features",
        "required_closeout_sections",
        "required_final_limitations",
    ):
        serialized[sequence_field] = list(serialized[sequence_field])
    return serialized


def stage6_final_result_report_closeout_summary(
    closeout: Stage6FinalResultReportCloseout,
) -> dict[str, Any]:
    """Return compact Stage 6 closeout summary without performance claims."""

    validated = validate_stage6_final_result_report_closeout(closeout)
    return {
        "current_stage": validated.current_stage,
        "current_feature": validated.current_feature,
        "closeout_status": validated.closeout_status,
        "closeout_decision": validated.closeout_decision,
        "final_current_feature": validated.final_current_feature,
        "final_stage_status": validated.final_stage_status,
        "scope": validated.scope,
        "record_level": validated.record_level,
        "execution_scope": validated.execution_scope,
        "stage7_policy": validated.stage7_policy,
        "prediction_metric_scope": validated.prediction_metric_scope,
        "performance_claim_policy": validated.performance_claim_policy,
        "external_validation_policy": validated.external_validation_policy,
        "performance_claims_added": validated.performance_claims_added,
    }
