# Thesis Template Rewrite Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the graduation thesis output so the local `.docx` follows the provided university format, removes the appendix by folding material into the main chapters, expands the main body toward 50 pages, and synchronizes the full content to a Lark document.

**Architecture:** Keep a single Python document generator in `scripts/` as the source of truth for thesis content, typography, charts, and code screenshots. Generate all assets locally, export a strict-format `.docx` to the desktop, derive a Markdown mirror from the same structured content, then create or update a Lark doc with matching sections and images.

**Tech Stack:** Python, `python-docx`, `matplotlib`, `Pillow`, `pygments`, Lark CLI docs APIs

---

### Task 1: Restructure Thesis Content

**Files:**
- Modify: `scripts/generate_enhanced_thesis_docx.py`

- [ ] **Step 1: Expand the chapter outline**
  - Replace appendix-oriented content with expanded Chapter 2-5 body sections.
  - Add explicit sections for system architecture, state management, tool safety, frontend workbench, knowledgebase editor, experiment design, case study, and error analysis.

- [ ] **Step 2: Merge appendix material into body**
  - Move code excerpts into Chapter 4 implementation analysis.
  - Move sample dialogues and evaluation observations into Chapter 5 experiment analysis.

- [ ] **Step 3: Add richer academic prose**
  - Increase each chapter with background, design rationale, trade-off analysis, and engineering interpretation so the body reaches about 50 Word pages.

### Task 2: Enforce Word Template Formatting

**Files:**
- Modify: `scripts/generate_enhanced_thesis_docx.py`

- [ ] **Step 1: Rebuild cover page**
  - Generate a standalone cover with placeholder fields: college, major, student name, student ID, advisor, completion date.
  - Do not add header/footer to the cover page.

- [ ] **Step 2: Reconfigure page layout**
  - Set margins to top `2.5cm`, bottom `2.5cm`, left `3.0cm`, right `2.0cm`.
  - Apply `1.5` line spacing and proper Chinese/English font pairs.

- [ ] **Step 3: Rebuild front matter**
  - Add Chinese title, abstract, keywords, English title, abstract, keywords, and table of contents placeholder structure.
  - Use Roman numeral footer page numbers for front matter.

- [ ] **Step 4: Rebuild body styles**
  - Start each chapter on a new page.
  - Apply title hierarchy, first-line indents, figure/table captions, and reference section formatting.

### Task 3: Refresh Figures and Code Screenshots

**Files:**
- Modify: `scripts/generate_enhanced_thesis_docx.py`
- Read: `evaluation/results/latest.json`
- Read: project source files for screenshots

- [ ] **Step 1: Keep existing charts and improve captions**
  - Preserve architecture, stack flow, workbench, dataset distribution, and metric charts.

- [ ] **Step 2: Add implementation screenshots into body chapters**
  - Render key snippets from `state.py`, `experts.py`, `tools.py`, `runner.py`, `trace_service.py`, and `WorkbenchPage.tsx`.

- [ ] **Step 3: Insert figures at narrative positions**
  - Place each figure near the text that explains it, with chapter-consistent numbering and analysis.

### Task 4: Generate Local Docx and Validate

**Files:**
- Modify: `scripts/generate_enhanced_thesis_docx.py`
- Output: `/Users/bytedance/Desktop/基于对话管理的生活服务_AI_Agent_多轮交互策略_严格格式版.docx`

- [ ] **Step 1: Run generator**
  - Run: `python3 scripts/generate_enhanced_thesis_docx.py`

- [ ] **Step 2: Validate output structure**
  - Check the file exists, inspect zip integrity, and confirm the output is not corrupted.

- [ ] **Step 3: Smoke-check document size**
  - Confirm the output is meaningfully larger than the previous trimmed version and still opens as a valid docx container.

### Task 5: Sync Lark Document

**Files:**
- Create or update: generated markdown artifact under `.thesis_assets/`
- Use: Lark docs APIs

- [ ] **Step 1: Export Markdown mirror**
  - Produce a Markdown version from the same source content for Lark upload.

- [ ] **Step 2: Create or replace Lark doc**
  - Use `lark-cli docs +create` with the thesis body and then upload local images.

- [ ] **Step 3: Verify links and report paths**
  - Return both the Lark doc link and the local desktop docx path.
