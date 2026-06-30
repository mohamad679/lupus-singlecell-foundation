import pytest

from lupusfm.data.labels import (
    ClinicalStatus,
    DonorLabel,
    infer_clinical_status_from_donor_id,
    make_donor_label,
    make_donor_labels,
    normalize_donor_id,
)


@pytest.mark.parametrize(
    ("donor_id", "expected"),
    [
        ("FLARE1", ClinicalStatus.FLARE),
        ("FLARE-001", ClinicalStatus.FLARE),
        ("flare_patient_01", ClinicalStatus.FLARE),
        ("HC-001", ClinicalStatus.HEALTHY),
        ("hc-abc", ClinicalStatus.HEALTHY),
        ("IGTB123", ClinicalStatus.HEALTHY),
        ("igtb-control", ClinicalStatus.HEALTHY),
        ("123", ClinicalStatus.MANAGED),
        ("00045", ClinicalStatus.MANAGED),
    ],
)
def test_infer_clinical_status_from_known_donor_patterns(donor_id, expected):
    assert infer_clinical_status_from_donor_id(donor_id) == expected


def test_normalize_donor_id_strips_whitespace():
    assert normalize_donor_id("  FLARE1  ") == "FLARE1"


@pytest.mark.parametrize("bad_donor_id", [None, "", "   "])
def test_normalize_donor_id_rejects_missing_values(bad_donor_id):
    with pytest.raises(ValueError, match="donor_id"):
        normalize_donor_id(bad_donor_id)


@pytest.mark.parametrize(
    "unknown_donor_id",
    [
        "SLE-001",
        "CONTROL-001",
        "123A",
        "patient_01",
    ],
)
def test_infer_clinical_status_fails_closed_for_unknown_patterns(unknown_donor_id):
    with pytest.raises(ValueError, match="Unrecognized donor_id pattern"):
        infer_clinical_status_from_donor_id(unknown_donor_id)


def test_make_donor_label_returns_frozen_record():
    label = make_donor_label("  HC-001 ")

    assert label == DonorLabel(
        donor_id="HC-001",
        clinical_status=ClinicalStatus.HEALTHY,
    )


def test_make_donor_labels_preserves_input_order():
    labels = make_donor_labels(["FLARE1", "123", "IGTB1"])

    assert [label.clinical_status for label in labels] == [
        ClinicalStatus.FLARE,
        ClinicalStatus.MANAGED,
        ClinicalStatus.HEALTHY,
    ]
