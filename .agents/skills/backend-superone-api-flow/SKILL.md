---
name: backend-superone-api-flow
description: 当用户要在 backend-superone 新增或修改 Gin API 接口、DTO、UseCase、Service、路由或 API 文档时使用；基于 backend-superone 当前技术栈和全新指导规范快速开发。
metadata:
  short-description: backend-superone API 开发
---

# backend-superone API 开发

本 skill 自包含，不依赖仓库内知识库目录。项目约定：路由在 `app/api_service/*.go`，UseCase 在 `use_case/*.go`，DTO 在 `internal/domain/{domain}/{domain}_dto`，Service 在 `internal/domain/{domain}/{domain}_service`，错误包使用 `internal/infrastructure/ecode`，BizContext 使用 `internal/infrastructure/bizctx`。

## 流程

1. 确认 domain、接口路径、HTTP 方法、是否需要 JWT。
2. 在 `internal/domain/{domain}/{domain}_dto` 定义请求和响应结构：请求字段同时加 `form`、`json`，必填字段加 `binding:"required"`。
3. 在 `internal/domain/{domain}/{domain}_service` 增加 service 接口方法和实现，返回 `(*Resp, *ecode.BizError)`。
4. 在 `use_case/{domain}_use_case.go` 或既有 `use_case/{domain}.go` 增加 UseCase 方法，从 `ctx.GetReqParam().(dto.XReq)` 取参数并调用 service。
5. 在 `app/api_service/*.go` 的对应路由组注册路由：`middleware.HandleRequest(useCase.Method, dto.XReq{})`。
6. 新 domain 时同步更新 `app/api_service/api_service.go`、`app/api_service/wire.go` 和相关 injector。
7. 如果接口、DTO、响应或错误码影响前端，执行 `backend-frontend-contract-flow` 更新工作台协议仓 `business-repo/frontend-contracts/openapi/{domain}_api.yaml` 和 `business-repo/frontend-contracts`。
8. 执行 `wire ./...`、`gofmt`、聚焦测试或 `go test ./...`。

## 输出要求

- 直接列出需要修改/新增的文件。
- 如果落代码，保持当前相对目录结构和本 skill 约定。
- 影响前端时必须列出前端契约复制清单。
- 不引入新框架，不重构无关历史代码。
