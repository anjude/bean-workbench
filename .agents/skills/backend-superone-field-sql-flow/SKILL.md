---
name: backend-superone-field-sql-flow
description: 当用户要为 backend-superone 设计字段、生成 DDL/DML SQL、更新 GORM 表模型或补充字段 comment 时使用；基于当前项目字段习惯输出 SQL 文件。
metadata:
  short-description: backend-superone 字段 SQL
---

# backend-superone 字段 SQL

本 skill 自包含，不依赖仓库内知识库目录。字段细则优先读取本 skill 目录内的 `references/field-design-norms.md`；如果该文件不可用，直接使用本文档内置规范。

## 字段规范

- 主键：`id`。
- 时间字段：沿用当前项目习惯，优先 `create_time`、`update_time`。
- GORM tag：`gorm:"column:{field};...;comment:'...'"`，自动时间使用 `autoCreateTime` / `autoUpdateTime`。
- SQL 新增字段必须带 `COMMENT`。
- 状态/枚举字段在 SQL comment 中写清取值含义。
- 金额/费率不用 float。

## 输出

- 用户只要 SQL 时，直接输出 DDL/DML。
- 用户要落文件时，先查项目是否已有 SQL/migration 目录；没有则建议合适路径。
- 用户要同步代码时，同时更新 `internal/model/*_tab.go` 里的 GORM struct。
- 用户要连接 test/live 库、执行 DDL/DML 或使用迁移脚本时，配合 `backend-superone-db-change-flow`。
- 如果字段会进入 API 请求/响应、前端展示、前端筛选或枚举判断，配合 `backend-frontend-contract-flow` 同步 YAML 和前端契约。
