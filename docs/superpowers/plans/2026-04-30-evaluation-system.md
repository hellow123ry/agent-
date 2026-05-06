# Evaluation System Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为当前生活服务多智能体系统补齐可批量运行、可计算指标、可做基线对比的实验与评测框架。

**Architecture:** 在现有 `run_dialog()` 之上增加一层独立的评测模块，负责读取自定义 JSON 数据集、驱动多轮对话、汇总最终状态并计算指标。与此同时新增一个“不带栈式记忆和全局黑板”的基线系统，保证同一份数据集、同一套指标可直接做基线对比和消融实验。

**Tech Stack:** Python 3.9, pytest, json, pathlib, 现有 LangGraph 多智能体系统

---

### Task 1: 统一评测数据格式

**Files:**
- Create: `evaluation/__init__.py`
- Create: `evaluation/datasets/life_service_eval.json`
- Test: `tests/test_evaluation_dataset.py`

- [ ] **Step 1: 写失败测试，约束数据集最小字段**

```python
import json
from pathlib import Path


def test_eval_dataset_schema():
    data = json.loads(Path("evaluation/datasets/life_service_eval.json").read_text())
    assert isinstance(data, list)
    sample = data[0]
    assert "id" in sample
    assert "domain" in sample
    assert "user_turns" in sample
    assert "expected_slots" in sample
    assert "success_conditions" in sample
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `pytest tests/test_evaluation_dataset.py -v`
Expected: FAIL，因为数据文件不存在

- [ ] **Step 3: 创建最小可用数据集**

```json
[
  {
    "id": "dining_basic_001",
    "domain": "dining",
    "user_turns": ["我想订明天北京的烤肉店", "3个人", "晚上6点"],
    "expected_slots": {
      "location": "北京",
      "people_count": 3,
      "date": "明天",
      "restaurant_type": "烤肉店"
    },
    "success_conditions": {
      "contains_any": ["预订成功", "有位", "查询到"]
    }
  }
]
```

- [ ] **Step 4: 再跑测试，确认通过**

Run: `pytest tests/test_evaluation_dataset.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add evaluation/__init__.py evaluation/datasets/life_service_eval.json tests/test_evaluation_dataset.py
git commit -m "test: add evaluation dataset schema"
```

### Task 2: 抽离统一的对话系统接口

**Files:**
- Create: `evaluation/systems.py`
- Modify: `multi_agent_dialog/graph.py`
- Test: `tests/test_evaluation_systems.py`

- [ ] **Step 1: 写失败测试，约束系统接口**

```python
from evaluation.systems import build_state, run_system_turns


def test_run_system_turns_returns_final_state():
    state = build_state()
    result = run_system_turns("stacked_multi_agent", state, ["你好"])
    assert "messages" in result
    assert "task_stack" in result
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `pytest tests/test_evaluation_systems.py -v`
Expected: FAIL，因为模块不存在

- [ ] **Step 3: 实现统一接口**

```python
def build_state(use_stack: bool = True, use_blackboard: bool = True) -> DialogState:
    ...


def run_system_turns(system_name: str, state: DialogState, user_turns: list[str]) -> DialogState:
    ...
```

- [ ] **Step 4: 增加基线系统**

```python
def run_baseline_dialog(initial_state: DialogState) -> DialogState:
    # 不使用 task_stack / global_blackboard，仅保留当前意图和专家执行
    ...
```

- [ ] **Step 5: 跑测试确认通过**

Run: `pytest tests/test_evaluation_systems.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add evaluation/systems.py multi_agent_dialog/graph.py tests/test_evaluation_systems.py
git commit -m "feat: add evaluation system adapters"
```

### Task 3: 先写指标测试，再实现指标模块

**Files:**
- Create: `evaluation/metrics.py`
- Test: `tests/test_evaluation_metrics.py`

- [ ] **Step 1: 写失败测试，约束三个核心指标**

```python
from evaluation.metrics import task_success_rate, average_turns, slot_f1


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
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `pytest tests/test_evaluation_metrics.py -v`
Expected: FAIL，因为模块不存在

- [ ] **Step 3: 实现指标计算**

```python
def task_success_rate(results: list[bool]) -> float:
    ...


def average_turns(turns: list[int]) -> float:
    ...


def slot_f1(predicted: dict, expected: dict) -> tuple[float, float, float]:
    ...
```

- [ ] **Step 4: 跑测试确认通过**

Run: `pytest tests/test_evaluation_metrics.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add evaluation/metrics.py tests/test_evaluation_metrics.py
git commit -m "feat: add evaluation metrics"
```

### Task 4: 实现批量评测 Runner

**Files:**
- Create: `evaluation/runner.py`
- Test: `tests/test_evaluation_runner.py`

- [ ] **Step 1: 写失败测试，约束 runner 输出结构**

```python
from evaluation.runner import run_dataset


def test_run_dataset_returns_summary():
    result = run_dataset("evaluation/datasets/life_service_eval.json", "stacked_multi_agent")
    assert "samples" in result
    assert "metrics" in result
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `pytest tests/test_evaluation_runner.py -v`
Expected: FAIL，因为 runner 未实现

- [ ] **Step 3: 实现 runner**

```python
def run_sample(sample: dict, system_name: str) -> dict:
    ...


def run_dataset(dataset_path: str, system_name: str) -> dict:
    ...
```

- [ ] **Step 4: 在 sample 结果中产出统一字段**

```python
{
    "id": "...",
    "success": True,
    "turn_count": 3,
    "predicted_slots": {...},
    "expected_slots": {...},
    "final_reply": "..."
}
```

- [ ] **Step 5: 跑测试确认通过**

Run: `pytest tests/test_evaluation_runner.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add evaluation/runner.py tests/test_evaluation_runner.py
git commit -m "feat: add batch evaluation runner"
```

### Task 5: 增加可执行入口与基线对比

**Files:**
- Create: `evaluation/run_eval.py`
- Test: `tests/test_run_eval.py`

- [ ] **Step 1: 写失败测试，约束入口返回对比结果**

```python
from evaluation.run_eval import compare_systems


def test_compare_systems_contains_baseline_and_agent():
    result = compare_systems("evaluation/datasets/life_service_eval.json")
    assert "stacked_multi_agent" in result
    assert "baseline_single_agent" in result
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `pytest tests/test_run_eval.py -v`
Expected: FAIL，因为入口不存在

- [ ] **Step 3: 实现入口脚本**

```python
def compare_systems(dataset_path: str) -> dict:
    return {
        "stacked_multi_agent": run_dataset(dataset_path, "stacked_multi_agent"),
        "baseline_single_agent": run_dataset(dataset_path, "baseline_single_agent"),
    }
```

- [ ] **Step 4: 支持命令行运行**

Run: `python3 evaluation/run_eval.py`
Expected: 输出两个系统的成功率、平均轮次、槽位 F1

- [ ] **Step 5: 跑测试确认通过**

Run: `pytest tests/test_run_eval.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add evaluation/run_eval.py tests/test_run_eval.py
git commit -m "feat: add evaluation comparison entrypoint"
```

### Task 6: 集成验证与回归测试

**Files:**
- Modify: `tests/test_graph.py`
- Modify: `tests/test_router.py`
- Modify: `tests/test_experts.py`
- Modify: `tests/test_blackboard.py`

- [ ] **Step 1: 跑新增测试集合**

Run: `pytest tests/test_evaluation_dataset.py tests/test_evaluation_systems.py tests/test_evaluation_metrics.py tests/test_evaluation_runner.py tests/test_run_eval.py -v`
Expected: PASS

- [ ] **Step 2: 跑全量测试**

Run: `pytest -v`
Expected: PASS，全量旧测试和新测试都通过

- [ ] **Step 3: 跑评测脚本**

Run: `python3 evaluation/run_eval.py`
Expected: 终端打印多 Agent 与 baseline 的指标对比

- [ ] **Step 4: 检查输出是否适合论文引用**

需要确认：
- 成功率字段稳定
- 轮次数字段稳定
- F1 字段稳定
- 每条样本有可追溯的明细结果

- [ ] **Step 5: Commit**

```bash
git add evaluation tests
git commit -m "feat: add evaluation and benchmarking framework"
```
