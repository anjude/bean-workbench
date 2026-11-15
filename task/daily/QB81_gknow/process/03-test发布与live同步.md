# test 发布与 live 同步 · 过程记录

- 任务目录：`task/daily/QB81_gknow/`
- 时间：2026-11-09

## test 发布

按用户要求，通过 test 管理 API 将当前全部测试与副本设为发布状态；更新使用原配置版本作并发检查，更新后逐项回读确认：

| 内容 | test_key / story_key | 发布后版本 |
| --- | --- | ---: |
| 测试 | `stock-methods` | 8 |
| 测试 | `goose-bti` | 7 |
| 测试 | `finance-personality` | 9 |
| 副本 | `big-tech-life` | 4 |
| 副本 | `life-windfall` | 6 |
| 副本 | `love-speedrun` | 5 |
| 副本 | `finance-market-ai-leek` | 4 |
| 副本 | `finance-market-structural` | 4 |
| 副本 | `finance-market-leverage` | 4 |
| 副本 | `finance-market-internet` | 4 |
| 副本 | `finance-market-opening` | 4 |

回读结果：测试 3/3 的 `test_status=1`，副本 8/8 的 `status=1`。

## live 建表与同步

- 用户确认后，在 live schema `weiyi_superone_db` 执行后端迁移文件 [gknow_story.sql](../../../business-repo/backend-superone/scripts/migration/sql/gknow_story.sql)，成功创建 `gknow_story_tab`。该 DDL 只新增空表。
- `gknow_assessment_tab` 原已存在且为空；副本表新建后也为空。使用后端迁移包配置的 test/live 数据库连接，在同一 live 事务内从 test 两表复制全部记录；拒绝覆盖非空 live 表，插入前核实 test 正好有 3 条测试、8 条副本且全部已发布。
- 回读 live 并与 test 对照：测试 3 条、副本 8 条；所有状态为已发布；key、类型、标题、简介、封面、排序、版本、创建/更新者及配置内容一致。副本 `content_json` 原文一致，测试配置按模型解析后字段一致。
- API 检查：当前本地管理员 JWT 可用于 test，但 live API 返回签名无效；本次同步通过已授权的后端数据库迁移连接完成，没有把 test JWT 用作 live 身份凭证。
- 执行命令：`go run . -action=exec-sql -sql-file=sql/gknow_story.sql -env=live`（工作目录 `backend-superone/scripts/migration`）。数据复制程序为临时核验脚本，执行成功后已删除。
- 结果：live 表结构创建成功，3 条测试与 8 条副本已同步并回读核验，均保持发布状态。本次未部署后端或小程序代码。
