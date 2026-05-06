# Visual Workbench Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local visual workbench that exposes chat debugging, trace inspection, evaluation runs, and report viewing through a React + TypeScript frontend backed by a FastAPI service.

**Architecture:** Keep the current LangGraph dialog system and evaluation pipeline as the single source of truth. Add a thin FastAPI service layer that wraps chat/evaluation/report capabilities and emits structured trace events, then build a Vite-based React workbench that renders conversation, state, trace timeline, and evaluation results in one page.

**Tech Stack:** Python, FastAPI, Pydantic, Uvicorn, React, TypeScript, Vite, existing evaluation/reporting modules

---

## File Map

**Backend create**
- `app/server.py` — FastAPI bootstrap, router registration, static mounting, CORS
- `app/api/chat.py` — chat session routes
- `app/api/eval.py` — evaluation job routes
- `app/api/reports.py` — report/history routes
- `app/schemas/chat.py` — request/response models for chat
- `app/schemas/eval.py` — request/response models for evaluation/reporting
- `app/services/chat_service.py` — stateful chat orchestration around `run_dialog`
- `app/services/eval_service.py` — async eval job execution and progress tracking
- `app/services/report_service.py` — report discovery and file loading
- `app/services/trace_service.py` — trace event collector and serializer
- `app/state/session_store.py` — in-memory chat/eval stores
- `tests/test_api_chat.py`
- `tests/test_api_eval.py`
- `tests/test_api_reports.py`
- `tests/test_trace_service.py`

**Backend modify**
- `multi_agent_dialog/router.py` — emit router trace hooks
- `multi_agent_dialog/experts.py` — emit expert/tool/filter/blackboard trace hooks
- `evaluation/runner.py` — optional progress callback support for API jobs
- `evaluation/run_eval.py` — keep CLI compatibility while sharing service logic where useful

**Frontend create**
- `web/package.json`
- `web/tsconfig.json`
- `web/vite.config.ts`
- `web/index.html`
- `web/src/main.tsx`
- `web/src/App.tsx`
- `web/src/pages/WorkbenchPage.tsx`
- `web/src/lib/api.ts`
- `web/src/types/chat.ts`
- `web/src/types/eval.ts`
- `web/src/types/trace.ts`
- `web/src/components/chat/ChatPanel.tsx`
- `web/src/components/chat/MessageList.tsx`
- `web/src/components/chat/InputBox.tsx`
- `web/src/components/trace/TracePanel.tsx`
- `web/src/components/trace/TraceTimeline.tsx`
- `web/src/components/state/StatePanel.tsx`
- `web/src/components/eval/EvalPanel.tsx`
- `web/src/components/eval/MetricsCards.tsx`
- `web/src/components/eval/SampleTable.tsx`
- `web/src/components/eval/SampleDetailDrawer.tsx`
- `web/src/components/reports/ReportsPanel.tsx`
- `web/src/styles.css`

---

### Task 1: Prepare Dependencies and Runtime Entry Points

**Files:**
- Create or Modify: `requirements.txt` or `pyproject.toml` (choose one project-standard dependency entry)
- Optional Create: `scripts/dev-workbench.sh`
- Test: environment bootstrap notes in plan execution

- [ ] **Step 1: Add backend dependencies before API tests**

```txt
fastapi
uvicorn
pydantic
python-multipart
```

- [ ] **Step 2: Add frontend scaffold command notes**

Run: `mkdir -p web && cd web && npm create vite@latest . -- --template react-ts`
Expected: Vite React TypeScript app scaffolded locally

- [ ] **Step 3: Install backend dependencies in active environment**

Run: `python3 -m pip install -r requirements.txt`
Expected: FastAPI/Uvicorn available for tests and local dev

---

### Task 2: Scaffold FastAPI Service Shell

**Files:**
- Create: `app/server.py`
- Create: `app/api/chat.py`
- Create: `app/api/eval.py`
- Create: `app/api/reports.py`
- Create: `app/schemas/chat.py`
- Create: `app/schemas/eval.py`
- Create: `app/state/session_store.py`
- Test: `tests/test_api_chat.py`
- Test: `tests/test_api_eval.py`
- Test: `tests/test_api_reports.py`

- [ ] **Step 1: Write failing API smoke tests**
- [ ] **Step 1: Write failing API smoke tests**

```python
from fastapi.testclient import TestClient
from app.server import app

client = TestClient(app)

def test_create_chat_session():
    response = client.post("/api/chat/session")
    assert response.status_code == 200
    assert "session_id" in response.json()
```

- [ ] **Step 2: Run targeted tests to verify failures**

Run: `python3 -m pytest tests/test_api_chat.py tests/test_api_eval.py tests/test_api_reports.py -q`
Expected: FAIL because `app.server` and route modules do not exist yet

- [ ] **Step 3: Create minimal FastAPI app and routers**

```python
app = FastAPI(title="Multi Agent Dialog Workbench")
app.include_router(chat_router, prefix="/api/chat")
app.include_router(eval_router, prefix="/api/eval")
app.include_router(report_router, prefix="/api/reports")
```

- [ ] **Step 4: Add in-memory stores for sessions and jobs**

```python
chat_sessions: dict[str, dict] = {}
eval_jobs: dict[str, dict] = {}
```

- [ ] **Step 5: Re-run targeted tests to verify passes**

Run: `python3 -m pytest tests/test_api_chat.py tests/test_api_eval.py tests/test_api_reports.py -q`
Expected: PASS with placeholder JSON responses

---

### Task 3: Add Chat Service and Session State Serialization

**Files:**
- Create: `app/services/chat_service.py`
- Modify: `app/api/chat.py`
- Modify: `app/schemas/chat.py`
- Test: `tests/test_api_chat.py`

- [ ] **Step 1: Write failing tests for create/get/reset/send-turn flows**

```python
def test_send_chat_turn_returns_messages_and_state(client):
    session_id = client.post("/api/chat/session").json()["session_id"]
    response = client.post(f"/api/chat/session/{session_id}/turn", json={"message": "你好"})
    body = response.json()
    assert "messages" in body
    assert "state" in body
```

- [ ] **Step 2: Run targeted test to verify failure**

Run: `python3 -m pytest tests/test_api_chat.py -q`
Expected: FAIL because turn endpoint does not yet call dialog logic

- [ ] **Step 3: Implement `chat_service` around current dialog state**

```python
def create_session() -> dict: ...
def get_session(session_id: str) -> dict: ...
def run_turn(session_id: str, message: str) -> dict: ...
def reset_session(session_id: str) -> dict: ...
```

- [ ] **Step 4: Mirror existing CLI flow when sending turns**

```python
session_state["messages"].append(HumanMessage(content=message))
updated_state = run_dialog(session_state)
store_session_state(session_id, updated_state)
```

- [ ] **Step 5: Serialize LangChain messages for frontend**

```python
{"role": "assistant", "content": "...", "message_type": "AIMessage"}
```

- [ ] **Step 6: Re-run targeted chat API tests**

Run: `python3 -m pytest tests/test_api_chat.py -q`
Expected: PASS with live session state returned

---

### Task 4: Add Trace Collection Hooks

**Files:**
- Create: `app/services/trace_service.py`
- Modify: `multi_agent_dialog/router.py`
- Modify: `multi_agent_dialog/experts.py`
- Modify: `app/services/chat_service.py`
- Test: `tests/test_trace_service.py`
- Test: `tests/test_experts.py`
- Test: `tests/test_router.py`

- [ ] **Step 1: Write failing tests for trace event capture**

```python
def test_trace_collector_records_tool_call():
    collector = TraceCollector()
    collector.record("tool_call", {"tool_name": "search_hotels"})
    assert collector.events[0]["type"] == "tool_call"
```

- [ ] **Step 2: Run targeted tests to verify failures**

Run: `python3 -m pytest tests/test_trace_service.py tests/test_experts.py tests/test_router.py -q`
Expected: FAIL because trace collector/hooks do not exist yet

- [ ] **Step 3: Implement trace collector and request-scoped registration**

```python
collector.record("router", {"intent": intent}, latency_ms=123)
collector.record("filter_block", {"tool_name": "book_hotel"})
```

- [ ] **Step 4: Wire hooks into router and experts**

```python
trace_collector = get_active_trace_collector()
if trace_collector:
    trace_collector.record(...)
```

- [ ] **Step 5: Return traces from chat responses**

Run: `python3 -m pytest tests/test_trace_service.py tests/test_experts.py tests/test_router.py -q`
Expected: PASS with trace lists available

---

### Task 5: Add Evaluation Job API and Progress Tracking

**Files:**
- Create: `app/services/eval_service.py`
- Modify: `app/api/eval.py`
- Modify: `app/schemas/eval.py`
- Modify: `evaluation/runner.py`
- Modify: `app/state/session_store.py`
- Test: `tests/test_api_eval.py`
- Test: `tests/test_evaluation_runner.py`

- [ ] **Step 1: Write failing tests for async eval lifecycle**

```python
def test_start_eval_job_and_fetch_result(client):
    job = client.post("/api/eval/run", json={"dataset_path": "evaluation/datasets/life_service_eval.json"}).json()
    assert job["status"] == "running"
```

- [ ] **Step 2: Run targeted tests to verify failures**

Run: `python3 -m pytest tests/test_api_eval.py tests/test_evaluation_runner.py -q`
Expected: FAIL because background jobs/progress callbacks are missing

- [ ] **Step 3: Extend runner with optional progress callback**

```python
def run_dataset(..., progress_callback: Callable | None = None) -> dict:
    ...
    if progress_callback:
        progress_callback(sample_result, index, len(dataset))
```

- [ ] **Step 4: Fix eval job result schema before frontend work starts**

```python
{
  "job_id": "...",
  "status": "completed",
  "result": {
    "stacked_multi_agent": {...},
    "baseline_single_agent": {...},
    "reports": {...}
  }
}
```

- [ ] **Step 5: Run long evaluation jobs in a separate process**

```python
def start_eval_job(dataset_path: str, systems: list[str]) -> str: ...
def get_eval_job(job_id: str) -> dict: ...
def get_eval_result(job_id: str) -> dict: ...
```

- [ ] **Step 6: Keep per-sample timeout compatible with async API**

```python
# Do not rely on SIGALRM in non-main-thread background tasks.
# Spawn a child process for the full eval job and let existing timeout logic run there.
```

- [ ] **Step 7: Add IPC for progress and partial metrics**

```python
# Parent process owns job state.
# Child process sends progress events through multiprocessing.Queue.
# Parent thread consumes queue messages and updates app/state/session_store.py.
```

- [ ] **Step 8: Define progress event payloads**

```python
{"type": "sample_progress", "job_id": "...", "system": "stacked_multi_agent", "completed": 8, "total": 22}
{"type": "partial_metrics", "job_id": "...", "system": "stacked_multi_agent", "metrics": {...}}
{"type": "completed", "job_id": "...", "result": {...}}
```

- [ ] **Step 9: Persist reports when jobs finish**

Run: `python3 -m pytest tests/test_api_eval.py tests/test_evaluation_runner.py tests/test_run_eval.py -q`
Expected: PASS with progress and final reports available

---

### Task 6: Add Report/History API

**Files:**
- Create: `app/services/report_service.py`
- Modify: `app/api/reports.py`
- Test: `tests/test_api_reports.py`
- Reuse: `evaluation/results/*`

- [ ] **Step 1: Write failing tests for latest/history endpoints**

```python
def test_reports_latest_returns_existing_artifacts(client):
    response = client.get("/api/reports/latest")
    assert response.status_code == 200
    assert "latest_html" in response.json()
```

- [ ] **Step 2: Run targeted report tests to verify failures**

Run: `python3 -m pytest tests/test_api_reports.py -q`
Expected: FAIL because report service logic is not implemented

- [ ] **Step 3: Implement report discovery and JSON loading**

```python
def get_latest_report() -> dict: ...
def list_report_history(limit: int = 20) -> list[dict]: ...
def load_report_json(path: str) -> dict: ...
```

- [ ] **Step 4: Re-run report API tests**

Run: `python3 -m pytest tests/test_api_reports.py -q`
Expected: PASS with filesystem-backed responses

---

### Task 7: Scaffold React + TypeScript Workbench

**Files:**
- Create: `web/package.json`
- Create: `web/tsconfig.json`
- Create: `web/vite.config.ts`
- Create: `web/index.html`
- Create: `web/src/main.tsx`
- Create: `web/src/App.tsx`
- Create: `web/src/pages/WorkbenchPage.tsx`
- Create: `web/src/styles.css`
- Create: `web/src/components/chat/ChatPanel.tsx`
- Create: `web/src/components/trace/TracePanel.tsx`
- Create: `web/src/components/eval/EvalPanel.tsx`

- [ ] **Step 1: Scaffold Vite React TS app files**

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build"
  }
}
```

- [ ] **Step 2: Add shell layout with three panels**

```tsx
<main className="workbench-grid">
  <ChatPanel />
  <TracePanel />
  <EvalPanel />
</main>
```

- [ ] **Step 3: Add placeholder panel components so the first build can pass**

```tsx
export function ChatPanel() { return <section>ChatPanel</section> }
```

- [ ] **Step 4: Install dependencies and verify build**

Run: `cd web && npm install`
Run: `cd web && npm run build`
Expected: build succeeds with placeholder components

---

### Task 8: Build Chat, Trace, and State Panels

**Files:**
- Create: `web/src/lib/api.ts`
- Create: `web/src/types/chat.ts`
- Create: `web/src/types/trace.ts`
- Create: `web/src/components/chat/ChatPanel.tsx`
- Create: `web/src/components/chat/MessageList.tsx`
- Create: `web/src/components/chat/InputBox.tsx`
- Create: `web/src/components/trace/TracePanel.tsx`
- Create: `web/src/components/trace/TraceTimeline.tsx`
- Create: `web/src/components/state/StatePanel.tsx`
- Modify: `web/src/pages/WorkbenchPage.tsx`

- [ ] **Step 1: Define shared frontend types**

```ts
export type ChatState = {
  current_intent: string
  active_task: string
  task_stack: string[]
  global_blackboard: Record<string, unknown>
}
```

- [ ] **Step 2: Implement API adapter and session bootstrap**

```ts
export async function createSession() { ... }
export async function sendTurn(sessionId: string, message: string) { ... }
```

- [ ] **Step 3: Render chat messages, state cards, and trace timeline**

```tsx
<section className="center-column">
  <TracePanel traces={traces} />
  <StatePanel state={state} />
</section>
```

Run: `cd web && npm run build`
Expected: build succeeds and panels render mocked data first, then live API data

---

### Task 9: Build Evaluation and Reports Panels

**Files:**
- Create: `web/src/types/eval.ts`
- Create: `web/src/components/eval/EvalPanel.tsx`
- Create: `web/src/components/eval/MetricsCards.tsx`
- Create: `web/src/components/eval/SampleTable.tsx`
- Create: `web/src/components/eval/SampleDetailDrawer.tsx`
- Create: `web/src/components/reports/ReportsPanel.tsx`
- Modify: `web/src/pages/WorkbenchPage.tsx`

- [ ] **Step 1: Wire eval job actions and polling**

```ts
export async function startEvalRun() { ... }
export async function getEvalJob(jobId: string) { ... }
export async function getEvalResult(jobId: string) { ... }
```

- [ ] **Step 2: Match frontend types to the fixed backend result schema**

```ts
type EvalCompareResult = {
  stacked_multi_agent: SystemEvalResult
  baseline_single_agent: SystemEvalResult
  reports: ReportArtifacts
}
```

- [ ] **Step 3: Render metric cards and sample detail**

```tsx
<MetricsCards metrics={result.stacked_multi_agent.metrics} />
<SampleTable samples={result.stacked_multi_agent.samples} />
```

- [ ] **Step 4: Render latest report links and embedded charts**

Run: `cd web && npm run build`
Expected: build succeeds and evaluation data displays without console errors

---

### Task 10: End-to-End Integration and Developer Entry Points

**Files:**
- Modify: `app/server.py`
- Optional Create: `scripts/dev-workbench.sh`
- Modify: `README.md` or create `docs/superpowers/plans/README-workbench.md` if desired
- Verify: `tests/test_api_chat.py`
- Verify: `tests/test_api_eval.py`
- Verify: `tests/test_api_reports.py`

- [ ] **Step 1: Add CORS and local dev startup instructions**

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- [ ] **Step 2: Verify backend test suite**

Run: `python3 -m pytest tests/test_api_chat.py tests/test_api_eval.py tests/test_api_reports.py tests/test_trace_service.py -q`
Expected: PASS

- [ ] **Step 3: Verify existing regression suite still passes**

Run: `python3 -m pytest tests/test_experts.py tests/test_router.py tests/test_evaluation_runner.py tests/test_run_eval.py -q`
Expected: PASS

- [ ] **Step 4: Verify frontend build**

Run: `cd web && npm run build`
Expected: PASS

- [ ] **Step 5: Verify manual local workflow**

Run backend: `python3 -m uvicorn app.server:app --reload --port 8000`
Run frontend: `cd web && npm run dev`
Expected:
- open workbench in browser
- create session and send one turn
- see traces and blackboard/task stack updates
- start one eval run and see metrics/report links appear

---

## Notes

- Assume frontend scaffold uses `Vite + React + TypeScript`.
- Keep the first version single-user and in-memory.
- Do not replace existing CLI flows; the workbench is an additive local tool.
- Prefer hook-based instrumentation over deep refactors to preserve current dialog behavior.
