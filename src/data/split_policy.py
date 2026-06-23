"""Patient-level and cohort-level split policy utilities.

These helpers validate local split policy configuration and mock split
manifests. They do not download datasets, preprocess data, create AnnData
outputs, split cells, create real train/test assignments, or perform modeling.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "configs" / "splitting.yaml"

REQUIRED_ALLOWED_SPLIT_UNITS = ["patient_id", "donor_id", "cohort_id"]
REQUIRED_FORBIDDEN_SPLIT_UNITS = ["cell_id", "barcode"]
REQUIRED_SPLIT_TYPES = [
    "internal_patient_holdout",
    "leave_cohort_out",
    "external_validation",
]
REQUIRED_MANIFEST_FIELDS = [
    "entity_id",
    "entity_type",
    "dataset_id",
    "cohort_id",
    "split",
    "disease_label",
    "n_cells",
    "n_samples",
    "audit_status",
]
SPLIT_MANIFEST_HEADERS = REQUIRED_MANIFEST_FIELDS + ["notes"]
ALLOWED_SPLIT_VALUES = ["train", "validation", "test", "external_validation", "holdout"]
REQUIRED_TRUE_POLICY_FLAGS = [
    "require_no_patient_overlap",
    "require_no_donor_overlap",
    "require_no_sample_overlap_when_patient_unknown",
    "require_cohort_holdout_for_external_validation",
    "require_split_manifest",
]


class SplitPolicyError(ValueError):
    """Raised when split policy or mock manifest validation fails."""


def _parse_scalar(value: str) -> object:
    normalized = value.strip()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    if normalized.isdigit():
        return int(normalized)
    return normalized


def load_split_config(path: Path | str = DEFAULT_CONFIG_PATH) -> Dict[str, object]:
    """Parse the small local YAML shape used by configs/splitting.yaml."""
    config_path = Path(path)
    data: Dict[str, object] = {}
    current_key: str | None = None
    current_nested_key: str | None = None

    for line_number, raw_line in enumerate(config_path.read_text().splitlines(), start=1):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        stripped = line.strip()

        if indent == 0 and ":" in stripped:
            key, value = stripped.split(":", 1)
            current_key = key.strip()
            current_nested_key = None
            value = value.strip()
            data[current_key] = _parse_scalar(value) if value else None
            continue

        if current_key is None:
            raise SplitPolicyError(f"Nested value without section at line {line_number}")

        if indent == 2 and stripped.startswith("- "):
            section = data.get(current_key)
            if section is None:
                section = []
                data[current_key] = section
            if not isinstance(section, list):
                raise SplitPolicyError(
                    f"List item under non-list section {current_key} at line {line_number}"
                )
            section.append(_parse_scalar(stripped[2:]))
            continue

        if indent == 2 and ":" in stripped:
            section = data.get(current_key)
            if section is None:
                section = {}
                data[current_key] = section
            if not isinstance(section, dict):
                raise SplitPolicyError(
                    f"Mapping item under non-mapping section {current_key} at line {line_number}"
                )
            key, value = stripped.split(":", 1)
            current_nested_key = key.strip()
            value = value.strip()
            section[current_nested_key] = _parse_scalar(value) if value else []
            continue

        if indent == 4 and stripped.startswith("- "):
            section = data.get(current_key)
            if not isinstance(section, dict) or current_nested_key is None:
                raise SplitPolicyError(f"Nested list without key at line {line_number}")
            nested = section.get(current_nested_key)
            if not isinstance(nested, list):
                raise SplitPolicyError(
                    f"List item under non-list key {current_nested_key} at line {line_number}"
                )
            nested.append(_parse_scalar(stripped[2:]))
            continue

        raise SplitPolicyError(f"Unsupported split config YAML shape at line {line_number}")

    return data


def _require_list_values(
    config: Mapping[str, object],
    key: str,
    expected_values: Iterable[str],
) -> None:
    values = config.get(key)
    if not isinstance(values, list):
        raise SplitPolicyError(f"{key} must be a list")
    missing = [value for value in expected_values if value not in values]
    if missing:
        raise SplitPolicyError(f"{key} missing required values: " + ", ".join(missing))


def validate_split_config(config: Mapping[str, object]) -> None:
    """Validate split config blocks cell-level splitting and requires manifests."""
    split_policy = config.get("split_policy")
    if not isinstance(split_policy, Mapping):
        raise SplitPolicyError("split_policy must be a mapping")

    allowed_units = split_policy.get("allowed_split_units")
    forbidden_units = split_policy.get("forbidden_split_units")
    if not isinstance(allowed_units, list):
        raise SplitPolicyError("split_policy.allowed_split_units must be a list")
    if not isinstance(forbidden_units, list):
        raise SplitPolicyError("split_policy.forbidden_split_units must be a list")

    missing_allowed = [
        unit for unit in REQUIRED_ALLOWED_SPLIT_UNITS if unit not in allowed_units
    ]
    if missing_allowed:
        raise SplitPolicyError(
            "split_policy.allowed_split_units missing: " + ", ".join(missing_allowed)
        )
    missing_forbidden = [
        unit for unit in REQUIRED_FORBIDDEN_SPLIT_UNITS if unit not in forbidden_units
    ]
    if missing_forbidden:
        raise SplitPolicyError(
            "split_policy.forbidden_split_units missing: " + ", ".join(missing_forbidden)
        )

    if split_policy.get("default_split_unit") != "patient_id":
        raise SplitPolicyError("split_policy.default_split_unit must be patient_id")
    if split_policy.get("allow_cell_level_split") is not False:
        raise SplitPolicyError("split_policy.allow_cell_level_split must be false")
    for flag in REQUIRED_TRUE_POLICY_FLAGS:
        if split_policy.get(flag) is not True:
            raise SplitPolicyError(f"split_policy.{flag} must be true")

    _require_list_values(config, "split_types", REQUIRED_SPLIT_TYPES)
    _require_list_values(config, "required_manifest_fields", REQUIRED_MANIFEST_FIELDS)
    _require_list_values(config, "allowed_split_values", ALLOWED_SPLIT_VALUES)


def validate_split_manifest_headers(columns: Sequence[str]) -> None:
    """Validate split manifest columns for header-only or mock report tables."""
    missing = [header for header in SPLIT_MANIFEST_HEADERS if header not in columns]
    if missing:
        raise SplitPolicyError(
            "split_manifest missing required headers: " + ", ".join(missing)
        )


def _overlap(left_ids: Iterable[Any], right_ids: Iterable[Any]) -> list[str]:
    left = {str(value) for value in left_ids if value is not None and value != ""}
    right = {str(value) for value in right_ids if value is not None and value != ""}
    return sorted(left.intersection(right))


def detect_patient_overlap(train_ids: Iterable[Any], test_ids: Iterable[Any]) -> list[str]:
    """Return overlapping patient IDs in mock train/test identifiers."""
    return _overlap(train_ids, test_ids)


def detect_donor_overlap(train_ids: Iterable[Any], test_ids: Iterable[Any]) -> list[str]:
    """Return overlapping donor IDs in mock train/test identifiers."""
    return _overlap(train_ids, test_ids)


def reject_cell_level_split(entity_type: str) -> None:
    """Reject forbidden cell-level or barcode-level split units."""
    normalized = str(entity_type).strip()
    if normalized in REQUIRED_FORBIDDEN_SPLIT_UNITS:
        raise SplitPolicyError(f"{normalized} is forbidden for split manifests")


def validate_mock_split_manifest(
    rows: Sequence[Mapping[str, Any]],
    config: Mapping[str, object] | None = None,
) -> None:
    """Validate mock split manifest rows without creating real split assignments."""
    if config is None:
        config = load_split_config()
    validate_split_config(config)

    split_policy = config["split_policy"]
    if not isinstance(split_policy, Mapping):
        raise SplitPolicyError("split_policy must be a mapping")
    allowed_units = {str(unit) for unit in split_policy["allowed_split_units"]}
    allowed_splits = {str(value) for value in config["allowed_split_values"]}

    split_values_by_entity: dict[str, set[str]] = {}
    for index, row in enumerate(rows, start=1):
        missing = [header for header in SPLIT_MANIFEST_HEADERS if header not in row]
        if missing:
            raise SplitPolicyError(
                f"split manifest row {index} missing headers: " + ", ".join(missing)
            )
        if not row.get("audit_status"):
            raise SplitPolicyError(f"split manifest row {index} missing audit_status")

        entity_type = str(row.get("entity_type", "")).strip()
        reject_cell_level_split(entity_type)
        if entity_type not in allowed_units:
            raise SplitPolicyError(
                f"split manifest row {index} has unsupported entity_type: {entity_type}"
            )

        split_value = str(row.get("split", "")).strip()
        if split_value not in allowed_splits:
            raise SplitPolicyError(
                f"split manifest row {index} has unsupported split value: {split_value}"
            )

        entity_id = str(row.get("entity_id", "")).strip()
        if not entity_id:
            raise SplitPolicyError(f"split manifest row {index} missing entity_id")
        split_values_by_entity.setdefault(entity_id, set()).add(split_value)

    overlapping_entities = sorted(
        entity_id
        for entity_id, split_values in split_values_by_entity.items()
        if {"train", "test"}.issubset(split_values)
    )
    if overlapping_entities:
        raise SplitPolicyError(
            "train/test entity overlap detected: " + ", ".join(overlapping_entities)
        )
