# Dotenv Auto Load Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make both the FastAPI server entrypoint and the CLI entrypoint automatically load the local `.env` file.

**Architecture:** Add a small shared helper that resolves the project root and loads `.env` once via `python-dotenv`. Call that helper before startup logic in `app/server.py` and `main.py`, and cover the helper with a focused test so the behavior is stable without needing an end-to-end startup test for each entrypoint.

**Tech Stack:** Python, FastAPI, python-dotenv, pytest

---

### Task 1: Add A Shared Env Loader

**Files:**
- Create: `app/env.py`
- Modify: `requirements.txt`
- Test: `tests/test_env.py`

- [ ] **Step 1: Write the failing test**

Add a test that creates a temporary `.env` file and asserts the loader populates `OPENAI_API_KEY` when the variable is absent.

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_env.py -q`
Expected: FAIL because the loader module/function does not exist yet

- [ ] **Step 3: Write minimal implementation**

Create `app/env.py` with a `load_project_env()` helper that calls `load_dotenv()` against the project root `.env`, and add `python-dotenv` to `requirements.txt`.

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m pytest tests/test_env.py -q`
Expected: PASS

### Task 2: Wire Both Entrypoints

**Files:**
- Modify: `app/server.py`
- Modify: `main.py`

- [ ] **Step 1: Load `.env` in the FastAPI entrypoint**

Import and call `load_project_env()` before the app and router setup.

- [ ] **Step 2: Load `.env` in the CLI entrypoint**

Import and call `load_project_env()` before modules that may need env-backed configuration during runtime.

### Task 3: Verify Runtime

**Files:**
- Modify: running processes only

- [ ] **Step 1: Re-run focused tests**

Run: `python3 -m pytest tests/test_env.py tests/test_llm.py -q`
Expected: PASS

- [ ] **Step 2: Verify server startup without manual export**

Start: `python3 -m uvicorn app.server:app --host 127.0.0.1 --port 8000`
Expected: server starts using values from local `.env`

- [ ] **Step 3: Verify chat API reaches the LLM**

Create a session and send a minimal turn through `/api/chat/session/{session_id}/turn`.
Expected: `200` response with an assistant message, without manually exporting env vars first
