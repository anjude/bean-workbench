# Topic 记录嵌套（log 的 log）· 方案文档

- 任务目录：`task/261002_topic-log-nesting/`
- 日期：2026-10-02
- 归属：business-repo/backend-superone（后端 + 迁移）+ frontend-contracts（契约）

## 背景

`topic`（主题）→ `topic_log`（主题记录）当前是两层、且 `topic_log` 是**平铺**的：一个 topic 下挂一堆 log，log 之间没有父子关系（`GetTopicLogList` 按 `topic_type + topic_id` 一把拉平，无 parent 字段）。

需求：在某一条 log（一件事/事件）下面持续挂"跟进记录"（log 的 log），形成"事件 → 跟进"的层级。

## 方案选型结论

采用 **单表自引用 `parent_log_id`**（Option A），理由：

- "跟进一条事"的记录与"记一件事"的记录在业务上是一类东西（都是某 topic 下、带内容、带时间的条目），区别只在"挂在谁下面"。用关系（`parent_log_id`）而非新实体表达最贴合模型。
- 兼容性成本最低：纯加列，旧数据自动全为根（parent_log_id=0），零数据迁移。
- 扩展性好：支持任意层级（UI 先只渲染两层）。

明确**不采用**的方案：

- 新建子表（`topic_log_track_tab` 等）：代码量翻倍（新 model/repo/use_case/dto/路由/迁移），且把"跟进"写死成一层固定 schema。
- topic 顶层加层级（Topic→SubTopic→Log）：错误维度，会牵动 topic 模型与所有权限/查询，blast radius 最大。
- `log_level` 整数档位：混淆"深度"与"分类"，改用关系字段。
- `root_log_id` 冗余列：本需求只要一层、点开取子，用不上，按"不留缝"原则不加（将来要多层级整线程再考虑）。

## 接口设计（不加新接口）

复用现有 `POST /topic/log/list`，仅新增可选字段 `parent_log_id`：

- **不传 / 传 0** → `WHERE parent_log_id = 0` → 返回根节点（列表视图，分页只数根）。
- **传 X** → `WHERE parent_log_id = X` → 返回 X 的子记录（点击展开，分页复用）。

每次调用都是"纯根"或"纯某父的子"，不会混，分页数量始终对齐。前端：列表视图不传 `parent_log_id`；点击某条 log 时带 `parent_log_id=该log.id` 再调同一接口。

## 数据模型变更

`internal/model/topic_log_tab.go` 增加：

```go
ParentLogID int64 `gorm:"column:parent_log_id;not null;default:0;index:idx_parent_log" json:"parent_log_id"` // 父记录ID，0表示根记录
```

## 后端改动清单

| 层 | 文件 | 改动 |
| --- | --- | --- |
| model | `internal/model/topic_log_tab.go` | 加 `ParentLogID` 字段 + 索引 |
| entity | `internal/domain/topic/topic_entity/topic_entity.go` | `TopicLog` 加字段；`NewTopicLog` 加 `parentLogID` 参数；`ToTab`/`FromTab` 透传 |
| dto | `internal/domain/topic/topic_dto/topic_dto.go` | `GetTopicLogListReq`/`CreateTopicLogReq` 加 `ParentLogID`；`TopicLogListItem`/`TopicLogDetailResp`/`CreateTopicLogResp` 返回 `parent_log_id` |
| factory | `internal/domain/topic/topic_factory/topic_factory.go` | 4 处响应/实体构造透传 `ParentLogID` |
| repo | `internal/repo/topic_repo.go` | `GetTopicLogListByIDs` 加 `parentLogID` 参数，`WHERE parent_log_id = ?`（始终生效） |
| service | `internal/domain/topic/topic_service/topic_service.go` | `GetTopicLogList` 透传 `req.ParentLogID`；`CreateTopicLog` 透传 `req.ParentLogID` |
| 其他调用点 | `internal/domain/user/user_service/user_service.go` | `NewTopicLog` 末尾补 `0`（根记录） |

## 数据库迁移（共享测试库）

`scripts/migration/sql/20261002_add_topic_log_parent.sql`：

```sql
ALTER TABLE topic_log_tab ADD COLUMN parent_log_id BIGINT NOT NULL DEFAULT 0 COMMENT '父记录ID...';
CREATE INDEX idx_topic_log_parent ON topic_log_tab (parent_log_id);
```

执行：`go run ./scripts/migration -action=exec-sql -sql-file=scripts/migration/sql/20261002_add_topic_log_parent.sql -env=test`
（共享测试库，DDL 需用户"继续"逐项授权）

## 契约维护（frontend-contracts）

- `openapi/topic_api.yaml`：`GetTopicLogListReq` / `CreateTopicLogReq` 增加 `parent_log_id`；list/detail/create 响应示例补充 `parent_log_id`。
- `types/topic.ts`：`GetTopicLogListReq` / `CreateTopicLogReq` 加 `parentLogId?`；`TopicLogListItem` / `TopicLogDetailView` / `CreateTopicLogResp` 加 `parentLogId`。
- `apis/topic.ts` 无需改动（仅引用类型）。

## 验证

- `go build ./...` / `go vet ./...` / `gofmt -l` 通过（仅本次改动文件）。
- 列表不传 `parent_log_id` 仅返根；传 `parent_log_id=X` 仅返 X 的子；分页 `total` 只数当前层级。
- DDL 在测试库成功执行，旧 log 的 `parent_log_id` 全为 0。
- dev-flow-0301 收口。

## 数据库执行记录

### Live 环境（2026-10-06）

- 目标库：`weiyi_superone_db`（live）。
- 目标表：`topic_log_tab`。
- 执行命令：`go run ./scripts/migration -action=exec-sql -sql-file=scripts/migration/sql/20261002_add_topic_log_parent.sql -env=live`。
- 执行结果：两条 DDL 均成功；新增 `parent_log_id BIGINT NOT NULL DEFAULT 0` 字段及 `idx_topic_log_parent` 索引。
- 只读验证：查询 `information_schema.columns` 确认字段类型为 `bigint`、不可空、默认值 `0`、comment 正确；查询 `information_schema.statistics` 确认索引指向 `parent_log_id`。
- 历史数据验证：`SELECT COUNT(*) FROM topic_log_tab WHERE parent_log_id <> 0` 返回 `0`，现有记录均为根记录。
