import os

from app.env import load_project_env


def test_load_project_env_reads_dotenv_file(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text("OPENAI_API_KEY=test-key\n", encoding="utf-8")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    load_project_env(env_path=env_path)

    assert os.getenv("OPENAI_API_KEY") == "test-key"
