"""Explicit mitochondrial-gene detection utilities.

Mitochondrial-gene annotation is intentionally based on a caller-declared
gene-symbol column from ``adata.var``. These helpers do not silently fall back
to ``adata.var_names`` because CELLxGENE/AnnData indices are not guaranteed to
be human-readable gene symbols.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any


DEFAULT_MITO_PREFIX = "MT-"


class MitochondrialGeneAnnotationError(ValueError):
    """Raised when mitochondrial gene annotation cannot be performed safely."""


def _get_var(adata: Any) -> Any:
    """Return ``adata.var`` or raise a clear error for non-AnnData objects."""

    if not hasattr(adata, "var"):
        raise TypeError("Expected an AnnData-like object with a .var attribute.")

    return adata.var


def _var_column_names(var: Any) -> set[str]:
    """Return available variable/gene column names from table-like metadata."""

    if hasattr(var, "columns"):
        return {str(column) for column in var.columns}

    if isinstance(var, Mapping):
        return {str(column) for column in var.keys()}

    raise TypeError(
        "Expected adata.var to be a pandas DataFrame-like object or a Mapping."
    )


def require_var_columns(adata: Any, required_columns: Iterable[str]) -> tuple[str, ...]:
    """Validate that required columns exist in ``adata.var``."""

    var = _get_var(adata)
    required = tuple(str(column) for column in required_columns)
    available = _var_column_names(var)
    missing = tuple(column for column in required if column not in available)

    if missing:
        missing_text = ", ".join(repr(column) for column in missing)
        raise MitochondrialGeneAnnotationError(
            f"Missing required adata.var column(s): {missing_text}."
        )

    return required


def require_explicit_gene_symbol_column(gene_symbol_column: str | None) -> str:
    """Return a valid gene-symbol column name or fail closed."""

    if gene_symbol_column is None:
        raise MitochondrialGeneAnnotationError(
            "gene_symbol_column must be provided explicitly; refusing to infer "
            "mitochondrial genes from adata.var_names."
        )

    normalized = str(gene_symbol_column).strip()
    if not normalized:
        raise MitochondrialGeneAnnotationError(
            "gene_symbol_column must not be empty."
        )

    return normalized


def get_var_column_values(adata: Any, column: str) -> list[object]:
    """Return values from one ``adata.var`` column as a Python list."""

    require_var_columns(adata, [column])
    values = _get_var(adata)[column]

    if hasattr(values, "tolist"):
        values = values.tolist()

    if isinstance(values, str | bytes):
        raise TypeError(
            f"Expected adata.var[{column!r}] to contain row values, not a scalar."
        )

    return list(values)


def normalize_gene_symbol(gene_symbol: object) -> str:
    """Normalize one gene symbol or raise for missing/empty values."""

    if gene_symbol is None:
        raise MitochondrialGeneAnnotationError("gene symbol must not be None.")

    normalized = str(gene_symbol).strip()
    if not normalized:
        raise MitochondrialGeneAnnotationError("gene symbol must not be empty.")

    return normalized


def extract_gene_symbols(
    adata: Any,
    gene_symbol_column: str | None,
) -> list[str]:
    """Extract normalized gene symbols from an explicit ``adata.var`` column."""

    column = require_explicit_gene_symbol_column(gene_symbol_column)
    return [
        normalize_gene_symbol(gene_symbol)
        for gene_symbol in get_var_column_values(adata, column)
    ]


def is_mitochondrial_gene_symbol(
    gene_symbol: object,
    mito_prefix: str = DEFAULT_MITO_PREFIX,
) -> bool:
    """Return True when a normalized gene symbol uses the mitochondrial prefix."""

    symbol = normalize_gene_symbol(gene_symbol)
    prefix = normalize_gene_symbol(mito_prefix)
    return symbol.upper().startswith(prefix.upper())


def make_mitochondrial_gene_mask(
    adata: Any,
    gene_symbol_column: str | None,
    mito_prefix: str = DEFAULT_MITO_PREFIX,
) -> list[bool]:
    """Create a mitochondrial-gene boolean mask from an explicit symbol column."""

    return [
        is_mitochondrial_gene_symbol(gene_symbol, mito_prefix=mito_prefix)
        for gene_symbol in extract_gene_symbols(adata, gene_symbol_column)
    ]


def count_mitochondrial_genes(
    adata: Any,
    gene_symbol_column: str | None,
    mito_prefix: str = DEFAULT_MITO_PREFIX,
) -> int:
    """Count mitochondrial genes from an explicit symbol column."""

    return sum(make_mitochondrial_gene_mask(adata, gene_symbol_column, mito_prefix))


def summarize_mitochondrial_gene_annotation(
    adata: Any,
    gene_symbol_column: str | None,
    mito_prefix: str = DEFAULT_MITO_PREFIX,
) -> dict[str, int]:
    """Summarize mitochondrial annotation without filtering any genes or cells."""

    mask = make_mitochondrial_gene_mask(
        adata,
        gene_symbol_column=gene_symbol_column,
        mito_prefix=mito_prefix,
    )
    mitochondrial_gene_count = sum(mask)
    total_gene_count = len(mask)

    return {
        "total_gene_count": total_gene_count,
        "mitochondrial_gene_count": mitochondrial_gene_count,
        "non_mitochondrial_gene_count": total_gene_count - mitochondrial_gene_count,
    }
