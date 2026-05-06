# Evaluation Reporting Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为评测系统补齐结果持久化、HTML 报告和 SVG 图表导出能力，方便论文分析与截图。

**Architecture:** 在现有 `evaluation/run_eval.py` 的对比结果之上增加一层 `reporting` 模块，负责将结果保存为 JSON，并基于同一份数据生成 HTML 和 SVG。`run_eval.py` 保持为统一入口，执行完评测后同时输出终端结果和文件结果。

**Tech Stack:** Python 3.9, json, pathlib, 原生 HTML, 原生 SVG, pytest

---

### Task 1: 为 reporting 写失败测试

**Files:**
- Create: `tests/test_reporting.py`
- Modify: `tests/test_run_eval.py`

- [ ] **Step 1: 写 JSON 落盘失败测试**
- [ ] **Step 2: 写 HTML 报告生成失败测试**
- [ ] **Step 3: 写 SVG 图表生成失败测试**
- [ ] **Step 4: 跑测试确认因缺少模块而失败**

### Task 2: 实现 reporting 模块

**Files:**
- Create: `evaluation/reporting.py`

- [ ] **Step 1: 实现结果目录创建与时间戳文件名**
- [ ] **Step 2: 实现 JSON 保存**
- [ ] **Step 3: 实现 HTML 报告生成**
- [ ] **Step 4: 实现 3 个 SVG 指标图生成**
- [ ] **Step 5: 跑 reporting 测试确认通过**

### Task 3: 接入 run_eval 入口

**Files:**
- Modify: `evaluation/run_eval.py`

- [ ] **Step 1: 在 compare 结果基础上调用 reporting**
- [ ] **Step 2: 输出保存路径信息**
- [ ] **Step 3: 保持脚本直接运行兼容**
- [ ] **Step 4: 跑入口测试确认通过**

### Task 4: 真实验证

**Files:**
- Create: `evaluation/results/`（运行时生成）

- [ ] **Step 1: 跑全量测试**
- [ ] **Step 2: 运行 `python3 evaluation/run_eval.py`**
- [ ] **Step 3: 确认生成 `json/html/svg` 文件**
- [ ] **Step 4: 检查输出文件适合论文使用**
