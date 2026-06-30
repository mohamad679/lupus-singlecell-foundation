"""Lightweight AnnData schema validation utilities.

These helpers validate AnnData-like object structure without importing Scanpy,
loading files, filtering cells, extracting embeddings, or training models.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from lupusfm.data.metadata import DEFAULT_DONOR_COLUMN


DEFAULT_GENE_SYMBOL_COLUMN = "gene_symbol"

DEFAULT_FORBIDDEN_SPLIT_VALUES = (
    "cell",
    "cell_level",
    "cell_level_split",
    "random_cell_split",
)


class AnnDataSchemaError(ValueError):
    """Raised when an AnnData-like object violates the expected schema."""


@dataclass(frozen=True)
class AnnDataSchemaContract:
    """Configurable schema contract for lightweight AnnData-like validation."""

    required_obs_columns: tuple[str, ...] = (DEFAULT_DONOR_COLUMN,)
    required_var_columns: tuple[str, ...] = (DEFAULT_GENE_SYMBOL_COLUMN,)
    required_uns_keys: tuple[str, ...] = ()
    required_layers: tuple[str, ...] = ()
    require_x: bool = True
    validate_layer_shapes: bool = True
    split_column: str | None = None
    forbidden_split_values: tuple[str, ...] = DEFAULT_FORBIDDEN_SPLIT_VALUES
    allowed_split_values: tuple[str, ...] | None = None


@dataclass(frozen=True)
class AnnDataSchemaReport:
    """Compact validation result for an AnnData-like object."""

    n_obs: int
    n_vars: int
    x_shape: tuple[int, int] | None
    obs_columns: tuple[str, ...]
    var_columns: tuple[str, ...]
    validated_obs_columns: tuple[str, ...]
    validated_var_columns: tuple[str, ...]


PROJECT_INGESTION_SCHEMA = AnnDataSchemaContract()


def _get_attr_or_item(obj: Any, key: str) -> Any:
    """Return ``obj.key`` or ``obj[key]`` for mapping-like objects."""

    if isinstance(obj, Mapping):
        return obj.get(key)
    return getattr(obj, key, None)


def _column_container(table: Any) -> Any:
    """Return the object holding table columns."""

    if isinstance(table, Mapping) and "columns" in table:
        return table["columns"]
    return table


def _column_names(table: Any) -> tuple[str, ...]:
    """Return table column names from DataFrame-like or mapping-like metadata."""

    if table is None:
        raise AnnDataSchemaError("Metadata table is missing.")

    if hasattr(table, "columns"):
        return tuple(str(column) for column in table.columns)

    columns = _column_container(table)
    if isinstance(columns, Mapping):
        return tuple(str(column) for column in columns.keys() if column != "index")

    if isinstance(columns, Sequence) and not isinstance(columns, str | bytes):
        return tuple(str(column) for column in columns)

    raise AnnDataSchemaError(
        "Metadata table must be DataFrame-like or mapping-like with columns."
    )


def _column_values(table: Any, column: str) -> list[object]:
    """Return one metadata column as a list."""

    if hasattr(table, "columns"):
        try:
            values = table[column]
        except (KeyError, TypeError) as exc:
            raise AnnDataSchemaError(f"Missing metadata column: {column}") from exc
    else:
        columns = _column_container(table)
        if not isinstance(columns, Mapping) or column not in columns:
            raise AnnDataSchemaError(f"Missing metadata column: {column}")
        values = columns[column]

    if hasattr(values, "tolist"):
        values = values.tolist()

    if isinstance(values, str | bytes):
        return [values]

    try:
        return list(values)
    except TypeError:
        return [values]


def _index_length(table: Any) -> int | None:
    """Return explicit table index length when available."""

    if isinstance(table, Mapping):
        index = table.get("index")
        if index is not None:
            return len(index)

    index = getattr(table, "index", None)
    if index is not None:
        try:
            return len(index)
        except TypeError:
            return None

    return None


def _axis_length(table: Any, axis_name: str) -> int:
    """Infer axis length from shape, index, or column lengths."""

    shape = getattr(table, "shape", None)
    if shape is not None:
        return int(shape[0])

    index_length = _index_length(table)
    if index_length is not None:
        return index_length

    columns = _column_names(table)
    if not columns:
        raise AnnDataSchemaError(f"{axis_name} has no columns and no explicit index.")

    lengths = {column: len(_column_values(table, column)) for column in columns}
    unique_lengths = set(lengths.values())
    if len(unique_lengths) != 1:
        details = ", ".join(f"{column}={length}" for column, length in lengths.items())
        raise AnnDataSchemaError(f"{axis_name} columns have inconsistent lengths: {details}")

    return unique_lengths.pop()


def _validate_column_lengths(table: Any, axis_name: str, expected_length: int) -> None:
    """Ensure all metadata columns match the inferred axis length."""

    for column in _column_names(table):
        observed_length = len(_column_values(table, column))
        if observed_length != expected_length:
            raise AnnDataSchemaError(
                f"{axis_name} column {column!r} has length {observed_length}; "
                f"expected {expected_length}."
            )


def _matrix_shape(matrix: Any) -> tuple[int, int] | None:
    """Return matrix shape without materializing matrix contents."""

    if matrix is None:
        return None

    shape = getattr(matrix, "shape", None)
    if shape is None and isinstance(matrix, Mapping):
        shape = matrix.get("shape")

    if shape is not None:
        shape_values = tuple(shape)
        if len(shape_values) != 2:
            raise AnnDataSchemaError(f"Expected 2D matrix shape, got {shape_values}.")
        return int(shape_values[0]), int(shape_values[1])

    if isinstance(matrix, Sequence) and not isinstance(matrix, str | bytes):
        n_rows = len(matrix)
        n_cols = len(matrix[0]) if n_rows else 0
        return n_rows, n_cols

    return None


def _require_columns(
    available_columns: tuple[str, ...],
    required_columns: tuple[str, ...],
    axis_name: str,
) -> tuple[str, ...]:
    """Validate required column names."""

    available = set(available_columns)
    required = tuple(str(column) for column in required_columns)
    missing = tuple(column for column in required if column not in available)

    if missing:
        missing_text = ", ".join(repr(column) for column in missing)
        raise AnnDataSchemaError(
            f"{axis_name} missing required column(s): {missing_text}."
        )

    return required


def _require_mapping_keys(container: Any, required_keys: tuple[str, ...], name: str) -> None:
    """Validate required keys in mapping-like containers."""

    if not required_keys:
        return

    if not isinstance(container, Mapping):
        raise AnnDataSchemaError(f"{name} must be mapping-like.")

    missing = tuple(key for key in required_keys if key not in container)
    if missing:
        missing_text = ", ".join(repr(key) for key in missing)
        raise AnnDataSchemaError(f"{name} missing required key(s): {missing_text}.")


def _validate_split_values(obs: Any, contract: AnnDataSchemaContract) -> None:
    """Reject cell-level split labels and optionally enforce allowed values."""

    if contract.split_column is None:
        return

    obs_columns = _column_names(obs)
    if contract.split_column not in obs_columns:
        raise AnnDataSchemaError(
            f"obs missing split column {contract.split_column!r}."
        )

    split_values = {str(value) for value in _column_values(obs, contract.split_column)}
    forbidden = {str(value) for value in contract.forbidden_split_values}

    if split_values.intersection(forbidden):
        raise AnnDataSchemaError("cell-level split assignments are not allowed.")

    if contract.allowed_split_values is not None:
        allowed = {str(value) for value in contract.allowed_split_values}
        invalid = split_values.difference(allowed)
        if invalid:
            invalid_text = ", ".join(sorted(invalid))
            raise AnnDataSchemaError(
                "split values must be patient-level or cohort-level only; "
                f"got: {invalid_text}."
            )


def validate_anndata_schema(
    adata: Any,
    contract: AnnDataSchemaContract = PROJECT_INGESTION_SCHEMA,
) -> AnnDataSchemaReport:
    """Validate lightweight AnnData-like structure and return a compact report."""

    obs = _get_attr_or_item(adata, "obs")
    var = _get_attr_or_item(adata, "var")
    x_matrix = _get_attr_or_item(adata, "X")
    layers = _get_attr_or_item(adata, "layers") or {}
    uns = _get_attr_or_item(adata, "uns") or {}

    if obs is None:
        raise AnnDataSchemaError("AnnData-like object is missing .obs metadata.")
    if var is None:
        raise AnnDataSchemaError("AnnData-like object is missing .var metadata.")

    obs_columns = _column_names(obs)
    var_columns = _column_names(var)

    validated_obs_columns = _require_columns(
        obs_columns,
        contract.required_obs_columns,
        "obs",
    )
    validated_var_columns = _require_columns(
        var_columns,
        contract.required_var_columns,
        "var",
    )
    _require_mapping_keys(uns, contract.required_uns_keys, "uns")
    _require_mapping_keys(layers, contract.required_layers, "layers")

    n_obs = _axis_length(obs, "obs")
    n_vars = _axis_length(var, "var")
    _validate_column_lengths(obs, "obs", n_obs)
    _validate_column_lengths(var, "var", n_vars)

    x_shape = _matrix_shape(x_matrix)
    expected_shape = (n_obs, n_vars)

    if contract.require_x and x_shape is None:
        raise AnnDataSchemaError("AnnData-like object is missing X matrix shape.")

    if x_shape is not None and x_shape != expected_shape:
        raise AnnDataSchemaError(
            f"X must have shape {expected_shape}, got {x_shape}."
        )

    if contract.validate_layer_shapes:
        for layer_name in contract.required_layers:
            layer_shape = _matrix_shape(layers[layer_name])
            if layer_shape != expected_shape:
                raise AnnDataSchemaError(
                    f"Layer {layer_name!r} must have shape {expected_shape}, "
                    f"got {layer_shape}."
                )

    _validate_split_values(obs, contract)

    return AnnDataSchemaReport(
        n_obs=n_obs,
        n_vars=n_vars,
        x_shape=x_shape,
        obs_columns=obs_columns,
        var_columns=var_columns,
        validated_obs_columns=validated_obs_columns,
        validated_var_columns=validated_var_columns,
    )
