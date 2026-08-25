from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_streamlit_entrypoint_has_required_dashboard_sections():
    source = Path("app.py").read_text(encoding="utf-8")
    for label in (
        "Finance Insights Dashboard",
        "Overview",
        "Monthly trends",
        "Expense categories",
        "Unusually large transactions",
        "Download cleaned report",
    ):
        assert label in source
    assert "st.cache_data" in source
    assert "st.file_uploader" in source


def test_streamlit_app_renders_sample_dashboard():
    app = AppTest.from_file(Path(__file__).parents[1] / "app.py").run(timeout=30)
    assert not app.exception
    assert app.title[0].value == "Finance Insights Dashboard"
    assert len(app.metric) == 4
    assert [metric.label for metric in app.metric] == [
        "Income",
        "Expenses",
        "Balance",
        "Savings rate",
    ]
