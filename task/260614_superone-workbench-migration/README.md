# Superone 多仓规则完善

## 背景

Superone 的后端、前端、协议等独立仓统一由工作台 `business-repo/` 管理。工作台负责跨仓路由、上下文聚合和契约同步编排。

## 目标

1. 工作台成为 Superone 多仓协作的全局入口。
2. `backend-superone` 负责后端实现、数据模型、领域规则、接口和验证。
3. `uni-superone` 负责前端页面、状态、交互和接口消费。
4. `frontend-contracts` 作为协议仓，位置为 `business-repo/frontend-contracts`。
5. 更新相关 skill、知识库和路由文档中的路径与职责描述。

## 当前边界

- 本任务优先更新工作台规则、知识库、skill 和入口说明。
- 不直接改业务源码。
- 如果协议仓目录尚不存在，先统一规则中的目标路径，后续再补实际仓配置。

## 已沉淀规则

- Superone 需求先经工作台路由，再进入 `backend-superone`、`uni-superone` 或 `frontend-contracts`。
- 接口、DTO、枚举、错误码、字段语义变化必须同步工作台协议仓。
