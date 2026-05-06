from __future__ import annotations

import json
import signal
from pathlib import Path
from contextlib import contextmanager
from typing import Any, Callable

from evaluation.metrics import average_turns, slot_f1, task_success_rate
from evaluation.systems import build_state, run_system_turns

DEFAULT_SAMPLE_TIMEOUT_SECONDS = 45.0


class SampleTimeoutError(TimeoutError):
    pass


def load_dataset(dataset_path: str) -> list[dict]:
    return json.loads(Path(dataset_path).read_text(encoding="utf-8"))


@contextmanager
def _sample_timeout(seconds: float | None):
    if not seconds or seconds <= 0 or not hasattr(signal, "setitimer"):
        yield
        return

    def _handle_timeout(signum, frame):
        raise SampleTimeoutError(f"sample timed out after {seconds} seconds")

    previous_handler = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, _handle_timeout)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_handler)


def _normalize_slot_value(key: str, value: Any) -> Any:
    if value is None:
        return None

    if isinstance(value, str):
        normalized = value.strip()
        if key == "people_count" and normalized.isdigit():
            return int(normalized)
        if key == "date":
            for candidate in ("今天", "明天", "后天"):
                if candidate in normalized:
                    return candidate
        return normalized

    return value


def _normalize_slots(slots: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in slots.items():
        normalized_value = _normalize_slot_value(key, value)
        if normalized_value not in (None, ""):
            normalized[key] = normalized_value
    return normalized


def extract_predicted_slots(state: dict) -> dict:
    return _normalize_slots(dict(state.get("global_blackboard", {})))


def check_success(
    sample: dict,
    final_reply: str,
    predicted_slots: dict | None = None,
    final_state: dict | None = None,
) -> tuple[bool, list[str]]:
    conditions = sample.get("success_conditions", {})
    predicted_slots = _normalize_slots(predicted_slots or {})
    final_state = final_state or {}
    reasons: list[str] = []

    contains_any = conditions.get("contains_any", [])
    if contains_any and not any(keyword in final_reply for keyword in contains_any):
        reasons.append(f"contains_any failed: {contains_any}")

    contains_all = conditions.get("contains_all", [])
    missing_keywords = [keyword for keyword in contains_all if keyword not in final_reply]
    if missing_keywords:
        reasons.append(f"contains_all failed: {missing_keywords}")

    not_contains_any = conditions.get("not_contains_any", [])
    blocked_keywords = [keyword for keyword in not_contains_any if keyword in final_reply]
    if blocked_keywords:
        reasons.append(f"not_contains_any failed: {blocked_keywords}")

    required_slots = conditions.get("required_slots", [])
    missing_slots = [slot for slot in required_slots if slot not in predicted_slots]
    if missing_slots:
        reasons.append(f"required_slots failed: {missing_slots}")

    forbidden_slots = conditions.get("forbidden_slots", [])
    present_forbidden_slots = [slot for slot in forbidden_slots if slot in predicted_slots]
    if present_forbidden_slots:
        reasons.append(f"forbidden_slots failed: {present_forbidden_slots}")

    active_task_is = conditions.get("active_task_is")
    if active_task_is and final_state.get("active_task") != active_task_is:
        reasons.append(
            f"active_task_is failed: expected {active_task_is}, got {final_state.get('active_task')}"
        )

    task_stack_depth_at_least = conditions.get("task_stack_depth_at_least")
    if task_stack_depth_at_least is not None:
        stack_depth = len(final_state.get("task_stack", []))
        if stack_depth < task_stack_depth_at_least:
            reasons.append(
                "task_stack_depth_at_least failed: "
                f"expected >= {task_stack_depth_at_least}, got {stack_depth}"
            )

    if not conditions:
        return bool(final_reply), []

    return not reasons, reasons


def run_sample(
    sample: dict,
    system_name: str,
    sample_timeout_seconds: float = DEFAULT_SAMPLE_TIMEOUT_SECONDS,
) -> dict:
    use_blackboard = system_name != "baseline_single_agent"
    initial_state = build_state(use_stack=use_blackboard, use_blackboard=use_blackboard)
    try:
        with _sample_timeout(sample_timeout_seconds):
            final_state = run_system_turns(system_name, initial_state, sample["user_turns"])
    except SampleTimeoutError:
        timeout_message = (
            f"sample timeout after {sample_timeout_seconds} seconds"
        )
        return {
            "id": sample["id"],
            "success": False,
            "turn_count": len(sample["user_turns"]),
            "predicted_slots": {},
            "expected_slots": _normalize_slots(sample["expected_slots"]),
            "final_reply": timeout_message,
            "failure_reasons": [f"sample_timeout failed: {sample_timeout_seconds}s"],
        }

    final_reply = final_state["messages"][-1].content if final_state["messages"] else ""
    predicted_slots = extract_predicted_slots(final_state)
    expected_slots = _normalize_slots(sample["expected_slots"])
    success, failure_reasons = check_success(
        sample,
        final_reply,
        predicted_slots=predicted_slots,
        final_state=final_state,
    )

    return {
        "id": sample["id"],
        "success": success,
        "turn_count": len(sample["user_turns"]),
        "predicted_slots": predicted_slots,
        "expected_slots": expected_slots,
        "final_reply": final_reply,
        "failure_reasons": failure_reasons,
    }


def run_dataset_with_progress(
    dataset: list[dict],
    system_name: str,
    progress_callback: Callable[[dict, int, int, str], None] | None = None,
) -> dict:
    samples = []
    total = len(dataset)
    for index, sample in enumerate(dataset, start=1):
        sample_result = run_sample(sample, system_name)
        samples.append(sample_result)
        if progress_callback:
            progress_callback(sample_result, index, total, system_name)

    success_list = [sample["success"] for sample in samples]
    turn_list = [sample["turn_count"] for sample in samples]
    slot_scores = [
        slot_f1(sample["predicted_slots"], sample["expected_slots"]) for sample in samples
    ]

    if slot_scores:
        avg_precision = sum(item[0] for item in slot_scores) / len(slot_scores)
        avg_recall = sum(item[1] for item in slot_scores) / len(slot_scores)
        avg_f1 = sum(item[2] for item in slot_scores) / len(slot_scores)
    else:
        avg_precision = avg_recall = avg_f1 = 0.0

    return {
        "samples": samples,
        "metrics": {
            "task_success_rate": task_success_rate(success_list),
            "average_turns": average_turns(turn_list),
            "slot_precision": avg_precision,
            "slot_recall": avg_recall,
            "slot_f1": avg_f1,
        },
    }


def run_dataset(
    dataset_path: str,
    system_name: str,
    progress_callback: Callable[[dict, int, int, str], None] | None = None,
) -> dict:
    dataset = load_dataset(dataset_path)
    return run_dataset_with_progress(dataset, system_name, progress_callback)
