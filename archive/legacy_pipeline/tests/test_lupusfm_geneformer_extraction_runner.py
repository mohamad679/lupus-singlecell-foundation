import inspect

import pytest

import lupusfm.embeddings.extraction as extraction_module
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
from lupusfm.embeddings.config import make_primary_cellxgene_embedding_config
from lupusfm.embeddings.extraction import (
    GeneformerExtractionCallbacks,
    GeneformerExtractionPermission,
    GeneformerExtractionRunnerError,
    geneformer_extraction_run_result_to_dict,
    require_geneformer_extraction_callbacks,
    run_geneformer_embedding_extraction,
    validate_geneformer_extraction_permission,
)
from lupusfm.embeddings.provenance import make_embedding_provenance_from_config


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


def valid_permission():
    return GeneformerExtractionPermission(
        approved_environment="controlled_kaggle_gpu_session",
        approved_by="human_operator",
        reason="approved Stage 2 extraction runner test with fake callbacks",
        allow_runtime_execution=True,
        allow_downloads=False,
        allow_anndata_loading=True,
        allow_tokenizer_execution=True,
        allow_geneformer_execution=True,
        allow_embedding_extraction=True,
        allow_artifact_write=True,
        allow_modeling=False,
        allow_training=False,
        allow_external_validation=False,
        allow_performance_claims=False,
    )


def fake_callbacks(call_order):
    def load_anndata():
        call_order.append("load_anndata")
        return {"obs": "fake"}

    def sample_cells(adata, config):
        call_order.append("sample_cells")
        assert adata == {"obs": "fake"}
        assert config.cells_per_donor == 300
        return ["cell_a", "cell_b"]

    def tokenize_cells(sampled_cells, config):
        call_order.append("tokenize_cells")
        assert sampled_cells == ["cell_a", "cell_b"]
        assert config.max_sequence_length == 1024
        return {"input_ids": [[1, 2], [3, 4]]}

    def embed_tokens(tokenized_cells, config):
        call_order.append("embed_tokens")
        assert tokenized_cells == {"input_ids": [[1, 2], [3, 4]]}
        assert config.batch_size == 16
        return {"embeddings": [[0.1, 0.2], [0.3, 0.4]]}

    def write_artifacts(embeddings, config, provenance):
        call_order.append("write_artifacts")
        assert embeddings == {"embeddings": [[0.1, 0.2], [0.3, 0.4]]}
        assert provenance.extraction_performed is False
        return {
            "embeddings": config.output_paths.embeddings,
            "sampled_cell_ids": config.output_paths.sampled_cell_ids,
            "provenance": config.output_paths.provenance,
        }

    return GeneformerExtractionCallbacks(
        load_anndata=load_anndata,
        sample_cells=sample_cells,
        tokenize_cells=tokenize_cells,
        embed_tokens=embed_tokens,
        write_artifacts=write_artifacts,
    )


def test_default_permission_blocks_runtime_execution():
    with pytest.raises(
        GeneformerExtractionRunnerError,
        match="approved_environment",
    ):
        validate_geneformer_extraction_permission(GeneformerExtractionPermission())


def test_permission_accepts_explicit_extraction_only():
    validated = validate_geneformer_extraction_permission(valid_permission())

    assert validated.allow_runtime_execution is True
    assert validated.allow_anndata_loading is True
    assert validated.allow_tokenizer_execution is True
    assert validated.allow_geneformer_execution is True
    assert validated.allow_embedding_extraction is True
    assert validated.allow_artifact_write is True
    assert validated.allow_downloads is False
    assert validated.allow_modeling is False
    assert validated.allow_training is False
    assert validated.allow_external_validation is False
    assert validated.allow_performance_claims is False


@pytest.mark.parametrize(
    "field_name",
    [
        "allow_downloads",
        "allow_modeling",
        "allow_training",
        "allow_external_validation",
        "allow_performance_claims",
    ],
)
def test_permission_rejects_forbidden_downstream_or_download_flags(field_name):
    values = valid_permission().__dict__.copy()
    values[field_name] = True

    with pytest.raises(GeneformerExtractionRunnerError, match=field_name):
        validate_geneformer_extraction_permission(
            GeneformerExtractionPermission(**values)
        )


@pytest.mark.parametrize(
    "field_name",
    [
        "allow_runtime_execution",
        "allow_anndata_loading",
        "allow_tokenizer_execution",
        "allow_geneformer_execution",
        "allow_embedding_extraction",
        "allow_artifact_write",
    ],
)
def test_permission_requires_all_extraction_flags(field_name):
    values = valid_permission().__dict__.copy()
    values[field_name] = False

    with pytest.raises(GeneformerExtractionRunnerError, match=field_name):
        validate_geneformer_extraction_permission(
            GeneformerExtractionPermission(**values)
        )


def test_runner_requires_callbacks_after_permission():
    assert require_geneformer_extraction_callbacks(fake_callbacks([]))

    with pytest.raises(GeneformerExtractionRunnerError, match="callbacks"):
        require_geneformer_extraction_callbacks(None)


def test_runner_rejects_non_callable_callback():
    callbacks = fake_callbacks([])
    values = callbacks.__dict__.copy()
    values["embed_tokens"] = "not-callable"

    with pytest.raises(GeneformerExtractionRunnerError, match="embed_tokens"):
        require_geneformer_extraction_callbacks(
            GeneformerExtractionCallbacks(**values)
        )


def test_runner_executes_fake_callbacks_in_order_after_gates_pass():
    manifest, readiness_report, config, provenance = valid_inputs()
    call_order = []

    result = run_geneformer_embedding_extraction(
        manifest=manifest,
        readiness_report=readiness_report,
        config=config,
        provenance=provenance,
        permission=valid_permission(),
        callbacks=fake_callbacks(call_order),
    )

    expected_order = [
        "load_anndata",
        "sample_cells",
        "tokenize_cells",
        "embed_tokens",
        "write_artifacts",
    ]
    assert call_order == expected_order
    assert result.callback_order == tuple(expected_order)
    assert result.extraction_performed is True
    assert result.dry_run_ready is True
    assert result.artifact_paths["embeddings"] == config.output_paths.embeddings


def test_runner_aborts_before_callbacks_when_dry_run_is_not_ready():
    manifest, _readiness_report, config, provenance = valid_inputs()
    bad_readiness_report = IngestionReadinessReport(
        schema_report=None,
        cohort_summary=None,
        mitochondrial_gene_summary=None,
        checks=(ReadinessCheck("anndata_schema", False, "missing schema"),),
    )
    call_order = []

    with pytest.raises(ValueError, match="manifest_readiness"):
        run_geneformer_embedding_extraction(
            manifest=manifest,
            readiness_report=bad_readiness_report,
            config=config,
            provenance=provenance,
            permission=valid_permission(),
            callbacks=fake_callbacks(call_order),
        )

    assert call_order == []


def test_geneformer_extraction_run_result_to_dict_serializes_result():
    manifest, readiness_report, config, provenance = valid_inputs()
    result = run_geneformer_embedding_extraction(
        manifest=manifest,
        readiness_report=readiness_report,
        config=config,
        provenance=provenance,
        permission=valid_permission(),
        callbacks=fake_callbacks([]),
    )

    serialized = geneformer_extraction_run_result_to_dict(result)

    assert serialized["extraction_performed"] is True
    assert serialized["dry_run_ready"] is True
    assert serialized["callback_order"] == [
        "load_anndata",
        "sample_cells",
        "tokenize_cells",
        "embed_tokens",
        "write_artifacts",
    ]


def test_extraction_module_does_not_import_runtime_stack():
    source = inspect.getsource(extraction_module).lower()

    assert "import geneformer" not in source
    assert "from geneformer" not in source
    assert "import scanpy" not in source
    assert "import anndata" not in source
    assert "from anndata" not in source
    assert "import torch" not in source
    assert "from torch" not in source
