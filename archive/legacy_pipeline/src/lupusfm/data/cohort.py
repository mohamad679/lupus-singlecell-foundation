"""Patient/donor-level cohort summary utilities.

These helpers summarize AnnData/CELLxGENE observation metadata without loading
large matrices, filtering cells, extracting embeddings, or training models.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

from lupusfm.data.labels import (
    ClinicalStatus,
    infer_clinical_status_from_donor_id,
    normalize_donor_id,
)
from lupusfm.data.metadata import DEFAULT_DONOR_COLUMN, get_obs_column_values


CLINICAL_STATUS_ORDER = (
    ClinicalStatus.FLARE,
    ClinicalStatus.MANAGED,
    ClinicalStatus.HEALTHY,
)


@dataclass(frozen=True)
class DonorCellCount:
    """Cell-count summary for one donor."""

    donor_id: str
    clinical_status: ClinicalStatus
    n_cells: int


@dataclass(frozen=True)
class ClinicalStatusCellCount:
    """Donor and cell counts for one clinical-status group."""

    clinical_status: ClinicalStatus
    n_donors: int
    n_cells: int


@dataclass(frozen=True)
class CohortSummary:
    """Compact cohort summary from observation metadata."""

    total_cells: int
    total_donors: int
    donor_counts: tuple[DonorCellCount, ...]
    clinical_status_counts: tuple[ClinicalStatusCellCount, ...]


def _is_missing_metadata_value(value: object) -> bool:
    """Return True for common missing scalar metadata values."""

    if value is None:
        return True

    try:
        return bool(math.isnan(value))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False


def count_cells_by_donor(
    adata: Any,
    donor_column: str = DEFAULT_DONOR_COLUMN,
) -> list[DonorCellCount]:
    """Count cells per donor from ``adata.obs`` preserving first-seen order.

    Donor identifiers are normalized and labeled using the approved project
    donor-id rule. Unknown donor-id patterns fail closed via ``ValueError``.
    """

    donor_cell_counts: dict[str, int] = {}
    donor_statuses: dict[str, ClinicalStatus] = {}

    for row_index, donor_id in enumerate(get_obs_column_values(adata, donor_column)):
        if _is_missing_metadata_value(donor_id):
            raise ValueError(
                f"Missing donor id in adata.obs[{donor_column!r}] at row {row_index}."
            )

        normalized = normalize_donor_id(donor_id)
        clinical_status = infer_clinical_status_from_donor_id(normalized)

        if normalized not in donor_cell_counts:
            donor_cell_counts[normalized] = 0
            donor_statuses[normalized] = clinical_status

        donor_cell_counts[normalized] += 1

    return [
        DonorCellCount(
            donor_id=donor_id,
            clinical_status=donor_statuses[donor_id],
            n_cells=n_cells,
        )
        for donor_id, n_cells in donor_cell_counts.items()
    ]


def summarize_clinical_status_counts(
    adata: Any,
    donor_column: str = DEFAULT_DONOR_COLUMN,
) -> list[ClinicalStatusCellCount]:
    """Summarize donor and cell counts for each clinical-status group."""

    donor_counts = count_cells_by_donor(adata, donor_column=donor_column)
    status_totals = {
        clinical_status: {"n_donors": 0, "n_cells": 0}
        for clinical_status in CLINICAL_STATUS_ORDER
    }

    for donor_count in donor_counts:
        status_totals[donor_count.clinical_status]["n_donors"] += 1
        status_totals[donor_count.clinical_status]["n_cells"] += donor_count.n_cells

    return [
        ClinicalStatusCellCount(
            clinical_status=clinical_status,
            n_donors=status_totals[clinical_status]["n_donors"],
            n_cells=status_totals[clinical_status]["n_cells"],
        )
        for clinical_status in CLINICAL_STATUS_ORDER
    ]


def summarize_cohort_from_obs(
    adata: Any,
    donor_column: str = DEFAULT_DONOR_COLUMN,
) -> CohortSummary:
    """Create a compact donor/status summary from ``adata.obs``."""

    donor_counts = tuple(count_cells_by_donor(adata, donor_column=donor_column))
    clinical_status_counts = tuple(
        summarize_clinical_status_counts(adata, donor_column=donor_column)
    )

    return CohortSummary(
        total_cells=sum(donor_count.n_cells for donor_count in donor_counts),
        total_donors=len(donor_counts),
        donor_counts=donor_counts,
        clinical_status_counts=clinical_status_counts,
    )
