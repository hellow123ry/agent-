# Knowledgebase Editor Design

**Date:** 2026-04-30

**Goal**

在现有可视化工作台中增加一个“生活服务知识库”编辑窗口，让用户可以直接在前端查看、修改、新增、删除餐厅与酒店 mock 数据，并让对话系统与评测系统即时读取这份最新数据。

## Scope

本次只覆盖“生活服务知识库”：

- 餐厅数据
- 酒店数据

本次不覆盖：

- 用户长期偏好知识库
- 文档型 RAG 知识库
- 文件上传导入
- 版本管理/回滚
- 多用户并发编辑

### Concurrency Assumption

本次明确限定为：

- 单机
- 单用户
- 本地工作台

因此本次不引入版本号、ETag 或协同编辑协议。

如果未来出现多窗口并发编辑需求，再补冲突检测。

## Current State

当前知识数据硬编码在 [tools.py](file:///Users/bytedance/Desktop/multi_agent_dialog_system/multi_agent_dialog/tools.py)：

- `MOCK_RESTAURANTS`
- `MOCK_HOTELS`

这会带来两个问题：

- 前端无法直接修改
- 数据更新需要改代码，不能作为运行时配置

## Proposed Architecture

采用“数据文件 + 后端 service + 前端表单编辑器”的结构。

### Data Layer

新增运行时数据文件：

- `data/knowledgebase.json`

路径解析规则：

- 路径固定相对于项目根目录
- 不依赖当前工作目录

结构：

```json
{
  "restaurants": [
    {
      "name": "汉拿山韩式烤肉",
      "type": "烤肉店",
      "capacity": [2, 3, 4],
      "status": "有位"
    }
  ],
  "hotels": [
    {
      "name": "如家快捷酒店",
      "location": "火车站",
      "type": "经济",
      "price": 300,
      "status": "有房"
    }
  ]
}
```

### Backend

新增知识库 service，负责：

- 读取 `data/knowledgebase.json`
- 校验数据结构
- 以原子方式保存最新内容
- 为工具层提供统一读取入口
- 内置唯一的默认 seed 数据

保存策略：

- 先写临时文件
- 校验 JSON 完整性
- 再用 rename 覆盖正式文件

这样可以避免半截 JSON 写坏整个知识库。

新增知识库 API：

- `GET /api/knowledgebase`
  - 返回完整知识库
- `PUT /api/knowledgebase/restaurants`
  - 覆盖保存餐厅列表
- `PUT /api/knowledgebase/hotels`
  - 覆盖保存酒店列表

成功响应统一返回：

```json
{
  "ok": true,
  "data": ...
}
```

失败响应统一返回：

```json
{
  "ok": false,
  "error": {
    "code": "validation_error",
    "message": "capacity 必须是正整数数组",
    "field": "capacity"
  }
}
```

### Tool Integration

修改 `search_restaurants()` / `search_hotels()` / `book_hotel()`：

- 不再直接依赖硬编码常量
- 改为从知识库 service 读取当前数据

这样前端修改后：

- 新创建的会话会读取最新知识库
- 新发起的评测任务会读取最新知识库

一致性策略：

- 聊天会话在创建时固定一份知识库快照
- 评测任务在启动时固定一份知识库快照
- 同一个会话/同一个评测任务执行期间，不受中途编辑影响
- 用户保存新知识库后，只影响后续新建会话和后续新发起的评测

### Frontend

在当前工作台右侧新增一个 `知识库` 面板。

交互形式：

- Tab 1: `餐厅`
- Tab 2: `酒店`

每个 tab 内：

- 列表展示现有数据
- 每条记录支持编辑
- 支持新增一条
- 支持删除一条
- 支持“保存”
- 支持“重载最新”

字段设计：

餐厅：

- `name`
- `type`
- `capacity`，前端用逗号分隔输入，提交前转成整数数组
- `status`

酒店：

- `name`
- `location`
- `type`
- `price`
- `status`

## UX Decisions

采用表单化编辑，而不是原始 JSON 编辑。

理由：

- 更适合当前工作台场景
- 字段结构固定，表单比 JSON 更易用
- 可以顺手做最基础的输入校验

## Validation Rules

后端至少校验：

餐厅：

- `name` 非空
- `type` 非空
- `capacity` 为正整数数组
- `capacity` 去重
- `status` 非空
- `name` 在餐厅列表内唯一

酒店：

- `name` 非空
- `location` 非空
- `type` 非空
- `price` 为正数
- `status` 非空
- `name` 在酒店列表内唯一

前端做轻量校验，后端做最终校验。

## Error Handling

前端：

- 保存失败时显示错误提示
- 重载失败时显示错误提示

后端：

- 非法数据返回 `400`
- 数据文件缺失时用代码内置默认模板初始化一次
- 保存失败返回明确错误信息

默认模板来源：

- 在知识库 service 内维护唯一 seed 数据
- `tools.py` 不再作为默认数据源
- 只在目标文件不存在时触发，不覆盖已有文件

## Testing

后端测试：

- 读取默认知识库
- 更新餐厅数据
- 更新酒店数据
- 非法 payload 拒绝
- 工具层读取知识库后能反映最新数据

前端验证：

- 获取知识库成功渲染
- 编辑后保存成功
- 删除/新增后保存成功
- 重载能恢复服务端最新数据

## Rollout Order

1. 抽离硬编码 mock 数据到 `data/knowledgebase.json`
2. 增加知识库 service 和 API
3. 修改工具层读知识库快照/新数据源
4. 增加前端知识库面板
5. 联调：前端修改后对话搜索立即生效

## Success Criteria

满足以下条件即视为完成：

- 页面中可以直接编辑餐厅/酒店知识数据
- 点击保存后数据落盘
- 后续对话与评测读取的是最新知识库
- 非法输入不会静默写坏数据
