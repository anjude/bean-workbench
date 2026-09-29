# Superone 多仓规则完善

## 背景

Superone 的后端、前端、协议等独立仓统一由工作台 `business-repo/` 管理。工作台负责跨仓路由、上下文聚合和契约同步编排。

## 目标

1. 工作台成为 Superone 多仓协作的全局入口。
2. `backend-superone` 负责后端实现、数据模型、领域规则、接口和验证，位置为 `business-repo/backend-superone`。
3. `uni-superone` 负责前端页面、状态、交互和接口消费，位置为 `business-repo/uni-superone`。
4. `uni-carbon-space` 负责 Carbon Space 前端页面、状态、交互和接口消费，位置为 `business-repo/uni-carbon-space`。
5. `frontend-contracts` 作为协议仓，位置为 `business-repo/frontend-contracts`。
6. 其他历史子模块统一迁入 `business-repo/`，包括 Web、原生小程序、投资平台、uTools 和辅助工具仓。
7. 更新相关 skill、知识库和路由文档中的路径与职责描述。

## 当前边界

- 本任务优先更新工作台规则、知识库、skill 和入口说明。
- 不直接改业务源码。
- 已迁入工作台的业务仓不再通过 `backend-superone/submodule/*` 访问，不保留旧路径兼容。
- `backend-superone` 不再保留 `.gitmodules` 和 `submodule/*` 业务仓入口。

## 已沉淀规则

- Superone 需求先经工作台路由，再进入 `backend-superone`、`uni-superone` 或 `frontend-contracts`。
- 接口、DTO、枚举、错误码、字段语义变化必须同步工作台协议仓。
- 业务仓 Agent 说明统一命名为 `AGENTS.md`。
- `frontend-contracts`、`uni-carbon-space`、`uni-superone` 已从 `backend-superone` 旧 submodule 编排迁到工作台 `business-repo/`。
- `bt`、`frontend-investment-platform`、`frontend-superone`、`miniprogram-superone`、`utools-bean-note`、`utools-bean-option`、`utools-superone` 已迁到工作台 `business-repo/`。
