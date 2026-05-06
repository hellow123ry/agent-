# Evaluation A1 Tightening Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the evaluation dataset to around 20 samples and tighten evaluation rules so results better reflect actual system behavior.

**Architecture:** Keep the existing evaluation pipeline intact and concentrate changes in the dataset file and `evaluation/runner.py`. Add focused tests first, then implement stricter success-condition evaluation, light slot normalization, and richer sample result details without changing the reporting entrypoints.

**Tech Stack:** Python, pytest, JSON dataset, existing evaluation/reporting modules

---

### Task 1: Tighten runner behavior with TDD

**Files:**
- Modify: `evaluation/runner.py`
- Modify: `tests/test_evaluation_runner.py`

- [ ] **Step 1: Write failing tests for stricter success conditions**
- [ ] **Step 2: Run targeted pytest to verify failures**
- [ ] **Step 3: Implement minimal success-condition evaluation and slot normalization**
- [ ] **Step 4: Re-run targeted pytest to verify passes**

### Task 2: Expand the evaluation dataset

**Files:**
- Modify: `evaluation/datasets/life_service_eval.json`
- Modify: `tests/test_evaluation_dataset.py`

- [ ] **Step 1: Strengthen dataset schema tests for new condition keys**
- [ ] **Step 2: Run targeted pytest to verify failures**
- [ ] **Step 3: Expand dataset to around 20 samples across dining, hotel, filter, cross-domain, and task-stack scenarios**
- [ ] **Step 4: Re-run targeted pytest to verify passes**

### Task 3: End-to-end verification

**Files:**
- Verify: `evaluation/run_eval.py`
- Verify: `evaluation/results/*`

- [ ] **Step 1: Run focused pytest for evaluation modules**
- [ ] **Step 2: Run `python3 evaluation/run_eval.py`**
- [ ] **Step 3: Check generated report outputs and diagnostics**
