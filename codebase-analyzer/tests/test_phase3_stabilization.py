from pathlib import Path

from src.core.orchestrator import AnalysisOrchestrator
from src.models.project import Project
from src.utils.config import Config


def test_orchestrator_analyzes_project_and_generates_phase_3_docs(tmp_path):
    fixture_dir = tmp_path / "sample_project"
    (fixture_dir / "app").mkdir(parents=True)
    (fixture_dir / "tools").mkdir(parents=True)
    (fixture_dir / "app" / "main.py").write_text(
        "def start_app():\n"
        "    return 'ready'\n",
        encoding="utf-8",
    )
    (fixture_dir / "tools" / "main.py").write_text(
        "class ToolRunner:\n"
        "    def run(self):\n"
        "        return 'done'\n",
        encoding="utf-8",
    )

    orchestrator = AnalysisOrchestrator(Config(Path("missing-config.yaml")))
    project = orchestrator.analyze_project(
        str(fixture_dir),
        use_cache=False,
        use_ai=False,
    )

    assert isinstance(project, Project)

    output_dir = tmp_path / "docs"
    orchestrator.generate_documentation(project, str(output_dir))

    expected_files = [
        output_dir / "PROJECT_OVERVIEW.md",
        output_dir / "API_REFERENCE.md",
        output_dir / "INDEX.md",
        output_dir / "files" / "app_main.py.md",
        output_dir / "files" / "tools_main.py.md",
    ]
    for expected_file in expected_files:
        assert expected_file.exists()

    functionality_docs = list((output_dir / "functionality_groups").glob("*.md"))
    assert functionality_docs

    index_content = (output_dir / "INDEX.md").read_text(encoding="utf-8")
    assert "API_REFERENCE.md" in index_content
    assert "files/app_main.py.md" in index_content
    assert "files/tools_main.py.md" in index_content
