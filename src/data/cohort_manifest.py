"""Cohort manifest schema and mock-row validation utilities.

These helpers validate a central cohort manifest schema and caller-supplied
mock rows. They do not download datasets, preprocess data, create AnnData
outputs, approve cohorts, assign official training/external validation roles,
or modify selected datasets.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "metadata" / "cohort_manifest_schema.yaml"

REQUIRED_TOP_LEVEL_KEYS = ["schema_version", "required_fields", "fields"]
FIELD_SPEC_KEYS = [
    "description",
    "required",
    "allowed_values",
    "allowed_missing",
    "provenance_required",
]
ALLOWED_INTENDED_ROLES = {
    "candidate_training",
    "candidate_external_validation",
    "candidate_reference",
    "TODO",
}
SAFE_UNAPPROVED_ROLES = {"TODO", "none"}
APPROVED_ROLES_REQUIRING_GATE = {"training", "external_validation", "reference"}


class CohortManifestError(ValueError):
    """Raised when cohort manifest schema or row validation fails."""


def load_cohort_manifest_schema(
    path: Path | str = DEFAULT_SCHEMA_PATH,
) -> Dict[str, Any]:
    """Load JSON-compatible YAML schema without external dependencies."""
    schema_path = Path(path)
    try:
        schema = json.loads(schema_path.read_text())
    except json.JSONDecodeError as exc:
        raise CohortManifestError(
            f"{schema_path} must use JSON-compatible YAML syntax"
        ) from exc
    if not isinstance(schema, dict):
        raise CohortManifestError("cohort manifest schema must be a mapping")
    validate_cohort_manifest_schema(schema)
    return schema


def validate_cohort_manifest_schema(schema: Mapping[str, Any]) -> None:
    """Validate required schema sections and field specifications."""
    missing_keys = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in schema]
    if missing_keys:
        raise CohortManifestError(
            "cohort manifest schema missing required keys: " + ", ".join(missing_keys)
        )

    required_fields = schema.get("required_fields")
    fields = schema.get("fields")
    if not isinstance(required_fields, list) or not required_fields:
        raise CohortManifestError("required_fields must be a non-empty list")
    if not isinstance(fields, Mapping) or not fields:
        raise CohortManifestError("fields must be a non-empty mapping")

    missing_field_specs = [field for field in required_fields if field not in fields]
    if missing_field_specs:
        raise CohortManifestError(
            "fields missing required field specs: " + ", ".join(missing_field_specs)
        )

    invalid_specs = []
    for field_name in required_fields:
        field_spec = fields[field_name]
        if not isinstance(field_spec, Mapping):
            invalid_specs.append(str(field_name))
            continue
        missing_spec_keys = [key for key in FIELD_SPEC_KEYS if key not in field_spec]
        if missing_spec_keys:
            invalid_specs.append(f"{field_name} missing {', '.join(missing_spec_keys)}")
    if invalid_specs:
        raise CohortManifestError(
            "invalid cohort manifest field specs: " + "; ".join(invalid_specs)
        )


def validate_cohort_manifest_headers(
    columns: Sequence[str],
    schema: Mapping[str, Any],
) -> None:
    """Validate manifest headers against schema required fields."""
    validate_cohort_manifest_schema(schema)
    required_fields = [str(field) for field in schema["required_fields"]]
    missing = [field for field in required_fields if field not in columns]
    if missing:
        raise CohortManifestError(
            "cohort manifest missing required headers: " + ", ".join(missing)
        )


def _missing(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "yes", "1"}


def reject_approved_roles_without_human_gate(
    rows: Sequence[Mapping[str, Any]],
) -> None:
    """Reject approved roles unless human_gate_approved is explicitly true."""
    violations = []
    for index, row in enumerate(rows, start=1):
        approved_role = str(row.get("approved_role", "")).strip()
        if approved_role in SAFE_UNAPPROVED_ROLES:
            continue
        if approved_role in APPROVED_ROLES_REQUIRING_GATE and _as_bool(
            row.get("human_gate_approved")
        ):
            continue
        violations.append(f"row {index}: {approved_role or 'missing'}")
    if violations:
        raise CohortManifestError(
            "approved_role requires explicit human_gate_approved=true: "
            + ", ".join(violations)
        )


def validate_cohort_manifest_rows(
    rows: Sequence[Mapping[str, Any]],
    schema: Mapping[str, Any],
) -> None:
    """Validate mock manifest rows without approving or assigning cohorts."""
    validate_cohort_manifest_schema(schema)
    required_fields = [str(field) for field in schema["required_fields"]]
    fields = schema["fields"]

    for index, row in enumerate(rows, start=1):
        missing_columns = [field for field in required_fields if field not in row]
        if missing_columns:
            raise CohortManifestError(
                f"cohort manifest row {index} missing fields: "
                + ", ".join(missing_columns)
            )

        for field_name in required_fields:
            field_spec = fields[field_name]
            value = row.get(field_name)
            if field_spec.get("required") and not field_spec.get("allowed_missing"):
                if _missing(value):
                    raise CohortManifestError(
                        f"cohort manifest row {index} missing required value: {field_name}"
                    )

            allowed_values = field_spec.get("allowed_values", [])
            if allowed_values and not _missing(value):
                if str(value).strip() not in allowed_values:
                    raise CohortManifestError(
                        f"cohort manifest row {index} has invalid {field_name}: {value}"
                    )

        intended_role = str(row.get("intended_role", "")).strip()
        if intended_role not in ALLOWED_INTENDED_ROLES:
            raise CohortManifestError(
                f"cohort manifest row {index} has invalid intended_role: {intended_role}"
            )
        if not str(row.get("audit_status", "")).strip():
            raise CohortManifestError(f"cohort manifest row {index} missing audit_status")
        if not str(row.get("provenance_url", "")).strip():
            raise CohortManifestError(
                f"cohort manifest row {index} missing provenance_url"
            )
        if _as_bool(row.get("selected_dataset")):
            raise CohortManifestError(
                f"cohort manifest row {index} attempts selected dataset assignment"
            )

    reject_approved_roles_without_human_gate(rows)
