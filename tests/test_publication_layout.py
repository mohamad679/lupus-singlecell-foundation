from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_publication_layout_has_required_surface():
    for path in [
        "README.md", "CITATION.cff", "CHANGELOG.md", "requirements.txt",
        "assets/study_workflow.svg", "assets/social-preview.png",
        "docs/DATA.md", "docs/METHODS.md", "docs/REPRODUCIBILITY.md",
        "docs/LIMITATIONS.md", "docs/PROVENANCE.md",
        "scripts/reproduce.sh", "results/published/corrected_v1_shared_analysis.json",
    ]:
        assert (ROOT / path).is_file(), path

def test_development_workspace_is_not_on_publication_surface():
    for path in [
        "MODEL_CARD.md", "PROJECT_STATUS.md", "COLAB_RESULTS_STATUS.md",
        "src", "configs", "metadata", "data", "manuscript_drafts",
        "kaggle_notebooks",
    ]:
        assert not (ROOT / path).exists(), path

def test_active_scripts_are_compact_and_ordered():
    active = {p.name for p in (ROOT / "scripts").glob("*.py")}
    expected = {
        "01_score_corrected_models.py",
        "02_statistical_analysis.py",
        "03_gene_input_sensitivity.py",
        "04_descriptive_statistics.py",
        "05_cohort_probe.py",
        "06_generate_figures.py",
        "07_compare_reproduction.py",
        "_development_cv_core.py",
        "_cohort_probe_core.py",
        "correction_protocol.py",
        "correction_stats.py",
    }
    assert active == expected

def test_authoritative_reported_values():
    analysis = json.loads((ROOT / "results/published/corrected_v1_shared_analysis.json").read_text())
    assert analysis["n_donors"] == 56
    assert analysis["metrics"]["geneformer"]["auroc"] == 0.734375
    assert analysis["metrics"]["pseudobulk"]["auroc"] == 0.8984375
    assert analysis["metrics"]["metadata_only_age"]["auroc"] == 0.578125
