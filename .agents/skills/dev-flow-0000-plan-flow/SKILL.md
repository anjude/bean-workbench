---
name: dev-flow-0000-plan-flow
description: 当用户提出 backend-superone 或 uni-carbon-space 的新需求、要求先出方案、确认改动范围、评估影响面，或要开始一次跨端改动时使用；产出方案文档并确认后，按改动范围派发后端开发、前端开发和验证阶段的 skill。
metadata:
  short-description: 跨端方案设计与阶段派发
---

# 跨端方案设计

阶段 00，dev-flow 族链路入口。所有开发需求先走本 skill，产出方案文档，用户确认后才允许进入阶段 01 或阶段 02。

项目上下文（目录约定、分支与部署、技术栈、构建命令）不在此处重复，需要时读取 `dev-flow-tools-repo`。

## 定位

本 skill 只做三件事：把需求理解清楚、把改动范围钉死、把后续阶段派发下去。不写业务代码，不执行 SQL，不跑验证命令。

## 需求解析

从需求描述中提取，缺什么问什么，不替用户发明业务规则：

- 动作：新增、修改、删除。
- 对象：业务对象名称、字段、状态流转。
- 约束：权限、幂等、分页、排序、过滤、默认值、历史数据处理。
- 边界：本期做什么，明确不做什么。
- 数据：是否涉及新增表、改字段、改索引、回填 DML。
- 接口：是否有对外 API，是否影响前端展示或提交。
- 端：只动后端、只动前端、还是跨端。跨端需求必须写清两段的交接物。
- 页面：新增页面、改已有页面，还是只改组件和样式。
- 状态：是否存在加载中、空数据、失败、权限不足等非 happy path 分支。

缺失但能从现有同类功能安全推断的规则，要在方案里写明推断来源，不要静默假定。

## 影响面定位

用 `rg` / `find` 定位最相近的现有实现，方案里的每一处改动都要有落点。

后端落点：

- 路由：`app/api_service/*.go`
- UseCase：`use_case/*.go`
- DTO：`internal/domain/{domain}/{domain}_dto`
- Entity：`internal/domain/{domain}/{domain}_entity`
- Factory：`internal/domain/{domain}/{domain}_factory`
- Service：`internal/domain/{domain}/{domain}_service`
- Repo：优先 `internal/repo`，domain 已有局部 repo 时沿用
- 表模型：`internal/model/*_tab.go`
- Wire：`use_case/wire.go`、`app/api_service/wire.go`、`internal/domain/**/wire.go`
- 契约：`business-repo/frontend-contracts/openapi/{domain}_api.yaml`

前端落点：

- 页面与路由：`src/pages.json`、`src/pages/**/index.vue`
- API 与类型：`src/apis/*.ts`、`src/types/api/*.ts`
- 状态：`src/stores/*.ts`、`src/composables/use*.ts`
- 组件与样式：`src/components/cu-*.vue`、`src/components/business/*.vue`、`src/styles/index.css`

需要确认库表结构时，用 `dev-flow-tools-db-query` 只读查看，不在此阶段做写操作。

## 方案产出

方案落工作台 `task/YYMMDD_{主题}/README.md`。跨端需求前后端共用同一份方案，不往业务仓 `docs/feature/` 新增文件（历史文件保留）。

模板：

```markdown
# {需求主题}

## 背景

## 需求理解

## 目标与边界

### 本期目标

### 本期不做

## 改动范围

### 涉及仓库

### 涉及库表

### 涉及接口

### 涉及前端契约

## 实施方案

## 验收标准

## 推荐实施顺序

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

## 风险与回滚

## 落地记录
```

填写要求：

- 改动范围必须落到文件和表级别，不写抽象步骤。
- 涉及仓库要写清是 `backend-superone`、前端仓还是协议仓 `frontend-contracts`。
- 涉及接口要写 method、path、Req、Resp、鉴权方式。
- 涉及库表要写表名、字段、索引、默认值、comment、是否需要回填 DML。
- 验收标准要可判定，能对应到具体命令或请求。
- 测试方案三张表（功能、回归、兼容）必须填满，不留空占位。

## 门禁

以下任一项不满足，不得进入开发阶段（01 或 02）：

- 任务目的未写清。
- 改动范围未落到文件级别；涉及库表时未落到表级别。
- 涉及库表未列明。
- 涉及页面时未列明状态分支。
- 验收标准不可判定。

方案未确认前，不改代码、不执行 DDL/DML、不推进分支。

## 阶段派发

方案确认后，按改动范围派发，不需要的阶段跳过。

阶段 01 后端开发：

| 改动内容 | 派发到 |
| --- | --- |
| 领域层 entity / model / factory / repo / service、字段设计、DDL/DML SQL、GORM 表模型 | `dev-flow-0101-domain-flow` |
| 迁移脚本、test/live 执行、表结构验证 | `dev-flow-0102-db-change-flow` |
| DTO / UseCase / Service / 路由、Wire 依赖注入 | `dev-flow-0103-api-flow` |
| OpenAPI YAML 与前端契约生成 | `dev-flow-0104-contract-flow` |

阶段 02 前端开发：

| 改动内容 | 派发到 |
| --- | --- |
| 产品原型判断、信息骨架、CTA 结构、状态矩阵补全 | `dev-flow-0201-archetype-flow` |
| API 类型与请求封装、可选 Repo、Pinia store 与 Composable | `dev-flow-0202-data-flow` |
| 页面、路由与生命周期、组件与样式审美执行 | `dev-flow-0203-page-flow` |
| SVG 资产生产、品牌图标（命中品牌项目时叠加） | `dev-flow-0204-asset-flow` |
| 品牌 UI 规范约束（命中 carbon 时全程叠加） | `dev-flow-0205-space-ui` |

阶段 03 整体验证：

| 改动内容 | 派发到 |
| --- | --- |
| 后端 gofmt / wire / test / lint 与审查、前端 type-check / build 与交付验收、方案文档回填 | `dev-flow-0301-verify-flow` |

### 阶段 01 执行顺序

领域与表设计 → DDL 执行 → 接口与注入装配 → 契约。

落到文件级别时按依赖顺序改，不跳步：

1. 表模型和 SQL 文件。
2. entity / factory。
3. repo。
4. service。
5. dto。
6. use_case。
7. route。
8. wire。
9. 前端契约：更新 `business-repo/frontend-contracts/openapi`，生成可复制契约文件。
10. 测试。

### 阶段 02 执行顺序

原型与状态矩阵 → 数据层 → 页面与样式 → 资产（品牌规范全程叠加）。

第一步是硬门槛，不是可选项：

1. 原型与状态矩阵：先决定产品形态和信息层级，再补齐加载中、空数据、失败、权限不足等分支，最后才写 happy path。只有 happy path 视为未完成。
2. 数据层：请求/响应类型放 `src/types/api/*.ts`，业务实体放 `src/types/*.ts`；`src/apis/*.ts` 只做请求，字段兼容转换和业务错误处理放 store/composable 的统一 helper。Store 管跨页面状态和缓存，Composable 管页面业务流程。
3. 页面与样式：页面尽量薄，业务逻辑不堆在 `.vue` 里；样式在 `src/styles` 注册。
4. 资产：图标和空状态优先项目内 SVG 实现。
5. 品牌规范：命中 carbon 时必须叠加，检查页面结构、信息密度、CTA 数量、图标与动效是否跑偏。

每一步优先复用相邻代码风格，不引入新框架，不做无关重构、无关格式化、无关依赖升级。

需要项目约定、分支推进或部署时调用 `dev-flow-tools-repo`；需要数据库只读排查时调用 `dev-flow-tools-db-query`。

## 工作模式

### 方案确认模式

默认模式。用户表达「先出方案」「确认后执行」「评审方案」时使用。产出方案文档后停下等确认，不进入阶段 01 或 02。

方案确认模式的前端产出必须包含：产品原型判断、状态矩阵摘要、文件级方案、资产主权决策、品牌一致性注意点、验证命令。

### 全自动模式

用户表达「直接做」「自动完成」「不需要确认」时使用。一次走完方案、开发、执行、验证，但仍有两条硬约束：

1. 方案文档照常产出，作为过程记录和回看依据。
2. live 环境 DDL/DML 必须用户显式授权，不得由全自动模式推断。

全自动模式下，只要本次实现新增表、改字段、改索引或需要 DML，默认执行 `test` 环境并验证；用户明确说「只生成 SQL / 不执行数据库」时除外。

前端部分默认跑 `npm run type-check`；涉及平台差异时补目标平台 build。

## 最终输出格式

- 需求理解：一句话。
- 方案文档路径。
- 改动范围：按仓库、库表、接口、契约、页面分组。
- 派发计划：本次会走哪些阶段和 skill，跳过了哪些及原因。
- 产品完整性风险：只列真实缺口，例如状态分支缺失、外部依赖残留、品牌一致性未收口。
- 待确认项：只列真实阻塞或需要用户决策的点。
