---
name: dev-flow-tools-db-query
description: 需要确认 backend-superone 的库表结构、索引、字段 comment、数据量或排查线上数据问题时使用；只读查询与结构验证，不执行任何写操作。
metadata:
  short-description: backend-superone 数据库只读排查
---

# backend-superone 数据库只读排查

工具 skill，不占阶段号。方案设计阶段定位库表、后端开发阶段验证 DDL 结果、整体验证阶段核对数据都会用到。

## 边界

本 skill 只做读。需要建表、改字段、改索引、回填 DML 时，一律转 `dev-flow-0102-db-change-flow`，不在此处越界。

判断标准：语句以 `SELECT`、`SHOW`、`DESC`、`EXPLAIN` 开头才属于本 skill；出现 `INSERT`、`UPDATE`、`DELETE`、`CREATE`、`ALTER`、`DROP`、`TRUNCATE` 立即停止，交给 `dev-flow-0102-db-change-flow`。

## 环境语义

- `test`：对应 nonlive 验证链路，目标库 `TEST_DB_NAME`。
- `live`：对应生产链路，目标库 `DB_NAME`。
- 环境指数据库执行环境，不等于 Git 分支名。用户说「发 nonlive」通常指 `test` 库，说「发 live」指 `live` 库。
- 连接参数在 `business-repo/backend-superone/scripts/migration/config.go`：`DB_USER`、`DB_PASSWORD`、`DB_HOST`、`DB_PORT`、`DB_NAME`、`TEST_DB_NAME`。

## 连接方式

优先用 mysql 客户端直连，只读最安全：

```bash
mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" "$TEST_DB_NAME" -e "SHOW CREATE TABLE <table>;"
```

没有 mysql 客户端时，可以用迁移脚本执行只读语句：

```bash
go run ./scripts/migration --% -action=exec-sql -sql-file=<只读查询.sql> -env=test
```

PowerShell 下加 `--%`，bash/zsh 下不加。走这条路径前必须逐条确认 SQL 文件里只有查询语句，没有分号后跟的写操作。

## 常用查询

| 目的 | 语句 |
| --- | --- |
| 表结构 | `SHOW CREATE TABLE <table>;` |
| 字段与 comment | `SHOW FULL COLUMNS FROM <table>;` |
| 索引 | `SHOW INDEX FROM <table>;` |
| 数据量 | `SELECT COUNT(*) FROM <table> [WHERE ...];` |
| 样例数据 | `SELECT * FROM <table> WHERE ... LIMIT 3;` |
| 查询计划 | `EXPLAIN SELECT ...;` |
| carbon 表批量校验 | `go run ./scripts/migration --% -action=verify-carbon -env=test` |

## 与代码的一致性核对

查完库表要回头对一遍 GORM 模型 `internal/model/*_tab.go`：

- `TableName()` 与实际表名一致。
- `gorm:"column:...;comment:'...'"` 与库里的字段名、comment 一致。
- 字段类型、是否允许 NULL、默认值与库表一致。
- JSON 序列化类型、`Scan/Value` 实现与字段类型匹配。

不一致时先判断谁该改：库结构是设计产物就改模型，模型是设计产物就交给 `dev-flow-0102-db-change-flow` 出 DDL，不要就地改库。

## 输出要求

- 写明目标环境、`TEST_DB_NAME` 或 `DB_NAME`、目标表。
- 附上执行的查询语句和结果结论。
- 只报事实，不顺手改数据。

## 禁止事项

- 不执行任何 DDL/DML。
- 不把数据库密码、连接串写入文档或最终回答。
- 不为了排查方便清空或重置业务数据；确需清空走 `dev-flow-0102-db-change-flow` 的 clear action 并显式授权。
- 不在 live 环境跑未经评估的大范围查询，避免拖慢生产库。
