---
name: dev-flow-0102-db-change-flow
description: 当 backend-superone 需求涉及连接 test/live 数据库、生成或执行 DDL/DML、使用 scripts/migration、验证表结构或数据变更时使用。
metadata:
  short-description: backend-superone 数据库变更
---

# backend-superone 数据库变更

阶段 01 后端开发，执行顺序第 2 步。

本 skill 只处理数据库写操作与迁移执行。职责边界：

- 字段设计和 SQL 产出属于 `dev-flow-0101-domain-flow`，本 skill 不重新设计字段。
- 只读排查、结构核对、数据验证属于 `dev-flow-tools-db-query`，本 skill 不负责查询。
- 分支推进属于 `dev-flow-tools-repo`。
- 项目目录与常用命令见 `dev-flow-tools-repo`。

字段细则见 `dev-flow-0101-domain-flow` 目录内的 `references/field-design-norms.md`；不可用时使用本文档内置规范。

## 环境语义

数据库 `test` / `live` 指执行环境，不等同于 Git 分支名：`test` 对应 nonlive 验证链路，`live` 对应生产链路。不要把推进分支等同于执行该环境写操作。

## 迁移脚本

- 迁移脚本在 `scripts/migration`，SQL 文件在 `scripts/migration/sql/`。
- 表模型在 `internal/model/*_tab.go`，公共基础字段在 `internal/model/base_tab.go`，包含 `id`、`create_time`、`update_time`。
- `scripts/migration/config.go` 包含 `DB_USER`、`DB_PASSWORD`、`DB_HOST`、`DB_PORT`、`DB_NAME`、`TEST_DB_NAME` 以及 `tablesToCreate`。
- `scripts/migration/main.go` 默认环境必须是 `test`，避免参数解析异常时误执行 live；执行 live 必须显式传 `-env=live`，PowerShell 下优先带 `--%`。
- 支持的 action：
  - 默认创建表：`go run ./scripts/migration --% -env=<test|live>`
  - 清空用户数据：`go run ./scripts/migration -action=clear -openid=<openid> -env=<test|live>`
  - 数据迁移：`go run ./scripts/migration -action=migrate -openid=<openid> -env=<test|live>`
  - 导入地址：`go run ./scripts/migration -action=import-address -env=<test|live>`
  - 导入 Spot：`go run ./scripts/migration -action=import-spot -env=<test|live>`
  - 执行 SQL 文件：`go run ./scripts/migration --% -action=exec-sql -sql-file=<path.sql> -env=<test|live>`（PowerShell 推荐带 `--%`）
  - 验证 Carbon 表：`go run ./scripts/migration --% -action=verify-carbon -env=<test|live>`

## 模式

### 只生成 SQL

- 输出 DDL / DML 文件即可，不连接数据库。
- SQL 中每个字段必须有 `COMMENT`。
- SQL 注释写清楚业务含义、默认值、历史数据处理和执行注意事项。

### 准备迁移脚本

- 新表优先补 `internal/model/*_tab.go`。
- 将目标表加入 `scripts/migration/config.go` 的 `tablesToCreate` 或更小范围的表集合。
- 不把无关表加入本次迁移集合。
- 如需求只需要 SQL 文件，不强行使用 AutoMigrate。

### 执行 test/live

执行前确认执行模式：

- 方案确认模式（`dev-flow-0000-plan-flow` 的默认模式）：必须等用户确认后再执行。
- 全自动模式（`dev-flow-0000-plan-flow` 的显式模式）：本次改动涉及新增表、改字段、改索引或 DML 时，默认执行 `test` 环境并验证；用户已明确要求 `live` 时才执行 live。
- 未明确目标环境时，默认只生成 SQL，不执行数据库写操作。
- 用户说“发 nonlive / 配合 test 分支验证”时，优先理解为执行 `test` 环境数据库变更。
- 用户说“发 live / 配合 release 分支上线”时，优先理解为执行 `live` 环境数据库变更。
- 如果用户只说“合并 test/release”但没明确要求执行数据库写操作，不自动把分支推进等同于 live DDL/DML；数据库执行环境仍需单独判断。

PowerShell 执行 SQL 文件必须优先使用 `--%`：

```bash
go run ./scripts/migration --% -action=exec-sql -sql-file=scripts/migration/sql/xxx.sql -env=test
```

如果历史脚本或终端环境把 `.sql` 扩展名吞掉，迁移脚本应对无扩展名路径自动尝试追加 `.sql` 后读取。

执行时记录：

1. 目标环境：`test` 或 `live`。
   - 可附带说明其对应 `nonlive` 或 `live` 发布链路，避免和 Git 分支语义混淆。
2. 目标库：`TEST_DB_NAME` 或 `DB_NAME`。
3. 目标表和字段。
4. 执行命令。
5. 执行结果。
6. 验证 SQL 和验证结论。

## 字段和 SQL 规范

- 主键：`id bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID'`。
- 创建时间：`create_time int unsigned NOT NULL DEFAULT 0 COMMENT '创建时间'`，GORM 使用 `autoCreateTime`。
- 更新时间：`update_time int unsigned NOT NULL DEFAULT 0 COMMENT '更新时间'`，GORM 使用 `autoUpdateTime`。
- 用户维度字段沿用 `openid varchar(64)`，需要查询时加索引。
- 状态字段优先 `tinyint` 或已有 enum 类型，并在 comment 中列出枚举。
- 金额、比例、计数、时间戳、JSON、长文本按 `field-design-norms.md` 选择类型。
- 新增字段必须明确是否允许 `NULL`、默认值、历史数据回填 DML。
- 索引必须说明查询场景，避免无依据组合索引。

## 验证

执行完成必须验证，具体语句和只读连接方式见 `dev-flow-tools-db-query`：

- 表结构：`SHOW FULL COLUMNS FROM <table>;`
- 索引：`SHOW INDEX FROM <table>;`
- 行数或回填：`SELECT COUNT(*) ...;`
- 关键样例：按需求查询 1 到 3 条样例数据。
- GORM 模型：确认 `TableName()`、`gorm:"column:...;comment:'...'"`、JSON 序列化类型和 `Scan/Value` 实现。

没有验证结论不算执行完成。

## 禁止事项

- 不在没有用户授权或全自动明确要求时执行 live DDL/DML。
- 不把数据库密码、Token、连接串写入新文档或最终回答。
- 不为了迁移方便修改无关表模型。
- 不用 AutoMigrate 替代需要精确评审的复杂 DDL；复杂变更必须输出明确 SQL。
