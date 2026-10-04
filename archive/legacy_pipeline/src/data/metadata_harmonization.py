"""Metadata harmonization schema utilities.

These helpers validate schema contracts and mock canonical metadata records.
They do not load datasets, preprocess matrices, create AnnData objects, query
remote services, or perform modeling.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "metadata" / "metadata_harmonization_schema.yaml"
DEFAULT_MAPPING_PATH = REPO_ROOT / "metadata" / "source_field_mapping.yaml"

REQUIRED_SCHEMA_KEYS = ["schema_version", "allowed_unknown_values", "canonical_fields"]
REQUIRED_MAPPING_SOURCES = ["GEO", "CELLxGENE", "HCA"]
REQUIRED_MAPPING_KEYS = ["original_field", "canonical_field", "transformation", "notes"]
FORBIDDEN_SPLIT_VALUES = {"cell", "cell_level", "cell_level_split", "random_cell_split"}


class MetadataHarmonizationError(ValueError):
    """Raised when metadata harmonization validation fails."""


def _load_json_yaml(path: Path | str) -> Dict[str, Any]:
    """Load JSON-compatible YAML without adding a PyYAML dependency."""
    file_path = Path(path)
    try:
        payload = json.loads(file_path.read_text())
    except json.JSONDecodeError as exc:
        raise MetadataHarmonizationError(
            f"{file_path} must use JSON-compatible YAML syntax"
        ) from exc
    if not isinstance(payload, dict):
        raise MetadataHarmonizationError(f"{file_path} must define a mapping")
    return payload


def load_harmonization_schema(
    path: Path | str = DEFAULT_SCHEMA_PATH,
) -> Dict[str, Any]:
    """Load and validate the canonical metadata harmonization schema."""
    schema = _load_json_yaml(path)
    missing = [key for key in REQUIRED_SCHEMA_KEYS if key not in schema]
    if missing:
        raise MetadataHarmonizationError(
            "Harmonization schema missing required keys: " + ", ".join(missing)
        )

    canonical_fields = schema.get("canonical_fields")
    if not isinstance(canonical_fields, Mapping) or not canonical_fields:
        raise MetadataHarmonizationError("canonical_fields must be a non-empty mapping")

    required_field_keys = [
        "description",
        "required",
        "allowed_missing",
        "source_priority",
        "harmonization_notes",
    ]
    invalid_fields = []
    for field_name, field_spec in canonical_fields.items():
        if not isinstance(field_spec, Mapping):
            invalid_fields.append(str(field_name))
            continue
        missing_keys = [key for key in required_field_keys if key not in field_spec]
        if missing_keys:
            invalid_fields.append(f"{field_name} missing {', '.join(missing_keys)}")
    if invalid_fields:
        raise MetadataHarmonizationError(
            "Invalid canonical field specifications: " + "; ".join(invalid_fields)
        )

    return schema


def load_source_mapping(path: Path | str = DEFAULT_MAPPING_PATH) -> Dict[str, Any]:
    """Load and validate source-to-canonical metadata mapping placeholders."""
    mapping = _load_json_yaml(path)
    missing_sources = [source for source in REQUIRED_MAPPING_SOURCES if source not in mapping]
    if missing_sources:
        raise MetadataHarmonizationError(
            "Source mapping missing sections: " + ", ".join(missing_sources)
        )

    for source in REQUIRED_MAPPING_SOURCES:
        entries = mapping[source]
        if not isinstance(entries, list) or not entries:
            raise MetadataHarmonizationError(f"{source} mapping must be a non-empty list")
        for entry in entries:
            if not isinstance(entry, Mapping):
                raise MetadataHarmonizationError(f"{source} mapping entries must be mappings")
            missing_keys = [key for key in REQUIRED_MAPPING_KEYS if key not in entry]
            if missing_keys:
                raise MetadataHarmonizationError(
                    f"{source} mapping entry missing keys: " + ", ".join(missing_keys)
                )

    return mapping


def _metadata_columns(metadata: Mapping[str, Any]) -> Mapping[str, Any]:
    columns = metadata.get("columns")
    if isinstance(columns, Mapping):
        return columns
    return metadata


def _values(value: Any) -> Sequence[Any]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return list(value)
    return [value]


def _contains_missing(values: Iterable[Any], unknown_values: set[str]) -> bool:
    for value in values:
        if value is None or value == "":
            return True
        if isinstance(value, str) and value in unknown_values:
            return True
    return False


def validate_canonical_metadata(
    metadata: Mapping[str, Any],
    schema: Mapping[str, Any] | None = None,
) -> None:
    """Validate dictionary/mock canonical metadata against the schema.

    Required canonical fields must be present. Fields marked
    ``allowed_missing: false`` cannot contain ``TODO``, ``unclear``, empty
    strings, or null values.
    """
    if schema is None:
        schema = load_harmonization_schema()

    canonical_fields = schema.get("canonical_fields")
    if not isinstance(canonical_fields, Mapping):
        raise MetadataHarmonizationError("schema canonical_fields must be a mapping")

    columns = _metadata_columns(metadata)
    unknown_values = {str(value) for value in schema.get("allowed_unknown_values", [])}
    required_missing = []
    invalid_missing_values = []

    for field_name, field_spec in canonical_fields.items():
        if not isinstance(field_spec, Mapping):
            raise MetadataHarmonizationError(f"{field_name} schema entry is invalid")
        if not field_spec.get("required", False):
            continue
        if field_name not in columns:
            required_missing.append(str(field_name))
            continue
        if not field_spec.get("allowed_missing", False) and _contains_missing(
            _values(columns[field_name]), unknown_values
        ):
            invalid_missing_values.append(str(field_name))

    if required_missing:
        raise MetadataHarmonizationError(
            "metadata missing required canonical fields: " + ", ".join(required_missing)
        )
    if invalid_missing_values:
        raise MetadataHarmonizationError(
            "metadata has unresolved values for required fields: "
            + ", ".join(invalid_missing_values)
        )

    if "split_group" in columns:
        split_values = {str(value) for value in _values(columns["split_group"])}
        if split_values.intersection(FORBIDDEN_SPLIT_VALUES):
            raise MetadataHarmonizationError("cell-level split_group values are forbidden")
