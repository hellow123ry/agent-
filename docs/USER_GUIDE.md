# Multi-Agent Dialog System User Guide

## 1. 文档目标

本文档用于说明本系统的完整功能、典型使用方式、工作台各区域职责、后端接口清单以及常见操作流。

适用对象：

- 想快速运行项目并体验多智能体对话的开发者
- 需要在前端工作台里调试路由、状态和工具调用的使用者
- 需要批量评测、查看报告、修改知识库的研究或课程项目使用者

## 2. 系统概览

本项目是一个面向生活服务场景的多智能体对话系统原型，核心特征包括：

- 通过路由器将用户请求分发给餐饮、酒店等领域专家
- 通过 `task_stack` 管理多任务切换、打断与恢复
- 通过 `global_blackboard` 共享跨专家上下文
- 通过工具调用访问本地生活服务知识库
- 通过可视化工作台统一展示对话、Trace、状态、评测和报告

主要运行形态有两种：

- 命令行模式：适合快速试验对话
- Web 工作台模式：适合调试、演示、评测和数据维护

## 3. 功能总览

### 3.1 对话系统能力

- 支持生活服务任务型对话
- 支持餐厅预订类问答
- 支持酒店筛选和推荐类问答
- 支持多轮槽位补全与澄清提问
- 支持对话过程中的任务切换与恢复
- 支持返回完整消息列表、状态快照和 Trace 事件

### 3.2 可视化工作台能力

- 自动初始化会话
- 发送用户消息
- 重置会话
- 查看会话 ID、当前活动任务和评测状态
- 查看 Trace 事件时间线
- 查看对话状态中的任务栈与黑板
- 启动离线评测
- 查看评测实时进度条
- 查看对比系统指标
- 查看样本级评测明细
- 打开最新报告和历史报告
- 在线编辑知识库中的餐厅和酒店数据

### 3.3 数据与评测能力

- 使用本地数据集运行批量评测
- 同时评测 `stacked_multi_agent` 与 `baseline_single_agent`
- 输出成功率、平均轮次、槽位精确率、召回率和 F1
- 生成 HTML、JSON、SVG 报告
- 提供报告历史列表

## 4. 工作台说明

工作台采用三栏布局：

- 左栏：聊天面板 + 知识库编辑
- 中栏：Trace 面板 + State 面板
- 右栏：评测看板 + 报告文件

### 4.1 顶部摘要区

顶部 Header 展示三个运行摘要：

- `Session`
- `Active Task`
- `Eval Status`

适合快速确认当前会话是否创建成功、系统当前执行的任务类型，以及评测任务是否空闲、运行中或已完成。

### 4.2 聊天面板

聊天面板是系统的主交互入口，支持：

- 查看当前会话 ID
- 输入用户问题
- 发送消息
- 查看系统回复
- 展示用户/助手消息卡片
- 重置当前会话
- 在请求失败时显示错误信息

典型用途：

- 验证多智能体是否正确理解需求
- 观察系统是否会主动补充缺失槽位
- 验证知识库更新后新会话是否能读取到最新数据

### 4.3 Trace 面板

Trace 面板用于展示一次对话调用返回的事件轨迹，帮助定位：

- 路由器是否选择了正确专家
- 工具调用是否被触发
- 某一步发生了什么中间状态变化

适合开发调试和答辩展示。

### 4.4 State 面板

State 面板展示当前对话状态，重点包括：

- `task_stack`
- `active_task`
- `global_blackboard`
- `knowledgebase`

用途：

- 确认系统当前任务上下文
- 观察槽位是否已填充
- 确认知识库快照是否随会话绑定

### 4.5 评测看板

评测看板支持：

- 一键启动评测
- 查看 `job_id`
- 查看 `status`
- 查看 `current_system`
- 查看两个系统各自的进度条
- 查看指标卡片
- 查看样本级明细表

其中进度条分别展示：

- `stacked_multi_agent` 已完成样本数 / 总样本数
- `baseline_single_agent` 已完成样本数 / 总样本数

适合在演示时直观看到评测跑到哪里。

### 4.6 报告文件面板

报告文件区支持：

- 打开最新 HTML 报告
- 打开最新 JSON 报告
- 浏览历史 JSON 报告入口

报告通过后端接口以 HTTP 文件方式暴露，因此前端可以直接点击打开，而不需要手动进入目录查找文件。

### 4.7 知识库编辑面板

知识库编辑器位于左栏，采用表单化方式编辑数据，当前支持两个 Tab：

- 餐厅
- 酒店

餐厅编辑能力：

- 修改名称
- 修改类型
- 修改容量
- 修改状态
- 新增餐厅
- 删除餐厅
- 保存餐厅数据

酒店编辑能力：

- 修改名称
- 修改位置
- 修改类型
- 修改价格
- 修改状态
- 新增酒店
- 删除酒店
- 保存酒店数据

其他能力：

- 重新加载知识库
- 表单错误提示
- 保存成功提示
- 餐厅 `capacity` 文本自动解析为数字数组

快照语义说明：

- 新建会话读取最新知识库
- 重置会话读取最新知识库
- 新启动的评测任务读取最新知识库
- 已存在会话继续使用创建时的知识库快照

## 5. 典型使用流程

### 5.1 流程 A：体验一次真实对话

1. 启动后端服务
2. 启动前端服务
3. 打开工作台
4. 在聊天框输入如“我想订明天晚上的烤肉店，2个人”
5. 点击“发送”
6. 观察回复、Trace 与 State 是否符合预期

### 5.2 流程 B：修改知识库并验证生效

1. 打开知识库编辑器
2. 在“餐厅”或“酒店”页签中修改数据
3. 点击“保存餐厅”或“保存酒店”
4. 点击“重置会话”或新建会话
5. 再次发起相关问题
6. 观察回复是否已经使用最新数据

### 5.3 流程 C：运行评测并查看报告

1. 点击“运行评测”
2. 观察进度条逐步推进
3. 等待状态变为 `completed`
4. 查看指标卡片
5. 打开 `latest.html`
6. 如需留档，可同时打开 `latest.json`

## 6. 目录与关键文件

- `multi_agent_dialog/`
  - 多智能体对话核心逻辑
- `app/server.py`
  - FastAPI 应用入口
- `app/api/`
  - HTTP 接口定义
- `app/services/`
  - 聊天、评测、报告、知识库服务
- `web/src/pages/WorkbenchPage.tsx`
  - 工作台页面组装入口
- `web/src/lib/api.ts`
  - 前端 API 请求封装
- `evaluation/datasets/life_service_eval.json`
  - 生活服务评测数据集
- `evaluation/run_eval.py`
  - 批量评测入口
- `data/knowledgebase.json`
  - 运行时知识库数据
- `docs/assets/`
  - README 截图资源

## 7. 运行方式

### 7.1 环境要求

- Python `3.11+`
- Node.js `18+`
- npm `9+`

### 7.2 安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd web
npm install
cd ..
```

### 7.3 启动后端

```bash
python3 -m uvicorn app.server:app --host 127.0.0.1 --port 8000
```

### 7.4 启动前端

```bash
cd web
npm run dev -- --host 127.0.0.1 --port 5173
```

如果 `5173` 被占用，Vite 可能自动切换到 `5174`。

### 7.5 命令行模式

```bash
python3 main.py
```

### 7.6 运行评测

```bash
python3 evaluation/run_eval.py
```

## 8. 后端 API 清单

### 8.1 Chat API

- `POST /api/chat/session`
  - 创建新会话
- `GET /api/chat/session/{session_id}`
  - 获取现有会话
- `DELETE /api/chat/session/{session_id}`
  - 重置会话
- `POST /api/chat/session/{session_id}/turn`
  - 提交一轮用户输入，返回消息、状态和 traces

### 8.2 Eval API

- `POST /api/eval/run`
  - 启动评测任务，参数为数据集路径
- `GET /api/eval/jobs/{job_id}`
  - 查询评测任务状态、当前系统和部分指标
- `GET /api/eval/jobs/{job_id}/result`
  - 获取完整评测结果

### 8.3 Reports API

- `GET /api/reports/latest`
  - 获取最新报告文件元数据
- `GET /api/reports/history`
  - 获取历史报告列表
- `GET /api/reports/file?path=...`
  - 读取报告文件内容

### 8.4 Knowledgebase API

- `GET /api/knowledgebase`
  - 获取知识库
- `PUT /api/knowledgebase/restaurants`
  - 更新餐厅列表
- `PUT /api/knowledgebase/hotels`
  - 更新酒店列表

## 9. 输出文件说明

评测完成后常见输出包括：

- `evaluation/results/latest.json`
- `evaluation/results/latest.html`
- `evaluation/results/latest-task_success_rate.svg`
- `evaluation/results/latest-average_turns.svg`
- `evaluation/results/latest-slot_f1.svg`

这些文件会被报告面板消费，也可以直接通过接口打开。

## 10. 常见问题

### 10.1 前端打开后无法发送消息

优先检查：

- 后端是否已启动
- 前端请求的 API 地址是否正确
- 当前 Vite 端口是否发生切换
- 后端 CORS 是否允许当前前端端口

### 10.2 修改知识库后当前会话没有变化

这是预期行为。当前会话默认绑定创建时的知识库快照，需要重置会话或新建会话后再验证。

### 10.3 报告链接打不开

优先检查：

- 是否已经成功跑完至少一次评测
- `evaluation/results/` 下是否存在对应文件
- 后端服务是否正常运行

### 10.4 评测为什么耗时较长

批量评测会逐条样本运行两个系统，并生成完整结果与报告，因此耗时明显高于单轮聊天。

## 11. 建议使用场景

- 多智能体对话课程设计演示
- Agent 系统研究原型验证
- 任务型对话可视化调试平台
- 毕业设计项目答辩展示
