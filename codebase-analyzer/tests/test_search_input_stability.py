from types import SimpleNamespace

from src.ui.pages.findings_page import FindingsPage
from src.ui.pages.suggestions_page import SuggestionsPage

from .test_phase6_stabilization import make_finding, make_suggestion


def test_findings_search_keeps_text_field_value_during_filtering():
    findings_page = FindingsPage(findings=[make_finding()])
    findings_page.update = lambda: None

    findings_page._on_search(SimpleNamespace(control=SimpleNamespace(value="database")))

    assert findings_page._search_query == "database"
    assert findings_page._search_field.value == "database"
    assert len(findings_page.filtered_findings) == 1


def test_suggestions_search_keeps_text_field_value_during_filtering():
    suggestions_page = SuggestionsPage(suggestions=[make_suggestion()])
    suggestions_page.update = lambda: None

    suggestions_page._on_search(SimpleNamespace(control=SimpleNamespace(value="parameterized")))

    assert suggestions_page._search_query == "parameterized"
    assert suggestions_page._search_field.value == "parameterized"
    assert len(suggestions_page.filtered_suggestions) == 1
