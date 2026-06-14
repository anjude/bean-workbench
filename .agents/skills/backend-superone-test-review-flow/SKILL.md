---
name: backend-superone-test-review-flow
description: 当用户要检查 backend-superone 改动、补测试、运行 go test/make lint/gofmt/git diff --check 或做代码审查时使用。
metadata:
  short-description: backend-superone 测试审查
---

# backend-superone 测试与审查

本 skill 自包含，不依赖仓库内知识库目录。项目约定：路由在 `app/api_service/*.go`，UseCase 在 `use_case/*.go`，Service 返回 `*ecode.BizError`，表模型在 `internal/model/*_tab.go`。若涉及前端契约，最终应检查工作台协议仓 `business-repo/frontend-contracts` 是否同步。

## 验证顺序

1. `gofmt -w <changed-go-files>`
2. `wire ./...`（如果动了依赖注入）
3. 聚焦 `go test ./path/...`
4. 必要时 `go test ./...`
5. `make lint`
6. `git diff --check`

## Go test 性能注意

- backend-superone 在 Windows 环境下单包首次编译可能需要 15-30 秒；全仓或多个包并行跑容易超过 60/120 秒超时。
- 不要用并行工具同时跑多个 `go test` 包；优先串行执行，避免编译缓存和 CPU/IO 抢占导致误判。
- 命令 timeout 建议至少 180 秒。
- 只做编译检查时可用 `go test -run '^$' ./path`。
- 想跳过测试缓存但仍做编译时可用 `go test -count=0 ./path`。
- 如果一次超时但没有错误输出，先重复单包串行跑；warm cache 后通常会明显变快。

## 审查重点

- 是否符合 app/use_case/domain/repo/infrastructure 分层。
- Service 是否返回 `*ecode.BizError`，UseCase 是否透传。
- Gin 路由是否使用 `middleware.HandleRequest`。
- 请求 DTO 是否有 `form`、`json`、`binding` 标签。
- Repo 是否只做数据访问，事务是否放在 service。
- 新字段是否同步 `internal/model`、SQL comment、默认值和历史数据语义。
- 是否无关重构、无关格式化、无关依赖升级。
