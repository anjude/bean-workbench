# 业务仓知识库

这里按业务仓沉淀系统理解、上下文入口、常见约束和复用经验。

## 业务仓索引

- `backend-superone`：后端业务仓。
- `uni-superone`：uni-app 前端业务仓。
- `frontend-contracts`：前后端协议仓，位置为 `business-repo/frontend-contracts`。

## Superone 编排关系

- 工作台是 Superone 多仓协作的全局入口，负责判断需求应该落到后端、前端、协议仓，还是只沉淀到知识库或 skill。
- `backend-superone` 负责服务端实现、数据模型、领域规则、接口和验证。
- `uni-superone` 负责跨端前端页面、状态、交互和接口消费。
- `frontend-contracts` 负责 OpenAPI、前端类型、枚举和 API 契约文件。
- 涉及接口、DTO、枚举、错误码和字段语义变化时，由工作台编排后端实现与协议仓同步。

## 写入边界

这里只记录知识索引和稳定结论，不复制业务仓大段源码或文档。
