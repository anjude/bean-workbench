---
name: dev-flow-0101-domain-flow
description: 当要在 backend-superone 新增业务 domain、entity、model、factory、repo、service、store/cache 逻辑，或要设计字段、产出 DDL/DML SQL、更新 GORM 表模型、补充字段 comment 时使用。
metadata:
  short-description: backend-superone 领域与表设计
---

# backend-superone 领域与表设计

阶段 01 后端开发，执行顺序第 1 步。项目上下文见 `dev-flow-tools-repo`。

本 skill 只做**设计态**：领域分层代码 + 字段与 SQL 产出，**不连接数据库**。执行归 `dev-flow-0102-db-change-flow`，只读排查归 `dev-flow-tools-db-query`。

字段细则优先读取本 skill 目录内的 `references/field-design-norms.md`；不可用时使用本文档内置规范。

## 一、领域层

### 标准目录

```text
internal/domain/{domain}/
  {domain}_dto/
  {domain}_entity/
  {domain}_factory/
  {domain}_service/
internal/model/
internal/repo/
use_case/*.go
```

表模型在 `internal/model/*_tab.go`，Repo 优先在 `internal/repo`，Service 在 `internal/domain/{domain}/{domain}_service`，错误包 `internal/infrastructure/ecode`，BizContext `internal/infrastructure/bizctx`。

### 流程

1. 先定义 entity，表达业务含义。
2. 在 `internal/model/*_tab.go` 定义 GORM 表模型，提供 `TableName()`，公共基础字段复用 `model.BaseTab`。
3. 在 factory 中实现 model 到 entity 的转换；entity 需要落库时提供 `ToModel()`。
4. 在 repo 中定义 `I{Domain}Repo` 和 `{Domain}Repo`，使用 `bizctx` DB helper 或 GORM。
5. 在 service 中定义 `I{Domain}Service` 和 `{Domain}Service`，业务校验、事务和错误处理放在这里。
6. 如需 API，交给 `dev-flow-0103-api-flow` 做 DTO、UseCase、路由和 Wire 注入。
7. 如新增或修改前端可见枚举、状态、结构体字段，交给 `dev-flow-0104-contract-flow` 输出前端契约。
8. 需要落库时，把 SQL 交给 `dev-flow-0102-db-change-flow` 执行。

### 分层约束

- 分层顺序 app → use_case → domain → repo → infrastructure，不跨层直接调用 app 或 middleware。
- Service 返回 `*ecode.BizError`。
- 不在 repo 中写业务判断，事务放 service。
- 影响前端的枚举和结构体变更必须同步 OpenAPI YAML 和协议仓 `business-repo/frontend-contracts`。

## 二、字段与 SQL 设计

### 字段规范

- 主键：`id bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID'`。
- 时间字段：`create_time`、`update_time`，GORM 使用 `autoCreateTime` / `autoUpdateTime`。
- GORM tag：`gorm:"column:{field};...;comment:'...'"`。
- SQL 新增字段必须带 `COMMENT`；状态/枚举字段在 comment 中写清取值含义。
- 用户维度字段沿用 `openid varchar(64)`，需要查询时加索引。
- 状态字段优先 `tinyint` 或已有 enum 类型，并在 comment 中列出枚举。
- 金额、比例、计数、时间戳、JSON、长文本按 `references/field-design-norms.md` 选择类型；金额/费率不用 float。
- 新增字段必须明确是否允许 `NULL`、默认值、历史数据回填 DML。
- 索引必须说明查询场景，避免无依据组合索引。

### 输出

- 用户只要 SQL 时，直接输出 DDL/DML，每个字段带 `COMMENT`，注释写清业务含义、默认值、历史数据处理和执行注意事项。
- 用户要落文件时，SQL 放 `scripts/migration/sql/YYYYMMDD_*.sql`。
- 用户要同步代码时，同时更新 `internal/model/*_tab.go` 里的 GORM struct。
- 用户要连库执行、用迁移脚本时，交 `dev-flow-0102-db-change-flow`；只查结构交 `dev-flow-tools-db-query`。
- 字段会进入 API 请求/响应、前端展示、前端筛选或枚举判断时，交 `dev-flow-0104-contract-flow` 同步 YAML 和前端契约。
- 新增 carbon 业务表时，记得把表名加进 `scripts/migration/exec_sql.go` 的 `carbonTables`，否则 `verify-carbon` 覆盖不到。
