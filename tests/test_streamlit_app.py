from app.ui import streamlit_app
from lib.utils.markdown import format_response_for_markdown
from lib.clients import corenest as new_corenest


def test_format_response_for_markdown_escapes_dollar_signs():
    assert format_response_for_markdown("$364 billion") == r"\$364 billion"


def test_streamlit_module_imports_current_corenest_client():
    assert streamlit_app.perform_rag is not None
    assert new_corenest.fetch_embeddings is not None
