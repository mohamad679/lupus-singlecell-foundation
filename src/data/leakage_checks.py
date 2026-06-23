"""Mock-only leakage prevention checks.

These utilities validate row dictionaries supplied by tests or future scaffold
code. They do not read real data files, create split manifests, preprocess
datasets, create AnnData outputs, download data, or perform modeling.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, Mapping, Sequence


FORBIDDEN_ENTITY_TYPES = {"cell_id", "barcode"}
MISSING_VALUES = {"", "TODO", "unclear", "None", "none", "null"}


class LeakageCheckError(ValueError):
    """Raised when a mock leakage check fails."""


def _known(value: Any) -> bool:
    return value is not None and str(value).strip() not in MISSING_VALUES


def _split_value(row: Mapping[str, Any]) -> str:
    return str(row.get("split", "")).strip()


def _require_audit_status(rows: Sequence[Mapping[str, Any]]) -> None:
    missing_rows = [
        str(index)
        for index, row in enumerate(rows, start=1)
        if not str(row.get("audit_status", "")).strip()
    ]
    if missing_rows:
        raise LeakageCheckError(
            "audit_status is required for rows: " + ", ".join(missing_rows)
        )


def check_no_overlap(
    train_ids: Iterable[Any],
    test_ids: Iterable[Any],
    entity_name: str,
) -> None:
    """Reject overlap between mock train and test IDs for a named entity."""
    train = {str(value) for value in train_ids if _known(value)}
    test = {str(value) for value in test_ids if _known(value)}
    overlap = sorted(train.intersection(test))
    if overlap:
        raise LeakageCheckError(
            f"{entity_name} overlap between train and test: " + ", ".join(overlap)
        )


def _check_entity_one_split(rows: Sequence[Mapping[str, Any]], field: str) -> None:
    splits_by_entity: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        value = row.get(field)
        if _known(value):
            splits_by_entity[str(value).strip()].add(_split_value(row))

    overlapping = sorted(
        entity_id
        for entity_id, splits in splits_by_entity.items()
        if len({split for split in splits if split}) > 1
    )
    if overlapping:
        raise LeakageCheckError(
            f"{field} appears in multiple splits: " + ", ".join(overlapping)
        )


def check_no_patient_overlap(rows: Sequence[Mapping[str, Any]]) -> None:
    """Reject any patient_id appearing in more than one split."""
    _check_entity_one_split(rows, "patient_id")


def check_no_donor_overlap(rows: Sequence[Mapping[str, Any]]) -> None:
    """Reject any donor_id appearing in more than one split."""
    _check_entity_one_split(rows, "donor_id")


def check_no_sample_overlap(rows: Sequence[Mapping[str, Any]]) -> None:
    """Reject any sample_id appearing in more than one split."""
    _check_entity_one_split(rows, "sample_id")


def check_no_cell_level_split(rows: Sequence[Mapping[str, Any]]) -> None:
    """Reject cell-level or barcode-level split entity types."""
    forbidden_rows = []
    for index, row in enumerate(rows, start=1):
        entity_type = str(row.get("entity_type", "")).strip()
        if entity_type in FORBIDDEN_ENTITY_TYPES:
            forbidden_rows.append(f"row {index}: {entity_type}")
    if forbidden_rows:
        raise LeakageCheckError(
            "cell-level or barcode-level split entities are forbidden: "
            + ", ".join(forbidden_rows)
        )


def check_no_duplicate_cell_ids(rows: Sequence[Mapping[str, Any]]) -> None:
    """Reject duplicated cell_id values appearing across multiple splits."""
    splits_by_cell: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        cell_id = row.get("cell_id")
        if _known(cell_id):
            splits_by_cell[str(cell_id).strip()].add(_split_value(row))

    duplicated_across_splits = sorted(
        cell_id
        for cell_id, splits in splits_by_cell.items()
        if len({split for split in splits if split}) > 1
    )
    if duplicated_across_splits:
        raise LeakageCheckError(
            "duplicated cell_id values across splits: "
            + ", ".join(duplicated_across_splits)
        )


def check_no_cohort_contamination(rows: Sequence[Mapping[str, Any]]) -> None:
    """Reject cohorts shared between training-like and holdout/external splits."""
    splits_by_cohort: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        cohort_id = row.get("cohort_id")
        if _known(cohort_id):
            splits_by_cohort[str(cohort_id).strip()].add(_split_value(row))

    training_splits = {"train", "validation", "test"}
    holdout_splits = {"external_validation", "holdout"}
    contaminated = sorted(
        cohort_id
        for cohort_id, splits in splits_by_cohort.items()
        if splits.intersection(training_splits) and splits.intersection(holdout_splits)
    )
    if contaminated:
        raise LeakageCheckError(
            "cohort contamination detected across training and holdout/external splits: "
            + ", ".join(contaminated)
        )


def check_no_batch_confounding(rows: Sequence[Mapping[str, Any]]) -> None:
    """Fail when any split has only one known batch_id."""
    batches_by_split: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        split = _split_value(row)
        batch_id = row.get("batch_id")
        if split and _known(batch_id):
            batches_by_split[split].add(str(batch_id).strip())

    confounded = sorted(
        split for split, batches in batches_by_split.items() if len(batches) == 1
    )
    if confounded:
        raise LeakageCheckError(
            "batch confounding detected; split has only one batch_id: "
            + ", ".join(confounded)
        )


def check_no_label_leakage(rows: Sequence[Mapping[str, Any]]) -> None:
    """Fail when labels are perfectly tied to split membership."""
    labels_by_split: dict[str, set[str]] = defaultdict(set)
    splits_by_label: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        split = _split_value(row)
        label = row.get("disease_label")
        if split and _known(label):
            label_value = str(label).strip()
            labels_by_split[split].add(label_value)
            splits_by_label[label_value].add(split)

    if len(labels_by_split) < 2 or len(splits_by_label) < 2:
        return

    labels_are_split_specific = all(len(splits) == 1 for splits in splits_by_label.values())
    split_label_sets = list(labels_by_split.values())
    split_sets_are_disjoint = all(
        not left.intersection(right)
        for left_index, left in enumerate(split_label_sets)
        for right in split_label_sets[left_index + 1 :]
    )
    if labels_are_split_specific and split_sets_are_disjoint:
        raise LeakageCheckError("label leakage detected; disease_label is tied to split")


def run_all_leakage_checks(rows: Sequence[Mapping[str, Any]]) -> Dict[str, object]:
    """Run all mock leakage checks and return PASS/FAIL status."""
    checks = [
        _require_audit_status,
        check_no_cell_level_split,
        check_no_patient_overlap,
        check_no_donor_overlap,
        check_no_sample_overlap,
        check_no_duplicate_cell_ids,
        check_no_cohort_contamination,
        check_no_batch_confounding,
        check_no_label_leakage,
    ]
    errors = []
    for check in checks:
        try:
            check(rows)
        except LeakageCheckError as exc:
            errors.append(str(exc))

    return {
        "status": "FAIL" if errors else "PASS",
        "errors": errors,
        "checked_rows": len(rows),
    }
