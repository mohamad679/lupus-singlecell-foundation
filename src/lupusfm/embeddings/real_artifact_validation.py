"""Stage 4 real embedding artifact validation contract.

This module validates safe metadata and filesystem metadata for a user-supplied
local embedding artifact path. It may check path existence, file size, and an
optional checksum. It does not parse embedding tables, load AnnData files,
execute Geneformer, execute tokenizers, extract embeddings, aggregate
embeddings, fit scalers, fit models, compute metrics, perform external
validation, or add performance claims.
"""

from __future__ import annotations

import hashlib
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from lupusfm.data.anndata_schema import DEFAULT_FORBIDDEN_SPLIT_VALUES
from lupusfm.data.manifest import (
    FORBIDDEN_OUTPUT_SUFFIXES,
    PRIMARY_CELLXGENE_CENSUS_VERSION,
    PRIMARY_CELLXGENE_DATASET_ID,
)
from lupusfm.data.metadata import DEFAULT_DONOR_COLUMN
from lupusfm.embeddings.artifact_schema import (
    ALLOWED_ARTIFACT_SPLIT_LEVELS,
    ALLOWED_EMBEDDING_ARTIFACT_FORMATS,
    ALLOWED_EMBEDDING_RECORD_LEVELS,
    DEFAULT_EMBEDDING_COLUMN,
    DEFAULT_EMBEDDING_DIMENSION,
    DEFAULT_EMBEDDING_SOURCE,
)

STAGE4_CURRENT_FEATURE = "STAGE4-F001"
DEFAULT_HASH_ALGORITHM = "sha256"
ALLOWED_HASH_ALGORITHMS = (DEFAULT_HASH_ALGORITHM,)

NPY_DIRECTORY_ARTIFACT_FORMAT = "npy_directory"
ALLOWED_REAL_EMBEDDING_ARTIFACT_FORMATS = (
    *ALLOWED_EMBEDDING_ARTIFACT_FORMATS,
    NPY_DIRECTORY_ARTIFACT_FORMAT,
)

SINGLE_FILE_ARTIFACT_LAYOUT = "single_file"
DIRECTORY_ARTIFACT_LAYOUT = "directory"
ALLOWED_ARTIFACT_LAYOUTS = (SINGLE_FILE_ARTIFACT_LAYOUT, DIRECTORY_ARTIFACT_LAYOUT)

DEFAULT_DIRECTORY_EMBEDDING_SUFFIX = ".npy"
ALLOWED_DIRECTORY_EMBEDDING_SUFFIXES = (DEFAULT_DIRECTORY_EMBEDDING_SUFFIX,)

NOT_CHECKED = "not_checked"
VALIDATED = "validated"
MISSING = "missing"
BLOCKED = "blocked"
ALLOWED_VALIDATION_STATUSES = (NOT_CHECKED, VALIDATED, MISSING, BLOCKED)

FORBIDDEN_DECLARED_COLUMN_FRAGMENTS = (
    "split",
    "fold",
    "train",
    "test",
    "prediction",
    "predicted",
    "probability",
    "metric",
    "auroc",
    "auprc",
    "balanced_accuracy",
    "sensitivity",
    "specificity",
    "logit",
    "model_output",
)


class RealEmbeddingArtifactValidationError(ValueError):
    """Raised when Stage 4 real artifact validation violates the contract."""


@dataclass(frozen=True)
class RealEmbeddingArtifactManifest:
    """Safe manifest for a local real embedding artifact path.

    The manifest may contain paths and metadata, but must not contain real
    embedding vectors, model artifacts, training outputs, predictions, metrics,
    or committed large artifacts.
    """

    local_artifact_path: str
    dataset_id: str = PRIMARY_CELLXGENE_DATASET_ID
    source: str = "CELLxGENE Census"
    census_version: str = PRIMARY_CELLXGENE_CENSUS_VERSION
    current_feature: str = STAGE4_CURRENT_FEATURE
    artifact_format: str = "parquet"
    artifact_layout: str = SINGLE_FILE_ARTIFACT_LAYOUT
    directory_file_suffix: str | None = None
    record_level: str = "cell"
    split_level: str = "patient"
    donor_id_column: str = DEFAULT_DONOR_COLUMN
    cell_id_column: str | None = "cell_id"
    sampled_cell_id_column: str | None = None
    embedding_column: str = DEFAULT_EMBEDDING_COLUMN
    embedding_dimension: int = DEFAULT_EMBEDDING_DIMENSION
    embedding_source: str = DEFAULT_EMBEDDING_SOURCE
    declared_columns: tuple[str, ...] = ()
    size_bytes: int | None = None
    expected_file_count: int | None = None
    observed_file_count: int | None = None
    total_size_bytes: int | None = None
    min_file_size_bytes: int | None = None
    max_file_size_bytes: int | None = None
    all_files_same_size: bool | None = None
    sha256: str | None = None
    hash_algorithm: str | None = None
    validation_status: str = NOT_CHECKED
    artifact_commit_allowed: bool = False
    commit_real_artifact: bool = False
    contains_model_artifact: bool = False
    contains_training_artifact: bool = False
    contains_split_columns: bool = False
    contains_predictions: bool = False
    contains_performance_metrics: bool = False
    allow_file_metadata_inspection: bool = True
    allow_header_inspection: bool = False
    allow_anndata_loading: bool = False
    allow_geneformer_execution: bool = False
    allow_tokenizer_execution: bool = False
    allow_embedding_extraction: bool = False
    allow_embedding_table_parsing: bool = False
    allow_aggregation: bool = False
    allow_feature_extraction: bool = False
    allow_global_preprocessing: bool = False
    allow_scaler_outside_fold: bool = False
    allow_model_fitting: bool = False
    allow_metric_computation: bool = False
    allow_modeling: bool = False
    allow_training: bool = False
    allow_external_validation: bool = False
    performance_claims_added: bool = False
    notes: str = ""


@dataclass(frozen=True)
class RealEmbeddingArtifactFilesystemMetadata:
    """Filesystem metadata collected without parsing the artifact payload."""

    local_artifact_path: str
    exists: bool
    is_file: bool
    is_dir: bool
    size_bytes: int | None = None
    sha256: str | None = None
    hash_algorithm: str | None = None


@dataclass(frozen=True)
class RealEmbeddingArtifactDirectoryMetadata:
    """Directory metadata collected without loading .npy embedding payloads."""

    local_artifact_path: str
    exists: bool
    is_dir: bool
    file_suffix: str = DEFAULT_DIRECTORY_EMBEDDING_SUFFIX
    total_top_level_files: int = 0
    embedding_files: int = 0
    non_embedding_files: int = 0
    total_embedding_size_bytes: int = 0
    min_embedding_file_size_bytes: int | None = None
    max_embedding_file_size_bytes: int | None = None
    all_embedding_files_same_size: bool | None = None
    filename_category_counts: tuple[tuple[str, int], ...] = ()


def _clean_required_string(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise RealEmbeddingArtifactValidationError(
            f"{field_name} must not be empty."
        )
    if "\x00" in normalized:
        raise RealEmbeddingArtifactValidationError(
            f"{field_name} must not contain null bytes."
        )

    return normalized


def _clean_optional_string(value: object) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip()
    if not normalized:
        return None

    return normalized


def _as_bool(value: object) -> bool:
    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {"1", "true", "yes"}


def _validate_choice(value: object, allowed: tuple[str, ...], field_name: str) -> str:
    normalized = _clean_required_string(value, field_name)
    if normalized not in allowed:
        allowed_text = ", ".join(allowed)
        raise RealEmbeddingArtifactValidationError(
            f"{field_name} must be one of: {allowed_text}; got {normalized!r}."
        )

    return normalized


def _require_positive_int(value: object, field_name: str) -> int:
    if isinstance(value, bool):
        raise RealEmbeddingArtifactValidationError(
            f"{field_name} must be an integer, not bool."
        )

    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise RealEmbeddingArtifactValidationError(
            f"{field_name} must be an integer."
        ) from exc

    if parsed <= 0:
        raise RealEmbeddingArtifactValidationError(f"{field_name} must be positive.")

    return parsed


def _optional_positive_int(value: object, field_name: str) -> int | None:
    if value is None:
        return None

    return _require_positive_int(value, field_name)


def _normalize_declared_columns(columns: Sequence[object]) -> tuple[str, ...]:
    if isinstance(columns, (str, bytes)) or not isinstance(columns, Sequence):
        raise RealEmbeddingArtifactValidationError(
            "declared_columns must be a sequence."
        )

    normalized = tuple(
        _clean_required_string(column, "declared_columns item")
        for column in columns
    )
    lowered = tuple(column.lower() for column in normalized)

    forbidden = sorted(
        column
        for column in lowered
        if any(
            fragment in column
            for fragment in FORBIDDEN_DECLARED_COLUMN_FRAGMENTS
        )
    )
    if forbidden:
        raise RealEmbeddingArtifactValidationError(
            "declared_columns must not include split, prediction, model, "
            "or metric fields."
        )

    return normalized


def _validate_local_artifact_path(path: object) -> str:
    normalized = _clean_required_string(path, "local_artifact_path")
    lowered = normalized.lower()
    if lowered.endswith(FORBIDDEN_OUTPUT_SUFFIXES):
        raise RealEmbeddingArtifactValidationError(
            "local_artifact_path must not point to a model/training artifact-like "
            f"output: {normalized!r}."
        )

    return normalized


def _validate_directory_file_suffix(value: object) -> str:
    suffix = _clean_required_string(value, "directory_file_suffix")
    if not suffix.startswith("."):
        raise RealEmbeddingArtifactValidationError(
            "directory_file_suffix must start with '.'."
        )
    return _validate_choice(
        suffix,
        ALLOWED_DIRECTORY_EMBEDDING_SUFFIXES,
        "directory_file_suffix",
    )


def _optional_bool(value: object, field_name: str) -> bool | None:
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    text_value = str(value).strip().lower()
    if text_value in {"1", "true", "yes"}:
        return True
    if text_value in {"0", "false", "no"}:
        return False

    raise RealEmbeddingArtifactValidationError(
        f"{field_name} must be bool-like or None."
    )


def _validate_sha256(value: object, algorithm: object) -> tuple[str | None, str | None]:
    digest = _clean_optional_string(value)
    hash_algorithm = _clean_optional_string(algorithm)

    if digest is None:
        if hash_algorithm is not None:
            raise RealEmbeddingArtifactValidationError(
                "hash_algorithm requires a sha256 digest."
            )
        return None, None

    if hash_algorithm is None:
        hash_algorithm = DEFAULT_HASH_ALGORITHM

    hash_algorithm = _validate_choice(
        hash_algorithm,
        ALLOWED_HASH_ALGORITHMS,
        "hash_algorithm",
    )
    if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest.lower()):
        raise RealEmbeddingArtifactValidationError(
            "sha256 must be a 64-character hexadecimal digest."
        )

    return digest.lower(), hash_algorithm


def validate_real_embedding_artifact_manifest(
    manifest: RealEmbeddingArtifactManifest,
) -> RealEmbeddingArtifactManifest:
    """Validate and normalize a Stage 4 real embedding artifact manifest."""

    current_feature = _validate_choice(
        manifest.current_feature,
        (STAGE4_CURRENT_FEATURE,),
        "current_feature",
    )
    dataset_id = _clean_required_string(manifest.dataset_id, "dataset_id")
    census_version = _clean_required_string(manifest.census_version, "census_version")

    if dataset_id != PRIMARY_CELLXGENE_DATASET_ID:
        raise RealEmbeddingArtifactValidationError(
            "dataset_id must match the approved primary CELLxGENE contract."
        )
    if census_version != PRIMARY_CELLXGENE_CENSUS_VERSION:
        raise RealEmbeddingArtifactValidationError(
            "census_version must match the approved primary CELLxGENE contract."
        )

    artifact_format = _validate_choice(
        manifest.artifact_format,
        ALLOWED_REAL_EMBEDDING_ARTIFACT_FORMATS,
        "artifact_format",
    )
    artifact_layout = _validate_choice(
        manifest.artifact_layout,
        ALLOWED_ARTIFACT_LAYOUTS,
        "artifact_layout",
    )
    directory_file_suffix = _clean_optional_string(manifest.directory_file_suffix)

    if artifact_format == NPY_DIRECTORY_ARTIFACT_FORMAT:
        if artifact_layout != DIRECTORY_ARTIFACT_LAYOUT:
            raise RealEmbeddingArtifactValidationError(
                "npy_directory artifacts must use directory layout."
            )
        directory_file_suffix = _validate_directory_file_suffix(
            directory_file_suffix or DEFAULT_DIRECTORY_EMBEDDING_SUFFIX
        )
    elif artifact_layout == DIRECTORY_ARTIFACT_LAYOUT:
        raise RealEmbeddingArtifactValidationError(
            "directory layout is currently only allowed for npy_directory artifacts."
        )
    record_level = _validate_choice(
        manifest.record_level,
        ALLOWED_EMBEDDING_RECORD_LEVELS,
        "record_level",
    )
    split_level = _validate_choice(
        manifest.split_level,
        ALLOWED_ARTIFACT_SPLIT_LEVELS,
        "split_level",
    )
    forbidden_split_levels = {str(item) for item in DEFAULT_FORBIDDEN_SPLIT_VALUES}
    if split_level in forbidden_split_levels:
        raise RealEmbeddingArtifactValidationError(
            "cell-level split assignments are not allowed."
        )

    cell_id_column = _clean_optional_string(manifest.cell_id_column)
    sampled_cell_id_column = _clean_optional_string(manifest.sampled_cell_id_column)
    if record_level == "cell" and cell_id_column is None and sampled_cell_id_column is None:
        raise RealEmbeddingArtifactValidationError(
            "cell-level artifacts require cell_id_column or sampled_cell_id_column."
        )
    if artifact_format == NPY_DIRECTORY_ARTIFACT_FORMAT and record_level != "donor":
        raise RealEmbeddingArtifactValidationError(
            "npy_directory artifacts are expected to be donor-level files."
        )

    sha256, hash_algorithm = _validate_sha256(
        manifest.sha256,
        manifest.hash_algorithm,
    )

    if not _as_bool(manifest.allow_file_metadata_inspection):
        raise RealEmbeddingArtifactValidationError(
            "Stage 4-F001 requires safe filesystem metadata inspection."
        )

    forbidden_flags = {
        "artifact_commit_allowed": manifest.artifact_commit_allowed,
        "commit_real_artifact": manifest.commit_real_artifact,
        "contains_model_artifact": manifest.contains_model_artifact,
        "contains_training_artifact": manifest.contains_training_artifact,
        "contains_split_columns": manifest.contains_split_columns,
        "contains_predictions": manifest.contains_predictions,
        "contains_performance_metrics": manifest.contains_performance_metrics,
        "allow_header_inspection": manifest.allow_header_inspection,
        "allow_anndata_loading": manifest.allow_anndata_loading,
        "allow_geneformer_execution": manifest.allow_geneformer_execution,
        "allow_tokenizer_execution": manifest.allow_tokenizer_execution,
        "allow_embedding_extraction": manifest.allow_embedding_extraction,
        "allow_embedding_table_parsing": manifest.allow_embedding_table_parsing,
        "allow_aggregation": manifest.allow_aggregation,
        "allow_feature_extraction": manifest.allow_feature_extraction,
        "allow_global_preprocessing": manifest.allow_global_preprocessing,
        "allow_scaler_outside_fold": manifest.allow_scaler_outside_fold,
        "allow_model_fitting": manifest.allow_model_fitting,
        "allow_metric_computation": manifest.allow_metric_computation,
        "allow_modeling": manifest.allow_modeling,
        "allow_training": manifest.allow_training,
        "allow_external_validation": manifest.allow_external_validation,
        "performance_claims_added": manifest.performance_claims_added,
    }
    enabled = sorted(name for name, value in forbidden_flags.items() if _as_bool(value))
    if enabled:
        raise RealEmbeddingArtifactValidationError(
            "Stage 4-F001 manifest keeps runtime/modeling/training/performance "
            f"flags disabled; enabled: {', '.join(enabled)}."
        )

    return RealEmbeddingArtifactManifest(
        local_artifact_path=_validate_local_artifact_path(
            manifest.local_artifact_path,
        ),
        dataset_id=dataset_id,
        source=_clean_required_string(manifest.source, "source"),
        census_version=census_version,
        current_feature=current_feature,
        artifact_format=artifact_format,
        artifact_layout=artifact_layout,
        directory_file_suffix=directory_file_suffix,
        record_level=record_level,
        split_level=split_level,
        donor_id_column=_clean_required_string(
            manifest.donor_id_column,
            "donor_id_column",
        ),
        cell_id_column=cell_id_column,
        sampled_cell_id_column=sampled_cell_id_column,
        embedding_column=_clean_required_string(
            manifest.embedding_column,
            "embedding_column",
        ),
        embedding_dimension=_require_positive_int(
            manifest.embedding_dimension,
            "embedding_dimension",
        ),
        embedding_source=_clean_required_string(
            manifest.embedding_source,
            "embedding_source",
        ),
        declared_columns=_normalize_declared_columns(manifest.declared_columns),
        size_bytes=_optional_positive_int(manifest.size_bytes, "size_bytes"),
        expected_file_count=_optional_positive_int(
            manifest.expected_file_count,
            "expected_file_count",
        ),
        observed_file_count=_optional_positive_int(
            manifest.observed_file_count,
            "observed_file_count",
        ),
        total_size_bytes=_optional_positive_int(
            manifest.total_size_bytes,
            "total_size_bytes",
        ),
        min_file_size_bytes=_optional_positive_int(
            manifest.min_file_size_bytes,
            "min_file_size_bytes",
        ),
        max_file_size_bytes=_optional_positive_int(
            manifest.max_file_size_bytes,
            "max_file_size_bytes",
        ),
        all_files_same_size=_optional_bool(
            manifest.all_files_same_size,
            "all_files_same_size",
        ),
        sha256=sha256,
        hash_algorithm=hash_algorithm,
        validation_status=_validate_choice(
            manifest.validation_status,
            ALLOWED_VALIDATION_STATUSES,
            "validation_status",
        ),
        artifact_commit_allowed=False,
        commit_real_artifact=False,
        contains_model_artifact=False,
        contains_training_artifact=False,
        contains_split_columns=False,
        contains_predictions=False,
        contains_performance_metrics=False,
        allow_file_metadata_inspection=True,
        allow_header_inspection=False,
        allow_anndata_loading=False,
        allow_geneformer_execution=False,
        allow_tokenizer_execution=False,
        allow_embedding_extraction=False,
        allow_embedding_table_parsing=False,
        allow_aggregation=False,
        allow_feature_extraction=False,
        allow_global_preprocessing=False,
        allow_scaler_outside_fold=False,
        allow_model_fitting=False,
        allow_metric_computation=False,
        allow_modeling=False,
        allow_training=False,
        allow_external_validation=False,
        performance_claims_added=False,
        notes=str(manifest.notes).strip(),
    )


def real_embedding_artifact_manifest_from_mapping(
    data: Mapping[str, Any],
) -> RealEmbeddingArtifactManifest:
    """Build and validate a Stage 4 manifest from mapping data."""

    return validate_real_embedding_artifact_manifest(
        RealEmbeddingArtifactManifest(
            local_artifact_path=data.get("local_artifact_path", ""),
            dataset_id=data.get("dataset_id", PRIMARY_CELLXGENE_DATASET_ID),
            source=data.get("source", "CELLxGENE Census"),
            census_version=data.get(
                "census_version",
                PRIMARY_CELLXGENE_CENSUS_VERSION,
            ),
            current_feature=data.get("current_feature", STAGE4_CURRENT_FEATURE),
            artifact_format=data.get("artifact_format", "parquet"),
            artifact_layout=data.get("artifact_layout", SINGLE_FILE_ARTIFACT_LAYOUT),
            directory_file_suffix=data.get("directory_file_suffix"),
            record_level=data.get("record_level", "cell"),
            split_level=data.get("split_level", "patient"),
            donor_id_column=data.get("donor_id_column", DEFAULT_DONOR_COLUMN),
            cell_id_column=data.get("cell_id_column", "cell_id"),
            sampled_cell_id_column=data.get("sampled_cell_id_column"),
            embedding_column=data.get("embedding_column", DEFAULT_EMBEDDING_COLUMN),
            embedding_dimension=data.get(
                "embedding_dimension",
                DEFAULT_EMBEDDING_DIMENSION,
            ),
            embedding_source=data.get("embedding_source", DEFAULT_EMBEDDING_SOURCE),
            declared_columns=tuple(data.get("declared_columns", ())),
            size_bytes=data.get("size_bytes"),
            expected_file_count=data.get("expected_file_count"),
            observed_file_count=data.get("observed_file_count"),
            total_size_bytes=data.get("total_size_bytes"),
            min_file_size_bytes=data.get("min_file_size_bytes"),
            max_file_size_bytes=data.get("max_file_size_bytes"),
            all_files_same_size=data.get("all_files_same_size"),
            sha256=data.get("sha256"),
            hash_algorithm=data.get("hash_algorithm"),
            validation_status=data.get("validation_status", NOT_CHECKED),
            artifact_commit_allowed=data.get("artifact_commit_allowed", False),
            commit_real_artifact=data.get("commit_real_artifact", False),
            contains_model_artifact=data.get("contains_model_artifact", False),
            contains_training_artifact=data.get("contains_training_artifact", False),
            contains_split_columns=data.get("contains_split_columns", False),
            contains_predictions=data.get("contains_predictions", False),
            contains_performance_metrics=data.get(
                "contains_performance_metrics",
                False,
            ),
            allow_file_metadata_inspection=data.get(
                "allow_file_metadata_inspection",
                True,
            ),
            allow_header_inspection=data.get("allow_header_inspection", False),
            allow_anndata_loading=data.get("allow_anndata_loading", False),
            allow_geneformer_execution=data.get("allow_geneformer_execution", False),
            allow_tokenizer_execution=data.get("allow_tokenizer_execution", False),
            allow_embedding_extraction=data.get("allow_embedding_extraction", False),
            allow_embedding_table_parsing=data.get(
                "allow_embedding_table_parsing",
                False,
            ),
            allow_aggregation=data.get("allow_aggregation", False),
            allow_feature_extraction=data.get("allow_feature_extraction", False),
            allow_global_preprocessing=data.get("allow_global_preprocessing", False),
            allow_scaler_outside_fold=data.get("allow_scaler_outside_fold", False),
            allow_model_fitting=data.get("allow_model_fitting", False),
            allow_metric_computation=data.get("allow_metric_computation", False),
            allow_modeling=data.get("allow_modeling", False),
            allow_training=data.get("allow_training", False),
            allow_external_validation=data.get("allow_external_validation", False),
            performance_claims_added=data.get("performance_claims_added", False),
            notes=data.get("notes", ""),
        )
    )


def real_embedding_artifact_manifest_to_dict(
    manifest: RealEmbeddingArtifactManifest,
) -> dict[str, Any]:
    """Validate and serialize a Stage 4 real artifact manifest."""

    return asdict(validate_real_embedding_artifact_manifest(manifest))


def collect_artifact_filesystem_metadata(
    local_artifact_path: str,
    *,
    compute_sha256: bool = False,
    chunk_size: int = 1024 * 1024,
) -> RealEmbeddingArtifactFilesystemMetadata:
    """Collect path existence, size, and optional checksum without parsing data."""

    normalized_path = _validate_local_artifact_path(local_artifact_path)
    path = Path(normalized_path)

    if chunk_size <= 0:
        raise RealEmbeddingArtifactValidationError("chunk_size must be positive.")

    exists = path.exists()
    is_file = path.is_file()
    is_dir = path.is_dir()
    size_bytes = path.stat().st_size if is_file else None
    digest: str | None = None
    hash_algorithm: str | None = None

    if compute_sha256:
        if not is_file:
            raise RealEmbeddingArtifactValidationError(
                "sha256 can only be computed for an existing regular file."
            )

        hasher = hashlib.sha256()
        with path.open("rb") as artifact:
            for chunk in iter(lambda: artifact.read(chunk_size), b""):
                hasher.update(chunk)
        digest = hasher.hexdigest()
        hash_algorithm = DEFAULT_HASH_ALGORITHM

    return RealEmbeddingArtifactFilesystemMetadata(
        local_artifact_path=normalized_path,
        exists=exists,
        is_file=is_file,
        is_dir=is_dir,
        size_bytes=size_bytes,
        sha256=digest,
        hash_algorithm=hash_algorithm,
    )


def _filename_category(filename: str) -> str:
    """Classify donor-like filenames without opening embedding payloads."""

    stem = Path(filename).stem
    if stem.startswith("FLARE"):
        return "flare_like"
    if stem.startswith("HC-"):
        return "healthy_hc_like"
    if stem.startswith("IGTB"):
        return "healthy_igtb_like"
    if stem == "ICC_control":
        return "control_like"
    if stem.isdigit():
        return "managed_sle_numeric_like"

    return "other"


def collect_embedding_directory_metadata(
    local_artifact_path: str,
    *,
    file_suffix: str = DEFAULT_DIRECTORY_EMBEDDING_SUFFIX,
) -> RealEmbeddingArtifactDirectoryMetadata:
    """Collect directory metadata without loading .npy embedding payloads."""

    normalized_path = _validate_local_artifact_path(local_artifact_path)
    suffix = _validate_directory_file_suffix(file_suffix)
    path = Path(normalized_path)

    if not path.exists():
        return RealEmbeddingArtifactDirectoryMetadata(
            local_artifact_path=normalized_path,
            exists=False,
            is_dir=False,
            file_suffix=suffix,
        )

    if not path.is_dir():
        raise RealEmbeddingArtifactValidationError(
            "embedding directory metadata requires an existing directory."
        )

    files = sorted(child for child in path.iterdir() if child.is_file())
    embedding_files = [child for child in files if child.suffix == suffix]
    non_embedding_files = [child for child in files if child.suffix != suffix]
    sizes = [child.stat().st_size for child in embedding_files]
    category_counts = Counter(_filename_category(child.name) for child in embedding_files)

    return RealEmbeddingArtifactDirectoryMetadata(
        local_artifact_path=normalized_path,
        exists=True,
        is_dir=True,
        file_suffix=suffix,
        total_top_level_files=len(files),
        embedding_files=len(embedding_files),
        non_embedding_files=len(non_embedding_files),
        total_embedding_size_bytes=sum(sizes),
        min_embedding_file_size_bytes=min(sizes) if sizes else None,
        max_embedding_file_size_bytes=max(sizes) if sizes else None,
        all_embedding_files_same_size=(len(set(sizes)) == 1) if sizes else None,
        filename_category_counts=tuple(sorted(category_counts.items())),
    )
