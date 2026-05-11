from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_project_env(env_path: Path | None = None) -> bool:
    dotenv_path = env_path or PROJECT_ROOT / ".env"
    return load_dotenv(dotenv_path=dotenv_path, override=False)
