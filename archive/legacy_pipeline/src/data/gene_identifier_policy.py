"""Gene identifier policy utilities.

These helpers validate a static gene identifier policy and mock gene tables.
They do not load real datasets, download references, map genes, preprocess
matrices, create AnnData objects, or perform modeling.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY_PATH = REPO_ROOT / "metadata" / "gene_identifier_policy.yaml"

REQUIRED_TOP_LEVEL_KEYS = [
    "schema_version",
    "canonical_gene_fields",
    "policy_rules",
    "foundation_model_requirements",
    "pathway_analysis_requirements",
]
REQUIRED_POLICY_RULES = [
    "preserve_original_gene_ids",
    "preserve_original_gene_symbols",
    "require_unique_var_index",
    "forbid_silent_gene_drop",
    "forbid_silent_duplicate_collapse",
    "require_mapping_report",
    "require_unmapped_gene_report",
    "require_duplicate_gene_report",
    "allowed_unknown_value",
]
REQUIRED_FOUNDATION_MODEL_REQUIREMENTS = [
    "track_gene_vocabulary_overlap",
    "require_model_vocab_version",
    "require_unmatched_vocab_report",
]
REQUIRED_PATHWAY_REQUIREMENTS = [
    "require_valid_gene_symbols",
    "require_multiple_testing_correction_later",
    "forbid_pathway_claims_without_mapping",
]


class GeneIdentifierPolicyError(ValueError):
    """Raised when gene identifier policy validation fails."""


def load_gene_identifier_policy(
    path: Path | str = DEFAULT_POLICY_PATH,
) -> Dict[str, Any]:
    """Load the JSON-compatible YAML policy without extra dependencies."""
    policy_path = Path(path)
    try:
        policy = json.loads(policy_path.read_text())
    except json.JSONDecodeError as exc:
        raise GeneIdentifierPolicyError(
            f"{policy_path} must use JSON-compatible YAML syntax"
        ) from exc
    if not isinstance(policy, dict):
        raise GeneIdentifierPolicyError("gene identifier policy must be a mapping")
    validate_gene_policy(policy)
    return policy


def validate_gene_policy(policy: Mapping[str, Any]) -> None:
    """Validate required policy sections and safety-critical rules."""
    missing = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in policy]
    if missing:
        raise GeneIdentifierPolicyError(
            "gene identifier policy missing required keys: " + ", ".join(missing)
        )

    canonical_fields = policy.get("canonical_gene_fields")
    if not isinstance(canonical_fields, list) or not canonical_fields:
        raise GeneIdentifierPolicyError("canonical_gene_fields must be a non-empty list")

    policy_rules = policy.get("policy_rules")
    if not isinstance(policy_rules, Mapping):
        raise GeneIdentifierPolicyError("policy_rules must be a mapping")
    missing_rules = [rule for rule in REQUIRED_POLICY_RULES if rule not in policy_rules]
    if missing_rules:
        raise GeneIdentifierPolicyError(
            "policy_rules missing required rules: " + ", ".join(missing_rules)
        )

    true_required_rules = [
        "preserve_original_gene_ids",
        "preserve_original_gene_symbols",
        "require_unique_var_index",
        "forbid_silent_gene_drop",
        "forbid_silent_duplicate_collapse",
        "require_mapping_report",
        "require_unmapped_gene_report",
        "require_duplicate_gene_report",
    ]
    disabled_rules = [
        rule for rule in true_required_rules if policy_rules.get(rule) is not True
    ]
    if disabled_rules:
        raise GeneIdentifierPolicyError(
            "safety-critical gene policy rules must be true: "
            + ", ".join(disabled_rules)
        )

    foundation_requirements = policy.get("foundation_model_requirements")
    if not isinstance(foundation_requirements, Mapping):
        raise GeneIdentifierPolicyError("foundation_model_requirements must be a mapping")
    missing_foundation = [
        key
        for key in REQUIRED_FOUNDATION_MODEL_REQUIREMENTS
        if key not in foundation_requirements
    ]
    if missing_foundation:
        raise GeneIdentifierPolicyError(
            "foundation_model_requirements missing keys: "
            + ", ".join(missing_foundation)
        )
    disabled_foundation = [
        key
        for key in REQUIRED_FOUNDATION_MODEL_REQUIREMENTS
        if foundation_requirements.get(key) is not True
    ]
    if disabled_foundation:
        raise GeneIdentifierPolicyError(
            "foundation model requirements must be true: "
            + ", ".join(disabled_foundation)
        )

    pathway_requirements = policy.get("pathway_analysis_requirements")
    if not isinstance(pathway_requirements, Mapping):
        raise GeneIdentifierPolicyError("pathway_analysis_requirements must be a mapping")
    missing_pathway = [
        key for key in REQUIRED_PATHWAY_REQUIREMENTS if key not in pathway_requirements
    ]
    if missing_pathway:
        raise GeneIdentifierPolicyError(
            "pathway_analysis_requirements missing keys: "
            + ", ".join(missing_pathway)
        )
    disabled_pathway = [
        key
        for key in REQUIRED_PATHWAY_REQUIREMENTS
        if pathway_requirements.get(key) is not True
    ]
    if disabled_pathway:
        raise GeneIdentifierPolicyError(
            "pathway analysis requirements must be true: "
            + ", ".join(disabled_pathway)
        )


def _columns_from_rows_or_columns(rows_or_columns: Any) -> set[str]:
    if isinstance(rows_or_columns, Mapping):
        if "columns" in rows_or_columns:
            columns = rows_or_columns["columns"]
            if isinstance(columns, Mapping):
                return {str(column) for column in columns.keys()}
            return {str(column) for column in columns}
        return {str(column) for column in rows_or_columns.keys()}

    if isinstance(rows_or_columns, Sequence) and not isinstance(
        rows_or_columns, (str, bytes)
    ):
        if not rows_or_columns:
            return set()
        if all(isinstance(item, str) for item in rows_or_columns):
            return {str(item) for item in rows_or_columns}
        columns: set[str] = set()
        for row in rows_or_columns:
            if not isinstance(row, Mapping):
                raise GeneIdentifierPolicyError(
                    "gene table rows must be mappings when rows are supplied"
                )
            columns.update(str(column) for column in row.keys())
        return columns

    raise GeneIdentifierPolicyError("gene table must be columns, a mapping, or row mappings")


def validate_gene_table_schema(
    rows_or_columns: Any,
    policy: Mapping[str, Any],
) -> None:
    """Validate mock gene-table columns against canonical gene fields."""
    validate_gene_policy(policy)
    required_fields = {str(field) for field in policy["canonical_gene_fields"]}
    columns = _columns_from_rows_or_columns(rows_or_columns)
    missing = sorted(required_fields.difference(columns))
    if missing:
        raise GeneIdentifierPolicyError(
            "gene table missing required fields: " + ", ".join(missing)
        )


def detect_duplicate_gene_symbols(gene_symbols: Iterable[Any]) -> list[str]:
    """Return duplicate non-empty mock gene symbols without collapsing them."""
    normalized_symbols = [
        str(symbol)
        for symbol in gene_symbols
        if symbol is not None and str(symbol) not in {"", "TODO", "unclear"}
    ]
    counts = Counter(normalized_symbols)
    return sorted(symbol for symbol, count in counts.items() if count > 1)


def summarize_gene_mapping_status(rows: Sequence[Mapping[str, Any]]) -> Dict[str, int]:
    """Summarize already-provided mock gene mapping statuses.

    This function does not map identifiers. It only counts fields present in
    caller-supplied mock report rows.
    """
    summary = {
        "total_rows": 0,
        "mapped_rows": 0,
        "unmapped_rows": 0,
        "duplicate_rows": 0,
        "foundation_vocab_matches": 0,
        "pathway_eligible_rows": 0,
    }
    for row in rows:
        if not isinstance(row, Mapping):
            raise GeneIdentifierPolicyError("mapping summary rows must be mappings")
        summary["total_rows"] += 1
        if str(row.get("mapping_status", "")).lower() == "mapped":
            summary["mapped_rows"] += 1
        if str(row.get("unmapped_flag", "")).lower() in {"true", "yes", "1"}:
            summary["unmapped_rows"] += 1
        if str(row.get("duplicate_flag", "")).lower() in {"true", "yes", "1"}:
            summary["duplicate_rows"] += 1
        if str(row.get("foundation_vocab_match", "")).lower() in {"true", "yes", "1"}:
            summary["foundation_vocab_matches"] += 1
        if str(row.get("pathway_eligible", "")).lower() in {"true", "yes", "1"}:
            summary["pathway_eligible_rows"] += 1
    return summary
