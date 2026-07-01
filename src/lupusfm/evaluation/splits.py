"""Stage 3 leakage-safe patient/donor split utilities.

This module defines fake-data utilities for donor-level split construction and
validation. It does not load real embedding artifacts, load AnnData files,
execute Geneformer, execute tokenizers, extract embeddings, fit scalers, train
models, evaluate model performance, perform external validation, or add
performance claims.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

from lupusfm.data.anndata_schema import DEFAULT_FORBIDDEN_SPLIT_VALUES


DEFAULT_SPLIT_LEVEL = "patient"
ALLOWED_SPLIT_LEVELS = ("patient", "donor")

LEAVE_ONE_DONOR_OUT = "leave_one_donor_out"
GROUP_K_FOLD = "group_k_fold"
ALLOWED_SPLIT_METHODS = (LEAVE_ONE_DONOR_OUT, GROUP_K_FOLD)


class LeakageSafeSplitError(ValueError):
    """Raised when leakage-safe split construction violates the contract."""


@dataclass(frozen=True)
class DonorLabelRecord:
    """One fake donor-level label record used for split design."""

    donor_id: str
    label: str


@dataclass(frozen=True)
class LeakageSafeSplitConfig:
    """Metadata-only configuration for leakage-safe donor-level splits."""

    split_method: str = LEAVE_ONE_DONOR_OUT
    split_level: str = DEFAULT_SPLIT_LEVEL
    n_splits: int | None = None
    stratify_by_label: bool = False
    allow_cell_level_split: bool = False
    allow_real_artifact_loading: bool = False
    allow_anndata_loading: bool = False
    allow_global_preprocessing: bool = False
    allow_scaler_outside_fold: bool = False
    allow_model_fitting: bool = False
    allow_modeling: bool = False
    allow_training: bool = False
    allow_external_validation: bool = False
    performance_claims_added: bool = False
    notes: str = ""


@dataclass(frozen=True)
class SplitFold:
    """One donor-level train/test fold."""

    fold_id: str
    train_donor_ids: tuple[str, ...]
    test_donor_ids: tuple[str, ...]
    split_method: str
    split_level: str = DEFAULT_SPLIT_LEVEL


def _clean_required_string(value: object, field_name: str) -> str:
    """Return a non-empty normalized string or raise."""

    normalized = str(value).strip()
    if not normalized:
        raise LeakageSafeSplitError(f"{field_name} must not be empty.")
    return normalized


def _as_bool(value: object) -> bool:
    """Parse common bool-like values."""

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {"1", "true", "yes"}


def _validate_choice(value: object, allowed: tuple[str, ...], field_name: str) -> str:
    """Validate a normalized string against an allowed set."""

    normalized = _clean_required_string(value, field_name)
    if normalized not in allowed:
        allowed_text = ", ".join(allowed)
        raise LeakageSafeSplitError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _optional_positive_int(value: object, field_name: str) -> int | None:
    """Return None or a positive integer."""

    if value is None:
        return None

    if isinstance(value, bool):
        raise LeakageSafeSplitError(f"{field_name} must be an integer, not bool.")

    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise LeakageSafeSplitError(f"{field_name} must be an integer.") from exc

    if parsed <= 0:
        raise LeakageSafeSplitError(f"{field_name} must be positive.")

    return parsed


def _normalize_donor_ids(values: Sequence[object], field_name: str) -> tuple[str, ...]:
    """Normalize donor IDs and reject duplicates within one sequence."""

    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise LeakageSafeSplitError(f"{field_name} must be a sequence.")

    donor_ids = tuple(_clean_required_string(value, field_name) for value in values)
    duplicates = sorted(
        donor_id for donor_id, count in Counter(donor_ids).items() if count > 1
    )
    if duplicates:
        raise LeakageSafeSplitError(f"{field_name} contains duplicate donor IDs.")

    return donor_ids


def validate_leakage_safe_split_config(
    config: LeakageSafeSplitConfig,
) -> LeakageSafeSplitConfig:
    """Validate split config without fitting models or touching real artifacts."""

    split_method = _validate_choice(
        config.split_method,
        ALLOWED_SPLIT_METHODS,
        "split_method",
    )
    split_level = _validate_choice(
        config.split_level,
        ALLOWED_SPLIT_LEVELS,
        "split_level",
    )

    forbidden_split_levels = {str(value) for value in DEFAULT_FORBIDDEN_SPLIT_VALUES}
    if split_level in forbidden_split_levels:
        raise LeakageSafeSplitError("cell-level split assignments are not allowed.")

    if _as_bool(config.allow_cell_level_split):
        raise LeakageSafeSplitError("cell-level split assignments are not allowed.")
    if _as_bool(config.allow_real_artifact_loading):
        raise LeakageSafeSplitError("split utilities must not load real artifacts.")
    if _as_bool(config.allow_anndata_loading):
        raise LeakageSafeSplitError("split utilities must not load AnnData.")
    if _as_bool(config.allow_global_preprocessing):
        raise LeakageSafeSplitError(
            "global preprocessing across folds is not allowed."
        )
    if _as_bool(config.allow_scaler_outside_fold):
        raise LeakageSafeSplitError(
            "scaler fitting outside the training fold is not allowed."
        )
    if _as_bool(config.allow_model_fitting):
        raise LeakageSafeSplitError(
            "model fitting is not allowed in split utilities."
        )
    if _as_bool(config.allow_modeling):
        raise LeakageSafeSplitError("Stage 3 split utilities keep modeling disabled.")
    if _as_bool(config.allow_training):
        raise LeakageSafeSplitError("Stage 3 split utilities keep training disabled.")
    if _as_bool(config.allow_external_validation):
        raise LeakageSafeSplitError(
            "Stage 3 split utilities keep external validation disabled."
        )
    if _as_bool(config.performance_claims_added):
        raise LeakageSafeSplitError(
            "Stage 3 split utilities must not add performance claims."
        )

    return LeakageSafeSplitConfig(
        split_method=split_method,
        split_level=split_level,
        n_splits=_optional_positive_int(config.n_splits, "n_splits"),
        stratify_by_label=_as_bool(config.stratify_by_label),
        allow_cell_level_split=False,
        allow_real_artifact_loading=False,
        allow_anndata_loading=False,
        allow_global_preprocessing=False,
        allow_scaler_outside_fold=False,
        allow_model_fitting=False,
        allow_modeling=False,
        allow_training=False,
        allow_external_validation=False,
        performance_claims_added=False,
        notes=str(config.notes).strip(),
    )


def validate_donor_label_record(
    record: DonorLabelRecord | Mapping[str, Any],
) -> DonorLabelRecord:
    """Validate one fake donor-level label record."""

    if isinstance(record, Mapping):
        donor_id = record.get("donor_id", "")
        label = record.get("label", "")
    else:
        donor_id = record.donor_id
        label = record.label

    return DonorLabelRecord(
        donor_id=_clean_required_string(donor_id, "donor_id"),
        label=_clean_required_string(label, "label"),
    )


def validate_donor_label_records(
    records: Sequence[DonorLabelRecord | Mapping[str, Any]],
) -> tuple[DonorLabelRecord, ...]:
    """Validate fake donor-level label records and reject duplicate donors."""

    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise LeakageSafeSplitError("records must be a sequence.")
    if not records:
        raise LeakageSafeSplitError("records must not be empty.")

    validated = tuple(validate_donor_label_record(record) for record in records)
    donor_counts = Counter(record.donor_id for record in validated)
    duplicates = sorted(
        donor_id for donor_id, count in donor_counts.items() if count > 1
    )
    if duplicates:
        raise LeakageSafeSplitError("donor_id values must be unique.")

    return tuple(sorted(validated, key=lambda record: record.donor_id))


def validate_split_fold(fold: SplitFold) -> SplitFold:
    """Validate one donor-level fold."""

    split_method = _validate_choice(
        fold.split_method,
        ALLOWED_SPLIT_METHODS,
        "split_method",
    )
    split_level = _validate_choice(
        fold.split_level,
        ALLOWED_SPLIT_LEVELS,
        "split_level",
    )
    train_donor_ids = _normalize_donor_ids(
        fold.train_donor_ids,
        "train_donor_ids",
    )
    test_donor_ids = _normalize_donor_ids(
        fold.test_donor_ids,
        "test_donor_ids",
    )

    if not train_donor_ids:
        raise LeakageSafeSplitError("train_donor_ids must not be empty.")
    if not test_donor_ids:
        raise LeakageSafeSplitError("test_donor_ids must not be empty.")

    overlap = sorted(set(train_donor_ids).intersection(test_donor_ids))
    if overlap:
        raise LeakageSafeSplitError("donor leakage detected across train/test fold.")

    return SplitFold(
        fold_id=_clean_required_string(fold.fold_id, "fold_id"),
        train_donor_ids=tuple(sorted(train_donor_ids)),
        test_donor_ids=tuple(sorted(test_donor_ids)),
        split_method=split_method,
        split_level=split_level,
    )


def validate_split_folds(
    folds: Sequence[SplitFold],
    expected_donor_ids: Sequence[object] | None = None,
) -> tuple[SplitFold, ...]:
    """Validate multiple donor-level folds and optional donor coverage."""

    if isinstance(folds, (str, bytes)) or not isinstance(folds, Sequence):
        raise LeakageSafeSplitError("folds must be a sequence.")
    if not folds:
        raise LeakageSafeSplitError("folds must not be empty.")

    validated = tuple(validate_split_fold(fold) for fold in folds)
    fold_ids = [fold.fold_id for fold in validated]
    duplicates = sorted(
        fold_id for fold_id, count in Counter(fold_ids).items() if count > 1
    )
    if duplicates:
        raise LeakageSafeSplitError("fold_id values must be unique.")

    if expected_donor_ids is not None:
        expected = set(_normalize_donor_ids(expected_donor_ids, "expected_donor_ids"))
        observed_test = set()
        observed_all = set()
        for fold in validated:
            observed_test.update(fold.test_donor_ids)
            observed_all.update(fold.train_donor_ids)
            observed_all.update(fold.test_donor_ids)

        if observed_all - expected:
            raise LeakageSafeSplitError("folds include unknown donor IDs.")
        if expected - observed_test:
            raise LeakageSafeSplitError(
                "each donor must appear in a held-out test fold."
            )

    return validated


def make_leave_one_donor_out_splits(
    records: Sequence[DonorLabelRecord | Mapping[str, Any]],
    config: LeakageSafeSplitConfig | None = None,
) -> tuple[SplitFold, ...]:
    """Create leave-one-donor-out folds over fake donor-level records."""

    validated_config = validate_leakage_safe_split_config(
        config or LeakageSafeSplitConfig(split_method=LEAVE_ONE_DONOR_OUT)
    )
    if validated_config.split_method != LEAVE_ONE_DONOR_OUT:
        raise LeakageSafeSplitError("split_method must be leave_one_donor_out.")

    donor_records = validate_donor_label_records(records)
    donor_ids = tuple(record.donor_id for record in donor_records)
    if len(donor_ids) < 2:
        raise LeakageSafeSplitError("leave-one-donor-out requires at least 2 donors.")

    folds = []
    for index, test_donor_id in enumerate(donor_ids):
        train_donor_ids = tuple(
            donor_id for donor_id in donor_ids if donor_id != test_donor_id
        )
        folds.append(
            SplitFold(
                fold_id=f"loocv_{index + 1:03d}",
                train_donor_ids=train_donor_ids,
                test_donor_ids=(test_donor_id,),
                split_method=LEAVE_ONE_DONOR_OUT,
                split_level=validated_config.split_level,
            )
        )

    return validate_split_folds(folds, expected_donor_ids=donor_ids)


def is_stratification_feasible(
    records: Sequence[DonorLabelRecord | Mapping[str, Any]],
    n_splits: int,
) -> bool:
    """Return whether each label has at least n_splits donors."""

    donor_records = validate_donor_label_records(records)
    parsed_n_splits = _optional_positive_int(n_splits, "n_splits")
    if parsed_n_splits is None:
        return False

    label_counts = Counter(record.label for record in donor_records)
    return bool(label_counts) and all(
        count >= parsed_n_splits for count in label_counts.values()
    )


def make_group_k_fold_splits(
    records: Sequence[DonorLabelRecord | Mapping[str, Any]],
    config: LeakageSafeSplitConfig,
) -> tuple[SplitFold, ...]:
    """Create deterministic donor-level GroupKFold-like fake splits."""

    validated_config = validate_leakage_safe_split_config(config)
    if validated_config.split_method != GROUP_K_FOLD:
        raise LeakageSafeSplitError("split_method must be group_k_fold.")
    if validated_config.n_splits is None:
        raise LeakageSafeSplitError("n_splits is required for group_k_fold.")

    donor_records = validate_donor_label_records(records)
    donor_ids = tuple(record.donor_id for record in donor_records)
    n_splits = validated_config.n_splits

    if n_splits < 2:
        raise LeakageSafeSplitError("group_k_fold requires at least 2 splits.")
    if n_splits > len(donor_ids):
        raise LeakageSafeSplitError("n_splits cannot exceed number of donors.")

    test_groups: list[list[str]] = [[] for _ in range(n_splits)]
    if validated_config.stratify_by_label:
        if not is_stratification_feasible(donor_records, n_splits):
            raise LeakageSafeSplitError("label stratification is not feasible.")

        by_label: dict[str, list[str]] = defaultdict(list)
        for record in donor_records:
            by_label[record.label].append(record.donor_id)

        for label in sorted(by_label):
            for index, donor_id in enumerate(sorted(by_label[label])):
                test_groups[index % n_splits].append(donor_id)
    else:
        for index, donor_id in enumerate(donor_ids):
            test_groups[index % n_splits].append(donor_id)

    folds = []
    donor_id_set = set(donor_ids)
    for index, test_donor_ids in enumerate(test_groups):
        test_tuple = tuple(sorted(test_donor_ids))
        train_tuple = tuple(sorted(donor_id_set - set(test_tuple)))
        folds.append(
            SplitFold(
                fold_id=f"group_k_fold_{index + 1:03d}",
                train_donor_ids=train_tuple,
                test_donor_ids=test_tuple,
                split_method=GROUP_K_FOLD,
                split_level=validated_config.split_level,
            )
        )

    return validate_split_folds(folds, expected_donor_ids=donor_ids)


def leakage_safe_split_config_from_mapping(
    data: Mapping[str, Any],
) -> LeakageSafeSplitConfig:
    """Build and validate a leakage-safe split config from a mapping."""

    return validate_leakage_safe_split_config(
        LeakageSafeSplitConfig(
            split_method=data.get("split_method", LEAVE_ONE_DONOR_OUT),
            split_level=data.get("split_level", DEFAULT_SPLIT_LEVEL),
            n_splits=data.get("n_splits"),
            stratify_by_label=data.get("stratify_by_label", False),
            allow_cell_level_split=data.get("allow_cell_level_split", False),
            allow_real_artifact_loading=data.get("allow_real_artifact_loading", False),
            allow_anndata_loading=data.get("allow_anndata_loading", False),
            allow_global_preprocessing=data.get("allow_global_preprocessing", False),
            allow_scaler_outside_fold=data.get("allow_scaler_outside_fold", False),
            allow_model_fitting=data.get("allow_model_fitting", False),
            allow_modeling=data.get("allow_modeling", False),
            allow_training=data.get("allow_training", False),
            allow_external_validation=data.get("allow_external_validation", False),
            performance_claims_added=data.get("performance_claims_added", False),
            notes=data.get("notes", ""),
        )
    )


def split_folds_to_dicts(folds: Sequence[SplitFold]) -> list[dict[str, Any]]:
    """Serialize validated split folds to plain dictionaries."""

    return [asdict(fold) for fold in validate_split_folds(folds)]


def leakage_safe_split_config_to_dict(
    config: LeakageSafeSplitConfig,
) -> dict[str, Any]:
    """Serialize a validated split config to a plain dictionary."""

    return asdict(validate_leakage_safe_split_config(config))
