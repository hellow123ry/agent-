# Usage Documentation Refresh Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Update in-repo documentation so users can start the project with local `.env` auto-loading and understand the main usage flows.

**Architecture:** Keep `README.md` focused on fast startup and key entrypoints, and expand `docs/USER_GUIDE.md` into the detailed operational manual. Commit these docs together with the pending dotenv auto-load code changes, then re-verify targeted tests before pushing.

**Tech Stack:** Markdown, Python, pytest, git

---

### Task 1: Refresh Quick Start

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Add `.env` setup instructions**

Document copying `.env.example` to `.env`, and note that server and CLI now auto-load `.env`.

- [ ] **Step 2: Clarify standard ports and entrypoints**

Keep backend on `8000` and frontend on `5173`, and mention the CLI and evaluation entrypoints.

### Task 2: Expand Detailed User Guide

**Files:**
- Modify: `docs/USER_GUIDE.md`

- [ ] **Step 1: Add environment preparation guidance**

Describe Python/Node versions, dependency installation, and `.env` configuration.

- [ ] **Step 2: Add operational usage flows**

Document web workbench usage, CLI usage, evaluation usage, knowledgebase editing, and common troubleshooting.

### Task 3: Verify And Publish

**Files:**
- Modify: git index only

- [ ] **Step 1: Re-run targeted regression tests**

Run: `python3 -m pytest tests/test_env.py tests/test_llm.py -q`
Expected: PASS

- [ ] **Step 2: Review final diff**

Run: `git status --short`
Expected: only intended code and documentation files

- [ ] **Step 3: Commit and push**

Run:

```bash
git add README.md docs/USER_GUIDE.md docs/superpowers/plans/2026-05-09-usage-doc-refresh.md app/server.py main.py requirements.txt app/env.py tests/test_env.py
git commit -m "docs: update usage guide for dotenv startup"
git push origin main
```
