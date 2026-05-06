from __future__ import annotations

from pathlib import Path


RESULTS_DIR = Path("evaluation/results")


def get_latest_report() -> dict:
    return {
        "latest_html": str(RESULTS_DIR / "latest.html"),
        "latest_json": str(RESULTS_DIR / "latest.json"),
    }


def list_report_history(limit: int = 20) -> list[dict]:
    items = []
    for path in sorted(RESULTS_DIR.glob("*.json"), reverse=True):
        if path.name == "latest.json":
            continue
        items.append({"name": path.name, "path": str(path)})
        if len(items) >= limit:
            break
    return items


def resolve_report_file(path: str) -> Path:
    candidate = (RESULTS_DIR / path).resolve()
    if RESULTS_DIR.resolve() not in candidate.parents and candidate != RESULTS_DIR.resolve():
        raise ValueError("invalid report path")
    if not candidate.exists() or not candidate.is_file():
        raise FileNotFoundError(path)
    return candidate
