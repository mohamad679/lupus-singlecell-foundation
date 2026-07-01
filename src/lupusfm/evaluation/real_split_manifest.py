"""Stage 4 real leakage-safe split manifest validation contract.

This module validates donor-level split manifest metadata for the real
donor-level embedding artifact observed in Stage 4-F001/F002. It does not load
.npy payloads, parse embedding vectors, execute real aggregation, fit models,
compute metrics, train models, perform external validation, or add performance
claims.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any


STAGE4_CURRENT_FEATURE = "STAGE4-F003"

DONOR_SPLIT_LEVEL = "donor"
PATIENT_SPLIT_LEVEL = "patient"
ALLOWED_SPLIT_LEVELS = (DONOR_SPLIT_LEVEL, PATIENT_SPLIT_LEVEL)

TRAIN_SPLIT = "train"
VALIDATION_SPLIT = "validation"
TEST_SPLIT = "test"
ALLOWED_SPLIT_NAMES = (TRAIN_SPLIT, VALIDATION_SPLIT, TEST_SPLIT)

FLARE_LIKE = "flare_like"
HEALTHY_HC_LIKE = "healthy_hc_like"
HEALTHY_IGTB_LIKE = "healthy_igtb_like"
MANAGED_SLE_NUMERIC_LIKE = "managed_sle_numeric_like"
CONTROL_LIKE = "control_like"
ALLOWED_LABEL_GROUPS = (
    FLARE_LIKE,
    HEALTHY_HC_LIKE,
    HEALTHY_IGTB_LIKE,
    MANAGED_SLE_NUMERIC_LIKE,
    CONTROL_LIKE,
)

PENDING = "pending"
VALIDATED = "validated"
BLOCKED = "blocked"
ALLOWED_MANIFEST_STATUSES = (PENDING, VALIDATED, BLOCKED)


class RealSplitManifestValidationError(ValueError):
    """Raised when a real donor split manifest violates the Stage 4-F003 contract."""


@dataclass(frozen=True)
class RealDonorSplitRecord:
    """One donor-level split manifest record.

    This record stores donor identifiers, split assignment, and coarse label
    group metadata only. It must not include embeddings, predictions, metrics,
    model outputs, or cell-level split assignments.
    """

    donor_id: str
    split: str
    label_group: str


@dataclass(frozen=True)
class RealLeakageSafeSplitManifest:
    """Metadata-only donor split manifest for Stage 4-F003 validation."""

    records: tuple[RealDonorSplitRecord, ...]
    current_feature: str = STAGE4_CURRENT_FEATURE
    manifest_status: str = PENDING
    split_level: str = DONOR_SPLIT_LEVEL
    donor_id_column: str = "donor_id"
    split_column: str = "split"
    label_group_column: str = "label_group"
    expected_donor_count: int | None = None
    required_splits: tuple[str, ...] = ALLOWED_SPLIT_NAMES
    required_label_groups: tuple[str, ...] = ALLOWED_LABEL_GROUPS
    require_all_required_splits_present: bool = True
    require_unique_donor_ids: bool = True
    allow_cell_level_splits: bool = False
    allow_duplicate_donors_across_splits: bool = False
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
        raise RealSplitManifestValidationError(f"{field_name} must not be empty.")
    if "\x00" in normalized:
        raise RealSplitManifestValidationError(
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
        raise RealSplitManifestValidationError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _require_positive_int(value: object, field_name: str) -> int:
    if isinstance(value, bool):
        raise RealSplitManifestValidationError(
            f"{field_name} must be an integer, not bool."
        )

    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise RealSplitManifestValidationError(
            f"{field_name} must be an integer."
        ) from exc

    if parsed <= 0:
        raise RealSplitManifestValidationError(f"{field_name} must be positive.")

    return parsed


def _optional_positive_int(value: object, field_name: str) -> int | None:
    if value is None:
        return None

    return _require_positive_int(value, field_name)


def _normalize_required_choices(
    values: Sequence[object],
    allowed: tuple[str, ...],
    field_name: str,
) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise RealSplitManifestValidationError(f"{field_name} must be a sequence.")

    normalized = tuple(_validate_choice(value, allowed, field_name) for value in values)
    if not normalized:
        raise RealSplitManifestValidationError(f"{field_name} must not be empty.")

    if len(set(normalized)) != len(normalized):
        raise RealSplitManifestValidationError(f"{field_name} must not contain duplicates.")

    return normalized


def _normalize_record(record: RealDonorSplitRecord | Mapping[str, Any]) -> RealDonorSplitRecord:
    if isinstance(record, Mapping):
        donor_id = record.get("donor_id", "")
        split = record.get("split", "")
        label_group = record.get("label_group", "")
    else:
        donor_id = record.donor_id
        split = record.split
        label_group = record.label_group

    return RealDonorSplitRecord(
        donor_id=_clean_required_string(donor_id, "donor_id"),
        split=_validate_choice(split, ALLOWED_SPLIT_NAMES, "split"),
        label_group=_validate_choice(label_group, ALLOWED_LABEL_GROUPS, "label_group"),
    )


def validate_real_leakage_safe_split_manifest(
    manifest: RealLeakageSafeSplitManifest,
) -> RealLeakageSafeSplitManifest:
    """Validate a metadata-only donor-level split manifest."""

    current_feature = _validate_choice(
        manifest.current_feature,
        (STAGE4_CURRENT_FEATURE,),
        "current_feature",
    )
    manifest_status = _validate_choice(
        manifest.manifest_status,
        ALLOWED_MANIFEST_STATUSES,
        "manifest_status",
    )
    split_level = _validate_choice(
        manifest.split_level,
        ALLOWED_SPLIT_LEVELS,
        "split_level",
    )
    if split_level == PATIENT_SPLIT_LEVEL:
        split_level = DONOR_SPLIT_LEVEL

    if _as_bool(manifest.allow_cell_level_splits):
        raise RealSplitManifestValidationError("cell-level splits are not allowed.")

    donor_id_column = _clean_required_string(manifest.donor_id_column, "donor_id_column")
    split_column = _clean_required_string(manifest.split_column, "split_column")
    label_group_column = _clean_required_string(
        manifest.label_group_column,
        "label_group_column",
    )
    forbidden_column_names = {"cell_id", "cell", "barcode", "prediction", "metric"}
    if {
        donor_id_column.lower(),
        split_column.lower(),
        label_group_column.lower(),
    } & forbidden_column_names:
        raise RealSplitManifestValidationError(
            "split manifest columns must not be cell-level, prediction, or metric columns."
        )

    required_splits = _normalize_required_choices(
        manifest.required_splits,
        ALLOWED_SPLIT_NAMES,
        "required_splits",
    )
    required_label_groups = _normalize_required_choices(
        manifest.required_label_groups,
        ALLOWED_LABEL_GROUPS,
        "required_label_groups",
    )

    if isinstance(manifest.records, (str, bytes)) or not isinstance(
        manifest.records,
        Sequence,
    ):
        raise RealSplitManifestValidationError("records must be a sequence.")

    records = tuple(_normalize_record(record) for record in manifest.records)
    if not records:
        raise RealSplitManifestValidationError("records must not be empty.")

    expected_donor_count = _optional_positive_int(
        manifest.expected_donor_count,
        "expected_donor_count",
    )
    if expected_donor_count is not None and len(records) != expected_donor_count:
        raise RealSplitManifestValidationError(
            "expected_donor_count must match the number of split manifest records."
        )

    donor_ids = [record.donor_id for record in records]
    if _as_bool(manifest.require_unique_donor_ids) and len(set(donor_ids)) != len(donor_ids):
        raise RealSplitManifestValidationError(
            "donor_id values must be unique across all splits."
        )

    donor_to_splits: dict[str, set[str]] = {}
    for record in records:
        donor_to_splits.setdefault(record.donor_id, set()).add(record.split)
    duplicate_split_donors = sorted(
        donor_id for donor_id, splits in donor_to_splits.items() if len(splits) > 1
    )
    if duplicate_split_donors and not _as_bool(
        manifest.allow_duplicate_donors_across_splits
    ):
        raise RealSplitManifestValidationError(
            "donors must not appear in multiple splits."
        )

    observed_splits = {record.split for record in records}
    missing_splits = sorted(set(required_splits) - observed_splits)
    if _as_bool(manifest.require_all_required_splits_present) and missing_splits:
        raise RealSplitManifestValidationError(
            "required splits are missing: " + ", ".join(missing_splits)
        )

    observed_label_groups = {record.label_group for record in records}
    disallowed_label_groups = sorted(observed_label_groups - set(required_label_groups))
    if disallowed_label_groups:
        raise RealSplitManifestValidationError(
            "unexpected label groups: " + ", ".join(disallowed_label_groups)
        )

    forbidden_flags = {
        "allow_duplicate_donors_across_splits": manifest.allow_duplicate_donors_across_splits,
        "allow_real_artifact_loading": manifest.allow_real_artifact_loading,
        "allow_npy_payload_loading": manifest.allow_npy_payload_loading,
        "allow_embedding_vector_parsing": manifest.allow_embedding_vector_parsing,
        "allow_real_aggregation_execution": manifest.allow_real_aggregation_execution,
        "allow_anndata_loading": manifest.allow_anndata_loading,
        "allow_geneformer_execution": manifest.allow_geneformer_execution,
        "allow_tokenizer_execution": manifest.allow_tokenizer_execution,
        "allow_embedding_extraction": manifest.allow_embedding_extraction,
        "allow_feature_extraction": manifest.allow_feature_extraction,
        "allow_global_preprocessing": manifest.allow_global_preprocessing,
        "allow_scaler_outside_fold": manifest.allow_scaler_outside_fold,
        "allow_model_fitting": manifest.allow_model_fitting,
        "allow_metric_computation": manifest.allow_metric_computation,
        "allow_modeling": manifest.allow_modeling,
        "allow_training": manifest.allow_training,
        "allow_external_validation": manifest.allow_external_validation,
        "performance_claims_added": manifest.performance_claims_added,
    }
    enabled = sorted(name for name, value in forbidden_flags.items() if _as_bool(value))
    if enabled:
        raise RealSplitManifestValidationError(
            "Stage 4-F003 keeps leakage, payload loading, aggregation execution, "
            f"modeling, training, metrics, and claims disabled; enabled: {', '.join(enabled)}."
        )

    return RealLeakageSafeSplitManifest(
        records=records,
        current_feature=current_feature,
        manifest_status=manifest_status,
        split_level=DONOR_SPLIT_LEVEL,
        donor_id_column=donor_id_column,
        split_column=split_column,
        label_group_column=label_group_column,
        expected_donor_count=expected_donor_count,
        required_splits=required_splits,
        required_label_groups=required_label_groups,
        require_all_required_splits_present=_as_bool(
            manifest.require_all_required_splits_present
        ),
        require_unique_donor_ids=True,
        allow_cell_level_splits=False,
        allow_duplicate_donors_across_splits=False,
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
        notes=str(manifest.notes).strip(),
    )


def split_manifest_summary(
    manifest: RealLeakageSafeSplitManifest,
) -> dict[str, Any]:
    """Return split and label counts without computing model metrics."""

    validated = validate_real_leakage_safe_split_manifest(manifest)
    split_counts = Counter(record.split for record in validated.records)
    label_counts = Counter(record.label_group for record in validated.records)

    return {
        "current_feature": validated.current_feature,
        "manifest_status": validated.manifest_status,
        "split_level": validated.split_level,
        "n_donors": len(validated.records),
        "split_counts": dict(sorted(split_counts.items())),
        "label_group_counts": dict(sorted(label_counts.items())),
        "allow_modeling": False,
        "allow_metric_computation": False,
        "performance_claims_added": False,
    }


def real_leakage_safe_split_manifest_from_mapping(
    data: Mapping[str, Any],
) -> RealLeakageSafeSplitManifest:
    """Build and validate a split manifest from mapping data."""

    records = tuple(
        _normalize_record(record)
        for record in data.get("records", ())
    )

    return validate_real_leakage_safe_split_manifest(
        RealLeakageSafeSplitManifest(
            records=records,
            current_feature=data.get("current_feature", STAGE4_CURRENT_FEATURE),
            manifest_status=data.get("manifest_status", PENDING),
            split_level=data.get("split_level", DONOR_SPLIT_LEVEL),
            donor_id_column=data.get("donor_id_column", "donor_id"),
            split_column=data.get("split_column", "split"),
            label_group_column=data.get("label_group_column", "label_group"),
            expected_donor_count=data.get("expected_donor_count"),
            required_splits=tuple(data.get("required_splits", ALLOWED_SPLIT_NAMES)),
            required_label_groups=tuple(
                data.get("required_label_groups", ALLOWED_LABEL_GROUPS)
            ),
            require_all_required_splits_present=data.get(
                "require_all_required_splits_present",
                True,
            ),
            require_unique_donor_ids=data.get("require_unique_donor_ids", True),
            allow_cell_level_splits=data.get("allow_cell_level_splits", False),
            allow_duplicate_donors_across_splits=data.get(
                "allow_duplicate_donors_across_splits",
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


def real_leakage_safe_split_manifest_to_dict(
    manifest: RealLeakageSafeSplitManifest,
) -> dict[str, Any]:
    """Validate and serialize a donor split manifest."""

    validated = validate_real_leakage_safe_split_manifest(manifest)
    serialized = asdict(validated)
    serialized["records"] = [asdict(record) for record in validated.records]
    return serialized
