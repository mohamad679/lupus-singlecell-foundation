import pytest

from lupusfm.evaluation.protocol import (
    REQUIRED_PRIMARY_METRICS,
    EvaluationProtocol,
    EvaluationProtocolError,
    MetricSpec,
    PermutationSpec,
    UncertaintySpec,
    evaluation_protocol_from_mapping,
    evaluation_protocol_to_dict,
    validate_evaluation_protocol,
    validate_metric_spec,
    validate_permutation_spec,
    validate_uncertainty_spec,
)


def _valid_protocol(**overrides):
    values = {
        "task": "flare_vs_managed",
        "split_level": "patient",
        "metrics": (
            MetricSpec("auroc", requires_probabilities=True),
            MetricSpec("auprc", requires_probabilities=True),
            MetricSpec("balanced_accuracy"),
            MetricSpec("sensitivity"),
            MetricSpec("specificity"),
        ),
        "uncertainty": UncertaintySpec("bootstrap_ci", n_resamples=1000),
        "permutation": PermutationSpec("label_permutation", n_permutations=1000),
        "require_baseline_comparison": True,
        "require_confounder_controls": True,
    }
    values.update(overrides)
    return EvaluationProtocol(**values)


def test_evaluation_protocol_accepts_safe_metadata_only_contract():
    protocol = _valid_protocol(notes="  protocol only  ")

    validated = validate_evaluation_protocol(protocol)

    assert validated.task == "flare_vs_managed"
    assert validated.split_level == "patient"
    assert tuple(metric.name for metric in validated.metrics) == (
        "auroc",
        "auprc",
        "balanced_accuracy",
        "sensitivity",
        "specificity",
    )
    assert validated.uncertainty.method == "bootstrap_ci"
    assert validated.permutation.method == "label_permutation"
    assert validated.require_baseline_comparison is True
    assert validated.require_confounder_controls is True
    assert validated.allow_model_fitting is False
    assert validated.allow_metric_computation is False
    assert validated.allow_modeling is False
    assert validated.performance_claims_added is False
    assert validated.notes == "protocol only"


@pytest.mark.parametrize(
    "task",
    ["flare_vs_managed", "flare_vs_healthy", "flare_vs_nonflare"],
)
def test_evaluation_protocol_accepts_allowed_tasks(task):
    validated = validate_evaluation_protocol(_valid_protocol(task=task))

    assert validated.task == task


def test_metric_spec_normalizes_mapping():
    metric = validate_metric_spec(
        {
            "name": " auroc ",
            "required": "true",
            "requires_probabilities": "yes",
            "notes": "  primary  ",
        }
    )

    assert metric == MetricSpec(
        "auroc",
        required=True,
        requires_probabilities=True,
        notes="primary",
    )


def test_uncertainty_spec_requires_resamples_for_bootstrap():
    with pytest.raises(EvaluationProtocolError, match="n_resamples"):
        validate_uncertainty_spec({"method": "bootstrap_ci", "n_resamples": None})


def test_uncertainty_spec_rejects_invalid_confidence_level():
    with pytest.raises(EvaluationProtocolError, match="confidence_level"):
        validate_uncertainty_spec(
            {"method": "bootstrap_ci", "n_resamples": 1000, "confidence_level": 1.5}
        )


def test_permutation_spec_requires_positive_permutation_count():
    with pytest.raises(EvaluationProtocolError, match="n_permutations"):
        validate_permutation_spec(
            {"method": "label_permutation", "n_permutations": 0}
        )


def test_evaluation_protocol_requires_all_primary_metrics():
    protocol = _valid_protocol(
        metrics=(
            MetricSpec("auroc", requires_probabilities=True),
            MetricSpec("balanced_accuracy"),
        )
    )

    with pytest.raises(EvaluationProtocolError, match="required primary metrics"):
        validate_evaluation_protocol(protocol)


def test_evaluation_protocol_rejects_duplicate_metrics():
    protocol = _valid_protocol(
        metrics=(
            MetricSpec("auroc", requires_probabilities=True),
            MetricSpec("auroc", requires_probabilities=True),
            MetricSpec("auprc", requires_probabilities=True),
            MetricSpec("balanced_accuracy"),
        )
    )

    with pytest.raises(EvaluationProtocolError, match="metric names must be unique"):
        validate_evaluation_protocol(protocol)


def test_evaluation_protocol_rejects_cell_level_split():
    with pytest.raises(EvaluationProtocolError, match="split_level must be one of"):
        validate_evaluation_protocol(_valid_protocol(split_level="cell"))


@pytest.mark.parametrize(
    "flag_name",
    [
        "allow_cell_level_split",
        "allow_real_artifact_loading",
        "allow_anndata_loading",
        "allow_global_preprocessing",
        "allow_scaler_outside_fold",
        "allow_model_fitting",
        "allow_metric_computation",
        "allow_modeling",
        "allow_training",
        "allow_external_validation",
        "performance_claims_added",
    ],
)
def test_evaluation_protocol_keeps_forbidden_flags_disabled(flag_name):
    protocol = _valid_protocol(**{flag_name: True})

    with pytest.raises(EvaluationProtocolError):
        validate_evaluation_protocol(protocol)


def test_evaluation_protocol_requires_baseline_comparison():
    with pytest.raises(EvaluationProtocolError, match="baseline comparison"):
        validate_evaluation_protocol(
            _valid_protocol(require_baseline_comparison=False)
        )


def test_evaluation_protocol_requires_confounder_controls():
    with pytest.raises(EvaluationProtocolError, match="confounder controls"):
        validate_evaluation_protocol(
            _valid_protocol(require_confounder_controls=False)
        )


def test_evaluation_protocol_from_mapping_uses_safe_defaults():
    protocol = evaluation_protocol_from_mapping(
        {
            "task": "flare_vs_healthy",
            "split_level": "donor",
            "uncertainty": {"method": "bootstrap_ci", "n_resamples": "500"},
            "permutation": {
                "method": "finite_label_permutation",
                "n_permutations": "250",
                "finite_sample_correction": "true",
            },
            "notes": "  normalized  ",
        }
    )

    assert protocol.task == "flare_vs_healthy"
    assert protocol.split_level == "donor"
    assert {metric.name for metric in protocol.metrics} == set(REQUIRED_PRIMARY_METRICS)
    assert protocol.uncertainty.n_resamples == 500
    assert protocol.permutation.n_permutations == 250
    assert protocol.permutation.finite_sample_correction is True
    assert protocol.notes == "normalized"


def test_evaluation_protocol_to_dict_validates_before_serializing():
    serialized = evaluation_protocol_to_dict(_valid_protocol())

    assert serialized["task"] == "flare_vs_managed"
    assert serialized["metrics"][0]["name"] == "auroc"
    assert serialized["uncertainty"]["method"] == "bootstrap_ci"
    assert serialized["permutation"]["method"] == "label_permutation"
    assert serialized["allow_modeling"] is False
