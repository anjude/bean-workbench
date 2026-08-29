---
name: dev-flow-0301-verify-flow
description: 当需求开发完成要收口时使用：跑后端 gofmt / wire / test / lint、前端 type-check 与平台 build、核对前后端契约一致性、做代码审查、处理构建失败，并把验证结果回填方案文档。
metadata:
  short-description: 整体验证与收口
---

# 整体验证与收口

阶段 03，唯一收口 skill。进入前提：阶段 01 的代码与契约已产出，涉及前端的需求前端已按契约接通。

按本次改动实际涉及的端执行对应小节：纯后端改动只跑「后端验证」，纯前端改动只跑「前端验证」，跨端需求两节都跑。方案文档回填统一由本 skill 负责。

项目上下文和命令清单见 `dev-flow-tools-repo`。本 skill 只规定验证什么、按什么顺序验证。

## 阶段门禁复核

先确认前面的阶段没有跳过：

- 方案文档已产出（`dev-flow-0000-plan-flow`），本次改动没超出方案里的改动范围。
- 涉及库表变更的，DDL/DML 已执行并有验证结论（`dev-flow-0102-db-change-flow` + `dev-flow-tools-db-query`）。
- 涉及接口、DTO、枚举、错误码变更的，契约已同步（`dev-flow-0104-contract-flow`）。
- 涉及前端的：新增或改动页面已过原型判断与状态矩阵（`dev-flow-0201-archetype-flow`），不是只有 happy path；跨端需求的前端类型与后端 DTO 已对齐；命中 carbon 的已按 `dev-flow-0205-space-ui` 核对品牌一致性。
- 涉及前端的改动，前端已按契约接通，不是后端单方面宣布完成。

任一前置未完成，先补上再验证，不要带着缺口往下走。

## 后端验证顺序

1. `gofmt -w <changed-go-files>`
2. `make wire`（改动依赖注入时）
3. 聚焦 `go test ./<changed-package>/...`
4. `make test`（全仓快速测试，等价 `go test -short ./...`）
5. `make test-integration`（涉及集成测试时）
6. `make lint`
7. `git diff --check`
8. 契约核对：协议仓 `business-repo/frontend-contracts` 与后端代码是否一致

失败时先自行分析和修复，只有外部依赖、凭据、live 权限或需求歧义阻塞时才交还用户。

### Go test 性能注意

- backend-superone 在 Windows 环境下单包首次编译可能需要 15-30 秒；全仓或多个包并行跑容易超时。
- 不要用并行工具同时跑多个 `go test` 包；优先串行执行。
- 命令 timeout 建议至少 180 秒。
- 只做编译检查时可用 `go test -run '^$' ./path`；想跳过缓存但仍编译时可用 `go test -count=0 ./path`。
- 一次超时但没有错误输出，先重复单包串行跑；warm cache 后通常会明显变快。

### 后端审查重点

- 是否符合 app / use_case / domain / repo / infrastructure 分层。
- Service 是否返回 `*ecode.BizError`，UseCase 是否透传。
- Gin 路由是否使用 `middleware.HandleRequest`，请求 DTO 是否有 `form`、`json`、`binding` 标签。
- Repo 是否只做数据访问，事务是否放在 service。
- 新字段是否同步 `internal/model`、SQL comment、默认值和历史数据语义。
- 是否无关重构、无关格式化、无关依赖升级。

## 前端验证顺序

1. `npm run type-check`（`vue-tsc --noEmit`），必过门禁。
2. 涉及页面或样式时 `npm run build:h5`。
3. 涉及微信小程序能力时 `npm run build:mp-weixin`。
4. 涉及其他平台时对应的 `build:mp-*`。
5. `git diff --check`。
6. 审查改动是否只覆盖本需求。

### 前端常见检查点

- `src/pages.json` 是否是合法 JSON，新增页面路径是否与文件一致。
- API 类型是否从 `src/types/api.ts` 导出，API 实现是否从 `src/apis/index.ts` 导出。
- 页面是否直接调用 API；如果是，应下沉到 composable/store/repo。
- Store 是否维护本地缓存和 force refresh，Composable 是否统一处理错误和 toast。
- 样式文件是否在 `src/styles/index.css` 注册。
- 是否误改无关页面、无关格式化或依赖版本。

### 前端审查重点

- 页面是否薄，业务逻辑是否下沉到 composable/store。
- 空、加载、失败、有数据四种状态是否都有落地。
- 没有把大量 scoped style 写进页面。
- 图标和空状态是否走项目内资产，没有引入外部图标平台。
- 命中品牌项目的，CTA 数量、信息密度、动效节奏是否跑偏。
- 是否引入新 UI 框架或新状态库，是否新增了不必要的依赖。

### 构建失败处理

- TypeScript 报错：优先修类型契约，不用 `any` 绕过，除非第三方平台类型缺失且已有同类写法。
- 页面路径错误：同步修 `src/pages.json` 和实际文件路径。
- 样式缺失：确认 `src/styles/index.css` import。
- 平台 API 报错：使用 uni-app 条件编译，保留非目标平台降级。
- 依赖缺失：先检查 `package.json` 是否已有可复用库，不主动新增依赖。

## 方案文档回填

验证通过后，把执行结果写回方案文档的「落地记录」章节：

- 实际改动与方案的差异
- DDL/DML 执行环境与结论
- 验证命令和结果（已运行 / 未运行及原因）
- 页面入口和手工验收步骤
- 已知风险、遗留项和需要用户验收的点

方案文档是这次需求的回看入口，不写落地记录等于链路没闭合。
