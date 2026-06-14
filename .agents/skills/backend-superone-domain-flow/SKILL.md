---
name: backend-superone-domain-flow
description: 当用户要在 backend-superone 新增业务 domain、entity、model、factory、repo、service 或 store/cache 逻辑时使用；按当前项目的 DDD + Clean Architecture 风格生成代码。
metadata:
  short-description: backend-superone 领域开发
---

# backend-superone 领域开发

本 skill 自包含，不依赖仓库内知识库目录。项目约定：表模型在 `internal/model/*_tab.go`，Repo 优先在 `internal/repo`，Service 在 `internal/domain/{domain}/{domain}_service`，错误包使用 `internal/infrastructure/ecode`，BizContext 使用 `internal/infrastructure/bizctx`。

## 标准目录

```text
internal/domain/{domain}/
  {domain}_dto/
  {domain}_entity/
  {domain}_factory/
  {domain}_service/
internal/model/
internal/repo/
use_case/*.go
```

## 流程

1. 先定义 entity，表达业务含义。
2. 在 `internal/model/*_tab.go` 定义 GORM 表模型，提供 `TableName()`。
3. 在 factory 中实现 model 到 entity 的转换；entity 需要落库时提供 `ToModel()`。
4. 在 repo 中定义 `I{Domain}Repo` 和 `{Domain}Repo`，使用 `bizctx` DB helper 或 GORM。
5. 在 service 中定义 `I{Domain}Service` 和 `{Domain}Service`，业务校验、事务和错误处理放在这里。
6. 如需 API，再配合 `backend-superone-api-flow` 做 DTO、UseCase 和路由。
7. 如新增或修改前端可见枚举、状态、结构体字段，配合 `backend-frontend-contract-flow` 输出前端契约。
8. 更新 Wire ProviderSet，运行 `wire ./...`。

## 约束

- Service 返回 `*ecode.BizError`。
- 不在 repo 中写业务判断。
- 不跨层直接调用 app 或 middleware。
- 事务沿用项目当前 `bizctx`/GORM 事务工具。
- 影响前端的枚举和结构体变更必须同步 OpenAPI YAML 和工作台协议仓 `business-repo/frontend-contracts`。
