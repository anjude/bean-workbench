# 字段设计与 SQL 输出规范

## 字段设计

- 字段名使用当前项目已有命名风格，通常为 snake_case。
- 字段必须有明确业务含义，避免 `flag`、`type`、`status` 这类无上下文命名。
- 新增字段需要说明默认值、是否允许 NULL、历史数据语义和是否需要 DML 初始化。
- 新表必须优先设计基础字段：`id`、`create_time`、`modify_time`。
- 金额、费率、数量、重量等字段必须选择精确类型；金额和费率不要使用 float。
- 状态/枚举字段需要写清楚取值含义，必要时在 comment 里体现。
- 时间字段跟随当前表风格，例如 int timestamp、datetime 或 timestamp。
- JSON/text 扩展字段只适合低频、非索引、非核心业务查询的数据。
- 需要查询、筛选、排序、关联或导出的核心字段应设计成明确列。

## 基础字段规范

### 主键字段

- 默认使用 `id` 作为主键字段名。
- MySQL 自增主键建议使用 `bigint unsigned NOT NULL AUTO_INCREMENT`。
- `id` 必须是 `PRIMARY KEY`。
- `id` comment 建议为 `primary key` 或当前项目已有表达。
- 不要用业务编号替代自增主键；业务唯一标识单独建字段和唯一索引。

示例：

```sql
`id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT 'primary key',
PRIMARY KEY (`id`)
```

### 创建时间字段

- 默认字段名使用 `create_time`。
- 用于记录行创建时间，不承载业务发生时间。
- 如果当前项目没有明确时间类型偏好，MySQL 建议使用 `datetime NOT NULL DEFAULT CURRENT_TIMESTAMP`。
- 如果项目使用 Unix timestamp，则跟随项目现有 int/bigint 风格。
- comment 建议为 `create time`。

示例：

```sql
`create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'create time'
```

### 修改时间字段

- backend-superone 默认字段名使用 `update_time`；其他项目如已有 `modify_time` 再跟随项目现有命名。
- 用于记录行最后修改时间。
- 如果当前项目没有明确时间类型偏好，MySQL 建议使用 `datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP`。
- 如果项目使用 Unix timestamp，则跟随项目现有 int/bigint 风格，并由代码维护更新时间。
- comment 建议为 `update time` 或当前项目已有中文表达。

示例：

```sql
`update_time` int unsigned NOT NULL DEFAULT 0 COMMENT 'update time'
```

### 业务编号字段

- 业务编号不要命名为 `id`。
- 常见命名：`order_no`、`task_no`、`biz_id`、`biz_no`、`request_id`。
- 如果业务编号需要幂等或去重，必须配唯一索引。
- 字符串业务编号默认 `varchar(64)` 或按已有项目长度约定。

### 状态字段

- 状态字段命名应体现业务对象，例如 `order_status`、`task_status`、`process_status`。
- 避免单独使用 `status`，除非当前表上下文非常明确。
- 类型通常为 `tinyint unsigned` 或 `int unsigned`，按现有项目风格选择。
- 默认值必须代表明确状态，例如 `0 unknown`、`0 init` 或 `1 active`。
- comment 中写清主要枚举值。

示例：

```sql
`task_status` tinyint unsigned NOT NULL DEFAULT 0 COMMENT 'task status: 0 init, 1 processing, 2 success, 3 failed'
```

### 软删除字段

- 如果项目使用软删除，优先跟随已有字段名，例如 `deleted_at`、`is_deleted`、`delete_time`。
- 新项目默认可使用 `is_deleted tinyint unsigned NOT NULL DEFAULT 0`。
- `is_deleted` 取值建议：`0 not deleted, 1 deleted`。
- 软删除字段通常需要进入常用查询条件；是否建组合索引取决于查询形态。

### 操作人字段

- 如果需要审计，使用 `created_by`、`modified_by` 或项目已有命名。
- 用户标识类型跟随系统用户 ID 类型；字符串账号通常用 `varchar(128)`。
- 不要把操作人信息塞进 remark 或 extra JSON。

### 备注字段

- 备注字段常用 `remark`。
- 普通备注可用 `varchar(512)`；长文本备注再使用 `text`。
- 备注不应承载可查询的核心业务语义。

### 扩展字段

- 扩展字段常用 `extra_data` 或项目已有命名。
- MySQL 5.7+ 可考虑 `json` 类型；如果项目已有 `text`/`varchar` 存 JSON，跟随项目。
- 扩展字段必须只放低频、非索引、非核心查询内容。
- 如果后续需要筛选或统计，应独立成明确字段。

### 金额和费率字段

- 金额字段使用 `decimal`，不要用 `float` 或 `double`。
- 常见金额类型：`decimal(20, 6)` 或跟随当前项目已有精度。
- 费率字段使用 `decimal`，例如 `decimal(10, 6)`，按业务精度调整。
- comment 中说明单位，例如 amount、fee、rate、percent。

### 数量、重量、体积字段

- 整数数量使用 `int unsigned` 或 `bigint unsigned`。
- 重量、体积等可能有小数的字段使用 `decimal`。
- comment 中说明单位，例如 kg、g、cm3。

### 索引字段

- 高频查询字段、唯一业务键、关联字段才考虑索引。
- 低基数字段如状态、类型不建议单独建索引，优先与高选择性字段组合。
- 索引命名建议：
  - 普通索引：`idx_{field1}_{field2}`
  - 唯一索引：`uniq_{field1}_{field2}`

## DDL 生成

- 沿用当前项目 SQL 文件目录和命名方式。
- `ALTER TABLE` 新增字段时，写清字段类型、默认值、NULL 约束和 `COMMENT`。
- 新增字段必须带 `COMMENT`。
- 字段用途、枚举取值、历史数据语义、执行注意事项可以写在 SQL 注释里。
- 如果影响多张分表，要为每张物理表生成 DDL，或说明生成规则。
- 索引必须对应真实查询条件，不为低基数字段单独建索引。
- 避免破坏性变更，例如直接 `DROP COLUMN`、缩窄字段类型、无默认值新增 `NOT NULL` 字段。

## DML 生成

- DML 必须有明确 WHERE 条件，避免全表误更新。
- 历史数据初始化要用 SQL 注释说明初始化规则和影响范围。
- 批量修复建议给出可分批执行的 SQL 或按主键范围执行的方案。
- `DELETE` 需要谨慎；能用状态字段禁用时优先生成 `UPDATE`。
