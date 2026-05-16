from pathlib import Path

from src.core.orchestrator import AnalysisOrchestrator
from src.models.finding import Finding
from src.utils.config import Config


def test_orchestrator_generates_docs_and_review_reports(tmp_path):
    fixture_dir = tmp_path / "review_sample"
    fixture_dir.mkdir()
    (fixture_dir / "app.py").write_text(
        "password = 'hardcoded-secret'\n"
        "\n"
        "def collect(items=[]):\n"
        "    try:\n"
        "        return items == None\n"
        "    except:\n"
        "        pass\n",
        encoding="utf-8",
    )

    orchestrator = AnalysisOrchestrator(Config(Path("missing-config.yaml")))
    project = orchestrator.analyze_project(
        str(fixture_dir),
        use_cache=False,
        use_ai=False,
    )

    docs_dir = tmp_path / "docs"
    docs_path = orchestrator.generate_documentation(project, str(docs_dir))

    assert docs_path == docs_dir
    assert (docs_dir / "PROJECT_OVERVIEW.md").exists()
    assert (docs_dir / "API_REFERENCE.md").exists()
    assert (docs_dir / "INDEX.md").exists()

    review_dir = tmp_path / "review"
    review_result = orchestrator.review_project(
        project,
        output_dir=str(review_dir),
        enable_ai=False,
    )

    assert review_result["total_findings"] > 0
    assert all(isinstance(finding, Finding) for finding in review_result["findings"])
    assert project.findings == review_result["findings"]
    assert project.finding_summary is not None
    assert (review_dir / "review-findings.json").exists()
    assert (review_dir / "REVIEW_REPORT.md").exists()
