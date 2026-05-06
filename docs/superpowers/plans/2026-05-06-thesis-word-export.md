# Thesis Word Export Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 生成一份约 50 页、包含评测图、结构图、代码截图的本地 Word 论文，并输出到桌面。

**Architecture:** 复用项目中的真实评测结果与核心代码文件，先程序化生成图片素材，再由 `python-docx` 统一排版生成 `.docx`。正文采用扩写后的章节内容，图片包含真实评测图、结构示意图与关键代码截图，最终通过本地脚本一次性导出。

**Tech Stack:** Python 3, `python-docx`, `Pillow`, `Pygments`, `matplotlib`, `cairosvg`

---

### Task 1: 准备素材清单

**Files:**
- Read: `evaluation/results/latest.json`
- Read: `evaluation/results/latest-*.svg`
- Read: `multi_agent_dialog/state.py`
- Read: `multi_agent_dialog/router.py`
- Read: `multi_agent_dialog/experts.py`
- Read: `multi_agent_dialog/tools.py`
- Read: `evaluation/runner.py`
- Read: `evaluation/metrics.py`
- Read: `evaluation/systems.py`
- Read: `app/services/trace_service.py`
- Read: `web/src/pages/WorkbenchPage.tsx`

- [ ] 记录论文中的真实实验指标与可引用代码片段
- [ ] 选定需转成图片的评测图、架构图与代码截图

### Task 2: 生成图片素材

**Files:**
- Create: `tmp/thesis_assets/*.png`
- Create: `scripts/generate_thesis_assets.py`

- [ ] 用 `cairosvg` 将已有评测 SVG 转成 PNG
- [ ] 用 `matplotlib` 生成补充图，如任务流程图、系统组成图、样本分布图
- [ ] 用 `Pygments + Pillow` 将关键代码片段渲染成截图
- [ ] 验证所有图片生成成功且尺寸适合插入 Word

### Task 3: 生成增强版论文正文

**Files:**
- Create: `tmp/thesis_enhanced.md`
- Create: `scripts/build_thesis_docx.py`

- [ ] 编写扩展版论文正文，覆盖摘要、英文摘要、目录、六章正文、参考文献、致谢、附录
- [ ] 按 50 页目标扩写理论基础、系统实现、实验分析与案例研究
- [ ] 在正文中插入图题、表题、代码截图说明和附录说明

### Task 4: 导出桌面 Word 文档

**Files:**
- Output: `/Users/bytedance/Desktop/基于对话管理的生活服务_AI_Agent_多轮交互策略_增强版.docx`

- [ ] 使用 `python-docx` 设置页面、标题、字体、段落、图注和表格
- [ ] 插入所有图片与代码截图
- [ ] 保存到桌面
- [ ] 检查文件存在且大小正常

### Task 5: 验证与收尾

**Files:**
- Verify: `/Users/bytedance/Desktop/基于对话管理的生活服务_AI_Agent_多轮交互策略_增强版.docx`

- [ ] 验证文档可打开
- [ ] 记录最终输出路径
- [ ] 向用户说明当前版本包含的素材类型与仍可继续优化的部分
