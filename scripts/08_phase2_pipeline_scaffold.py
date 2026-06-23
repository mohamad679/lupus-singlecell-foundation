"""Validate Phase 2 data pipeline scaffold restrictions.

This script reads local configuration only. It does not download data,
preprocess data, create AnnData objects, or perform modeling.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List


REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "configs" / "data_pipeline.yaml"

REQUIRED_TRUE_FIELDS = ["forbid_cell_level_split"]
REQUIRED_FALSE_FIELDS = ["allow_downloads", "allow_modeling"]
REQUIRED_METADATA_FIELDS = [
    "patient_id",
    "donor_id",
    "sample_id",
    "cohort_id",
    "batch_id",
    "disease_label",
    "tissue",
    "assay_type",
]


class Phase2ScaffoldError(ValueError):
    """Raised when Phase 2 scaffold config violates safety controls."""


def _parse_scalar(value: str) -> object:
    normalized = value.strip()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    if normalized.isdigit():
        return int(normalized)
    return normalized


def load_simple_yaml(path: Path) -> Dict[str, object]:
    """Parse the small top-level scalar/list YAML shape used by this config."""
    data: Dict[str, object] = {}
    current_key: str | None = None

    for line_number, raw_line in enumerate(path.read_text().splitlines(), start=1):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        if not raw_line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            value = value.strip()
            data[current_key] = _parse_scalar(value) if value else []
            continue

        if line.startswith("  - "):
            if current_key is None:
                raise Phase2ScaffoldError(f"List item without key at line {line_number}")
            section = data.setdefault(current_key, [])
            if not isinstance(section, list):
                raise Phase2ScaffoldError(
                    f"List item under scalar key {current_key} at line {line_number}"
                )
            section.append(_parse_scalar(line[4:]))
            continue

        raise Phase2ScaffoldError(
            f"Unsupported YAML shape at line {line_number}: {raw_line}"
        )

    return data


def validate_config(config: Dict[str, object]) -> Dict[str, object]:
    if config.get("phase") != 2:
        raise Phase2ScaffoldError("phase must be 2")

    for field in REQUIRED_FALSE_FIELDS:
        if config.get(field) is not False:
            raise Phase2ScaffoldError(f"{field} must be false")

    for field in REQUIRED_TRUE_FIELDS:
        if config.get(field) is not True:
            raise Phase2ScaffoldError(f"{field} must be true")

    if config.get("split_policy") != "patient_or_cohort_only":
        raise Phase2ScaffoldError("split_policy must be patient_or_cohort_only")

    allowed = config.get("allowed_candidate_datasets")
    restricted = config.get("restricted_candidate_datasets")
    required_metadata = config.get("required_future_metadata")

    if not isinstance(allowed, list) or not allowed:
        raise Phase2ScaffoldError("allowed_candidate_datasets must be a non-empty list")
    if not isinstance(restricted, list) or not restricted:
        raise Phase2ScaffoldError("restricted_candidate_datasets must be a non-empty list")
    if not isinstance(required_metadata, list):
        raise Phase2ScaffoldError("required_future_metadata must be a list")

    missing_metadata: List[str] = [
        field for field in REQUIRED_METADATA_FIELDS if field not in required_metadata
    ]
    if missing_metadata:
        raise Phase2ScaffoldError(
            "required_future_metadata missing: " + ", ".join(missing_metadata)
        )

    return {
        "phase": config["phase"],
        "allowed_candidate_count": len(allowed),
        "restricted_candidate_count": len(restricted),
        "allow_downloads": config["allow_downloads"],
        "allow_modeling": config["allow_modeling"],
        "split_policy": config["split_policy"],
        "forbid_cell_level_split": config["forbid_cell_level_split"],
    }


def run_validation(config_path: Path = CONFIG_PATH) -> Dict[str, object]:
    config = load_simple_yaml(config_path)
    return validate_config(config)


def main() -> int:
    summary = run_validation()
    print("Phase 2 scaffold validation passed")
    for key, value in summary.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
