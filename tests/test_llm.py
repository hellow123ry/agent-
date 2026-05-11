import pytest

from multi_agent_dialog.llm import get_llm


def test_get_llm_requires_openai_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        get_llm()
