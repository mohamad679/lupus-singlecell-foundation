"""Safe AnnData/CELLxGENE metadata extraction utilities.

These helpers keep dataset-ingestion logic explicit and testable before any
modeling code is allowed to consume patient labels.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import math
from typing import Any

from lupusfm.data.labels import DonorLabel, make_donor_labels, normalize_donor_id


DEFAULT_DONOR_COLUMN = "donor_id"


def _get_obs(adata: Any) -> Any:
    """Return ``adata.obs`` or raise a clear error for non-AnnData objects."""

    if not hasattr(adata, "obs"):
        raise TypeError("Expected an AnnData-like object with an .obs attribute.")

    return adata.obs


def _obs_column_names(obs: Any) -> set[str]:
    """Return available observation column names from DataFrame-like metadata."""

    if hasattr(obs, "columns"):
        return {str(column) for column in obs.columns}

    if isinstance(obs, Mapping):
        return {str(column) for column in obs.keys()}

    raise TypeError(
        "Expected adata.obs to be a pandas DataFrame-like object or a Mapping."
    )


def require_obs_columns(adata: Any, required_columns: Iterable[str]) -> tuple[str, ...]:
    """Validate that required columns exist in ``adata.obs``.

    Parameters
    ----------
    adata:
        AnnData-like object with an ``obs`` metadata table.
    required_columns:
        Column names that must be present.

    Returns
    -------
    tuple[str, ...]
        Normalized required column names, preserving input order.

    Raises
    ------
    TypeError
        If the object is not AnnData-like or ``obs`` is not table-like.
    ValueError
        If one or more required columns are missing.
    """

    obs = _get_obs(adata)
    required = tuple(str(column) for column in required_columns)
    available = _obs_column_names(obs)
    missing = tuple(column for column in required if column not in available)

    if missing:
        missing_text = ", ".join(repr(column) for column in missing)
        raise ValueError(f"Missing required adata.obs column(s): {missing_text}.")

    return required


def get_obs_column_values(adata: Any, column: str) -> list[object]:
    """Return values from one ``adata.obs`` column as a Python list."""

    require_obs_columns(adata, [column])
    values = _get_obs(adata)[column]

    if hasattr(values, "tolist"):
        values = values.tolist()

    if isinstance(values, str | bytes):
        raise TypeError(
            f"Expected adata.obs[{column!r}] to contain row values, not a scalar."
        )

    return list(values)


def _is_missing_metadata_value(value: object) -> bool:
    """Return True for common missing scalar metadata values."""

    if value is None:
        return True

    try:
        return bool(math.isnan(value))  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False


def extract_donor_ids(
    adata: Any,
    donor_column: str = DEFAULT_DONOR_COLUMN,
) -> list[str]:
    """Extract unique donor IDs from ``adata.obs`` preserving first-seen order."""

    donor_ids: list[str] = []
    seen: set[str] = set()

    for row_index, donor_id in enumerate(get_obs_column_values(adata, donor_column)):
        if _is_missing_metadata_value(donor_id):
            raise ValueError(
                f"Missing donor id in adata.obs[{donor_column!r}] at row {row_index}."
            )

        normalized = normalize_donor_id(donor_id)
        if normalized not in seen:
            donor_ids.append(normalized)
            seen.add(normalized)

    return donor_ids


def make_donor_labels_from_obs(
    adata: Any,
    donor_column: str = DEFAULT_DONOR_COLUMN,
) -> list[DonorLabel]:
    """Create project donor-label records from an AnnData ``obs`` table."""

    return make_donor_labels(extract_donor_ids(adata, donor_column=donor_column))
