---
name: workbench-router
description: 工作台轻量路由 skill。用户提出 superone 需求、便签需求、业务仓需求、前端需求、后端需求、文档需求，或需要判断应进入哪个业务仓、哪个知识库、哪个任务上下文时使用。该 skill 只负责路由和上下文选择，不直接替代业务 skill。
---

# 工作台路由

## 路由步骤

1. 先读 `task/registry.md`，判断是否命中热任务。
2. 再读 `knowledge-base/README.md` 和相关索引，确认业务仓或系统上下文。
3. 命中明确业务需求时，进入对应业务仓并读取该仓自己的入口说明。
4. 未命中明确业务需求时，只在工作台层面补充任务、知识库或规则。

## 初始路由规则

- `superone`：路由到 `business-repo/`，再根据需求判断 `backend-superone`、`uni-superone` 或 `frontend-contracts`。
- `后端`、`API`、`数据库`、`SQL`：优先考虑 `business-repo/backend-superone`。
- `前端`、`页面`、`uni-app`、`小程序`：优先考虑 `business-repo/uni-superone`。
- `carbon`、`uni-carbon-space`：优先考虑 `business-repo/uni-carbon-space`，并叠加 `carbon-space-ui`、`carbon-icon-flow`。
- `OpenAPI`、`契约`、`frontend-contracts`、`DTO 同步`：优先考虑 `business-repo/frontend-contracts`。
- `便签`：先查 `task/registry.md` 和 `knowledge-base/`；没有明确归属时，不直接改业务仓。
- `工作台`、`skill`、`知识库`、`自进化`：只改工作台根级目录。

## 输出要求

- 给出命中的业务仓或工作台目录。
- 说明是否需要读取额外规则。
- 如果路由不清楚，先补充任务登记或痛点记录，不要盲目改业务仓。
