from evaluation.metrics import average_turns, slot_f1, task_success_rate


def test_task_success_rate():
    assert task_success_rate([True, False, True]) == 2 / 3


def test_average_turns():
    assert average_turns([2, 4, 6]) == 4


def test_slot_f1():
    predicted = {"location": "北京", "date": "明天"}
    expected = {"location": "北京", "date": "明天", "people_count": 3}
    precision, recall, f1 = slot_f1(predicted, expected)
    assert round(precision, 2) == 1.0
    assert round(recall, 2) == 0.67
    assert round(f1, 2) == 0.8
