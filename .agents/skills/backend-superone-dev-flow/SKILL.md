---
name: backend-superone-dev-flow
description: 当用户输入 backend-superone 的需求描述，希望自动输出完整改动方案，或直接完成代码、SQL、Wire、测试和验收闭环时使用；作为后端实现 skill，接受工作台总控编排并联动协议仓。
metadata:
  short-description: backend-superone 自动开发总控
---

# backend-superone 自动开发

本 skill 自包含，不依赖后端仓内知识库目录。跨仓路由、前端联动和协议仓写入由工作台总控，后端仓只负责服务端实现与验证。

## 项目上下文

- 目标项目：后端实现以 `business-repo/backend-superone` 为项目根目录；如果当前就在后端仓内，后端代码路径使用相对目录。
- 工作台根目录：跨仓需求以工作台根目录为协调目录，协议仓目标路径为 `business-repo/frontend-contracts`。
- 开发基线：默认在 `dev` 分支语义下完成需求实现；`test` / `release` 主要作为部署分支，不默认在其上直接开发。
- 分支流转：日常开发先落 `dev`，合并到 `test` 后自动部署 `nonlive`，合并到 `release` 后自动部署 `live`。
- 代码参考：评估兼容性或线上差异时，可以对照 `release`；但新增需求、方案设计、代码落点默认以 `dev` 当前结构为准。
- 技术栈：Go、Gin、GORM、MySQL、Viper、Wire、Logrus、JWT、Prometheus、pprof、Docker。
- 路由：`app/api_service/*.go`。
- UseCase：`use_case/*.go`。
- DTO：`internal/domain/{domain}/{domain}_dto`。
- Entity：`internal/domain/{domain}/{domain}_entity`。
- Factory：`internal/domain/{domain}/{domain}_factory`。
- Service：`internal/domain/{domain}/{domain}_service`。
- Repo：优先 `internal/repo`。
- 表模型：`internal/model/*_tab.go`，公共字段优先复用 `model.BaseTab`。
- 错误包：`internal/infrastructure/ecode`。
- BizContext：`internal/infrastructure/bizctx`。
- API 文档：`business-repo/frontend-contracts/openapi/{domain}_api.yaml`。
- 前端契约：`business-repo/frontend-contracts`。

按需求选择子 skill：

- API / DTO / UseCase / 路由：`backend-superone-api-flow`
- 领域模型 / service / repo / factory：`backend-superone-domain-flow`
- 字段设计 / DDL / DML / GORM 表模型：`backend-superone-field-sql-flow`
- OpenAPI YAML / 前端可复制契约：`backend-frontend-contract-flow`
- 数据库连接 / live 或 test DDL 执行 / 验证：`backend-superone-db-change-flow`
- Wire 依赖注入：`backend-superone-wire-flow`
- gofmt / wire / test / lint / diff 审查：`backend-superone-test-review-flow`

## 工作模式

## 分支与部署约定

- 用户未特别说明时，默认当前需求最终应先进入 `dev`。
- 需要“推 nonlive / 发测试环境”时，语义上对应合并或推进到 `test`。
- 需要“推 live / 发生产环境”时，语义上对应合并或推进到 `release`。
- `make nonlive` / `push.bat test` 属于把 `dev` 的已提交内容合并到 `test` 并触发 `nonlive` 部署，不应把它理解为普通本地开发命令。
- `test`、`release` 上若出现工作区脏文件，优先怀疑分支切换、脚本或换行符归一化，不要先假设是业务代码真实改动。

### 方案确认模式

当用户表达“先出方案”“确认后执行”“评审方案”时使用。

1. 读取需求描述，提取业务目标、验收标准、数据对象、接口对象、权限要求、是否涉及数据库变更。
2. 检索现有代码，定位最相近 domain、API、repo、model、service、use_case 和 route。
3. 输出改动方案，包含：
   - 业务理解和验收口径。
   - 受影响接口、表、字段、domain、repo、service、use_case、route。
   - DDL / DML 文件规划和是否需要执行到 test/live。
   - OpenAPI YAML 和前端契约文件规划。
   - 测试计划和验收命令。
   - 风险点、兼容策略和回滚点。
4. 等用户确认后再改代码、执行 SQL 或跑完整验证。

### 全自动模式

当用户表达“直接做”“自动完成”“不需要确认”“一次性完成”时使用。

1. 不等待中间确认，直接完成分析、方案、代码、SQL、Wire、测试、审查。
2. 只要本次实现新增表、改字段、改索引或需要 DML，并且已生成可执行 SQL 文件，默认执行 `test` 环境 DDL/DML 并验证；除非用户明确说“只生成 SQL / 不执行数据库”。
3. 如果需求明确要求 `live` DDL/DML，且项目脚本和连接配置可用，按 `backend-superone-db-change-flow` 执行并记录命令、目标库表、结果和验证 SQL。
4. 如果用户同时要求代码闭环和部署闭环，默认理解为：代码先在 `dev` 完成，按用户指令再推进到 `test` 或 `release`。
5. 如果 test/live 执行缺少必要信息、脚本不可用、连接失败或风险无法自动判断，生成可执行 SQL 和脚本改动，并在最终结果中标记阻塞原因。
6. 最终输出用户关心的验收信息：改了什么、如何验证、SQL 是否已执行、测试是否通过、剩余风险。

## 标准阶段

### 1. 需求解析

- 从需求描述中提取：新增/修改/删除、对象名称、字段、状态流转、权限、幂等、分页、排序、过滤、默认值、历史数据处理。
- 不凭空发明业务规则；缺失但可从现有同类功能推断的规则，要说明推断来源。
- 需求含糊但可以按现有项目模式安全推进时，选择最小可交付实现。

### 2. 代码定位

优先使用 `rg` / `find` 定位：

- 路由：`app/api_service/*.go`
- UseCase：`use_case/*.go`
- DTO：`internal/domain/{domain}/{domain}_dto`
- Entity：`internal/domain/{domain}/{domain}_entity`
- Factory：`internal/domain/{domain}/{domain}_factory`
- Service：`internal/domain/{domain}/{domain}_service`
- Repo：优先 `internal/repo`，如当前 domain 已有局部 repo 再沿用局部目录
- 表模型：`internal/model/*_tab.go`
- Wire：`use_case/wire.go`、`app/api_service/wire.go`、`internal/domain/**/wire.go`

### 3. 方案设计

方案必须落到文件级别，不只写抽象步骤：

- API：method、path、Req、Resp、鉴权方式。
- 数据：表、字段、索引、默认值、comment、历史数据 DML。
- 业务：校验、权限、状态、幂等、事务边界。
- 代码：每个文件新增/修改的结构、方法和调用链。
- 前端契约：是否影响 API/DTO/枚举/字段；若影响，规划 `business-repo/frontend-contracts/openapi` 和契约输出文件。
- 测试：单测或聚焦测试、手工验收请求、数据库验证 SQL。

### 4. 自动实现

按依赖顺序改动：

1. 表模型和 SQL 文件。
2. entity / factory。
3. repo。
4. service。
5. dto。
6. use_case。
7. route。
8. wire。
9. 前端契约：更新 `business-repo/frontend-contracts/openapi`，生成 `business-repo/frontend-contracts` 可复制文件。
10. 测试。

每一步优先复用现有相邻代码风格，不引入新框架、不做无关重构。

### 5. 数据库变更

- 只生成 SQL 时，使用 `backend-superone-field-sql-flow`。
- 全自动模式下，新增或修改表结构后必须执行 `test` 环境 SQL 并验证，除非用户明确禁止执行数据库。
- 需要执行 test/live DDL/DML 时，使用 `backend-superone-db-change-flow`。
- PowerShell 下执行 SQL 文件优先使用 `go run ./scripts/migration --% -action=exec-sql -sql-file=<path.sql> -env=<test|live>`，避免 `.sql` 扩展名或参数被解析异常。
- 迁移脚本默认环境必须保持为 `test`。不要把默认环境改成 `live`；live 只能在用户明确授权并显式传 `-env=live` 时执行。
- 数据库环境语义：`test` 对应 `nonlive` 验证链路，`live` 对应 `release`/生产链路；不要混淆“分支推进”和“数据库执行环境”。
- 新增或修改字段必须同步：SQL comment、GORM tag comment、DTO/Resp 语义、历史数据默认值。
- live 执行结果必须包含：目标环境、库、表、命令、成功/失败、验证 SQL 结果。

### 6. 前端契约

- 只要接口、DTO、响应、枚举、错误码或前端展示字段发生变化，就使用 `backend-frontend-contract-flow`。
- 更新 `business-repo/frontend-contracts/openapi/{domain}_api.yaml`。
- 生成或更新 `business-repo/frontend-contracts/openapi`、`business-repo/frontend-contracts/src/types`、`business-repo/frontend-contracts/src/apis` 中的可复制文件。
- 最终输出前端复制清单。

### 7. 验证闭环

按改动范围执行：

1. `gofmt -w <changed-go-files>`
2. `wire ./...`（改动依赖注入时）
3. `go test ./<changed-package>/...`
4. 必要时 `go test ./...`
5. 可用时 `make lint`
6. `git diff --check`

失败时先自行分析和修复；只有外部依赖、凭据、live 权限或需求歧义阻塞时才交还用户。


### 测试方案

每个 feature doc 末尾必须包含测试方案章节，按影响范围列出针对性功能测试用例：

```markdown
## 测试方案

### 功能测试

| 序号 | 场景 | 操作 | 预期结果 |
|---|---|---|---|
| 1 | ... | ... | ... |

### 回归测试

| 序号 | 场景 | 操作 | 预期结果 |
|---|---|---|---|
| 1 | ... | ... | ... |

### 兼容性测试

| 序号 | 场景 | 预期结果 |
|---|---|---|
| 1 | 旧数据（新字段默认值） | 不影响原有功能 |
```

## 最终输出格式

- 需求理解：一句话。
- 完成内容：按 API、数据、业务逻辑、测试分组。
- SQL/DDL 状态：已生成 / 已执行 test / 已执行 live / 未执行及原因。
- 前端契约：YAML 和可复制 TypeScript 文件是否已生成；列出复制清单。
- 验证结果：列出命令和结论。
- 剩余事项：只列真实阻塞或需要用户验收的点。

