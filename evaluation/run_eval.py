from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from evaluation.reporting import save_reports
from evaluation.runner import run_dataset


def compare_systems(dataset_path: str) -> dict:
    result = {
        "stacked_multi_agent": run_dataset(dataset_path, "stacked_multi_agent"),
        "baseline_single_agent": run_dataset(dataset_path, "baseline_single_agent"),
    }
    result["reports"] = save_reports(result)
    return result


def main() -> None:
    result = compare_systems("evaluation/datasets/life_service_eval.json")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
