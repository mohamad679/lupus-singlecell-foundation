"""Manifest and reproducibility contract utilities.

These helpers define and validate the Stage 1 ingestion manifest before any
Stage 2 embedding extraction or modeling is allowed. They do not download data,
load AnnData files, write outputs, extract embeddings, train models, or approve
datasets for modeling.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from lupusfm.data.anndata_schema import DEFAULT_GENE_SYMBOL_COLUMN
from lupusfm.data.ingestion_readiness import IngestionReadinessReport
from lupusfm.data.metadata import DEFAULT_DONOR_COLUMN


PRIMARY_CELLXGENE_DATASET_ID = "218acb0f-9f2f-4f76-b90b-15a4b7c7f629"
PRIMARY_CELLXGENE_CENSUS_VERSION = "2025-11-08"
PRIMARY_EXPECTED_TOTAL_DONORS = 261
PRIMARY_EXPECTED_TOTAL_CELLS = 1_263_438

DEFAULT_RANDOM_SEED = 42

FORBIDDEN_OUTPUT_SUFFIXES = (
    ".ckpt",
    ".joblib",
    ".onnx",
    ".pkl",
    ".pt",
    ".pth",
)


class IngestionManifestError(ValueError):
    """Raised when an ingestion manifest violates the Stage 1 contract."""


@dataclass(frozen=True)
class ManifestOutputPaths:
    """Declared output locations for Stage 1 reports/manifests only."""

    root: str
    manifest: str
    readiness_report: str
    cohort_summary: str


@dataclass(frozen=True)
class IngestionManifest:
    """Reproducibility contract for one ingestion-ready dataset."""

    dataset_id: str
    source: str
    census_version: str
    donor_column: str
    gene_symbol_column: str
    split_column: str | None
    expected_total_donors: int
    expected_total_cells: int
    random_seed: int
    output_paths: ManifestOutputPaths
    allow_downloads: bool = False
    allow_embedding_extraction: bool = False
    allow_modeling: bool = False
    allow_training: bool = False
    notes: str = ""


def _clean_required_string(value: object, field_name: str) -> str:
    """Return a non-empty normalized string or raise."""

    normalized = str(value).strip()
    if not normalized:
        raise IngestionManifestError(f"{field_name} must not be empty.")
    return normalized


def _require_non_negative_int(value: object, field_name: str) -> int:
    """Return a non-negative integer or raise."""

    if isinstance(value, bool):
        raise IngestionManifestError(f"{field_name} must be an integer, not bool.")

    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise IngestionManifestError(f"{field_name} must be an integer.") from exc

    if parsed < 0:
        raise IngestionManifestError(f"{field_name} must be non-negative.")

    return parsed


def _require_positive_int(value: object, field_name: str) -> int:
    """Return a positive integer or raise."""

    parsed = _require_non_negative_int(value, field_name)
    if parsed <= 0:
        raise IngestionManifestError(f"{field_name} must be positive.")
    return parsed


def _as_bool(value: object) -> bool:
    """Parse common bool-like values."""

    if isinstance(value, bool):
        return value

    return str(value).strip().lower() in {"1", "true", "yes"}


def _validate_output_path(path: str, field_name: str) -> str:
    """Validate one declared Stage 1 output path."""

    normalized = _clean_required_string(path, field_name)
    lowered = normalized.lower()

    if lowered.endswith(FORBIDDEN_OUTPUT_SUFFIXES):
        raise IngestionManifestError(
            f"{field_name} points to a model/artifact-like output: {normalized!r}."
        )

    return normalized


def validate_manifest_output_paths(output_paths: ManifestOutputPaths) -> ManifestOutputPaths:
    """Validate declared Stage 1 output paths."""

    return ManifestOutputPaths(
        root=_validate_output_path(output_paths.root, "output_paths.root"),
        manifest=_validate_output_path(output_paths.manifest, "output_paths.manifest"),
        readiness_report=_validate_output_path(
            output_paths.readiness_report,
            "output_paths.readiness_report",
        ),
        cohort_summary=_validate_output_path(
            output_paths.cohort_summary,
            "output_paths.cohort_summary",
        ),
    )


def validate_ingestion_manifest(manifest: IngestionManifest) -> IngestionManifest:
    """Validate a Stage 1 ingestion manifest and return a normalized copy."""

    expected_total_donors = _require_positive_int(
        manifest.expected_total_donors,
        "expected_total_donors",
    )
    expected_total_cells = _require_positive_int(
        manifest.expected_total_cells,
        "expected_total_cells",
    )

    if expected_total_cells < expected_total_donors:
        raise IngestionManifestError(
            "expected_total_cells must be greater than or equal to "
            "expected_total_donors."
        )

    if manifest.allow_downloads:
        raise IngestionManifestError("Stage 1 manifest must keep downloads disabled.")
    if manifest.allow_embedding_extraction:
        raise IngestionManifestError(
            "Stage 1 manifest must keep embedding extraction disabled."
        )
    if manifest.allow_modeling:
        raise IngestionManifestError("Stage 1 manifest must keep modeling disabled.")
    if manifest.allow_training:
        raise IngestionManifestError("Stage 1 manifest must keep training disabled.")

    return IngestionManifest(
        dataset_id=_clean_required_string(manifest.dataset_id, "dataset_id"),
        source=_clean_required_string(manifest.source, "source"),
        census_version=_clean_required_string(
            manifest.census_version,
            "census_version",
        ),
        donor_column=_clean_required_string(manifest.donor_column, "donor_column"),
        gene_symbol_column=_clean_required_string(
            manifest.gene_symbol_column,
            "gene_symbol_column",
        ),
        split_column=(
            None
            if manifest.split_column is None
            else _clean_required_string(manifest.split_column, "split_column")
        ),
        expected_total_donors=expected_total_donors,
        expected_total_cells=expected_total_cells,
        random_seed=_require_non_negative_int(manifest.random_seed, "random_seed"),
        output_paths=validate_manifest_output_paths(manifest.output_paths),
        allow_downloads=False,
        allow_embedding_extraction=False,
        allow_modeling=False,
        allow_training=False,
        notes=str(manifest.notes),
    )


def make_ingestion_manifest_from_mapping(row: Mapping[str, Any]) -> IngestionManifest:
    """Create and validate an ingestion manifest from mapping-like metadata."""

    output_paths_raw = row.get("output_paths")
    if not isinstance(output_paths_raw, Mapping):
        raise IngestionManifestError("output_paths must be a mapping.")

    output_paths = ManifestOutputPaths(
        root=output_paths_raw.get("root", ""),
        manifest=output_paths_raw.get("manifest", ""),
        readiness_report=output_paths_raw.get("readiness_report", ""),
        cohort_summary=output_paths_raw.get("cohort_summary", ""),
    )

    manifest = IngestionManifest(
        dataset_id=row.get("dataset_id", ""),
        source=row.get("source", ""),
        census_version=row.get("census_version", ""),
        donor_column=row.get("donor_column", DEFAULT_DONOR_COLUMN),
        gene_symbol_column=row.get("gene_symbol_column", DEFAULT_GENE_SYMBOL_COLUMN),
        split_column=row.get("split_column"),
        expected_total_donors=row.get("expected_total_donors", 0),
        expected_total_cells=row.get("expected_total_cells", 0),
        random_seed=row.get("random_seed", DEFAULT_RANDOM_SEED),
        output_paths=output_paths,
        allow_downloads=_as_bool(row.get("allow_downloads", False)),
        allow_embedding_extraction=_as_bool(
            row.get("allow_embedding_extraction", False)
        ),
        allow_modeling=_as_bool(row.get("allow_modeling", False)),
        allow_training=_as_bool(row.get("allow_training", False)),
        notes=row.get("notes", ""),
    )

    return validate_ingestion_manifest(manifest)


def make_primary_cellxgene_ingestion_manifest(
    output_root: str = "artifacts/stage1",
) -> IngestionManifest:
    """Create the locked primary CELLxGENE manifest contract for Stage 1."""

    return validate_ingestion_manifest(
        IngestionManifest(
            dataset_id=PRIMARY_CELLXGENE_DATASET_ID,
            source="CELLxGENE Census",
            census_version=PRIMARY_CELLXGENE_CENSUS_VERSION,
            donor_column=DEFAULT_DONOR_COLUMN,
            gene_symbol_column=DEFAULT_GENE_SYMBOL_COLUMN,
            split_column="split_group",
            expected_total_donors=PRIMARY_EXPECTED_TOTAL_DONORS,
            expected_total_cells=PRIMARY_EXPECTED_TOTAL_CELLS,
            random_seed=DEFAULT_RANDOM_SEED,
            output_paths=ManifestOutputPaths(
                root=output_root,
                manifest=f"{output_root}/ingestion_manifest.json",
                readiness_report=f"{output_root}/ingestion_readiness.json",
                cohort_summary=f"{output_root}/cohort_summary.json",
            ),
            notes="Primary exploratory CELLxGENE/Perez lupus cohort contract.",
        )
    )


def ingestion_manifest_to_dict(manifest: IngestionManifest) -> dict[str, Any]:
    """Serialize a validated manifest to a plain dictionary."""

    return asdict(validate_ingestion_manifest(manifest))


def validate_manifest_against_readiness_report(
    manifest: IngestionManifest,
    readiness_report: IngestionReadinessReport,
) -> None:
    """Validate manifest counts/columns against an ingestion-readiness report."""

    validated = validate_ingestion_manifest(manifest)

    if not readiness_report.is_ready:
        raise IngestionManifestError("readiness report is not ready.")

    if readiness_report.schema_report is None:
        raise IngestionManifestError("readiness report is missing schema_report.")

    if readiness_report.cohort_summary is None:
        raise IngestionManifestError("readiness report is missing cohort_summary.")

    schema_report = readiness_report.schema_report
    cohort_summary = readiness_report.cohort_summary

    if cohort_summary.total_donors != validated.expected_total_donors:
        raise IngestionManifestError(
            "manifest expected_total_donors does not match readiness report: "
            f"{validated.expected_total_donors} != {cohort_summary.total_donors}."
        )

    if cohort_summary.total_cells != validated.expected_total_cells:
        raise IngestionManifestError(
            "manifest expected_total_cells does not match readiness report: "
            f"{validated.expected_total_cells} != {cohort_summary.total_cells}."
        )

    if schema_report.n_obs != validated.expected_total_cells:
        raise IngestionManifestError(
            "schema_report.n_obs does not match manifest expected_total_cells: "
            f"{schema_report.n_obs} != {validated.expected_total_cells}."
        )

    if validated.donor_column not in schema_report.obs_columns:
        raise IngestionManifestError(
            f"donor_column {validated.donor_column!r} is missing from schema report."
        )

    if validated.gene_symbol_column not in schema_report.var_columns:
        raise IngestionManifestError(
            "gene_symbol_column "
            f"{validated.gene_symbol_column!r} is missing from schema report."
        )
