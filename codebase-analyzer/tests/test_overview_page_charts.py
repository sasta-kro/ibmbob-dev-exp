from src.ui.pages import OverviewPage

from .test_phase6_stabilization import make_project


def test_overview_page_builds_distribution_counts_from_project_data():
    overview_page = OverviewPage(project=make_project())

    assert overview_page._get_finding_severity_counts() == {"High": 1}
    assert overview_page._get_finding_type_counts() == {"Security": 1}
    assert overview_page._get_suggestion_severity_counts() == {"High": 1}
    assert overview_page._get_suggestion_type_counts() == {"Security": 1}


def test_overview_page_switches_chart_modes():
    overview_page = OverviewPage(project=make_project())
    overview_page.update = lambda: None

    overview_page._show_findings_type_chart(None)
    overview_page._show_suggestions_type_chart(None)

    assert overview_page._findings_chart_mode == "type"
    assert overview_page._suggestions_chart_mode == "type"

    overview_page._show_findings_severity_chart(None)
    overview_page._show_suggestions_severity_chart(None)

    assert overview_page._findings_chart_mode == "severity"
    assert overview_page._suggestions_chart_mode == "severity"
