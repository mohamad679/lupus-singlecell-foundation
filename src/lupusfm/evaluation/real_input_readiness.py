"""Stage 4 real evaluation input readiness validation contract.

This module validates metadata-only readiness for connecting the observed real
donor-level embedding artifact, the donor-level aggregation run plan, and the
leakage-safe split manifest contract. It does not load .npy payloads, materialize
evaluation arrays, fit models, compute metrics, train models, perform external
validation, or add performance claims.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

from lupusfm.embeddings.artifact_schema import DEFAULT_EMBEDDING_DIMENSION
from lupusfm.embeddings.real_aggregation_plan import (
    IDENTITY_DONOR_EMBEDDING_DIRECTORY,
)
from lupusfm.embeddings.real_artifact_validation import (
    DIRECTORY_ARTIFACT_LAYOUT,
    NPY_DIRECTORY_ARTIFACT_FORMAT,
)
from lupusfm.evaluation.real_split_manifest import (
    ALLOWED_LABEL_GROUPS,
    ALLOWED_SPLIT_NAMES,
    DONOR_SPLIT_LEVEL,
)


STAGE4_CURRENT_FEATURE = "STAGE4-F004"

PENDING = "pending"
VALIDATED = "validated"
BLOCKED = "blocked"
ALLOWED_READINESS_STATUSES = (PENDING, VALIDATED, BLOCKED)

COMPLETED = "completed"


class RealEvaluationInputReadinessError(ValueError):
    """Raised when the Stage 4-F004 readiness contract is unsafe or incomplete."""


@dataclass(frozen=True)
class RealEvaluationInputReadinessContract:
    """Metadata-only readiness contract for real evaluation inputs.

    This contract checks whether upstream metadata contracts are complete enough
    to plan evaluation input wiring. It must not contain embeddings, labels
    arrays, predictions, metrics, model outputs, or materialized train/test
    matrices.
    """

    current_feature: str = STAGE4_CURRENT_FEATURE
    readiness_status: str = PENDING
    artifact_validation_status: str = COMPLETED
    aggregation_plan_status: str = COMPLETED
    split_manifest_validation_status: str = COMPLETED
    artifact_format: str = NPY_DIRECTORY_ARTIFACT_FORMAT
    artifact_layout: str = DIRECTORY_ARTIFACT_LAYOUT
    artifact_record_level: str = DONOR_SPLIT_LEVEL
    aggregation_strategy: str = IDENTITY_DONOR_EMBEDDING_DIRECTORY
    split_level: str = DONOR_SPLIT_LEVEL
    expected_donor_count: int = 261
    observed_donor_count: int = 261
    expected_embedding_dimension: int = DEFAULT_EMBEDDING_DIMENSION
    required_split_names: tuple[str, ...] = ALLOWED_SPLIT_NAMES
    allowed_label_groups: tuple[str, ...] = ALLOWED_LABEL_GROUPS
    require_unique_donors_across_splits: bool = True
    require_no_cell_level_splits: bool = True
    require_no_prediction_or_metric_columns: bool = True
    allow_input_materialization: bool = False
    allow_label_array_creation: bool = False
    allow_real_artifact_loading: bool = False
    allow_npy_payload_loading: bool = False
    allow_embedding_vector_parsing: bool = False
    allow_real_aggregation_execution: bool = False
    allow_split_execution: bool = False
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
        raise RealEvaluationInputReadinessError(f"{field_name} must not be empty.")
    if "\x00" in normalized:
        raise RealEvaluationInputReadinessError(
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
        raise RealEvaluationInputReadinessError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _require_positive_int(value: object, field_name: str) -> int:
    if isinstance(value, bool):
        raise RealEvaluationInputReadinessError(
            f"{field_name} must be an integer, not bool."
        )

    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise RealEvaluationInputReadinessError(
            f"{field_name} must be an integer."
        ) from exc

    if parsed <= 0:
        raise RealEvaluationInputReadinessError(f"{field_name} must be positive.")

    return parsed


def _normalize_choices(
    values: Sequence[object],
    allowed: tuple[str, ...],
    field_name: str,
) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise RealEvaluationInputReadinessError(f"{field_name} must be a sequence.")

    normalized = tuple(_validate_choice(value, allowed, field_name) for value in values)
    if not normalized:
        raise RealEvaluationInputReadinessError(f"{field_name} must not be empty.")
    if len(set(normalized)) != len(normalized):
        raise RealEvaluationInputReadinessError(
            f"{field_name} must not contain duplicates."
        )

    return normalized


def validate_real_evaluation_input_readiness(
    contract: RealEvaluationInputReadinessContract,
) -> RealEvaluationInputReadinessContract:
    """Validate Stage 4-F004 metadata-only evaluation input readiness."""

    current_feature = _validate_choice(
        contract.current_feature,
        (STAGE4_CURRENT_FEATURE,),
        "current_feature",
    )
    readiness_status = _validate_choice(
        contract.readiness_status,
        ALLOWED_READINESS_STATUSES,
        "readiness_status",
    )

    artifact_validation_status = _validate_choice(
        contract.artifact_validation_status,
        (COMPLETED,),
        "artifact_validation_status",
    )
    aggregation_plan_status = _validate_choice(
        contract.aggregation_plan_status,
        (COMPLETED,),
        "aggregation_plan_status",
    )
    split_manifest_validation_status = _validate_choice(
        contract.split_manifest_validation_status,
        (COMPLETED,),
        "split_manifest_validation_status",
    )

    artifact_format = _validate_choice(
        contract.artifact_format,
        (NPY_DIRECTORY_ARTIFACT_FORMAT,),
        "artifact_format",
    )
    artifact_layout = _validate_choice(
        contract.artifact_layout,
        (DIRECTORY_ARTIFACT_LAYOUT,),
        "artifact_layout",
    )
    artifact_record_level = _validate_choice(
        contract.artifact_record_level,
        (DONOR_SPLIT_LEVEL,),
        "artifact_record_level",
    )
    aggregation_strategy = _validate_choice(
        contract.aggregation_strategy,
        (IDENTITY_DONOR_EMBEDDING_DIRECTORY,),
        "aggregation_strategy",
    )
    split_level = _validate_choice(
        contract.split_level,
        (DONOR_SPLIT_LEVEL,),
        "split_level",
    )

    expected_donor_count = _require_positive_int(
        contract.expected_donor_count,
        "expected_donor_count",
    )
    observed_donor_count = _require_positive_int(
        contract.observed_donor_count,
        "observed_donor_count",
    )
    if expected_donor_count != observed_donor_count:
        raise RealEvaluationInputReadinessError(
            "expected_donor_count must match observed_donor_count before readiness."
        )

    required_split_names = _normalize_choices(
        contract.required_split_names,
        ALLOWED_SPLIT_NAMES,
        "required_split_names",
    )
    allowed_label_groups = _normalize_choices(
        contract.allowed_label_groups,
        ALLOWED_LABEL_GROUPS,
        "allowed_label_groups",
    )

    required_true_flags = {
        "require_unique_donors_across_splits": contract.require_unique_donors_across_splits,
        "require_no_cell_level_splits": contract.require_no_cell_level_splits,
        "require_no_prediction_or_metric_columns": contract.require_no_prediction_or_metric_columns,
    }
    disabled_required = sorted(
        name for name, value in required_true_flags.items() if not _as_bool(value)
    )
    if disabled_required:
        raise RealEvaluationInputReadinessError(
            "required leakage/readiness gates must remain enabled; disabled: "
            + ", ".join(disabled_required)
        )

    forbidden_flags = {
        "allow_input_materialization": contract.allow_input_materialization,
        "allow_label_array_creation": contract.allow_label_array_creation,
        "allow_real_artifact_loading": contract.allow_real_artifact_loading,
        "allow_npy_payload_loading": contract.allow_npy_payload_loading,
        "allow_embedding_vector_parsing": contract.allow_embedding_vector_parsing,
        "allow_real_aggregation_execution": contract.allow_real_aggregation_execution,
        "allow_split_execution": contract.allow_split_execution,
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
        "allow_training": contract.allow_training,
        "allow_external_validation": contract.allow_external_validation,
        "performance_claims_added": contract.performance_claims_added,
    }
    enabled = sorted(name for name, value in forbidden_flags.items() if _as_bool(value))
    if enabled:
        raise RealEvaluationInputReadinessError(
            "Stage 4-F004 keeps input materialization, payload loading, split "
            "execution, modeling, metrics, training, and claims disabled; enabled: "
            + ", ".join(enabled)
        )

    return RealEvaluationInputReadinessContract(
        current_feature=current_feature,
        readiness_status=readiness_status,
        artifact_validation_status=artifact_validation_status,
        aggregation_plan_status=aggregation_plan_status,
        split_manifest_validation_status=split_manifest_validation_status,
        artifact_format=artifact_format,
        artifact_layout=artifact_layout,
        artifact_record_level=artifact_record_level,
        aggregation_strategy=aggregation_strategy,
        split_level=split_level,
        expected_donor_count=expected_donor_count,
        observed_donor_count=observed_donor_count,
        expected_embedding_dimension=_require_positive_int(
            contract.expected_embedding_dimension,
            "expected_embedding_dimension",
        ),
        required_split_names=required_split_names,
        allowed_label_groups=allowed_label_groups,
        require_unique_donors_across_splits=True,
        require_no_cell_level_splits=True,
        require_no_prediction_or_metric_columns=True,
        allow_input_materialization=False,
        allow_label_array_creation=False,
        allow_real_artifact_loading=False,
        allow_npy_payload_loading=False,
        allow_embedding_vector_parsing=False,
        allow_real_aggregation_execution=False,
        allow_split_execution=False,
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
        notes=str(contract.notes).strip(),
    )


def real_evaluation_input_readiness_from_mapping(
    data: Mapping[str, Any],
) -> RealEvaluationInputReadinessContract:
    """Build and validate a Stage 4-F004 readiness contract from mapping data."""

    return validate_real_evaluation_input_readiness(
        RealEvaluationInputReadinessContract(
            current_feature=data.get("current_feature", STAGE4_CURRENT_FEATURE),
            readiness_status=data.get("readiness_status", PENDING),
            artifact_validation_status=data.get(
                "artifact_validation_status",
                COMPLETED,
            ),
            aggregation_plan_status=data.get("aggregation_plan_status", COMPLETED),
            split_manifest_validation_status=data.get(
                "split_manifest_validation_status",
                COMPLETED,
            ),
            artifact_format=data.get("artifact_format", NPY_DIRECTORY_ARTIFACT_FORMAT),
            artifact_layout=data.get("artifact_layout", DIRECTORY_ARTIFACT_LAYOUT),
            artifact_record_level=data.get("artifact_record_level", DONOR_SPLIT_LEVEL),
            aggregation_strategy=data.get(
                "aggregation_strategy",
                IDENTITY_DONOR_EMBEDDING_DIRECTORY,
            ),
            split_level=data.get("split_level", DONOR_SPLIT_LEVEL),
            expected_donor_count=data.get("expected_donor_count", 261),
            observed_donor_count=data.get("observed_donor_count", 261),
            expected_embedding_dimension=data.get(
                "expected_embedding_dimension",
                DEFAULT_EMBEDDING_DIMENSION,
            ),
            required_split_names=tuple(
                data.get("required_split_names", ALLOWED_SPLIT_NAMES)
            ),
            allowed_label_groups=tuple(
                data.get("allowed_label_groups", ALLOWED_LABEL_GROUPS)
            ),
            require_unique_donors_across_splits=data.get(
                "require_unique_donors_across_splits",
                True,
            ),
            require_no_cell_level_splits=data.get(
                "require_no_cell_level_splits",
                True,
            ),
            require_no_prediction_or_metric_columns=data.get(
                "require_no_prediction_or_metric_columns",
                True,
            ),
            allow_input_materialization=data.get("allow_input_materialization", False),
            allow_label_array_creation=data.get("allow_label_array_creation", False),
            allow_real_artifact_loading=data.get("allow_real_artifact_loading", False),
            allow_npy_payload_loading=data.get("allow_npy_payload_loading", False),
            allow_embedding_vector_parsing=data.get(
                "allow_embedding_vector_parsing",
                False,
            ),
            allow_real_aggregation_execution=data.get(
                "allow_real_aggregation_execution",
                False,
            ),
            allow_split_execution=data.get("allow_split_execution", False),
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


def real_evaluation_input_readiness_to_dict(
    contract: RealEvaluationInputReadinessContract,
) -> dict[str, Any]:
    """Validate and serialize a Stage 4-F004 readiness contract."""

    return asdict(validate_real_evaluation_input_readiness(contract))


def readiness_gate_summary(
    contract: RealEvaluationInputReadinessContract,
) -> dict[str, Any]:
    """Summarize readiness gates without materializing inputs or metrics."""

    validated = validate_real_evaluation_input_readiness(contract)
    return {
        "current_feature": validated.current_feature,
        "readiness_status": validated.readiness_status,
        "artifact_validation_status": validated.artifact_validation_status,
        "aggregation_plan_status": validated.aggregation_plan_status,
        "split_manifest_validation_status": validated.split_manifest_validation_status,
        "expected_donor_count": validated.expected_donor_count,
        "observed_donor_count": validated.observed_donor_count,
        "split_level": validated.split_level,
        "allow_input_materialization": False,
        "allow_modeling": False,
        "allow_metric_computation": False,
        "performance_claims_added": False,
    }
