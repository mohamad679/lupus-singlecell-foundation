import pytest

from lupusfm.data.anndata_schema import AnnDataSchemaReport
from lupusfm.data.cohort import CohortSummary
from lupusfm.data.ingestion_readiness import (
    IngestionReadinessReport,
    ReadinessCheck,
)
from lupusfm.data.manifest import (
    DEFAULT_RANDOM_SEED,
    PRIMARY_CELLXGENE_CENSUS_VERSION,
    PRIMARY_CELLXGENE_DATASET_ID,
    PRIMARY_EXPECTED_TOTAL_CELLS,
    PRIMARY_EXPECTED_TOTAL_DONORS,
    IngestionManifest,
    IngestionManifestError,
    ManifestOutputPaths,
    ingestion_manifest_to_dict,
    make_ingestion_manifest_from_mapping,
    make_primary_cellxgene_ingestion_manifest,
    validate_ingestion_manifest,
    validate_manifest_against_readiness_report,
)


def valid_output_paths():
    return ManifestOutputPaths(
        root="artifacts/stage1",
        manifest="artifacts/stage1/ingestion_manifest.json",
        readiness_report="artifacts/stage1/ingestion_readiness.json",
        cohort_summary="artifacts/stage1/cohort_summary.json",
    )


def valid_manifest():
    return IngestionManifest(
        dataset_id="dataset-001",
        source="CELLxGENE Census",
        census_version="2025-11-08",
        donor_column="donor_id",
        gene_symbol_column="gene_symbol",
        split_column="split_group",
        expected_total_donors=3,
        expected_total_cells=4,
        random_seed=42,
        output_paths=valid_output_paths(),
        notes="test manifest",
    )


def ready_report():
    return IngestionReadinessReport(
        schema_report=AnnDataSchemaReport(
            n_obs=4,
            n_vars=2,
            x_shape=(4, 2),
            obs_columns=("donor_id", "cell_type", "split_group"),
            var_columns=("gene_symbol", "feature_type"),
            validated_obs_columns=("donor_id",),
            validated_var_columns=("gene_symbol",),
        ),
        cohort_summary=CohortSummary(
            total_cells=4,
            total_donors=3,
            donor_counts=(),
            clinical_status_counts=(),
        ),
        mitochondrial_gene_summary={
            "total_gene_count": 2,
            "mitochondrial_gene_count": 1,
            "non_mitochondrial_gene_count": 1,
        },
        checks=(
            ReadinessCheck("anndata_schema", True, "ok"),
            ReadinessCheck("cohort_summary", True, "ok"),
            ReadinessCheck("mitochondrial_annotation", True, "ok"),
        ),
    )


def test_validate_ingestion_manifest_accepts_valid_manifest():
    manifest = validate_ingestion_manifest(valid_manifest())

    assert manifest.dataset_id == "dataset-001"
    assert manifest.allow_downloads is False
    assert manifest.allow_embedding_extraction is False
    assert manifest.allow_modeling is False
    assert manifest.allow_training is False


@pytest.mark.parametrize(
    "field_name",
    ["dataset_id", "source", "census_version", "donor_column", "gene_symbol_column"],
)
def test_validate_ingestion_manifest_rejects_empty_required_strings(field_name):
    values = valid_manifest().__dict__.copy()
    values[field_name] = "   "

    with pytest.raises(IngestionManifestError, match=field_name):
        validate_ingestion_manifest(IngestionManifest(**values))


@pytest.mark.parametrize(
    ("field_name", "bad_value"),
    [
        ("expected_total_donors", 0),
        ("expected_total_cells", 0),
        ("random_seed", -1),
    ],
)
def test_validate_ingestion_manifest_rejects_bad_counts_and_seed(field_name, bad_value):
    values = valid_manifest().__dict__.copy()
    values[field_name] = bad_value

    with pytest.raises(IngestionManifestError, match=field_name):
        validate_ingestion_manifest(IngestionManifest(**values))


def test_validate_ingestion_manifest_requires_cells_at_least_donors():
    values = valid_manifest().__dict__.copy()
    values["expected_total_donors"] = 5
    values["expected_total_cells"] = 4

    with pytest.raises(IngestionManifestError, match="expected_total_cells"):
        validate_ingestion_manifest(IngestionManifest(**values))


@pytest.mark.parametrize(
    "flag_name",
    [
        "allow_downloads",
        "allow_embedding_extraction",
        "allow_modeling",
        "allow_training",
    ],
)
def test_validate_ingestion_manifest_keeps_stage2_work_disabled(flag_name):
    values = valid_manifest().__dict__.copy()
    values[flag_name] = True

    with pytest.raises(IngestionManifestError, match="disabled"):
        validate_ingestion_manifest(IngestionManifest(**values))


def test_validate_ingestion_manifest_rejects_model_artifact_output_suffixes():
    values = valid_manifest().__dict__.copy()
    values["output_paths"] = ManifestOutputPaths(
        root="artifacts/stage1",
        manifest="artifacts/stage1/model.pkl",
        readiness_report="artifacts/stage1/ingestion_readiness.json",
        cohort_summary="artifacts/stage1/cohort_summary.json",
    )

    with pytest.raises(IngestionManifestError, match="model/artifact-like"):
        validate_ingestion_manifest(IngestionManifest(**values))


def test_make_ingestion_manifest_from_mapping_parses_and_validates_values():
    manifest = make_ingestion_manifest_from_mapping(
        {
            "dataset_id": "dataset-001",
            "source": "CELLxGENE Census",
            "census_version": "2025-11-08",
            "donor_column": "donor_id",
            "gene_symbol_column": "gene_symbol",
            "split_column": "split_group",
            "expected_total_donors": "3",
            "expected_total_cells": "4",
            "random_seed": "7",
            "output_paths": {
                "root": "artifacts/stage1",
                "manifest": "artifacts/stage1/ingestion_manifest.json",
                "readiness_report": "artifacts/stage1/ingestion_readiness.json",
                "cohort_summary": "artifacts/stage1/cohort_summary.json",
            },
            "allow_downloads": "false",
            "allow_embedding_extraction": "false",
            "allow_modeling": "false",
            "allow_training": "false",
        }
    )

    assert manifest.expected_total_donors == 3
    assert manifest.expected_total_cells == 4
    assert manifest.random_seed == 7


def test_make_ingestion_manifest_from_mapping_requires_output_paths_mapping():
    with pytest.raises(IngestionManifestError, match="output_paths"):
        make_ingestion_manifest_from_mapping({"output_paths": None})


def test_primary_cellxgene_manifest_is_locked_for_stage1_contract():
    manifest = make_primary_cellxgene_ingestion_manifest()

    assert manifest.dataset_id == PRIMARY_CELLXGENE_DATASET_ID
    assert manifest.census_version == PRIMARY_CELLXGENE_CENSUS_VERSION
    assert manifest.expected_total_donors == PRIMARY_EXPECTED_TOTAL_DONORS
    assert manifest.expected_total_cells == PRIMARY_EXPECTED_TOTAL_CELLS
    assert manifest.random_seed == DEFAULT_RANDOM_SEED
    assert manifest.donor_column == "donor_id"
    assert manifest.gene_symbol_column == "gene_symbol"
    assert manifest.allow_downloads is False
    assert manifest.allow_embedding_extraction is False
    assert manifest.allow_modeling is False
    assert manifest.allow_training is False


def test_ingestion_manifest_to_dict_serializes_validated_manifest():
    serialized = ingestion_manifest_to_dict(valid_manifest())

    assert serialized["dataset_id"] == "dataset-001"
    assert serialized["output_paths"]["manifest"].endswith("ingestion_manifest.json")
    assert serialized["allow_modeling"] is False


def test_validate_manifest_against_readiness_report_accepts_matching_report():
    validate_manifest_against_readiness_report(valid_manifest(), ready_report())


def test_validate_manifest_against_readiness_report_rejects_failed_readiness():
    report = IngestionReadinessReport(
        schema_report=None,
        cohort_summary=None,
        mitochondrial_gene_summary=None,
        checks=(ReadinessCheck("anndata_schema", False, "bad"),),
    )

    with pytest.raises(IngestionManifestError, match="not ready"):
        validate_manifest_against_readiness_report(valid_manifest(), report)


def test_validate_manifest_against_readiness_report_rejects_donor_count_mismatch():
    manifest = valid_manifest()
    report = ready_report()
    report = IngestionReadinessReport(
        schema_report=report.schema_report,
        cohort_summary=CohortSummary(
            total_cells=4,
            total_donors=2,
            donor_counts=(),
            clinical_status_counts=(),
        ),
        mitochondrial_gene_summary=report.mitochondrial_gene_summary,
        checks=report.checks,
    )

    with pytest.raises(IngestionManifestError, match="expected_total_donors"):
        validate_manifest_against_readiness_report(manifest, report)


def test_validate_manifest_against_readiness_report_rejects_missing_columns():
    report = ready_report()
    report = IngestionReadinessReport(
        schema_report=AnnDataSchemaReport(
            n_obs=4,
            n_vars=2,
            x_shape=(4, 2),
            obs_columns=("cell_type", "split_group"),
            var_columns=("feature_type",),
            validated_obs_columns=(),
            validated_var_columns=(),
        ),
        cohort_summary=report.cohort_summary,
        mitochondrial_gene_summary=report.mitochondrial_gene_summary,
        checks=report.checks,
    )

    with pytest.raises(IngestionManifestError, match="donor_column"):
        validate_manifest_against_readiness_report(valid_manifest(), report)
