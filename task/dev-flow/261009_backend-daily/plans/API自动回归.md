# 后端 HTTP + DB 自动回归

## 目标

建立可重复执行的后端接口端到端回归入口。测试通过 HTTP 调用运行中的真实服务，再查询对应 test 数据库断言业务状态；不通过本地 handler、UseCase 或 Service 单测替代接口验证。

## 使用场景

- 本地服务默认监听 `localhost:80`，接口基址默认 `http://localhost`。
- 通过 `API_BASE_URL` 切换到已部署的 test 服务。
- 数据库连接默认读取 `ENV=TEST` 的项目配置；可用 `AUTOTEST_DB_*` 对应变量切换到与目标服务匹配的 test 库。数据库名必须以 `_test` 结尾。
- 使用一次性 `autotest-` OpenID 和 JWT。远程服务可用 `JWT_TOKEN` 覆盖本地生成的 token，并通过 `AUTOTEST_OPENID` 声明 token 对应的一次性测试身份。

## 当前范围

清单模块走完整 HTTP 链路：创建清单、详情和列表查询、创建执行记录、执行详情/列表/历史查询、更新完成状态、删除执行记录、删除清单；每个持久化阶段同时读取数据库核对身份、字段和记录数。清单标题、条目和执行总结含加密字段，数据库断言确认字段已加密，接口读回断言确认解密结果正确。

埋点模块覆盖缺少凭证、其他 App 凭证、未登记项目、混合事件逐条回执、未知 `actor_key` 被忽略且后端身份入库、重复事件保留首条。只清理本用例生成的事件 ID。

## 实施方案

- 在后端仓库根目录增加 `autotest/` Go 集成测试包。每个业务用例对应一个 `Test...` 方法，方法体通过公共 HTTP client 调接口并用标准 `testing.T` 断言响应与数据库；不在测试中直接调用 handler、UseCase 或 Service。复用项目现有 Go、MySQL driver、JWT 和测试配置，不增加依赖。
- `API_BASE_URL` 控制 HTTP 目标；`JWT_TOKEN` / `AUTOTEST_OPENID` 控制远端测试身份；`AUTOTEST_DB_ADDR`、`AUTOTEST_DB_USER`、`AUTOTEST_DB_PASSWORD`、`AUTOTEST_DB_NAME` 可显式指定目标对应的测试库。所有配置只从环境读取或合并测试配置，不打印 token、密码或接口响应正文。
- 自动生成带唯一标识的测试身份和业务 fixture。清单成功路径通过删除接口清理并断言数据库记录删除；埋点写入事件通过唯一事件 ID 清理；测试中途失败时也只回收本轮数据。
- Makefile 增加 `make test-api` 作为统一入口，设置专用 `RUN_API_AUTOTEST=1` 后执行 `go test ./autotest -count=1 -v`。普通 `go test ./...` 默认跳过这些外部集成测试。它不启动服务，便于分别连接本地 `localhost:80` 或远端 test URL。
- 后续模块按业务目录增加 HTTP 用例和 DB 断言，公共的目标 URL、身份、请求、数据库连接与安全校验复用 runner。

## 验收标准

- 目标 URL 可以通过环境变量在 `http://localhost` 与远程 test 服务之间切换。
- 数据库必须是 `_test` 库；缺少认证或目标库配置时安全失败，不回退到 live。
- 清单和执行记录用例通过真实 HTTP API 完成创建、查询、执行更新、删除，并通过数据库核对写入和清理结果。
- 日志不输出 JWT、数据库密码或业务响应数据。

## 风险与边界

- 远程 URL 与数据库连接必须指向同一 test 环境；配置不匹配时响应与库断言会分离。运行命令显式输出经脱敏的 API 主机和数据库名，运行者核对二者。
- 不提供任意用户 token 写业务数据的默认路径。外部 token 必须配套 `autotest-` 专用 OpenID。
- 服务启动与回归 runner 分开，避免测试程序意外启动后台任务或服务监听。

## 落地记录

- 新增 `autotest/` 集成测试包、清单模块和 `make test-api`。每个用例是独立 `Test...` 方法，通过 HTTP 请求和标准 Go 断言核对响应与数据库；没有使用本地 handler/UseCase/Service 替代 HTTP。普通 `go test ./...` 默认跳过，写操作强制 `_test` 库，失败清理限定本轮测试身份与 fixture。
- `API_BASE_URL=http://localhost:18081 make test-api` 通过，连接 `weiyi_superone_db_test`；清单创建、详情、列表、执行创建、详情/列表/历史、更新、执行删除、清单删除与执行记录级联删除等独立用例全部通过，数据库断言通过。自动生成的 JWT、OpenID 和数据库密码未输出。
- 将原 `app/api_service/api_analytics_integration_test.go` 的用例迁入 `autotest/analytics_test.go`，拆为独立 HTTP + DB `Test...` 方法；旧 `httptest` 集成入口已删除。当前 `make test-api` 的 analytics 与 checklist 用例全部通过，test 事件及业务 fixture 均清理。
- 按要求默认地址为 `http://localhost:80`。本机 80 端口已被一个现存 Go 进程占用，无法确认其服务归属，因此未停止或向它写入；本轮将真实服务运行在 18081 并用 `API_BASE_URL` 切换验证。远程 test URL 尚未执行。
- 服务启动时发现现有埋点 DTO 调用缺失的 `json_util.DecodeStrict`，补回严格 JSON 解码入口后真实服务成功启动。普通接口现有 `DecodeSingleJSON` 行为未改变。
