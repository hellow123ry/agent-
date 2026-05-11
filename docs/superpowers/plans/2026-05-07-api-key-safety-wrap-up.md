# API Key Safety Wrap-Up Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove committed API key usage, document local environment setup, and safely publish the remediation commit.

**Architecture:** Keep the runtime behavior change isolated to `multi_agent_dialog/llm.py`, add a focused regression test in `tests/test_llm.py`, and add local environment guardrails via `.env.example` and `.gitignore`. Verification stays targeted to the changed paths before committing and pushing to `origin/main`.

**Tech Stack:** Python, pytest, git

---

### Task 1: Environment Template And Ignore Rules

**Files:**
- Create: `.env.example`
- Modify: `.gitignore`

- [ ] **Step 1: Add a checked-in environment template**

Create `.env.example` with:

```dotenv
OPENAI_API_KEY=
API_BASE_URL=http://aidp.bytedance.net/api/modelhub/online/v2/crawl/openai/deployments/gpt_openapi
```

- [ ] **Step 2: Ignore local environment files**

Add to `.gitignore`:

```gitignore
# Local environment files
.env
.env.*
!.env.example
```

### Task 2: Verify Security Fix

**Files:**
- Modify: `multi_agent_dialog/llm.py`
- Test: `tests/test_llm.py`

- [ ] **Step 1: Run the focused regression test**

Run: `python3 -m pytest tests/test_llm.py -q`
Expected: `1 passed`

- [ ] **Step 2: Re-scan for the removed hardcoded key**

Run a content search for the removed secret literal.
Expected: no matches in tracked source files

### Task 3: Commit And Push

**Files:**
- Modify: Git index and branch `main`

- [ ] **Step 1: Review staged file set**

Run: `git status --short`
Expected: only the intended remediation files are present

- [ ] **Step 2: Commit the remediation**

Run:

```bash
git add multi_agent_dialog/llm.py tests/test_llm.py .env.example .gitignore docs/superpowers/plans/2026-05-07-api-key-safety-wrap-up.md
git commit -m "fix: remove hardcoded api key"
```

- [ ] **Step 3: Push to remote**

Run: `git push origin main`
Expected: branch `main` updates on `origin`
