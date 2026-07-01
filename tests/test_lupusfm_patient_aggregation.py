import pytest

from lupusfm.embeddings.aggregation import (
    DEFAULT_PATIENT_AGGREGATION,
    CellEmbeddingRecord,
    PatientAggregationConfig,
    PatientAggregationError,
    aggregate_embeddings_by_donor,
    donor_embedding_records_to_dicts,
    patient_aggregation_config_from_mapping,
    patient_aggregation_config_to_dict,
    validate_cell_embedding_record,
    validate_patient_aggregation_config,
)


def _records():
    return (
        CellEmbeddingRecord(" donor_b ", " cell_3 ", (10, 20, 30)),
        CellEmbeddingRecord("donor_a", "cell_1", (1.0, 2.0, 3.0)),
        CellEmbeddingRecord("donor_a", "cell_2", (3.0, 4.0, 5.0)),
    )


def test_patient_aggregation_config_accepts_metadata_only_defaults():
    config = PatientAggregationConfig(
        expected_embedding_dimension="3",
        min_cells_per_donor="1",
        notes="  fake data only  ",
    )

    validated = validate_patient_aggregation_config(config)

    assert validated.aggregation_method == DEFAULT_PATIENT_AGGREGATION
    assert validated.split_level == "patient"
    assert validated.expected_embedding_dimension == 3
    assert validated.min_cells_per_donor == 1
    assert validated.allow_real_artifact_loading is False
    assert validated.allow_modeling is False
    assert validated.allow_training is False
    assert validated.performance_claims_added is False
    assert validated.notes == "fake data only"


def test_aggregate_embeddings_by_donor_mean_pools_fake_cell_records():
    donor_records = aggregate_embeddings_by_donor(
        _records(),
        PatientAggregationConfig(expected_embedding_dimension=3),
    )

    assert [record.donor_id for record in donor_records] == ["donor_a", "donor_b"]
    assert donor_records[0].embedding == (2.0, 3.0, 4.0)
    assert donor_records[0].n_cells == 2
    assert donor_records[0].aggregation_method == "mean_pool_per_donor"
    assert donor_records[1].embedding == (10.0, 20.0, 30.0)
    assert donor_records[1].n_cells == 1


def test_aggregate_embeddings_by_donor_accepts_mapping_records():
    donor_records = aggregate_embeddings_by_donor(
        [
            {"donor_id": "d1", "cell_id": "c1", "embedding": [1, 2]},
            {"donor_id": "d1", "cell_id": "c2", "embedding": [3, 4]},
        ],
        PatientAggregationConfig(expected_embedding_dimension=None),
    )

    assert donor_records[0].donor_id == "d1"
    assert donor_records[0].embedding == (2.0, 3.0)
    assert donor_records[0].n_cells == 2


def test_validate_cell_embedding_record_normalizes_strings_and_numbers():
    record = validate_cell_embedding_record(
        {"donor_id": " donor_1 ", "cell_id": " cell_1 ", "embedding": ("1", 2)},
        expected_embedding_dimension=2,
    )

    assert record.donor_id == "donor_1"
    assert record.cell_id == "cell_1"
    assert record.embedding == (1.0, 2.0)


def test_patient_aggregation_config_rejects_cell_level_split():
    with pytest.raises(PatientAggregationError, match="split_level must be one of"):
        validate_patient_aggregation_config(PatientAggregationConfig(split_level="cell"))


@pytest.mark.parametrize(
    "flag_name",
    [
        "allow_real_artifact_loading",
        "allow_anndata_loading",
        "allow_geneformer_execution",
        "allow_tokenizer_execution",
        "allow_embedding_extraction",
        "allow_modeling",
        "allow_training",
        "allow_external_validation",
        "performance_claims_added",
    ],
)
def test_patient_aggregation_config_keeps_forbidden_flags_disabled(flag_name):
    config = PatientAggregationConfig(**{flag_name: True})

    with pytest.raises(PatientAggregationError):
        validate_patient_aggregation_config(config)


def test_aggregate_embeddings_by_donor_rejects_empty_records():
    with pytest.raises(PatientAggregationError, match="records must not be empty"):
        aggregate_embeddings_by_donor(
            [],
            PatientAggregationConfig(expected_embedding_dimension=None),
        )


def test_aggregate_embeddings_by_donor_rejects_dimension_mismatch():
    with pytest.raises(PatientAggregationError, match="same dimension"):
        aggregate_embeddings_by_donor(
            [
                CellEmbeddingRecord("d1", "c1", (1.0, 2.0)),
                CellEmbeddingRecord("d1", "c2", (1.0, 2.0, 3.0)),
            ],
            PatientAggregationConfig(expected_embedding_dimension=None),
        )


def test_aggregate_embeddings_by_donor_rejects_expected_dimension_mismatch():
    with pytest.raises(
        PatientAggregationError,
        match="expected_embedding_dimension",
    ):
        aggregate_embeddings_by_donor(
            [CellEmbeddingRecord("d1", "c1", (1.0, 2.0))],
            PatientAggregationConfig(expected_embedding_dimension=3),
        )


def test_aggregate_embeddings_by_donor_rejects_duplicate_cell_ids():
    with pytest.raises(PatientAggregationError, match="cell_id values must be unique"):
        aggregate_embeddings_by_donor(
            [
                CellEmbeddingRecord("d1", "same_cell", (1.0, 2.0)),
                CellEmbeddingRecord("d2", "same_cell", (3.0, 4.0)),
            ],
            PatientAggregationConfig(expected_embedding_dimension=2),
        )


def test_aggregate_embeddings_by_donor_enforces_min_cells_per_donor():
    with pytest.raises(
        PatientAggregationError,
        match="min_cells_per_donor",
    ):
        aggregate_embeddings_by_donor(
            [
                CellEmbeddingRecord("d1", "c1", (1.0, 2.0)),
                CellEmbeddingRecord("d2", "c2", (3.0, 4.0)),
                CellEmbeddingRecord("d2", "c3", (5.0, 6.0)),
            ],
            PatientAggregationConfig(
                expected_embedding_dimension=2,
                min_cells_per_donor=2,
            ),
        )


@pytest.mark.parametrize(
    "bad_embedding",
    [
        (),
        ("not-a-number",),
        (float("nan"),),
        (float("inf"),),
        (True,),
        "1,2,3",
    ],
)
def test_validate_cell_embedding_record_rejects_invalid_embeddings(bad_embedding):
    with pytest.raises(PatientAggregationError):
        validate_cell_embedding_record(
            CellEmbeddingRecord("d1", "c1", bad_embedding),
            expected_embedding_dimension=None,
        )


def test_patient_aggregation_config_from_mapping_normalizes_values():
    config = patient_aggregation_config_from_mapping(
        {
            "aggregation_method": "mean_pool_per_donor",
            "split_level": "donor",
            "expected_embedding_dimension": "2",
            "min_cells_per_donor": "3",
            "notes": "  normalized  ",
        }
    )

    assert config.split_level == "donor"
    assert config.expected_embedding_dimension == 2
    assert config.min_cells_per_donor == 3
    assert config.notes == "normalized"


def test_patient_aggregation_config_to_dict_validates_before_serializing():
    serialized = patient_aggregation_config_to_dict(
        PatientAggregationConfig(expected_embedding_dimension=2)
    )

    assert serialized["aggregation_method"] == "mean_pool_per_donor"
    assert serialized["expected_embedding_dimension"] == 2
    assert serialized["allow_modeling"] is False


def test_donor_embedding_records_to_dicts_serializes_aggregation_output():
    donor_records = aggregate_embeddings_by_donor(
        [CellEmbeddingRecord("d1", "c1", (1.0, 3.0))],
        PatientAggregationConfig(expected_embedding_dimension=2),
    )

    serialized = donor_embedding_records_to_dicts(donor_records)

    assert serialized == [
        {
            "donor_id": "d1",
            "embedding": (1.0, 3.0),
            "n_cells": 1,
            "aggregation_method": "mean_pool_per_donor",
            "source_record_level": "cell",
        }
    ]
