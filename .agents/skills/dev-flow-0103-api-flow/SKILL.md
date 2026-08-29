---
name: dev-flow-0103-api-flow
description: 当要在 backend-superone 新增或修改 Gin API 接口、DTO、UseCase、Service、路由、API 文档，或新增 service/repo/use_case/router 后需要配置 Google Wire、修复依赖注入时使用。
metadata:
  short-description: backend-superone 接口与注入装配
---

# backend-superone 接口与注入装配

阶段 01 后端开发，执行顺序第 3 步。项目上下文见 `dev-flow-tools-repo`。

职责两层：**接口层**（DTO / UseCase / Service / 路由）+ **注入装配**（Wire）。新增接口后必然要补 Wire，两者不拆开跑。

## 一、接口层

落点：路由 `app/api_service/*.go`，UseCase `use_case/*.go`，DTO `internal/domain/{domain}/{domain}_dto`，Service `internal/domain/{domain}/{domain}_service`，错误包 `internal/infrastructure/ecode`，BizContext `internal/infrastructure/bizctx`。

### 流程

1. 确认 domain、接口路径、HTTP 方法、是否需要 JWT。
2. 在 `internal/domain/{domain}/{domain}_dto` 定义请求和响应结构：请求字段同时加 `form`、`json`，必填字段加 `binding:"required"`。
   - 数值字段若 `0` 是合法语义（取消表态、默认状态），不要用 `binding:"required"`，改用 `binding:"gte=0"`，否则 gin 会把 0 当零值拒绝。
3. 在 `{domain}_service` 增加 service 接口方法和实现，返回 `(*Resp, *ecode.BizError)`。
4. 在 `use_case/{domain}_use_case.go` 或既有 `use_case/{domain}.go` 增加 UseCase 方法，从 `ctx.GetReqParam().(dto.XReq)` 取参数并调用 service。
5. 在 `app/api_service/*.go` 的对应路由组注册路由：`middleware.HandleRequest(useCase.Method, dto.XReq{})`。
6. 新 domain 时同步更新 `app/api_service/api_service.go`、`app/api_service/wire.go` 和相关 injector。

## 二、Wire 注入装配

落点：API 层 `app/api_service/wire.go`，UseCase 层 `use_case/wire.go`，Service 层 `internal/domain/{domain}/{domain}_service/wire.go`，Repo 层沿用 `internal/repo` 已有注入方式。

### 规则

- `wire.go` 使用 `//go:build wireinject` 和 `// +build wireinject`。
- 使用 `wire.Struct(new(Type), "*")` 注入结构体字段。
- 接口绑定使用 `wire.Bind(new(IInterface), new(*Impl))`。
- 新增 constructor 或 ProviderSet 后，更新调用链上层的 `wire.Build`。

### 装配流程

1. 新增 constructor 或 ProviderSet。
2. 更新调用链上层的 `wire.Build`。
3. 运行 `wire ./...`（等价 `make wire`）。
4. 失败时按报错修复缺失 provider、接口绑定或循环依赖。

## 收尾

- 如果接口、DTO、响应或错误码影响前端，执行 `dev-flow-0104-contract-flow`，更新 `business-repo/frontend-contracts/openapi/{domain}_api.yaml` 和前端契约文件。
- 执行 `gofmt -w`、聚焦测试或 `go test ./...`。

## 输出要求

- 直接列出需要修改/新增的文件。
- 影响前端时必须列出前端契约复制清单。
- 不引入新框架，不重构无关历史代码。
