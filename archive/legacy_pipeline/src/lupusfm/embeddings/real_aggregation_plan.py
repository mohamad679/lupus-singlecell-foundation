"""Stage 4 real donor-level aggregation run plan.

This module defines a guarded plan for the real donor-level embedding artifact
observed in Stage 4-F001. It does not load .npy payloads, parse embedding
vectors, aggregate real embeddings, load AnnData files, execute Geneformer,
execute tokenizers, extract embeddings, fit scalers, fit models, compute
metrics, train models, perform external validation, or add performance claims.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any

from lupusfm.embeddings.artifact_schema import DEFAULT_EMBEDDING_DIMENSION
from lupusfm.embeddings.real_artifact_validation import (
    DEFAULT_DIRECTORY_EMBEDDING_SUFFIX,
    DIRECTORY_ARTIFACT_LAYOUT,
    NPY_DIRECTORY_ARTIFACT_FORMAT,
)


STAGE4_CURRENT_FEATURE = "STAGE4-F002"

IDENTITY_DONOR_EMBEDDING_DIRECTORY = "identity_donor_embedding_directory"
ALLOWED_REAL_DONOR_AGGREGATION_STRATEGIES = (IDENTITY_DONOR_EMBEDDING_DIRECTORY,)

DONOR_RECORD_LEVEL = "donor"
ALLOWED_REAL_AGGREGATION_RECORD_LEVELS = (DONOR_RECORD_LEVEL,)

PENDING = "pending"
VALIDATED = "validated"
BLOCKED = "blocked"
ALLOWED_REAL_AGGREGATION_PLAN_STATUSES = (PENDING, VALIDATED, BLOCKED)


class RealDonorAggregationRunPlanError(ValueError):
    """Raised when the Stage 4-F002 aggregation plan violates the contract."""


@dataclass(frozen=True)
class RealDonorAggregationRunPlan:
    """Metadata-only plan for using the observed donor-level artifact safely."""

    current_feature: str = STAGE4_CURRENT_FEATURE
    plan_status: str = PENDING
    aggregation_strategy: str = IDENTITY_DONOR_EMBEDDING_DIRECTORY
    artifact_format: str = NPY_DIRECTORY_ARTIFACT_FORMAT
    artifact_layout: str = DIRECTORY_ARTIFACT_LAYOUT
    directory_file_suffix: str = DEFAULT_DIRECTORY_EMBEDDING_SUFFIX
    input_record_level: str = DONOR_RECORD_LEVEL
    output_record_level: str = DONOR_RECORD_LEVEL
    split_level: str = DONOR_RECORD_LEVEL
    expected_embedding_dimension: int = DEFAULT_EMBEDDING_DIMENSION
    expected_donor_file_count: int = 261
    observed_donor_file_count: int = 261
    observed_total_size_bytes: int = 360839808
    observed_all_files_same_size: bool = True
    observed_flare_like_count: int = 14
    observed_healthy_hc_like_count: int = 48
    observed_healthy_igtb_like_count: int = 50
    observed_managed_sle_numeric_like_count: int = 148
    observed_control_like_count: int = 1
    requires_cell_to_donor_pooling: bool = False
    requires_payload_loading: bool = False
    requires_npy_payload_loading: bool = False
    requires_real_aggregation_execution: bool = False
    requires_anndata_loading: bool = False
    requires_geneformer_execution: bool = False
    requires_tokenizer_execution: bool = False
    requires_embedding_extraction: bool = False
    allow_real_artifact_loading: bool = False
    allow_npy_payload_loading: bool = False
    allow_embedding_vector_parsing: bool = False
    allow_real_aggregation_execution: bool = False
    allow_anndata_loading: bool = False
    allow_geneformer_execution: bool = False
    allow_tokenizer_execution: bool = False
    allow_embedding_extraction: bool = False
    allow_feature_extraction: bool = False
    allow_global_preprocessing: bool = False
    allow_scaler_outside_fold: bool = False
    allow_model_fitting: bool = False
    allow_metric_computation: bool = False
    allow_modeling: bool = False
    allow_training: bool = False
    allow_external_validation: bool = False
    performance_claims_added: bool = False
    notes: str = ""


def _clean_required_string(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise RealDonorAggregationRunPlanError(f"{field_name} must not be empty.")

    return normalized


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {"1", "true", "yes"}


def _validate_choice(value: object, allowed: tuple[str, ...], field_name: str) -> str:
    normalized = _clean_required_string(value, field_name)
    if normalized not in allowed:
        allowed_text = ", ".join(allowed)
        raise RealDonorAggregationRunPlanError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _require_positive_int(value: object, field_name: str) -> int:
    if isinstance(value, bool):
        raise RealDonorAggregationRunPlanError(
            f"{field_name} must be an integer, not bool."
        )

    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise RealDonorAggregationRunPlanError(
            f"{field_name} must be an integer."
        ) from exc

    if parsed <= 0:
        raise RealDonorAggregationRunPlanError(f"{field_name} must be positive.")

    return parsed


def validate_real_donor_aggregation_run_plan(
    plan: RealDonorAggregationRunPlan,
) -> RealDonorAggregationRunPlan:
    """Validate a metadata-only Stage 4-F002 donor aggregation run plan."""

    current_feature = _validate_choice(
        plan.current_feature,
        (STAGE4_CURRENT_FEATURE,),
        "current_feature",
    )
    plan_status = _validate_choice(
        plan.plan_status,
        ALLOWED_REAL_AGGREGATION_PLAN_STATUSES,
        "plan_status",
    )
    aggregation_strategy = _validate_choice(
        plan.aggregation_strategy,
        ALLOWED_REAL_DONOR_AGGREGATION_STRATEGIES,
        "aggregation_strategy",
    )
    input_record_level = _validate_choice(
        plan.input_record_level,
        ALLOWED_REAL_AGGREGATION_RECORD_LEVELS,
        "input_record_level",
    )
    output_record_level = _validate_choice(
        plan.output_record_level,
        ALLOWED_REAL_AGGREGATION_RECORD_LEVELS,
        "output_record_level",
    )
    split_level = _validate_choice(
        plan.split_level,
        ALLOWED_REAL_AGGREGATION_RECORD_LEVELS,
        "split_level",
    )

    artifact_format = _validate_choice(
        plan.artifact_format,
        (NPY_DIRECTORY_ARTIFACT_FORMAT,),
        "artifact_format",
    )
    artifact_layout = _validate_choice(
        plan.artifact_layout,
        (DIRECTORY_ARTIFACT_LAYOUT,),
        "artifact_layout",
    )
    directory_file_suffix = _validate_choice(
        plan.directory_file_suffix,
        (DEFAULT_DIRECTORY_EMBEDDING_SUFFIX,),
        "directory_file_suffix",
    )

    expected_donor_file_count = _require_positive_int(
        plan.expected_donor_file_count,
        "expected_donor_file_count",
    )
    observed_donor_file_count = _require_positive_int(
        plan.observed_donor_file_count,
        "observed_donor_file_count",
    )
    if expected_donor_file_count != observed_donor_file_count:
        raise RealDonorAggregationRunPlanError(
            "expected and observed donor file counts must match before F002 can proceed."
        )

    category_total = sum(
        _require_positive_int(value, field_name)
        for value, field_name in (
            (plan.observed_flare_like_count, "observed_flare_like_count"),
            (plan.observed_healthy_hc_like_count, "observed_healthy_hc_like_count"),
            (
                plan.observed_healthy_igtb_like_count,
                "observed_healthy_igtb_like_count",
            ),
            (
                plan.observed_managed_sle_numeric_like_count,
                "observed_managed_sle_numeric_like_count",
            ),
            (plan.observed_control_like_count, "observed_control_like_count"),
        )
    )
    if category_total != observed_donor_file_count:
        raise RealDonorAggregationRunPlanError(
            "filename category counts must sum to observed_donor_file_count."
        )

    if not _as_bool(plan.observed_all_files_same_size):
        raise RealDonorAggregationRunPlanError(
            "observed donor files must have consistent size before F002 can proceed."
        )

    forbidden_flags = {
        "requires_cell_to_donor_pooling": plan.requires_cell_to_donor_pooling,
        "requires_payload_loading": plan.requires_payload_loading,
        "requires_npy_payload_loading": plan.requires_npy_payload_loading,
        "requires_real_aggregation_execution": plan.requires_real_aggregation_execution,
        "requires_anndata_loading": plan.requires_anndata_loading,
        "requires_geneformer_execution": plan.requires_geneformer_execution,
        "requires_tokenizer_execution": plan.requires_tokenizer_execution,
        "requires_embedding_extraction": plan.requires_embedding_extraction,
        "allow_real_artifact_loading": plan.allow_real_artifact_loading,
        "allow_npy_payload_loading": plan.allow_npy_payload_loading,
        "allow_embedding_vector_parsing": plan.allow_embedding_vector_parsing,
        "allow_real_aggregation_execution": plan.allow_real_aggregation_execution,
        "allow_anndata_loading": plan.allow_anndata_loading,
        "allow_geneformer_execution": plan.allow_geneformer_execution,
        "allow_tokenizer_execution": plan.allow_tokenizer_execution,
        "allow_embedding_extraction": plan.allow_embedding_extraction,
        "allow_feature_extraction": plan.allow_feature_extraction,
        "allow_global_preprocessing": plan.allow_global_preprocessing,
        "allow_scaler_outside_fold": plan.allow_scaler_outside_fold,
        "allow_model_fitting": plan.allow_model_fitting,
        "allow_metric_computation": plan.allow_metric_computation,
        "allow_modeling": plan.allow_modeling,
        "allow_training": plan.allow_training,
        "allow_external_validation": plan.allow_external_validation,
        "performance_claims_added": plan.performance_claims_added,
    }
    enabled = sorted(name for name, value in forbidden_flags.items() if _as_bool(value))
    if enabled:
        raise RealDonorAggregationRunPlanError(
            "Stage 4-F002 keeps payload loading, aggregation execution, modeling, "
            f"training, metrics, and claims disabled; enabled: {', '.join(enabled)}."
        )

    return RealDonorAggregationRunPlan(
        current_feature=current_feature,
        plan_status=plan_status,
        aggregation_strategy=aggregation_strategy,
        artifact_format=artifact_format,
        artifact_layout=artifact_layout,
        directory_file_suffix=directory_file_suffix,
        input_record_level=input_record_level,
        output_record_level=output_record_level,
        split_level=split_level,
        expected_embedding_dimension=_require_positive_int(
            plan.expected_embedding_dimension,
            "expected_embedding_dimension",
        ),
        expected_donor_file_count=expected_donor_file_count,
        observed_donor_file_count=observed_donor_file_count,
        observed_total_size_bytes=_require_positive_int(
            plan.observed_total_size_bytes,
            "observed_total_size_bytes",
        ),
        observed_all_files_same_size=True,
        observed_flare_like_count=_require_positive_int(
            plan.observed_flare_like_count,
            "observed_flare_like_count",
        ),
        observed_healthy_hc_like_count=_require_positive_int(
            plan.observed_healthy_hc_like_count,
            "observed_healthy_hc_like_count",
        ),
        observed_healthy_igtb_like_count=_require_positive_int(
            plan.observed_healthy_igtb_like_count,
            "observed_healthy_igtb_like_count",
        ),
        observed_managed_sle_numeric_like_count=_require_positive_int(
            plan.observed_managed_sle_numeric_like_count,
            "observed_managed_sle_numeric_like_count",
        ),
        observed_control_like_count=_require_positive_int(
            plan.observed_control_like_count,
            "observed_control_like_count",
        ),
        requires_cell_to_donor_pooling=False,
        requires_payload_loading=False,
        requires_npy_payload_loading=False,
        requires_real_aggregation_execution=False,
        requires_anndata_loading=False,
        requires_geneformer_execution=False,
        requires_tokenizer_execution=False,
        requires_embedding_extraction=False,
        allow_real_artifact_loading=False,
        allow_npy_payload_loading=False,
        allow_embedding_vector_parsing=False,
        allow_real_aggregation_execution=False,
        allow_anndata_loading=False,
        allow_geneformer_execution=False,
        allow_tokenizer_execution=False,
        allow_embedding_extraction=False,
        allow_feature_extraction=False,
        allow_global_preprocessing=False,
        allow_scaler_outside_fold=False,
        allow_model_fitting=False,
        allow_metric_computation=False,
        allow_modeling=False,
        allow_training=False,
        allow_external_validation=False,
        performance_claims_added=False,
        notes=str(plan.notes).strip(),
    )


def real_donor_aggregation_run_plan_from_mapping(
    data: Mapping[str, Any],
) -> RealDonorAggregationRunPlan:
    """Build and validate a Stage 4-F002 run plan from mapping data."""

    return validate_real_donor_aggregation_run_plan(
        RealDonorAggregationRunPlan(
            current_feature=data.get("current_feature", STAGE4_CURRENT_FEATURE),
            plan_status=data.get("plan_status", PENDING),
            aggregation_strategy=data.get(
                "aggregation_strategy",
                IDENTITY_DONOR_EMBEDDING_DIRECTORY,
            ),
            artifact_format=data.get("artifact_format", NPY_DIRECTORY_ARTIFACT_FORMAT),
            artifact_layout=data.get("artifact_layout", DIRECTORY_ARTIFACT_LAYOUT),
            directory_file_suffix=data.get(
                "directory_file_suffix",
                DEFAULT_DIRECTORY_EMBEDDING_SUFFIX,
            ),
            input_record_level=data.get("input_record_level", DONOR_RECORD_LEVEL),
            output_record_level=data.get("output_record_level", DONOR_RECORD_LEVEL),
            split_level=data.get("split_level", DONOR_RECORD_LEVEL),
            expected_embedding_dimension=data.get(
                "expected_embedding_dimension",
                DEFAULT_EMBEDDING_DIMENSION,
            ),
            expected_donor_file_count=data.get("expected_donor_file_count", 261),
            observed_donor_file_count=data.get("observed_donor_file_count", 261),
            observed_total_size_bytes=data.get(
                "observed_total_size_bytes",
                360839808,
            ),
            observed_all_files_same_size=data.get("observed_all_files_same_size", True),
            observed_flare_like_count=data.get("observed_flare_like_count", 14),
            observed_healthy_hc_like_count=data.get("observed_healthy_hc_like_count", 48),
            observed_healthy_igtb_like_count=data.get(
                "observed_healthy_igtb_like_count",
                50,
            ),
            observed_managed_sle_numeric_like_count=data.get(
                "observed_managed_sle_numeric_like_count",
                148,
            ),
            observed_control_like_count=data.get("observed_control_like_count", 1),
            requires_cell_to_donor_pooling=data.get(
                "requires_cell_to_donor_pooling",
                False,
            ),
            requires_payload_loading=data.get("requires_payload_loading", False),
            requires_npy_payload_loading=data.get(
                "requires_npy_payload_loading",
                False,
            ),
            requires_real_aggregation_execution=data.get(
                "requires_real_aggregation_execution",
                False,
            ),
            requires_anndata_loading=data.get("requires_anndata_loading", False),
            requires_geneformer_execution=data.get(
                "requires_geneformer_execution",
                False,
            ),
            requires_tokenizer_execution=data.get(
                "requires_tokenizer_execution",
                False,
            ),
            requires_embedding_extraction=data.get(
                "requires_embedding_extraction",
                False,
            ),
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
            allow_anndata_loading=data.get("allow_anndata_loading", False),
            allow_geneformer_execution=data.get("allow_geneformer_execution", False),
            allow_tokenizer_execution=data.get("allow_tokenizer_execution", False),
            allow_embedding_extraction=data.get("allow_embedding_extraction", False),
            allow_feature_extraction=data.get("allow_feature_extraction", False),
            allow_global_preprocessing=data.get("allow_global_preprocessing", False),
            allow_scaler_outside_fold=data.get("allow_scaler_outside_fold", False),
            allow_model_fitting=data.get("allow_model_fitting", False),
            allow_metric_computation=data.get("allow_metric_computation", False),
            allow_modeling=data.get("allow_modeling", False),
            allow_training=data.get("allow_training", False),
            allow_external_validation=data.get("allow_external_validation", False),
            performance_claims_added=data.get("performance_claims_added", False),
            notes=data.get("notes", ""),
        )
    )


def real_donor_aggregation_run_plan_to_dict(
    plan: RealDonorAggregationRunPlan,
) -> dict[str, Any]:
    """Validate and serialize a Stage 4-F002 run plan."""

    return asdict(validate_real_donor_aggregation_run_plan(plan))
