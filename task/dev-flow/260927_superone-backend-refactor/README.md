# Superone 后端重构（下线老功能）

## 背景

Superone 后端（`business-repo/backend-superone`）长期累积了一批不再使用的老功能，准备做一次重构把它们下掉，降低维护面。

重构前已留好基线快照：

- **Tag:** `release-260927` —— 指向 `release` 分支 HEAD `e72d116`（边界功能已落地，工作树干净）
- **分支:** `version/release-260927` —— 从该 commit 切出，作为重构起点分支，已推远程并设上游跟踪

回滚随时 `git checkout release-260927`。

## 目标

- 识别并下掉不再使用的老功能模块 / 接口 / 字段。
- 重构后保持 `release` 分支可正常构建、可部署。
- 不引入新业务，只做减法与必要的清理。

## 下线范围（已确认）

`app/api_service/api_service_v1.go` 中 4 组路由确认下线：

| 路由组 | 函数 | 原标注 |
| --- | --- | --- |
| `/flow` | `initFlowApi` | `// deprecated` |
| `/link` | `initLinkApi` | `// deprecated` |
| `/schedule` | `initScheduleApi` | `// deprecated` |
| `/stock` | `initStockApi` | 无标注（用户确认整文件下线） |

## 依赖追踪结论（关键发现）

从路由入口反向追了一圈，确定清理波及路由 → UseCase → Domain → Repo → Store → Model → 迁移 → 前端契约共 11 层。关键纠缠点：

1. **link 不是独立域** —— 它全寄生在 `internal/domain/v1/flow/`（service/dto/factory/entity 都在 flow 里）。删 flow 即删 link，不用单独找。
2. **`play_score` 定时任务真依赖 flow** —— 用 `IFlowRepo` 给 info 打分。删 flow 必须连它一起拔（接线在 `cron_job/wire.go`、`task_service.go`、`task_service_test.go`）。
3. **`schedule` 被周打卡订阅处理器真依赖** —— `message_subscribe/subscribe_processor/weekly_checkin_processor.go` 调用 `IScheduleRepo.GetScheduleUserInfo`。删 schedule 需连带下线该处理器，或先把取数改走 `user_repo`。**需豆哥定。**
4. **Store 共享层把 link 焊死了** —— `define.go` 的 `IGlobalStore`、`db_store.go`、`cache_store.go` 都有 `GetLinkById`/`LinkCache`，删 link 要顺势清理。
5. **两处死字段** —— `user_service.go` 和 `db_store.go` 里的 `flowRepo` 都只声明没调用，删 flow 时顺手去掉。
6. **迁移工具早已排除这些表** —— `scripts/migration/config.go` 的 `tablesToCreate` 里 flow/link/schedule 的 `model.*` 早已注释掉；但 **`stock` 仍在 `userDataTables`（第 23 行）活跃建表**，删 stock 代码前得先从 config.go 移除该行。
7. **前端契约只有 stock 有引用** —— flow/link/schedule 在前端契约里已无痕迹；stock 在 `frontend-contracts` 有 `stock.ts`/`stock_api.yaml`/`types/api/stock.ts`/`types/enums/stock.ts` 及两处 index export。

## 清理清单（按层）

### 1. 路由层
- `app/api_service/api_service_v1.go`：删除 `initFlowApi` / `initLinkApi` / `initScheduleApi` / `initStockApi` 四个函数
- `app/api_service/api_service.go`：
  - `InitRouters` 删除 4 行调用（53-56）
  - `ApiGroup` 删除 4 字段：`FlowUseCase` / `StockUseCase` / `LinkUserCase` / `ScheduleUseCase`
  - 清理 import：`stock_dto`、`flow_dto`(dto2)、`schedule_dto`(dto4)

### 2. UseCase 层（整文件删）
- `use_case/flow_use_case.go`、`stock_use_case.go`、`schedule_use_case.go`、`link_use_case.go`
- `use_case/wire.go`：删 `NewFlowApiUseCase` / `NewStockUseCase` / `NewScheduleUseCase` / `NewLinkApiUseCase` 四个 provider + 对应 `wire.Bind`
- `use_case/wire_gen.go`：删对应生成代码

### 3. Domain 层（整目录删）
- `internal/domain/v1/flow/`（link 寄生于此，一并删）
- `internal/domain/v1/schedule/`
- `internal/domain/stock/`

### 4. Repo 层
- `internal/repo/flow_repo.go`、`comment_repo.go`、`link_repo.go`、`schedule_repo.go`、`stock_repo.go`
- `internal/repo/wire.go`：删 `NewFlowRepo` / `NewLinkRepo` / `NewScheduleRepo` / `NewStockRepo`
- `internal/repo/wire_gen.go`：删对应生成代码

### 5. Store 共享层（link 焊点）
- `internal/store/define.go`：`IGlobalStore` 删 `GetLinkById`，删 `flow_entity` import
- `internal/store/db_store.go`：删 `linkRepo` 字段 + 初始化 + `GetLinkById` 方法；删 `flowRepo` 死字段（声明未用）+ 初始化；删 `flow_entity` / `link_repo` import
- `internal/store/cache_store.go`：删 `LinkCache` 字段 + 初始化 + `GetLinkById`；删 `flow_entity` import
- `internal/store/cache_store/link_cache.go`：整文件删

### 6. 定时任务（flow 下游消费者）
- `app/task_service/cron_job/play_score/` 整目录删
- `app/task_service/cron_job/wire.go`：删 `NewPlayScoreJob` + `wire.Bind(CronJob, *PlayScoreJob)`
- `app/task_service/cron_job/wire_gen.go`：删对应生成代码
- `app/task_service/task_service.go`：删 `playScore` 字段 + 初始化
- `app/task_service/task_service_test.go`：删 `play_score` 引用

### 7. 订阅处理器（schedule 下游）—— ⚠️ 决策点
- `internal/domain/message_subscribe/subscribe_processor/weekly_checkin_processor.go`：整文件删（用了 `IScheduleRepo.GetScheduleUserInfo`）
- `subscribe_processor.go`：`NewSubscribeProcessors` 删 `weeklyCheckinProcessor` 两处（20、23 行）
- 连带孤儿：`model/weekly_checkin_tab.go`、`model/schedule_user_info_tab.go`
- **决策**：周打卡订阅功能是否一起下线？是 → 全删；否 → 需把 `GetScheduleUserInfo` 改从 `user_repo` 取数后，再删 schedule 域

### 8. Model 层（孤儿表结构，删前逐个确认引用）
可被删（仅被上述功能引用）：
- `model/info_tab.go` / `info_draft_tab.go` / `info_like_tab.go`
- `model/comment_tab.go`
- `model/link_tab.go`
- `model/schedule_plan_tab.go` / `schedule_reward_tab.go` / `schedule_reward_history_tab.go`
- `model/stock_tab.go` —— ⚠️ `config.go:23` 的 `userDataTables` 仍在建此表，删前先从 config.go 移除该行
- `model/checklist_tab.go`（legacy flow checklist；**注意 `checklist_v2_tab.go` 是活跃的，别误删**）
- `model/subscribe_tab.go` / `question_record_tab.go` / `weekly_checkin_tab.go` / `schedule_user_info_tab.go`

**不可删**（虽在 `showAvailableModels` 显示列表里，但被 active 路由引用）：
- `model/system_tab.go`（common `/system/get`、`/system/update`）
- `model/csdn_config_tab.go`（common `/csdn/*`）
- `model/data_hot_tab.go`（common `/hot_data/get`）

### 9. 迁移工具 config.go
- flow / link / schedule 的 `model.*` 已在 `tablesToCreate` 注释中，无需改
- stock：从 `userDataTables` 删除 `&model.StockTab{}`（第 23 行）
- `getOpenidFieldMap` 里的 `"stock_tab"` 映射（约第 68 行）一并删除

### 10. 前端契约（仅 stock 有引用）
- `frontend-contracts/src/apis/stock.ts`
- `frontend-contracts/openapi/stock_api.yaml`
- `frontend-contracts/src/types/api/stock.ts`
- `frontend-contracts/src/types/enums/stock.ts`（及 `index.ts` 里的 export）
- `frontend-contracts/src/apis/index.ts`：删 `stockApiPaths` export
- `frontend-contracts/src/types/api/index.ts`：删 `StockApi` export
- flow / link / schedule 在前端契约里已无引用（早清过），无需动

### 11. 死字段顺手清
- `internal/domain/user/user_service/user_service.go`：删 `flowRepo` 字段（声明未用）
- `internal/store/db_store.go`：删 `flowRepo` 字段（声明未用）

## 待决策点

1. `stock` 未标 `deprecated`，但用户已确认整文件下线，按此处理。
2. **周打卡订阅**：删 `schedule` 域需连带下线 `weekly_checkin_processor.go`，或先把 `GetScheduleUserInfo` 改走 `user_repo`。需豆哥定。
3. 测试库共享，`DROP` 旧表需逐项授权（沿用旧约定）。

## 验证

- `go build ./...` 全量编译通过（删完用 IDE 或 `make` 验证）
- `make check`（workbench 脚本）
- 确认 `InitRouters` 不再注册这 4 组路由
- 数据库：这些表已在迁移工具注释里排除，不自动建；如要彻底清数据，单独写 DROP 迁移（需授权，测试库共享）

## 流程

按工作台约定，业务仓开发需求走 `dev-flow-0000-plan-flow` 出方案（本文件即方案），确认后再按端派发：

1. 范围确认（已完成）→ 回填本文件「下线范围」。
2. 无争议部分（flow / link / stock）走 `dev-flow-0101`→`0102`→`0103`→`0104` 执行；schedule 待决策点 2 确认后同走。
3. 前端契约清理随 stock 一并走前端 skill（`dev-flow-0201` 起）。
4. 收口走 `dev-flow-0301-verify-flow`。

## 验收

- 下线清单逐项确认，无遗漏无误删。
- `make check` 及后端 gofmt/wire/test/lint 通过。
- 重构后 `release` 分支可构建可部署。
