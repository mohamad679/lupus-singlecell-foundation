import pytest

from lupusfm.evaluation.splits import (
    GROUP_K_FOLD,
    LEAVE_ONE_DONOR_OUT,
    DonorLabelRecord,
    LeakageSafeSplitConfig,
    LeakageSafeSplitError,
    SplitFold,
    is_stratification_feasible,
    leakage_safe_split_config_from_mapping,
    leakage_safe_split_config_to_dict,
    make_group_k_fold_splits,
    make_leave_one_donor_out_splits,
    split_folds_to_dicts,
    validate_donor_label_record,
    validate_donor_label_records,
    validate_leakage_safe_split_config,
    validate_split_fold,
    validate_split_folds,
)


def _records():
    return (
        DonorLabelRecord("donor_1", "flare"),
        DonorLabelRecord("donor_2", "managed"),
        DonorLabelRecord("donor_3", "flare"),
        DonorLabelRecord("donor_4", "managed"),
    )


def test_split_config_accepts_safe_defaults():
    config = LeakageSafeSplitConfig(notes="  fake splits only  ")

    validated = validate_leakage_safe_split_config(config)

    assert validated.split_method == LEAVE_ONE_DONOR_OUT
    assert validated.split_level == "patient"
    assert validated.allow_cell_level_split is False
    assert validated.allow_global_preprocessing is False
    assert validated.allow_scaler_outside_fold is False
    assert validated.allow_model_fitting is False
    assert validated.allow_modeling is False
    assert validated.allow_training is False
    assert validated.performance_claims_added is False
    assert validated.notes == "fake splits only"


def test_validate_donor_label_record_normalizes_mapping():
    record = validate_donor_label_record(
        {"donor_id": " donor_1 ", "label": " flare "}
    )

    assert record == DonorLabelRecord("donor_1", "flare")


def test_validate_donor_label_records_rejects_duplicate_donors():
    with pytest.raises(LeakageSafeSplitError, match="donor_id values must be unique"):
        validate_donor_label_records(
            [
                DonorLabelRecord("donor_1", "flare"),
                DonorLabelRecord("donor_1", "managed"),
            ]
        )


def test_leave_one_donor_out_holds_out_each_donor_once():
    folds = make_leave_one_donor_out_splits(_records())

    assert len(folds) == 4
    assert [fold.test_donor_ids for fold in folds] == [
        ("donor_1",),
        ("donor_2",),
        ("donor_3",),
        ("donor_4",),
    ]
    assert all(set(fold.train_donor_ids).isdisjoint(fold.test_donor_ids) for fold in folds)
    assert set().union(*(set(fold.test_donor_ids) for fold in folds)) == {
        "donor_1",
        "donor_2",
        "donor_3",
        "donor_4",
    }


def test_leave_one_donor_out_requires_at_least_two_donors():
    with pytest.raises(LeakageSafeSplitError, match="at least 2 donors"):
        make_leave_one_donor_out_splits([DonorLabelRecord("donor_1", "flare")])


def test_leave_one_donor_out_rejects_wrong_method_config():
    with pytest.raises(LeakageSafeSplitError, match="leave_one_donor_out"):
        make_leave_one_donor_out_splits(
            _records(),
            LeakageSafeSplitConfig(split_method=GROUP_K_FOLD),
        )


def test_group_k_fold_creates_non_overlapping_donor_folds():
    folds = make_group_k_fold_splits(
        _records(),
        LeakageSafeSplitConfig(split_method=GROUP_K_FOLD, n_splits=2),
    )

    assert len(folds) == 2
    assert all(set(fold.train_donor_ids).isdisjoint(fold.test_donor_ids) for fold in folds)
    assert set().union(*(set(fold.test_donor_ids) for fold in folds)) == {
        "donor_1",
        "donor_2",
        "donor_3",
        "donor_4",
    }


def test_group_k_fold_supports_feasible_label_stratification():
    folds = make_group_k_fold_splits(
        _records(),
        LeakageSafeSplitConfig(
            split_method=GROUP_K_FOLD,
            n_splits=2,
            stratify_by_label=True,
        ),
    )

    label_by_donor = {record.donor_id: record.label for record in _records()}
    for fold in folds:
        test_labels = {label_by_donor[donor_id] for donor_id in fold.test_donor_ids}
        assert test_labels == {"flare", "managed"}


def test_group_k_fold_rejects_infeasible_label_stratification():
    with pytest.raises(LeakageSafeSplitError, match="stratification is not feasible"):
        make_group_k_fold_splits(
            [
                DonorLabelRecord("donor_1", "flare"),
                DonorLabelRecord("donor_2", "managed"),
                DonorLabelRecord("donor_3", "managed"),
            ],
            LeakageSafeSplitConfig(
                split_method=GROUP_K_FOLD,
                n_splits=2,
                stratify_by_label=True,
            ),
        )


def test_is_stratification_feasible_reports_false_when_label_count_too_small():
    assert is_stratification_feasible(_records(), 2) is True
    assert is_stratification_feasible(_records(), 3) is False


def test_group_k_fold_requires_n_splits():
    with pytest.raises(LeakageSafeSplitError, match="n_splits is required"):
        make_group_k_fold_splits(
            _records(),
            LeakageSafeSplitConfig(split_method=GROUP_K_FOLD),
        )


def test_group_k_fold_rejects_too_many_splits():
    with pytest.raises(LeakageSafeSplitError, match="cannot exceed number of donors"):
        make_group_k_fold_splits(
            _records(),
            LeakageSafeSplitConfig(split_method=GROUP_K_FOLD, n_splits=5),
        )


def test_validate_split_fold_rejects_donor_leakage():
    with pytest.raises(LeakageSafeSplitError, match="donor leakage"):
        validate_split_fold(
            SplitFold(
                fold_id="bad",
                train_donor_ids=("donor_1", "donor_2"),
                test_donor_ids=("donor_2",),
                split_method=LEAVE_ONE_DONOR_OUT,
            )
        )


def test_validate_split_fold_rejects_duplicate_train_donors():
    with pytest.raises(LeakageSafeSplitError, match="duplicate donor IDs"):
        validate_split_fold(
            SplitFold(
                fold_id="bad",
                train_donor_ids=("donor_1", "donor_1"),
                test_donor_ids=("donor_2",),
                split_method=LEAVE_ONE_DONOR_OUT,
            )
        )


def test_validate_split_folds_requires_each_expected_donor_held_out():
    with pytest.raises(LeakageSafeSplitError, match="held-out test fold"):
        validate_split_folds(
            [
                SplitFold(
                    fold_id="fold_1",
                    train_donor_ids=("donor_1", "donor_2"),
                    test_donor_ids=("donor_3",),
                    split_method=GROUP_K_FOLD,
                )
            ],
            expected_donor_ids=("donor_1", "donor_2", "donor_3"),
        )


def test_validate_split_folds_rejects_unknown_donor_ids():
    with pytest.raises(LeakageSafeSplitError, match="unknown donor IDs"):
        validate_split_folds(
            [
                SplitFold(
                    fold_id="fold_1",
                    train_donor_ids=("donor_1",),
                    test_donor_ids=("donor_999",),
                    split_method=GROUP_K_FOLD,
                )
            ],
            expected_donor_ids=("donor_1", "donor_2"),
        )


def test_validate_split_folds_rejects_duplicate_fold_ids():
    with pytest.raises(LeakageSafeSplitError, match="fold_id values must be unique"):
        validate_split_folds(
            [
                SplitFold("fold_1", ("donor_1",), ("donor_2",), GROUP_K_FOLD),
                SplitFold("fold_1", ("donor_2",), ("donor_1",), GROUP_K_FOLD),
            ]
        )


def test_split_config_rejects_cell_level_split():
    with pytest.raises(LeakageSafeSplitError, match="split_level must be one of"):
        validate_leakage_safe_split_config(
            LeakageSafeSplitConfig(split_level="cell")
        )


@pytest.mark.parametrize(
    "flag_name",
    [
        "allow_cell_level_split",
        "allow_real_artifact_loading",
        "allow_anndata_loading",
        "allow_global_preprocessing",
        "allow_scaler_outside_fold",
        "allow_model_fitting",
        "allow_modeling",
        "allow_training",
        "allow_external_validation",
        "performance_claims_added",
    ],
)
def test_split_config_keeps_forbidden_flags_disabled(flag_name):
    with pytest.raises(LeakageSafeSplitError):
        validate_leakage_safe_split_config(
            LeakageSafeSplitConfig(**{flag_name: True})
        )


def test_config_from_mapping_normalizes_values():
    config = leakage_safe_split_config_from_mapping(
        {
            "split_method": GROUP_K_FOLD,
            "split_level": "donor",
            "n_splits": "2",
            "stratify_by_label": "true",
            "notes": "  normalized  ",
        }
    )

    assert config.split_method == GROUP_K_FOLD
    assert config.split_level == "donor"
    assert config.n_splits == 2
    assert config.stratify_by_label is True
    assert config.notes == "normalized"


def test_config_to_dict_validates_before_serializing():
    serialized = leakage_safe_split_config_to_dict(
        LeakageSafeSplitConfig(split_method=GROUP_K_FOLD, n_splits=2)
    )

    assert serialized["split_method"] == GROUP_K_FOLD
    assert serialized["n_splits"] == 2
    assert serialized["allow_modeling"] is False


def test_split_folds_to_dicts_serializes_valid_folds():
    folds = make_group_k_fold_splits(
        _records(),
        LeakageSafeSplitConfig(split_method=GROUP_K_FOLD, n_splits=2),
    )

    serialized = split_folds_to_dicts(folds)

    assert serialized[0]["fold_id"] == "group_k_fold_001"
    assert serialized[0]["split_method"] == GROUP_K_FOLD
    assert serialized[0]["split_level"] == "patient"
