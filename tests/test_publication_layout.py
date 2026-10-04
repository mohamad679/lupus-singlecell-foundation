from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

def test_publication_layout_has_only_active_surface():
    for path in [
        "README.md", "CITATION.cff", "CHANGELOG.md", "requirements.txt",
        "assets/study_workflow.svg", "docs/DATA.md", "docs/METHODS.md",
        "docs/REPRODUCIBILITY.md", "docs/LIMITATIONS.md", "docs/PROVENANCE.md",
        "scripts/reproduce.sh", "results/published/corrected_v1_shared_analysis.json",
    ]:
        assert (ROOT / path).is_file(), path

def test_authoritative_reported_values():
    analysis = json.loads((ROOT / "results/published/corrected_v1_shared_analysis.json").read_text())
    assert analysis["n_donors"] == 56
    assert analysis["metrics"]["geneformer"]["auroc"] == 0.734375
    assert analysis["metrics"]["pseudobulk"]["auroc"] == 0.8984375
    assert analysis["metrics"]["metadata_only_age"]["auroc"] == 0.578125
