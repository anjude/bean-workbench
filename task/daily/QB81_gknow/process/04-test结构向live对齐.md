# test 表结构向 live 对齐 · 过程记录

- 任务目录：`task/daily/QB81_gknow/`
- 时间：2026-11-09

## 判断依据

- `TopicLogListReq.TopicTypes` 是必填非空列表；`GetTopicLogListByIDs` 按 `topic_id IN (...)`、`topic_type IN (...)` 过滤。删除主题记录也同时过滤 `topic_id` 与 `topic_type`。
- test 和 live 对代表性列表 SQL 执行 `EXPLAIN` 后均使用 `idx_type_topic(topic_type, topic_id)`。test 预估扫描 10 行，live 预估 20 行，均为 `ref`，并有 `Using where; Using filesort`。
- 因请求必须包含类型，复合索引覆盖现有调用；test 的单列 `idx_topic_log_tab_topic_id` 对当前调用路径多余，按 live 结构移除。

## 执行与验证

- 按用户确认，以 live 为准在 test 库 `weiyi_superone_db_test` 执行 [20261109_align_test_schema_to_live.sql](../../../business-repo/backend-superone/scripts/migration/sql/20261109_align_test_schema_to_live.sql)。
- `recent_task_tab`：将 `deadline`、`top` 列顺序调整为与 live 一致。
- `system_tab`：添加 live 已有的 `idx_type(type)`。
- `topic_log_tab`：将 `topic_type` 列移到 live 顺序，并删除冗余的 `idx_topic_log_tab_topic_id(topic_id)`。
- 执行命令：`go run . -action=exec-sql -sql-file=sql/20261109_align_test_schema_to_live.sql -env=test`，3 条 ALTER 均执行成功。
- 回查 `information_schema.COLUMNS` 和 `information_schema.STATISTICS`：这三张表的列顺序、字段类型、NULL 属性、默认值、注释、字符集/排序规则及索引与 live 完全一致。
- 此次只变更 schema，没有执行数据 DML；未处理 test 独有的 `template_tab`。
