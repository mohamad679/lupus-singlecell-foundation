import inspect

import pytest

import lupusfm.embeddings.readiness as readiness_module
from lupusfm.data.anndata_schema import AnnDataSchemaReport
from lupusfm.data.cohort import CohortSummary
from lupusfm.data.ingestion_readiness import (
    IngestionReadinessReport,
    ReadinessCheck,
)
from lupusfm.data.manifest import (
    PRIMARY_EXPECTED_TOTAL_CELLS,
    PRIMARY_EXPECTED_TOTAL_DONORS,
    make_primary_cellxgene_ingestion_manifest,
)
from lupusfm.embeddings.config import (
    EmbeddingExtractionConfig,
    EmbeddingOutputPaths,
    make_primary_cellxgene_embedding_config,
)
from lupusfm.embeddings.provenance import (
    EmbeddingProvenanceManifest,
    make_embedding_provenance_from_config,
)
from lupusfm.embeddings.readiness import (
    EmbeddingDryRunReadinessError,
    build_embedding_dry_run_readiness_report,
    embedding_dry_run_readiness_to_dict,
    require_embedding_dry_run_ready,
)


def ready_ingestion_report():
    return IngestionReadinessReport(
        schema_report=AnnDataSchemaReport(
            n_obs=PRIMARY_EXPECTED_TOTAL_CELLS,
            n_vars=61_497,
            x_shape=(PRIMARY_EXPECTED_TOTAL_CELLS, 61_497),
            obs_columns=("donor_id", "cell_type", "split_group"),
            var_columns=("gene_symbol", "feature_type"),
            validated_obs_columns=("donor_id",),
            validated_var_columns=("gene_symbol",),
        ),
        cohort_summary=CohortSummary(
            total_cells=PRIMARY_EXPECTED_TOTAL_CELLS,
            total_donors=PRIMARY_EXPECTED_TOTAL_DONORS,
            donor_counts=(),
            clinical_status_counts=(),
        ),
        mitochondrial_gene_summary={
            "total_gene_count": 61_497,
            "mitochondrial_gene_count": 13,
            "non_mitochondrial_gene_count": 61_484,
        },
        checks=(
            ReadinessCheck("anndata_schema", True, "ok"),
            ReadinessCheck("cohort_summary", True, "ok"),
            ReadinessCheck("mitochondrial_annotation", True, "ok"),
        ),
    )


def valid_inputs():
    manifest = make_primary_cellxgene_ingestion_manifest()
    config = make_primary_cellxgene_embedding_config()
    provenance = make_embedding_provenance_from_config(config)
    return manifest, ready_ingestion_report(), config, provenance


def test_build_embedding_dry_run_readiness_report_accepts_valid_contracts():
    manifest, readiness_report, config, provenance = valid_inputs()

    report = build_embedding_dry_run_readiness_report(
        manifest=manifest,
        readiness_report=readiness_report,
        config=config,
        provenance=provenance,
    )

    assert report.is_ready is True
    assert report.failed_checks == ()
    assert [check.name for check in report.checks] == [
        "manifest_readiness",
        "embedding_config",
        "config_manifest_consistency",
        "embedding_provenance",
        "provenance_config_consistency",
        "output_paths",
    ]


def test_require_embedding_dry_run_ready_returns_ready_report():
    manifest, readiness_report, config, provenance = valid_inputs()

    report = require_embedding_dry_run_ready(
        manifest=manifest,
        readiness_report=readiness_report,
        config=config,
        provenance=provenance,
    )

    assert report.is_ready is True


def test_build_embedding_dry_run_readiness_report_collects_failed_readiness():
    manifest, readiness_report, config, provenance = valid_inputs()
    readiness_report = IngestionReadinessReport(
        schema_report=None,
        cohort_summary=None,
        mitochondrial_gene_summary=None,
        checks=(ReadinessCheck("anndata_schema", False, "missing schema"),),
    )

    report = build_embedding_dry_run_readiness_report(
        manifest=manifest,
        readiness_report=readiness_report,
        config=config,
        provenance=provenance,
    )

    assert report.is_ready is False
    assert "manifest_readiness" in {check.name for check in report.failed_checks}


def test_build_embedding_dry_run_readiness_report_collects_config_manifest_mismatch():
    manifest, readiness_report, config, provenance = valid_inputs()
    values = config.__dict__.copy()
    values["random_seed"] = 7
    config = EmbeddingExtractionConfig(**values)

    report = build_embedding_dry_run_readiness_report(
        manifest=manifest,
        readiness_report=readiness_report,
        config=config,
        provenance=provenance,
    )

    assert report.is_ready is False
    failed_names = {check.name for check in report.failed_checks}
    assert "config_manifest_consistency" in failed_names
    assert "provenance_config_consistency" in failed_names


def test_build_embedding_dry_run_readiness_report_collects_provenance_mismatch():
    manifest, readiness_report, config, provenance = valid_inputs()
    values = provenance.__dict__.copy()
    values["batch_size"] = 32
    provenance = EmbeddingProvenanceManifest(**values)

    report = build_embedding_dry_run_readiness_report(
        manifest=manifest,
        readiness_report=readiness_report,
        config=config,
        provenance=provenance,
    )

    assert report.is_ready is False
    assert "provenance_config_consistency" in {
        check.name for check in report.failed_checks
    }


def test_build_embedding_dry_run_readiness_report_collects_unsafe_provenance_flags():
    manifest, readiness_report, config, provenance = valid_inputs()
    values = provenance.__dict__.copy()
    values["allow_embedding_extraction"] = True
    provenance = EmbeddingProvenanceManifest(**values)

    report = build_embedding_dry_run_readiness_report(
        manifest=manifest,
        readiness_report=readiness_report,
        config=config,
        provenance=provenance,
    )

    assert report.is_ready is False
    assert "embedding_provenance" in {check.name for check in report.failed_checks}


def test_build_embedding_dry_run_readiness_report_rejects_duplicate_output_paths():
    manifest, readiness_report, config, provenance = valid_inputs()
    output_values = config.output_paths.__dict__.copy()
    output_values["sampled_cell_ids"] = output_values["config"]
    config_values = config.__dict__.copy()
    config_values["output_paths"] = EmbeddingOutputPaths(**output_values)
    config = EmbeddingExtractionConfig(**config_values)
    provenance = make_embedding_provenance_from_config(config)

    report = build_embedding_dry_run_readiness_report(
        manifest=manifest,
        readiness_report=readiness_report,
        config=config,
        provenance=provenance,
    )

    assert report.is_ready is False
    assert "output_paths" in {check.name for check in report.failed_checks}


def test_require_embedding_dry_run_ready_raises_for_failed_report():
    manifest, readiness_report, config, provenance = valid_inputs()
    readiness_report = IngestionReadinessReport(
        schema_report=None,
        cohort_summary=None,
        mitochondrial_gene_summary=None,
        checks=(ReadinessCheck("anndata_schema", False, "missing schema"),),
    )

    with pytest.raises(EmbeddingDryRunReadinessError, match="manifest_readiness"):
        require_embedding_dry_run_ready(
            manifest=manifest,
            readiness_report=readiness_report,
            config=config,
            provenance=provenance,
        )


def test_embedding_dry_run_readiness_to_dict_serializes_report():
    manifest, readiness_report, config, provenance = valid_inputs()
    report = build_embedding_dry_run_readiness_report(
        manifest=manifest,
        readiness_report=readiness_report,
        config=config,
        provenance=provenance,
    )

    serialized = embedding_dry_run_readiness_to_dict(report)

    assert serialized["is_ready"] is True
    assert serialized["checks"][0]["name"] == "manifest_readiness"


def test_readiness_module_does_not_load_runtime_stack():
    source = inspect.getsource(readiness_module)

    assert "import geneformer" not in source.lower()
    assert "from geneformer" not in source.lower()
    assert "import scanpy" not in source.lower()
    assert "import anndata" not in source.lower()
