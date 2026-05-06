from __future__ import annotations


def task_success_rate(results: list[bool]) -> float:
    if not results:
        return 0.0
    return sum(1 for item in results if item) / len(results)


def average_turns(turns: list[int]) -> float:
    if not turns:
        return 0.0
    return sum(turns) / len(turns)


def slot_f1(predicted: dict, expected: dict) -> tuple[float, float, float]:
    predicted_items = set(predicted.items())
    expected_items = set(expected.items())

    if not predicted_items and not expected_items:
        return 1.0, 1.0, 1.0

    true_positive = len(predicted_items & expected_items)
    precision = true_positive / len(predicted_items) if predicted_items else 0.0
    recall = true_positive / len(expected_items) if expected_items else 0.0

    if precision + recall == 0:
        return precision, recall, 0.0

    f1 = 2 * precision * recall / (precision + recall)
    return precision, recall, f1
