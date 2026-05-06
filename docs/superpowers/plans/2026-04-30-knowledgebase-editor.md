# Knowledgebase Editor Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a visual knowledgebase editor for restaurant and hotel mock data, persist it to a runtime JSON file, and make chat/evaluation consume the latest saved knowledgebase snapshots.

**Architecture:** Move hard-coded mock data into a single runtime data source under `data/knowledgebase.json`, managed by a backend service with validation and atomic writes. Expose FastAPI endpoints for reading/updating restaurant and hotel datasets, then add a frontend editor panel that can load, edit, save, and reload the knowledgebase. Tool calls consume snapshots passed from chat/evaluation entry points so a running session or evaluation job remains internally consistent.

**Tech Stack:** Python 3.9, FastAPI, Pydantic, pathlib/json, React, TypeScript, Vite, pytest

---

## File Map

**Create**
- `data/knowledgebase.json` — runtime knowledgebase data source
- `app/api/knowledgebase.py` — FastAPI routes for knowledgebase read/write
- `app/schemas/knowledgebase.py` — request/response payload models
- `app/services/knowledgebase_service.py` — read/validate/write/snapshot knowledgebase
- `tests/test_api_knowledgebase.py` — API coverage for knowledgebase routes
- `tests/test_knowledgebase_service.py` — service validation and atomic persistence tests
- `web/src/components/knowledgebase/KnowledgebasePanel.tsx` — editor UI

**Modify**
- `app/server.py` — register knowledgebase router
- `multi_agent_dialog/tools.py` — replace hard-coded constants with service-backed reads
- `app/services/chat_service.py` — attach knowledgebase snapshot to new sessions
- `evaluation/systems.py` — attach knowledgebase snapshot to evaluation state builders
- `multi_agent_dialog/state.py` — add optional knowledgebase snapshot field to dialog state
- `web/src/lib/api.ts` — frontend API methods for knowledgebase
- `web/src/pages/WorkbenchPage.tsx` — mount knowledgebase panel and wire save/reload flows
- `web/src/styles.css` — editor layout and form styles
- `web/src/types/chat.ts` — state typing update if needed

---

### Task 1: Create Knowledgebase Service and Data File

**Files:**
- Create: `data/knowledgebase.json`
- Create: `app/services/knowledgebase_service.py`
- Test: `tests/test_knowledgebase_service.py`

- [ ] **Step 1: Write failing service tests**

```python
def test_load_knowledgebase_returns_restaurants_and_hotels():
    data = load_knowledgebase()
    assert "restaurants" in data
    assert "hotels" in data
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_knowledgebase_service.py -q`
Expected: FAIL because service module does not exist

- [ ] **Step 3: Implement default seed, path resolution, validation, and atomic save**

```python
PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGEBASE_PATH = PROJECT_ROOT / "data" / "knowledgebase.json"
```

- [ ] **Step 4: Create initial `data/knowledgebase.json`**

```json
{"restaurants": [...], "hotels": [...]}
```

- [ ] **Step 5: Re-run service tests**

Run: `python3 -m pytest tests/test_knowledgebase_service.py -q`
Expected: PASS

---

### Task 2: Add Knowledgebase API

**Files:**
- Create: `app/api/knowledgebase.py`
- Create: `app/schemas/knowledgebase.py`
- Modify: `app/server.py`
- Test: `tests/test_api_knowledgebase.py`

- [ ] **Step 1: Write failing API tests**

```python
def test_get_knowledgebase():
    response = client.get("/api/knowledgebase")
    assert response.status_code == 200
```

- [ ] **Step 2: Run tests to verify failure**

Run: `python3 -m pytest tests/test_api_knowledgebase.py -q`
Expected: FAIL because route module is missing

- [ ] **Step 3: Implement routes**

```python
@router.get("")
@router.put("/restaurants")
@router.put("/hotels")
```

- [ ] **Step 4: Enforce success/error response envelope**

```python
{"ok": True, "data": {...}}
{"ok": False, "error": {"code": "validation_error", "message": "...", "field": "capacity"}}
```

- [ ] **Step 5: Register router in server**

```python
app.include_router(knowledgebase_router, prefix="/api/knowledgebase", tags=["knowledgebase"])
```

- [ ] **Step 6: Add 400 validation test cases**

Run: `python3 -m pytest tests/test_api_knowledgebase.py -q`
Expected: includes failing payload coverage for `capacity` / `price`

- [ ] **Step 7: Re-run API tests**

Run: `python3 -m pytest tests/test_api_knowledgebase.py -q`
Expected: PASS

---

### Task 3: Wire Tool Layer to Knowledgebase Snapshots

**Files:**
- Modify: `multi_agent_dialog/state.py`
- Modify: `multi_agent_dialog/tools.py`
- Modify: `app/services/chat_service.py`
- Modify: `evaluation/systems.py`
- Test: `tests/test_experts.py`
- Test: `tests/test_evaluation_runner.py`

- [ ] **Step 1: Write failing tests for snapshot-backed reads**

```python
def test_search_hotels_reads_snapshot():
    snapshot = {"hotels": [{"name": "测试酒店", ...}]}
    result = search_hotels("", "", knowledgebase=snapshot)
    assert "测试酒店" in result
```

- [ ] **Step 2: Run targeted tests to verify failure**

Run: `python3 -m pytest tests/test_experts.py tests/test_evaluation_runner.py -q`
Expected: FAIL because tool functions do not accept knowledgebase input

- [ ] **Step 3: Extend dialog state with knowledgebase snapshot**

```python
knowledgebase: Dict[str, Any]
```

- [ ] **Step 4: Attach snapshots when creating chat sessions and evaluation states**

```python
create_session() -> inject latest snapshot
reset_session() -> re-inject latest snapshot
build_state() -> inject latest snapshot for eval jobs
```

- [ ] **Step 5: Ensure reset flow refreshes snapshot for manual verification**

```python
state["knowledgebase"] = get_knowledgebase_snapshot()
```

- [ ] **Step 6: Update tool functions to read snapshot data**

Run: `python3 -m pytest tests/test_experts.py tests/test_evaluation_runner.py -q`
Expected: PASS

---

### Task 4: Build Frontend Knowledgebase Panel

**Files:**
- Create: `web/src/components/knowledgebase/KnowledgebasePanel.tsx`
- Modify: `web/src/lib/api.ts`
- Modify: `web/src/pages/WorkbenchPage.tsx`
- Modify: `web/src/styles.css`
- Modify: `web/src/types/chat.ts`

- [ ] **Step 1: Add frontend API methods**

```ts
getKnowledgebase()
updateRestaurants()
updateHotels()
```

- [ ] **Step 2: Build panel UI with two tabs**

```tsx
<KnowledgebasePanel />
```

- [ ] **Step 3: Add editable list rows**

```tsx
name / type / capacity / status
name / location / type / price / status
```

- [ ] **Step 4: Add `capacity` string<->int[] conversion**

```tsx
"2,3,4" <-> [2, 3, 4]
```

- [ ] **Step 5: Add save, reload, add, delete flows**

Run: `cd web && npm run build`
Expected: PASS

---

### Task 5: Integration Verification

**Files:**
- Verify: `app/services/knowledgebase_service.py`
- Verify: `app/api/knowledgebase.py`
- Verify: `web/src/components/knowledgebase/KnowledgebasePanel.tsx`

- [ ] **Step 1: Run backend knowledgebase tests**

Run: `python3 -m pytest tests/test_knowledgebase_service.py tests/test_api_knowledgebase.py -q`
Expected: PASS

- [ ] **Step 2: Run regression tests**

Run: `python3 -m pytest tests/test_api_chat.py tests/test_api_eval.py tests/test_api_reports.py tests/test_experts.py tests/test_evaluation_runner.py -q`
Expected: PASS

- [ ] **Step 3: Run frontend build**

Run: `cd web && npm run build`
Expected: PASS

- [ ] **Step 4: Manual local verification**

Run backend: `python3 -m uvicorn app.server:app --reload --port 8000`
Run frontend: `cd web && npm run dev`
Expected:
- knowledgebase panel loads current data
- save modifies JSON file
- new chat session reflects updated search results
- report/eval pages still work
