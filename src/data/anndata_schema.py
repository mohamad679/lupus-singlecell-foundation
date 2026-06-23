"""AnnData-like schema validation utilities.

These helpers validate a schema contract and lightweight AnnData-like mock
objects. They do not import Scanpy, load real AnnData files, download data, or
perform preprocessing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "metadata" / "anndata_schema.yaml"

REQUIRED_SCHEMA_SECTIONS = [
    "schema_version",
    "obs_required_fields",
    "var_required_fields",
    "layers_policy",
    "uns_required_fields",
    "valid_split_policies",
    "forbidden_split_values",
    "allowed_unknown_values",
    "integrity_rules",
]


class AnnDataSchemaError(ValueError):
    """Raised when schema or AnnData-like structure validation fails."""


def _clean_scalar(value: str) -> str | int:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    if value.isdigit():
        return int(value)
    return value


def load_anndata_schema(path: Path | str = DEFAULT_SCHEMA_PATH) -> Dict[str, object]:
    """Load the simple top-level scalar/list YAML shape used by this schema."""
    schema_path = Path(path)
    data: Dict[str, object] = {}
    current_key: str | None = None

    for line_number, raw_line in enumerate(schema_path.read_text().splitlines(), start=1):
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        if not raw_line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            value = value.strip()
            data[current_key] = _clean_scalar(value) if value else []
            continue

        if line.startswith("  - "):
            if current_key is None:
                raise AnnDataSchemaError(f"List item without key at line {line_number}")
            section = data.setdefault(current_key, [])
            if not isinstance(section, list):
                raise AnnDataSchemaError(
                    f"List item under scalar key {current_key} at line {line_number}"
                )
            section.append(_clean_scalar(line[4:]))
            continue

        raise AnnDataSchemaError(
            f"Unsupported schema YAML shape at line {line_number}: {raw_line}"
        )

    return data


def validate_required_schema_sections(schema: Mapping[str, object]) -> None:
    missing = [section for section in REQUIRED_SCHEMA_SECTIONS if section not in schema]
    if missing:
        raise AnnDataSchemaError(
            "AnnData schema missing required sections: " + ", ".join(missing)
        )

    list_sections = [
        section for section in REQUIRED_SCHEMA_SECTIONS if section != "schema_version"
    ]
    invalid_lists = [
        section
        for section in list_sections
        if not isinstance(schema.get(section), list) or not schema.get(section)
    ]
    if invalid_lists:
        raise AnnDataSchemaError(
            "AnnData schema sections must be non-empty lists: "
            + ", ".join(invalid_lists)
        )


def _get_attr_or_item(obj: Any, key: str) -> Any:
    if isinstance(obj, Mapping):
        return obj.get(key)
    return getattr(obj, key, None)


def _columns(table: Any) -> set[str]:
    if table is None:
        return set()
    if isinstance(table, Mapping):
        if "columns" in table:
            columns = table["columns"]
            if isinstance(columns, Mapping):
                return set(str(key) for key in columns.keys())
            return set(str(column) for column in columns)
        return set(str(key) for key in table.keys() if key != "index")
    columns = getattr(table, "columns", None)
    if columns is None:
        return set()
    return set(str(column) for column in columns)


def _column_values(table: Any, column: str) -> Sequence[Any]:
    if table is None:
        return []
    if isinstance(table, Mapping):
        if "columns" in table and isinstance(table["columns"], Mapping):
            values = table["columns"].get(column, [])
        else:
            values = table.get(column, [])
    else:
        try:
            values = table[column]
        except (TypeError, KeyError, AttributeError):
            values = getattr(table, column, [])

    if isinstance(values, str):
        return [values]
    try:
        return list(values)
    except TypeError:
        return [values]


def _index_values(table: Any) -> Sequence[Any]:
    if table is None:
        return []
    if isinstance(table, Mapping):
        return list(table.get("index", []))
    index = getattr(table, "index", [])
    try:
        return list(index)
    except TypeError:
        return []


def _row_count(table: Any) -> int:
    index = _index_values(table)
    if index:
        return len(index)
    columns = _columns(table)
    if not columns:
        return 0
    return max((len(_column_values(table, column)) for column in columns), default=0)


def _matrix_shape(matrix: Any) -> tuple[int, int] | None:
    if matrix is None:
        return None
    shape = getattr(matrix, "shape", None)
    if shape is None and isinstance(matrix, Mapping):
        shape = matrix.get("shape")
    if shape is not None:
        shape_values = tuple(shape)
        if len(shape_values) == 2:
            return int(shape_values[0]), int(shape_values[1])
    if isinstance(matrix, Sequence) and not isinstance(matrix, (str, bytes)):
        row_count = len(matrix)
        column_count = len(matrix[0]) if row_count else 0
        return row_count, column_count
    return None


def _is_unique(values: Sequence[Any]) -> bool:
    return len(values) == len(set(values))


def _missing_required_values(values: Iterable[Any]) -> bool:
    return any(value is None or value == "" for value in values)


def validate_anndata_like_structure(
    adata: Any,
    schema: Mapping[str, object],
) -> None:
    """Validate a lightweight AnnData-like object or dictionary.

    Accepted mock shape:
    {
        "obs": {"index": [...], "columns": {"patient_id": [...], ...}},
        "var": {"index": [...], "columns": {"gene_id": [...], ...}},
        "X": {"shape": (n_cells, n_genes)},
        "layers": {"counts": {"shape": (...)}, ...},
        "uns": {"patient_level_split_policy": "patient_level", ...},
    }
    """
    validate_required_schema_sections(schema)

    obs = _get_attr_or_item(adata, "obs")
    var = _get_attr_or_item(adata, "var")
    x_matrix = _get_attr_or_item(adata, "X")
    layers = _get_attr_or_item(adata, "layers") or {}
    uns = _get_attr_or_item(adata, "uns") or {}

    obs_required = [str(field) for field in schema["obs_required_fields"]]
    var_required = [str(field) for field in schema["var_required_fields"]]
    layer_required = [str(field) for field in schema["layers_policy"]]
    uns_required = [str(field) for field in schema["uns_required_fields"]]

    missing_obs = [field for field in obs_required if field not in _columns(obs)]
    if missing_obs:
        raise AnnDataSchemaError("obs missing required fields: " + ", ".join(missing_obs))

    missing_var = [field for field in var_required if field not in _columns(var)]
    if missing_var:
        raise AnnDataSchemaError("var missing required fields: " + ", ".join(missing_var))

    missing_layers = [field for field in layer_required if field not in layers]
    if missing_layers:
        raise AnnDataSchemaError(
            "layers missing required entries: " + ", ".join(missing_layers)
        )

    missing_uns = [field for field in uns_required if field not in uns]
    if missing_uns:
        raise AnnDataSchemaError("uns missing required fields: " + ", ".join(missing_uns))

    obs_index = _index_values(obs)
    var_index = _index_values(var)
    if obs_index and not _is_unique(obs_index):
        raise AnnDataSchemaError("obs index must be unique")
    if var_index and not _is_unique(var_index):
        raise AnnDataSchemaError("var index must be unique")

    x_shape = _matrix_shape(x_matrix)
    expected_shape = (_row_count(obs), _row_count(var))
    if x_shape != expected_shape:
        raise AnnDataSchemaError(
            f"X must be cells x genes with shape {expected_shape}, got {x_shape}"
        )

    if _missing_required_values(_column_values(obs, "patient_id")):
        raise AnnDataSchemaError("obs patient_id must not contain missing values")
    if _missing_required_values(_column_values(obs, "disease_label")):
        raise AnnDataSchemaError("obs disease_label must not contain missing values")

    forbidden_split_values = {str(value) for value in schema["forbidden_split_values"]}
    valid_split_policies = {str(value) for value in schema["valid_split_policies"]}
    split_values = {str(value) for value in _column_values(obs, "split_group")}
    if split_values.intersection(forbidden_split_values):
        raise AnnDataSchemaError("cell-level split assignment is forbidden")
    invalid_split_values = split_values.difference(valid_split_policies)
    if invalid_split_values:
        raise AnnDataSchemaError(
            "split_group must be patient-level or cohort-level only: "
            + ", ".join(sorted(invalid_split_values))
        )

    split_policy = str(uns.get("patient_level_split_policy", ""))
    if split_policy not in valid_split_policies:
        raise AnnDataSchemaError(
            "patient_level_split_policy must be patient-level or cohort-level"
        )
