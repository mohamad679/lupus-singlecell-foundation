"""Patient-level clinical label extraction for the lupus CELLxGENE cohort.

The current primary cohort uses donor identifiers with the following
project-specific convention:

- FLARE* donors are active flare patients.
- HC-* and IGTB* donors are healthy controls.
- purely numeric donor identifiers are managed SLE patients.

These functions intentionally fail closed for unknown donor-id patterns so
that label drift is caught during dataset ingestion instead of silently
creating incorrect supervision targets.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Iterable


class ClinicalStatus(str, Enum):
    """Patient-level clinical status used by the current project."""

    FLARE = "Flare"
    HEALTHY = "Healthy"
    MANAGED = "Managed"


@dataclass(frozen=True)
class DonorLabel:
    """Resolved label for one donor identifier."""

    donor_id: str
    clinical_status: ClinicalStatus


_FLARE_RE = re.compile(r"^FLARE", re.IGNORECASE)
_HEALTHY_HC_RE = re.compile(r"^HC-", re.IGNORECASE)
_HEALTHY_IGTB_RE = re.compile(r"^IGTB", re.IGNORECASE)
_MANAGED_RE = re.compile(r"^[0-9]+$")


def normalize_donor_id(donor_id: object) -> str:
    """Return a cleaned donor identifier or raise for missing values."""

    if donor_id is None:
        raise ValueError("donor_id must not be None")

    normalized = str(donor_id).strip()
    if not normalized:
        raise ValueError("donor_id must not be empty")

    return normalized


def infer_clinical_status_from_donor_id(donor_id: object) -> ClinicalStatus:
    """Infer the project clinical label from a donor identifier.

    Parameters
    ----------
    donor_id:
        Donor identifier from the CELLxGENE/Perez lupus cohort metadata.

    Returns
    -------
    ClinicalStatus
        Flare, Healthy, or Managed.

    Raises
    ------
    ValueError
        If the donor identifier does not match the approved project rules.
    """

    normalized = normalize_donor_id(donor_id)

    if _FLARE_RE.match(normalized):
        return ClinicalStatus.FLARE

    if _HEALTHY_HC_RE.match(normalized) or _HEALTHY_IGTB_RE.match(normalized):
        return ClinicalStatus.HEALTHY

    if _MANAGED_RE.match(normalized):
        return ClinicalStatus.MANAGED

    raise ValueError(
        "Unrecognized donor_id pattern. Expected FLARE*, HC-*, IGTB*, "
        f"or numeric managed-SLE identifier; got {normalized!r}."
    )


def make_donor_label(donor_id: object) -> DonorLabel:
    """Create a donor-label record from one donor identifier."""

    normalized = normalize_donor_id(donor_id)
    return DonorLabel(
        donor_id=normalized,
        clinical_status=infer_clinical_status_from_donor_id(normalized),
    )


def make_donor_labels(donor_ids: Iterable[object]) -> list[DonorLabel]:
    """Create donor-label records for an iterable of donor identifiers."""

    return [make_donor_label(donor_id) for donor_id in donor_ids]
