"""Stage 6 real artifact access and integrity gate.

This module validates the metadata-only STAGE6-F002 gate for real artifact
access and integrity planning. It records path/schema/permission/integrity
contracts only.

It does not access the filesystem for real artifacts, load .npy payloads,
parse embedding vectors, materialize input arrays, create labels from real
data, execute splits, aggregate embeddings, load AnnData files, execute
Geneformer/tokenizer code, extract embeddings, fit scalers, fit models,
generate predictions, compute metrics, train models, perform external
validation, or add performance claims.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, fields
from typing import Any


COMPLETED = "completed"
IN_PROGRESS = "in_progress"
BLOCKED = "blocked"

STAGE6_CURRENT_FEATURE = "STAGE6-F002"
STAGE6_NAME = "Stage 6 - Controlled donor-level modeling execution"
STAGE6_FEATURE_NAME = "Real artifact access and integrity gate"

STAGE6_COMPLETED_FEATURES = ("STAGE6-F001",)
REQUIRED_INTEGRITY_CONTRACTS = (
    "path_schema_contract",
    "permission_contract",
    "record_level_contract",
    "artifact_format_contract",
    "no_large_artifact_commit_contract",
)
DEFERRED_REAL_ARTIFACT_CHECKS = (
    "filesystem_existence_check",
    "file_count_scan",
    "checksum_calculation",
    "npy_payload_loading",
    "embedding_vector_parsing",
    "shape_validation_from_payload",
)

STAGE6_CONTROLLED_EXECUTION_PATH_AUTHORIZED = (
    "stage6_controlled_execution_path_authorized"
)
METADATA_ACCESS_INTEGRITY_GATE_OPENED = (
    "metadata_access_integrity_gate_opened"
)
PATH_SCHEMA_PERMISSION_CONTRACT_ONLY = "path_schema_permission_contract_only"
METADATA_INTEGRITY_CONTRACT_ONLY = "metadata_integrity_contract_only"
DONOR_LEVEL = "donor"
DONOR_LEVEL_ONLY = "donor_level_only"
CELL_LEVEL_SPLIT_FORBIDDEN = "cell_level_split_forbidden"
NPY_DIRECTORY = "npy_directory"
ONE_FILE_PER_DONOR_EMBEDDING = "one_file_per_donor_embedding"
EXTERNAL_NOT_COMMITTED = "external_local_or_remote_path_not_committed"
PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE = "prohibited_until_explicit_stage6_gate"

ALLOWED_STAGE6_STATUSES = (IN_PROGRESS, BLOCKED)
ALLOWED_GATE_STATUSES = (IN_PROGRESS, BLOCKED)
ALLOWED_GATE_DECISIONS = (METADATA_ACCESS_INTEGRITY_GATE_OPENED,)
ALLOWED_ACCESS_SCOPES = (PATH_SCHEMA_PERMISSION_CONTRACT_ONLY,)
ALLOWED_INTEGRITY_SCOPES = (METADATA_INTEGRITY_CONTRACT_ONLY,)
ALLOWED_RECORD_LEVELS = (DONOR_LEVEL,)
ALLOWED_POLICIES = (
    DONOR_LEVEL_ONLY,
    CELL_LEVEL_SPLIT_FORBIDDEN,
    PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
)
ALLOWED_FORMATS = (NPY_DIRECTORY,)
ALLOWED_LAYOUTS = (ONE_FILE_PER_DONOR_EMBEDDING,)
ALLOWED_LOCATION_POLICIES = (EXTERNAL_NOT_COMMITTED,)


class Stage6RealArtifactAccessIntegrityGateError(ValueError):
    """Raised when STAGE6-F002 artifact access/integrity metadata is unsafe."""


@dataclass(frozen=True)
class Stage6RealArtifactAccessIntegrityGate:
    """Metadata-only STAGE6-F002 artifact access and integrity gate."""

    current_stage: str = "Stage 6"
    stage_name: str = STAGE6_NAME
    current_feature: str = STAGE6_CURRENT_FEATURE
    feature_name: str = STAGE6_FEATURE_NAME
    stage6_status: str = IN_PROGRESS
    gate_status: str = IN_PROGRESS
    gate_decision: str = METADATA_ACCESS_INTEGRITY_GATE_OPENED
    previous_feature: str = "STAGE6-F001"
    previous_feature_status: str = COMPLETED
    completed_stage6_features: tuple[str, ...] = STAGE6_COMPLETED_FEATURES
    upstream_authorization_decision: str = STAGE6_CONTROLLED_EXECUTION_PATH_AUTHORIZED
    scope: str = "artifact_access_integrity_contract_only_no_runtime_execution"
    access_scope: str = PATH_SCHEMA_PERMISSION_CONTRACT_ONLY
    integrity_scope: str = METADATA_INTEGRITY_CONTRACT_ONLY
    artifact_family: str = "geneformer_donor_embeddings"
    expected_artifact_format: str = NPY_DIRECTORY
    expected_artifact_layout: str = ONE_FILE_PER_DONOR_EMBEDDING
    expected_record_level: str = DONOR_LEVEL
    expected_split_level: str = DONOR_LEVEL
    expected_artifact_location_policy: str = EXTERNAL_NOT_COMMITTED
    required_integrity_contracts: tuple[str, ...] = REQUIRED_INTEGRITY_CONTRACTS
    deferred_real_artifact_checks: tuple[str, ...] = DEFERRED_REAL_ARTIFACT_CHECKS
    next_feature: str = "STAGE6-F003"
    next_feature_name: str = "Donor-level input materialization gate"
    first_runtime_execution_feature: str = "STAGE6-F005"
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
    requires_completed_stage6_f001: bool = True
    requires_artifact_integrity_review: bool = True
    requires_permission_contract: bool = True
    requires_donor_level_only: bool = True
    forbids_cell_level_split: bool = True
    requires_no_large_artifact_commit: bool = True
    requires_payload_free_integrity_gate: bool = True
    requires_no_runtime_execution: bool = True
    allow_artifact_path_contract_recording: bool = True
    allow_schema_contract_recording: bool = True
    allow_permission_contract_recording: bool = True
    allow_filesystem_artifact_access: bool = False
    allow_real_artifact_loading: bool = False
    allow_file_count_scan: bool = False
    allow_checksum_calculation: bool = False
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
        raise Stage6RealArtifactAccessIntegrityGateError(
            f"{field_name} must not be empty."
        )
    if "\x00" in normalized:
        raise Stage6RealArtifactAccessIntegrityGateError(
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
        raise Stage6RealArtifactAccessIntegrityGateError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _normalize_exact_sequence(
    values: Sequence[object],
    expected: tuple[str, ...],
    field_name: str,
) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise Stage6RealArtifactAccessIntegrityGateError(
            f"{field_name} must be a sequence."
        )

    normalized = tuple(
        _clean_required_string(value, f"{field_name} item") for value in values
    )
    if normalized != expected:
        expected_text = ", ".join(expected)
        got = ", ".join(normalized)
        raise Stage6RealArtifactAccessIntegrityGateError(
            f"{field_name} must exactly equal: {expected_text}; got: {got}."
        )

    return normalized


def validate_stage6_real_artifact_access_integrity_gate(
    gate: Stage6RealArtifactAccessIntegrityGate,
) -> Stage6RealArtifactAccessIntegrityGate:
    """Validate the metadata-only STAGE6-F002 artifact access/integrity gate."""

    current_stage = _validate_choice(gate.current_stage, ("Stage 6",), "current_stage")
    current_feature = _validate_choice(
        gate.current_feature,
        (STAGE6_CURRENT_FEATURE,),
        "current_feature",
    )
    stage6_status = _validate_choice(
        gate.stage6_status,
        ALLOWED_STAGE6_STATUSES,
        "stage6_status",
    )
    gate_status = _validate_choice(
        gate.gate_status,
        ALLOWED_GATE_STATUSES,
        "gate_status",
    )
    gate_decision = _validate_choice(
        gate.gate_decision,
        ALLOWED_GATE_DECISIONS,
        "gate_decision",
    )
    previous_feature = _validate_choice(
        gate.previous_feature,
        ("STAGE6-F001",),
        "previous_feature",
    )
    previous_feature_status = _validate_choice(
        gate.previous_feature_status,
        (COMPLETED,),
        "previous_feature_status",
    )
    completed_stage6_features = _normalize_exact_sequence(
        gate.completed_stage6_features,
        STAGE6_COMPLETED_FEATURES,
        "completed_stage6_features",
    )
    upstream_authorization_decision = _validate_choice(
        gate.upstream_authorization_decision,
        (STAGE6_CONTROLLED_EXECUTION_PATH_AUTHORIZED,),
        "upstream_authorization_decision",
    )
    access_scope = _validate_choice(
        gate.access_scope,
        ALLOWED_ACCESS_SCOPES,
        "access_scope",
    )
    integrity_scope = _validate_choice(
        gate.integrity_scope,
        ALLOWED_INTEGRITY_SCOPES,
        "integrity_scope",
    )
    expected_artifact_format = _validate_choice(
        gate.expected_artifact_format,
        ALLOWED_FORMATS,
        "expected_artifact_format",
    )
    expected_artifact_layout = _validate_choice(
        gate.expected_artifact_layout,
        ALLOWED_LAYOUTS,
        "expected_artifact_layout",
    )
    expected_record_level = _validate_choice(
        gate.expected_record_level,
        ALLOWED_RECORD_LEVELS,
        "expected_record_level",
    )
    expected_split_level = _validate_choice(
        gate.expected_split_level,
        ALLOWED_RECORD_LEVELS,
        "expected_split_level",
    )
    expected_artifact_location_policy = _validate_choice(
        gate.expected_artifact_location_policy,
        ALLOWED_LOCATION_POLICIES,
        "expected_artifact_location_policy",
    )
    required_integrity_contracts = _normalize_exact_sequence(
        gate.required_integrity_contracts,
        REQUIRED_INTEGRITY_CONTRACTS,
        "required_integrity_contracts",
    )
    deferred_real_artifact_checks = _normalize_exact_sequence(
        gate.deferred_real_artifact_checks,
        DEFERRED_REAL_ARTIFACT_CHECKS,
        "deferred_real_artifact_checks",
    )
    next_feature = _validate_choice(gate.next_feature, ("STAGE6-F003",), "next_feature")
    first_runtime_execution_feature = _validate_choice(
        gate.first_runtime_execution_feature,
        ("STAGE6-F005",),
        "first_runtime_execution_feature",
    )

    required_policy_values = {
        "split_policy": (gate.split_policy, DONOR_LEVEL_ONLY),
        "leakage_policy": (gate.leakage_policy, CELL_LEVEL_SPLIT_FORBIDDEN),
        "artifact_loading_policy": (
            gate.artifact_loading_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "input_materialization_policy": (
            gate.input_materialization_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "label_creation_policy": (
            gate.label_creation_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "split_execution_policy": (
            gate.split_execution_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "aggregation_execution_policy": (
            gate.aggregation_execution_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "modeling_execution_policy": (
            gate.modeling_execution_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "prediction_generation_policy": (
            gate.prediction_generation_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "metric_computation_policy": (
            gate.metric_computation_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "external_validation_policy": (
            gate.external_validation_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
        "performance_claim_policy": (
            gate.performance_claim_policy,
            PROHIBITED_UNTIL_EXPLICIT_STAGE6_GATE,
        ),
    }
    for field_name, (value, expected) in required_policy_values.items():
        _validate_choice(value, ALLOWED_POLICIES, field_name)
        if value != expected:
            raise Stage6RealArtifactAccessIntegrityGateError(
                f"{field_name} must remain {expected}."
            )

    required_true_flags = {
        "requires_completed_stage6_f001": gate.requires_completed_stage6_f001,
        "requires_artifact_integrity_review": gate.requires_artifact_integrity_review,
        "requires_permission_contract": gate.requires_permission_contract,
        "requires_donor_level_only": gate.requires_donor_level_only,
        "forbids_cell_level_split": gate.forbids_cell_level_split,
        "requires_no_large_artifact_commit": gate.requires_no_large_artifact_commit,
        "requires_payload_free_integrity_gate": (
            gate.requires_payload_free_integrity_gate
        ),
        "requires_no_runtime_execution": gate.requires_no_runtime_execution,
        "allow_artifact_path_contract_recording": (
            gate.allow_artifact_path_contract_recording
        ),
        "allow_schema_contract_recording": gate.allow_schema_contract_recording,
        "allow_permission_contract_recording": (
            gate.allow_permission_contract_recording
        ),
    }
    disabled_required = sorted(
        name for name, value in required_true_flags.items() if not _as_bool(value)
    )
    if disabled_required:
        raise Stage6RealArtifactAccessIntegrityGateError(
            "required STAGE6-F002 gates/contracts must remain enabled; disabled: "
            + ", ".join(disabled_required)
        )

    forbidden_flags = {
        "allow_filesystem_artifact_access": gate.allow_filesystem_artifact_access,
        "allow_real_artifact_loading": gate.allow_real_artifact_loading,
        "allow_file_count_scan": gate.allow_file_count_scan,
        "allow_checksum_calculation": gate.allow_checksum_calculation,
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
        raise Stage6RealArtifactAccessIntegrityGateError(
            "STAGE6-F002 records metadata-only artifact access/integrity "
            "contracts and must not perform filesystem access, payload "
            "loading, vector parsing, input materialization, split execution, "
            "modeling, metrics, training, external validation, or claims; "
            "enabled: " + ", ".join(enabled)
        )

    return Stage6RealArtifactAccessIntegrityGate(
        current_stage=current_stage,
        stage_name=_clean_required_string(gate.stage_name, "stage_name"),
        current_feature=current_feature,
        feature_name=_clean_required_string(gate.feature_name, "feature_name"),
        stage6_status=stage6_status,
        gate_status=gate_status,
        gate_decision=gate_decision,
        previous_feature=previous_feature,
        previous_feature_status=previous_feature_status,
        completed_stage6_features=completed_stage6_features,
        upstream_authorization_decision=upstream_authorization_decision,
        scope=_clean_required_string(gate.scope, "scope"),
        access_scope=access_scope,
        integrity_scope=integrity_scope,
        artifact_family=_clean_required_string(gate.artifact_family, "artifact_family"),
        expected_artifact_format=expected_artifact_format,
        expected_artifact_layout=expected_artifact_layout,
        expected_record_level=expected_record_level,
        expected_split_level=expected_split_level,
        expected_artifact_location_policy=expected_artifact_location_policy,
        required_integrity_contracts=required_integrity_contracts,
        deferred_real_artifact_checks=deferred_real_artifact_checks,
        next_feature=next_feature,
        next_feature_name=_clean_required_string(
            gate.next_feature_name,
            "next_feature_name",
        ),
        first_runtime_execution_feature=first_runtime_execution_feature,
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
        requires_completed_stage6_f001=True,
        requires_artifact_integrity_review=True,
        requires_permission_contract=True,
        requires_donor_level_only=True,
        forbids_cell_level_split=True,
        requires_no_large_artifact_commit=True,
        requires_payload_free_integrity_gate=True,
        requires_no_runtime_execution=True,
        allow_artifact_path_contract_recording=True,
        allow_schema_contract_recording=True,
        allow_permission_contract_recording=True,
        allow_filesystem_artifact_access=False,
        allow_real_artifact_loading=False,
        allow_file_count_scan=False,
        allow_checksum_calculation=False,
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


def stage6_real_artifact_access_integrity_gate_from_mapping(
    values: Mapping[str, Any],
) -> Stage6RealArtifactAccessIntegrityGate:
    """Build and validate STAGE6-F002 artifact gate metadata from a mapping."""

    defaults = {
        field.name: getattr(Stage6RealArtifactAccessIntegrityGate(), field.name)
        for field in fields(Stage6RealArtifactAccessIntegrityGate)
    }
    merged = {**defaults, **dict(values)}
    for sequence_field in (
        "completed_stage6_features",
        "required_integrity_contracts",
        "deferred_real_artifact_checks",
    ):
        if sequence_field in merged and not isinstance(merged[sequence_field], tuple):
            merged[sequence_field] = tuple(merged[sequence_field])

    return validate_stage6_real_artifact_access_integrity_gate(
        Stage6RealArtifactAccessIntegrityGate(**merged)
    )


def stage6_real_artifact_access_integrity_gate_to_dict(
    gate: Stage6RealArtifactAccessIntegrityGate,
) -> dict[str, Any]:
    """Serialize validated STAGE6-F002 artifact access/integrity metadata."""

    validated = validate_stage6_real_artifact_access_integrity_gate(gate)
    serialized = asdict(validated)
    for sequence_field in (
        "completed_stage6_features",
        "required_integrity_contracts",
        "deferred_real_artifact_checks",
    ):
        serialized[sequence_field] = list(serialized[sequence_field])

    return serialized


def stage6_real_artifact_access_integrity_gate_summary(
    gate: Stage6RealArtifactAccessIntegrityGate,
) -> dict[str, Any]:
    """Return compact STAGE6-F002 artifact access/integrity summary."""

    validated = validate_stage6_real_artifact_access_integrity_gate(gate)
    return {
        "current_stage": validated.current_stage,
        "current_feature": validated.current_feature,
        "gate_status": validated.gate_status,
        "gate_decision": validated.gate_decision,
        "access_scope": validated.access_scope,
        "integrity_scope": validated.integrity_scope,
        "expected_artifact_format": validated.expected_artifact_format,
        "expected_record_level": validated.expected_record_level,
        "expected_artifact_location_policy": (
            validated.expected_artifact_location_policy
        ),
        "next_feature": validated.next_feature,
        "requires_donor_level_only": validated.requires_donor_level_only,
        "forbids_cell_level_split": validated.forbids_cell_level_split,
        "allow_artifact_path_contract_recording": (
            validated.allow_artifact_path_contract_recording
        ),
        "allow_filesystem_artifact_access": validated.allow_filesystem_artifact_access,
        "allow_real_artifact_loading": validated.allow_real_artifact_loading,
        "allow_npy_payload_loading": validated.allow_npy_payload_loading,
        "allow_embedding_vector_parsing": validated.allow_embedding_vector_parsing,
        "allow_input_materialization": validated.allow_input_materialization,
        "allow_model_fitting": validated.allow_model_fitting,
        "allow_prediction_generation": validated.allow_prediction_generation,
        "allow_metric_computation": validated.allow_metric_computation,
        "performance_claims_allowed": validated.performance_claims_allowed,
        "performance_claims_added": validated.performance_claims_added,
    }
