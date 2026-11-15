# AI 数据表命名方案

## 需求与范围

1. **统一数据表前缀。** 为 Superone 提供的 AI 内容同步数据使用统一前缀，便于未来通过 MCP、uTools 等客户端管理个人、公开和组织数据。
2. **调整现有 Skill 表。** 第一版使用 `user_skill_tab`，测试环境已有数据。表名变更需要保留现有记录，并同步服务端模型和迁移引用。
3. **预留后续命名空间。** 组织、共享等能力未来再按该前缀命名；具体表和功能以届时需求设计为准。

## 已确认的命名

采用前缀 `agent_`，现有表改为 `agent_user_skill_tab`。未来如新增组织、成员、邀请等表，可按 `agent_organization_tab`、`agent_organization_member_tab`、`agent_organization_invite_tab` 命名。这些是命名示例，不代表当前需要创建这些表。

`agent_` 描述 Agent 跨客户端同步内容，保留现有 `_tab` 后缀。

## 现有实现与改动范围

- `backend-superone/internal/model/user_skill_tab.go` 的 `TableName()` 返回现有表名；Repository 经 GORM 模型访问该表。
- `backend-superone/scripts/migration/sql/20261107_user_skill.sql` 定义首版建表，`scripts/migration/config.go` 注册模型。
- `backend-superone/app/api_service/api_skill_test.go` 存在直接引用的表名，需要随实现同步。
- test 环境已创建旧表并保存过 Skill，迁移需要核对目标表是否存在，采用重命名保留数据；不能只改模型后新建空表。原有迁移历史及其适用于新环境的方式需先核查，避免重复建表。

## 验收与状态

模型和直接引用已改为新表名，新增独立重命名 SQL。原建表 SQL 保留历史语义，新环境按原建表、重命名的顺序执行。执行前核对旧表存在、新表不存在，并在停写期间重命名后核对结构、记录数量和文件摘要，再切换代码。test 与 live 的数据库操作按环境分别授权；数据库迁移与真实 MCP 客户端验证尚未执行。
