# 后端开发细则

## 目录

- [领域模型与字段设计](#领域模型与字段设计)
- [一、领域层](#一领域层)
- [二、字段与 SQL 设计](#二字段与-sql-设计)
- [数据库变更执行](#数据库变更执行)
- [环境语义](#环境语义)
- [迁移脚本](#迁移脚本)
- [模式](#模式)
- [字段和 SQL 规范](#字段和-sql-规范)
- [验证](#验证)
- [禁止事项](#禁止事项)
- [API 与依赖注入](#api-与依赖注入)
- [一、接口层](#一接口层)
- [二、Wire 注入装配](#二wire-注入装配)
- [收尾](#收尾)
- [输出要求](#输出要求)
- [OpenAPI 与共享契约](#openapi-与共享契约)
- [目标](#目标)
- [触发条件](#触发条件)
- [输出位置](#输出位置)
- [文件职责](#文件职责)
- [生成规范](#生成规范)
- [工作流程](#工作流程)
- [自动开发集成](#自动开发集成)
- [阶段交接](#阶段交接)
- [验证](#验证)
- [禁止事项](#禁止事项)



## 领域模型与字段设计

# backend-superone 领域与表设计

后端领域和表结构设计。项目上下文见 `dev-flow-tools-repo`。

本节只做**设计态**：领域分层代码 + 字段与 SQL 产出，**不连接数据库**。执行归 `数据库变更执行细则`，只读排查归 `dev-flow-tools-db-query`。

字段细则优先读取本流程 `references/01-field-design-norms.md`；不可用时使用本文档内置规范。

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
6. 如需 API，交给 `API 与依赖注入细则` 做 DTO、UseCase、路由和 Wire 注入。
7. 如新增或修改客户端可见枚举、状态、结构体字段，交给 `OpenAPI 与共享契约细则` 同步唯一协议事实仓。
8. 需要落库时，把 SQL 交给 `数据库变更执行细则` 执行。

### 分层约束

- 分层顺序 app → use_case → domain → repo → infrastructure，不跨层直接调用 app 或 middleware。
- Service 返回 `*ecode.BizError`。
- 不在 repo 中写业务判断，事务放 service。
- 影响客户端的枚举和结构体变更必须同步 OpenAPI YAML 和唯一协议事实仓 `business-repo/frontend-contracts`，所有客户端消费同一份定义。

## 二、字段与 SQL 设计

### 字段规范

- 主键：`id bigint NOT NULL AUTO_INCREMENT COMMENT '主键ID'`。
- 时间字段：`create_time`、`update_time`，GORM 使用 `autoCreateTime` / `autoUpdateTime`。
- GORM tag：`gorm:"column:{field};...;comment:'...'"`。
- SQL 新增字段必须带 `COMMENT`；状态/枚举字段在 comment 中写清取值含义。
- 用户维度字段沿用 `openid varchar(64)`，需要查询时加索引。
- 状态字段优先 `tinyint` 或已有 enum 类型，并在 comment 中列出枚举。
- 金额、比例、计数、时间戳、JSON、长文本按 `01-field-design-norms.md` 选择类型；金额/费率不用 float。
- 新增字段必须明确是否允许 `NULL`、默认值、历史数据回填 DML。
- 索引必须说明查询场景，避免无依据组合索引。

### 输出

- 用户只要 SQL 时，直接输出 DDL/DML，每个字段带 `COMMENT`，注释写清业务含义、默认值、历史数据处理和执行注意事项。
- 用户要落文件时，SQL 放 `scripts/migration/sql/YYYYMMDD_*.sql`。
- 用户要同步代码时，同时更新 `internal/model/*_tab.go` 里的 GORM struct。
- 用户要连库执行、用迁移脚本时，交 `数据库变更执行细则`；只查结构交 `dev-flow-tools-db-query`。
- 字段会进入 API 请求/响应、客户端展示、筛选或枚举判断时，交 `OpenAPI 与共享契约细则` 同步 YAML 和共享协议。
- 新增 carbon 业务表时，记得把表名加进 `scripts/migration/exec_sql.go` 的 `carbonTables`，否则 `verify-carbon` 覆盖不到。


## 数据库变更执行

# backend-superone 数据库变更

数据库变更执行。

本节只处理数据库写操作与迁移执行。职责边界：

- 字段设计和 SQL 产出属于 `领域模型与字段设计细则`，本细则不重新设计字段。
- 只读排查、结构核对、数据验证属于 `dev-flow-tools-db-query`，本细则不负责查询。
- 分支推进属于 `dev-flow-tools-repo`。
- 项目目录与常用命令见 `dev-flow-tools-repo`。

字段细则见 `领域模型与字段设计细则` 目录内的 `01-field-design-norms.md`；不可用时使用本文档内置规范。

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

- 方案确认模式（开发流程的默认模式）：必须等用户确认后再执行。
- 全自动模式（开发流程的显式全自动模式）：本次改动涉及新增表、改字段、改索引或 DML 时，默认执行 `test` 环境并验证；用户已明确要求 `live` 时才执行 live。
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
- 金额、比例、计数、时间戳、JSON、长文本按 `01-field-design-norms.md` 选择类型。
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


## API 与依赖注入

# backend-superone 接口与注入装配

后端 API 与依赖注入。项目上下文见 `dev-flow-tools-repo`。

职责两层：**接口层**（DTO / UseCase / Service / 路由）+ **注入装配**（Wire）。新增接口后必然要补 Wire，两者不拆开跑。

## 一、接口层

落点：路由 `app/api_service/*.go`，UseCase `use_case/*.go`，DTO `internal/domain/{domain}/{domain}_dto`，Service `internal/domain/{domain}/{domain}_service`，错误包 `internal/infrastructure/ecode`，BizContext `internal/infrastructure/bizctx`。

### 流程

1. 确认 domain、接口路径、HTTP 方法、是否需要 JWT。
2. 在 `internal/domain/{domain}/{domain}_dto` 定义请求和响应结构：请求字段同时加 `form`、`json`，必填字段加 `binding:"required"`。
   - 数值字段若 `0` 是合法语义（取消表态、默认状态），不要用 `binding:"required"`，改用 `binding:"gte=0"`，否则 gin 会把 0 当零值拒绝。
3. 在 `{domain}_service` 增加 service 接口方法和实现，返回 `(*Resp, *ecode.BizError)`。
4. 在 `use_case/{domain}_use_case.go` 或既有 `use_case/{domain}.go` 增加 UseCase 方法，从 `ctx.GetReqParam().(dto.XReq)` 取参数并调用 service。
5. 在 `app/api_service/*.go` 的对应路由组注册路由：`middleware.HandleRequest(useCase.Method, dto.XReq{})`。
6. 新 domain 时同步更新 `app/api_service/api_service.go`、`app/api_service/wire.go` 和相关 injector。

## 二、Wire 注入装配

落点：API 层 `app/api_service/wire.go`，UseCase 层 `use_case/wire.go`，Service 层 `internal/domain/{domain}/{domain}_service/wire.go`，Repo 层沿用 `internal/repo` 已有注入方式。

### 规则

- `wire.go` 使用 `//go:build wireinject` 和 `// +build wireinject`。
- 使用 `wire.Struct(new(Type), "*")` 注入结构体字段。
- 接口绑定使用 `wire.Bind(new(IInterface), new(*Impl))`。
- 新增 constructor 或 ProviderSet 后，更新调用链上层的 `wire.Build`。

### 装配流程

1. 新增 constructor 或 ProviderSet。
2. 更新调用链上层的 `wire.Build`。
3. 运行 `wire ./...`（等价 `make wire`）。
4. 失败时按报错修复缺失 provider、接口绑定或循环依赖。

## 收尾

- 如果接口、DTO、响应或错误码影响客户端，执行 `OpenAPI 与共享契约细则`，更新唯一协议事实仓 `business-repo/frontend-contracts` 中的 OpenAPI 与共享契约，并明确受影响客户端同步的子仓 revision。
- 执行 `gofmt -w`、聚焦测试或 `go test ./...`。

## 输出要求

- 直接列出需要修改/新增的文件。
- 影响客户端时必须列出协议事实仓更新内容与客户端同步方式，不生成复制清单。
- 不引入新框架，不重构无关历史代码。


## OpenAPI 与共享契约

# 后端共享协议维护

OpenAPI 与共享契约维护；它是后端与客户端的数据交接点。

本节说明多仓、多客户端协作约定。执行任务时优先以工作台根目录为协调目录；如果当前工作目录在业务仓内，先识别工作台根目录，再定位唯一协议事实仓。当前工作台的协议事实仓是 `business-repo/frontend-contracts`，所有客户端项目共用，不按平台复制出多份协议。

## 目标

后端开发完成接口或枚举变更时，同步更新唯一协议事实仓。所有前端客户端都以 Git 子仓引入并消费同一份契约；客户端只实现自己的传输封装与产品交互，不复制或重新定义接口、结构体和枚举。

## 触发条件

只要本次后端改动包含以下任一项，就必须执行本节规则：

- 新增、删除或修改 API 路由、HTTP method、path。
- 修改请求 DTO、响应 DTO、分页结构、字段名、字段类型、必填规则。
- 修改业务枚举、状态值、错误码、常量含义。
- 修改前端会展示或提交的字段语义、默认值、时间戳、金额、JSON 字段。
- 修改认证要求、登录态、权限、订阅消息等前端调用条件。

## 输出位置

### OpenAPI YAML

- 接口文档放在 `business-repo/frontend-contracts/openapi/{domain}_api.yaml`。
- 已有 domain 更新原文件；新 domain 新建文件。
- YAML 使用 OpenAPI 3.x，保留 `servers.url: /api/so`。
- schema 字段使用后端 JSON 字段名，通常为 snake_case。

### 共享契约目录

统一放在：

```text
business-repo/frontend-contracts/
  openapi/
  apis/
  types/
```

如果唯一协议事实仓或本次需要的子目录不存在，先确认工作台接入约定，再保持最小结构补齐；不得在客户端仓另建一份协议作为替代事实来源。共享契约应平台无关，不依赖某个客户端的页面、状态管理或运行时。

## 文件职责

- `openapi/{domain}_api.yaml`：接口契约源文件。
- `types/{domain}.ts`：共享请求/响应类型、业务结构和枚举；按仓库约定组织与导出。
- `apis/{domain}.ts`：仅放跨客户端稳定且不绑定传输运行时的路径等契约常量；HTTP 请求封装属于客户端实现，不进入共享契约。

## 生成规范

### 命名转换

- 后端 JSON/YAML 字段保持 snake_case。
- TypeScript 类型字段默认使用 camelCase，前端 request 层负责 snake_case/camelCase 转换。
- 如果目标前端没有自动转换层，额外生成 snake_case 版本或在注释中明确字段映射。

### 类型映射

- Go `int`、`int32`、`int64`、`uint32`、`uint64` -> TypeScript `number`。
- Go `string` -> TypeScript `string`。
- Go `bool` -> TypeScript `boolean`。
- Go slice -> TypeScript array。
- Go map/JSON -> 明确结构；无法确定时使用 `Record<string, unknown>`，避免裸 `any`。
- 时间戳字段使用 `number`，注释说明单位。
- 金额如果后端可能返回 string，TypeScript 类型写成 `number | string`，Repo 层再转换。

### 枚举

- 后端新增或修改枚举时，必须生成 TypeScript `enum` 或 `as const` 常量。
- 注释写清每个取值的业务含义。
- YAML schema 的 `enum` 必须同步。
- 前端契约枚举名要包含业务上下文，避免通用 `Status`、`Type`。

### API 常量

如果共享契约仓包含 API 常量：

- 常量必须与 OpenAPI path 和 operationId 一致。
- 不绑定某个客户端的 request、响应包装、缓存或业务逻辑。

## 工作流程

1. 从代码读取真实路由、DTO、Resp、枚举、错误码，不凭空写契约。
2. 更新 `business-repo/frontend-contracts/openapi/{domain}_api.yaml`：
   - paths
   - operationId
   - requestBody 或 query parameters
   - responses
   - components.schemas
   - enum 和 required
3. 确保 `business-repo/frontend-contracts` 及本次需要的子目录存在；不存在则创建。
4. 生成或更新协议事实仓中的共享 TypeScript 类型、枚举和适用的契约常量。
5. 如果本次改动影响多个 domain，按 domain 拆文件，不写一个超大文件。
6. 确认受影响客户端通过 Git 子仓引用该协议事实仓，并给出需要同步的 revision 和消费验证方式；不输出文件复制清单。

## 自动开发集成

在后端 auto 开发流程中：

- API/DTO/枚举改动完成后立即同步本节契约。
- 测试前先保证唯一协议事实仓的 OpenAPI 与共享契约已同步。
- 最终结果必须说明：协议事实仓是否更新、客户端如何同步到该修订、客户端是否存在重复定义。

## 阶段交接

本节维护后端交付给客户端的契约输入：

- 客户端更新协议子仓 revision 后进入前端实现，由 `数据层与状态管理细则` 从共享契约导入类型和枚举，并在本地实现请求传输层。
- 前端接通后进入整体验收，由 `整体验证与交付细则` 收口，其中会再次核对契约与代码是否一致。
- 不影响前端的改动跳过本细则，直接进入整体验收。

## 验证

- YAML 可读性：检查缩进、`paths`、`components.schemas`、`$ref` 是否一致。
- 契约一致性：字段名、类型、必填、枚举、path、method 与代码一致。
- TypeScript 基本合法：避免重复导出、缺失 import、裸 `any`。
- `git diff --check`。

## 禁止事项

- 不只改代码而漏掉 YAML 和前端契约。
- 不把某个客户端私有业务逻辑写进共享契约仓。
- 不把某个客户端的页面、store、composable 或平台运行时请求封装放入共享契约仓。
- 不在客户端重新声明已有共享契约中的请求、响应类型或枚举。
- 不使用绝对路径。
