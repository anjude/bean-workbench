---
name: backend-superone-wire-flow
description: 当用户在 backend-superone 新增 service、repo、use_case、router 后需要配置 Google Wire、修复依赖注入或运行 wire ./... 时使用。
metadata:
  short-description: backend-superone Wire 注入
---

# backend-superone Wire 注入

本 skill 自包含，不依赖仓库内知识库目录。项目约定：API 层 Wire 在 `app/api_service/wire.go`，UseCase 层 Wire 在 `use_case/wire.go`，Service 层 Wire 通常在 `internal/domain/{domain}/{domain}_service/wire.go`。

## 规则

- `wire.go` 使用 `//go:build wireinject` 和 `// +build wireinject`。
- 使用 `wire.Struct(new(Type), "*")` 注入结构体字段。
- 接口绑定使用 `wire.Bind(new(IInterface), new(*Impl))`。
- API 层注入在 `app/api_service/wire.go`。
- UseCase 层 ProviderSet 在 `use_case/wire.go`。
- Service 层 Wire 文件通常在 `internal/domain/{domain}/{domain}_service/wire.go`。
- Repo 层优先沿用 `internal/repo` 的已有注入方式。

## 流程

1. 新增 constructor 或 ProviderSet。
2. 更新调用链上层的 `wire.Build`。
3. 运行 `wire ./...`。
4. 如果失败，按报错修复缺失 provider、接口绑定或循环依赖。
