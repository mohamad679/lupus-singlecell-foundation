"""Stage 3 patient-level embedding aggregation contract.

This module defines fake-data utilities for aggregating cell-level embedding
records into donor/patient-level embedding records. It does not load real
embedding artifacts, load AnnData files, execute Geneformer, execute tokenizers,
extract embeddings, train models, evaluate models, perform external validation,
or add performance claims.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

from lupusfm.data.anndata_schema import DEFAULT_FORBIDDEN_SPLIT_VALUES
from lupusfm.embeddings.artifact_schema import DEFAULT_EMBEDDING_DIMENSION


DEFAULT_PATIENT_AGGREGATION = "mean_pool_per_donor"
ALLOWED_PATIENT_AGGREGATIONS = (DEFAULT_PATIENT_AGGREGATION,)

DEFAULT_AGGREGATION_SPLIT_LEVEL = "patient"
ALLOWED_AGGREGATION_SPLIT_LEVELS = ("patient", "donor")


class PatientAggregationError(ValueError):
    """Raised when patient-level aggregation violates the Stage 3 contract."""


@dataclass(frozen=True)
class CellEmbeddingRecord:
    """One fake cell-level embedding record for aggregation tests."""

    donor_id: str
    cell_id: str
    embedding: tuple[float, ...]


@dataclass(frozen=True)
class DonorEmbeddingRecord:
    """One donor/patient-level embedding record produced by aggregation."""

    donor_id: str
    embedding: tuple[float, ...]
    n_cells: int
    aggregation_method: str
    source_record_level: str = "cell"


@dataclass(frozen=True)
class PatientAggregationConfig:
    """Metadata-only configuration for patient-level aggregation."""

    aggregation_method: str = DEFAULT_PATIENT_AGGREGATION
    split_level: str = DEFAULT_AGGREGATION_SPLIT_LEVEL
    expected_embedding_dimension: int | None = DEFAULT_EMBEDDING_DIMENSION
    min_cells_per_donor: int = 1
    allow_real_artifact_loading: bool = False
    allow_anndata_loading: bool = False
    allow_geneformer_execution: bool = False
    allow_tokenizer_execution: bool = False
    allow_embedding_extraction: bool = False
    allow_modeling: bool = False
    allow_training: bool = False
    allow_external_validation: bool = False
    performance_claims_added: bool = False
    notes: str = ""


def _clean_required_string(value: object, field_name: str) -> str:
    """Return a non-empty normalized string or raise."""

    normalized = str(value).strip()
    if not normalized:
        raise PatientAggregationError(f"{field_name} must not be empty.")
    return normalized


def _as_bool(value: object) -> bool:
    """Parse common bool-like values."""

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {"1", "true", "yes"}


def _validate_choice(value: object, allowed: tuple[str, ...], field_name: str) -> str:
    """Validate a normalized string against an allowed set."""

    normalized = _clean_required_string(value, field_name)
    if normalized not in allowed:
        allowed_text = ", ".join(allowed)
        raise PatientAggregationError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _require_positive_int(value: object, field_name: str) -> int:
    """Return a positive integer or raise."""

    if isinstance(value, bool):
        raise PatientAggregationError(f"{field_name} must be an integer, not bool.")

    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise PatientAggregationError(f"{field_name} must be an integer.") from exc

    if parsed <= 0:
        raise PatientAggregationError(f"{field_name} must be positive.")

    return parsed


def _optional_positive_int(value: object, field_name: str) -> int | None:
    """Return None or a positive integer."""

    if value is None:
        return None

    return _require_positive_int(value, field_name)


def _normalize_embedding(value: object, field_name: str) -> tuple[float, ...]:
    """Normalize a fake embedding sequence into a finite float tuple."""

    if isinstance(value, (str, bytes)):
        raise PatientAggregationError(f"{field_name} must be a numeric sequence.")

    if not isinstance(value, Sequence):
        raise PatientAggregationError(f"{field_name} must be a numeric sequence.")

    normalized = []
    for index, item in enumerate(value):
        if isinstance(item, bool):
            raise PatientAggregationError(
                f"{field_name}[{index}] must be numeric, not bool."
            )
        try:
            parsed = float(item)
        except (TypeError, ValueError) as exc:
            raise PatientAggregationError(
                f"{field_name}[{index}] must be numeric."
            ) from exc

        if not math.isfinite(parsed):
            raise PatientAggregationError(f"{field_name}[{index}] must be finite.")

        normalized.append(parsed)

    if not normalized:
        raise PatientAggregationError(f"{field_name} must not be empty.")

    return tuple(normalized)


def validate_patient_aggregation_config(
    config: PatientAggregationConfig,
) -> PatientAggregationConfig:
    """Validate Stage 3 patient-level aggregation configuration."""

    aggregation_method = _validate_choice(
        config.aggregation_method,
        ALLOWED_PATIENT_AGGREGATIONS,
        "aggregation_method",
    )
    split_level = _validate_choice(
        config.split_level,
        ALLOWED_AGGREGATION_SPLIT_LEVELS,
        "split_level",
    )

    forbidden_split_levels = {str(value) for value in DEFAULT_FORBIDDEN_SPLIT_VALUES}
    if split_level in forbidden_split_levels:
        raise PatientAggregationError("cell-level split assignments are not allowed.")

    if _as_bool(config.allow_real_artifact_loading):
        raise PatientAggregationError(
            "Stage 3 aggregation must not load real artifacts."
        )
    if _as_bool(config.allow_anndata_loading):
        raise PatientAggregationError("Stage 3 aggregation must not load AnnData.")
    if _as_bool(config.allow_geneformer_execution):
        raise PatientAggregationError(
            "Stage 3 aggregation must not execute Geneformer."
        )
    if _as_bool(config.allow_tokenizer_execution):
        raise PatientAggregationError(
            "Stage 3 aggregation must not execute tokenizers."
        )
    if _as_bool(config.allow_embedding_extraction):
        raise PatientAggregationError(
            "Stage 3 aggregation must not extract embeddings."
        )
    if _as_bool(config.allow_modeling):
        raise PatientAggregationError("Stage 3 aggregation must keep modeling disabled.")
    if _as_bool(config.allow_training):
        raise PatientAggregationError("Stage 3 aggregation must keep training disabled.")
    if _as_bool(config.allow_external_validation):
        raise PatientAggregationError(
            "Stage 3 aggregation must keep external validation disabled."
        )
    if _as_bool(config.performance_claims_added):
        raise PatientAggregationError(
            "Stage 3 aggregation must not add performance claims."
        )

    return PatientAggregationConfig(
        aggregation_method=aggregation_method,
        split_level=split_level,
        expected_embedding_dimension=_optional_positive_int(
            config.expected_embedding_dimension,
            "expected_embedding_dimension",
        ),
        min_cells_per_donor=_require_positive_int(
            config.min_cells_per_donor,
            "min_cells_per_donor",
        ),
        allow_real_artifact_loading=False,
        allow_anndata_loading=False,
        allow_geneformer_execution=False,
        allow_tokenizer_execution=False,
        allow_embedding_extraction=False,
        allow_modeling=False,
        allow_training=False,
        allow_external_validation=False,
        performance_claims_added=False,
        notes=str(config.notes).strip(),
    )


def validate_cell_embedding_record(
    record: CellEmbeddingRecord | Mapping[str, Any],
    *,
    expected_embedding_dimension: int | None = None,
) -> CellEmbeddingRecord:
    """Validate one fake cell-level embedding record."""

    if isinstance(record, Mapping):
        donor_id = record.get("donor_id", "")
        cell_id = record.get("cell_id", "")
        embedding = record.get("embedding", ())
    else:
        donor_id = record.donor_id
        cell_id = record.cell_id
        embedding = record.embedding

    normalized_embedding = _normalize_embedding(embedding, "embedding")
    expected_dim = _optional_positive_int(
        expected_embedding_dimension,
        "expected_embedding_dimension",
    )
    if expected_dim is not None and len(normalized_embedding) != expected_dim:
        raise PatientAggregationError(
            "embedding dimension does not match expected_embedding_dimension; all embeddings must have the same dimension."
        )

    return CellEmbeddingRecord(
        donor_id=_clean_required_string(donor_id, "donor_id"),
        cell_id=_clean_required_string(cell_id, "cell_id"),
        embedding=normalized_embedding,
    )


def aggregate_embeddings_by_donor(
    records: Sequence[CellEmbeddingRecord | Mapping[str, Any]],
    config: PatientAggregationConfig | None = None,
) -> tuple[DonorEmbeddingRecord, ...]:
    """Mean-pool fake cell embeddings into donor-level embeddings."""

    validated_config = validate_patient_aggregation_config(
        config or PatientAggregationConfig(expected_embedding_dimension=None)
    )

    if isinstance(records, (str, bytes)) or not isinstance(records, Sequence):
        raise PatientAggregationError("records must be a sequence.")
    if not records:
        raise PatientAggregationError("records must not be empty.")

    validated_records: list[CellEmbeddingRecord] = []
    seen_cell_ids: set[str] = set()
    inferred_dimension: int | None = validated_config.expected_embedding_dimension

    for raw_record in records:
        record = validate_cell_embedding_record(
            raw_record,
            expected_embedding_dimension=inferred_dimension,
        )

        if inferred_dimension is None:
            inferred_dimension = len(record.embedding)
        elif len(record.embedding) != inferred_dimension:
            raise PatientAggregationError("all embeddings must have the same dimension.")

        if record.cell_id in seen_cell_ids:
            raise PatientAggregationError("cell_id values must be unique.")
        seen_cell_ids.add(record.cell_id)

        validated_records.append(record)

    grouped: dict[str, list[CellEmbeddingRecord]] = defaultdict(list)
    for record in validated_records:
        grouped[record.donor_id].append(record)

    donor_records = []
    for donor_id in sorted(grouped):
        donor_cells = grouped[donor_id]
        if len(donor_cells) < validated_config.min_cells_per_donor:
            raise PatientAggregationError(
                "each donor must have at least min_cells_per_donor cells."
            )

        dimension = len(donor_cells[0].embedding)
        sums = [0.0] * dimension
        for cell in donor_cells:
            for index, value in enumerate(cell.embedding):
                sums[index] += value

        pooled = tuple(value / len(donor_cells) for value in sums)
        donor_records.append(
            DonorEmbeddingRecord(
                donor_id=donor_id,
                embedding=pooled,
                n_cells=len(donor_cells),
                aggregation_method=validated_config.aggregation_method,
            )
        )

    return tuple(donor_records)


def donor_embedding_records_to_dicts(
    records: Sequence[DonorEmbeddingRecord],
) -> list[dict[str, Any]]:
    """Serialize donor-level embedding records to plain dictionaries."""

    return [asdict(record) for record in records]


def patient_aggregation_config_from_mapping(
    data: Mapping[str, Any],
) -> PatientAggregationConfig:
    """Build and validate a patient aggregation config from a mapping."""

    return validate_patient_aggregation_config(
        PatientAggregationConfig(
            aggregation_method=data.get(
                "aggregation_method",
                DEFAULT_PATIENT_AGGREGATION,
            ),
            split_level=data.get("split_level", DEFAULT_AGGREGATION_SPLIT_LEVEL),
            expected_embedding_dimension=data.get(
                "expected_embedding_dimension",
                DEFAULT_EMBEDDING_DIMENSION,
            ),
            min_cells_per_donor=data.get("min_cells_per_donor", 1),
            allow_real_artifact_loading=data.get("allow_real_artifact_loading", False),
            allow_anndata_loading=data.get("allow_anndata_loading", False),
            allow_geneformer_execution=data.get("allow_geneformer_execution", False),
            allow_tokenizer_execution=data.get("allow_tokenizer_execution", False),
            allow_embedding_extraction=data.get("allow_embedding_extraction", False),
            allow_modeling=data.get("allow_modeling", False),
            allow_training=data.get("allow_training", False),
            allow_external_validation=data.get("allow_external_validation", False),
            performance_claims_added=data.get("performance_claims_added", False),
            notes=data.get("notes", ""),
        )
    )


def patient_aggregation_config_to_dict(
    config: PatientAggregationConfig,
) -> dict[str, Any]:
    """Serialize a validated patient aggregation config to a plain dictionary."""

    return asdict(validate_patient_aggregation_config(config))
