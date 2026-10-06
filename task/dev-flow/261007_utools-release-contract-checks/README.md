# uTools 发布与契约检查改造

## 背景

参考 Superone 多仓改造经验，为 `utools-superone` 补齐共享接口契约接入、发布分支约定和可重复的发布前检查；并同步移除已下线 stock 模块、支持日志跟进层级、修复近期任务状态筛选的持久化展示。用户已明确同意实施。

## 需求理解

以 `frontend-contracts` 作为 API 协议唯一事实来源，采用 uni-superone 的契约 client + 平台 adapt 模式：uTools 仅在 `adapt` 提供平台实现，业务调用生成 API；Store 管跨页状态和 CRUD，Composable 管页面流程，不保留 Repo 架构层。将 `release` 明确为发布分支，`master` 作为日常集成分支；为本地与 CI 提供一致验证入口。同步记录跟进能力，彻底移除 stock（包括历史兼容枚举），修复近期任务状态筛选持久化。

## 目标与边界

### 本期目标

- `utools-superone/src/contracts` 以 Git 子模块引用 `frontend-contracts`，跟随其 `release`，与 `uni-superone` 当前发布契约保持一致。
- 网络层实现 `frontend-contracts` 的 `HttpClient`，存储层实现通用 `StorageAdapter`；通过工厂实例化契约仓生成 API client 和平台无关 `CacheManager`。
- uTools 不保留手写 API 请求/类型副本；当前使用但契约缺失的后端接口先核对后端协议并补到 `frontend-contracts`，再生成并消费，不留客户端手写兜底。
- 业务数据流向 uni-superone 的 composable/API 模式迁移；跨页面状态与 CRUD 编排归 Store，页面流程归 Composable，Repo 不作为架构层。
- 清理 uTools 现有 Repo：将单一调用方的接口调用和状态编排收回到 store/composable，删除无调用方的 Repo/方法与无效转换；本地主题缓存直接归 topic store 管理，完成后删除 `src/repos/`。新 API 调用直接使用契约生成 client，不经手写转发层。
- 提供只读 lint、typecheck、build 和契约检查组成的 `npm run check`，并配置 GitHub Actions 在 `master`、`release` 和 PR 上运行。因现有 ESLint 全仓扫描会触发大量历史格式规则与第三方压缩产物，本期 lint 门禁只检查新增的契约检查脚本。
- 仓库说明明确 `master` 日常开发、`release` 发布，发布通过 PR/合并推进；不直接向 `release` 开发。
- 记录列表只显示根记录，记录详情可查看和创建 `parentLogId` 跟进，跟进支持继续嵌套。
- 完整移除 stock 模块与协议枚举，包含 uTools 消费端及 frontend-contracts 唯一事实源，不保留历史兼容分支。
- 近期任务筛选用持久缓存记住状态，重新进入后显示与过滤一致；迁移旧 localStorage 值。

### 本期不做

- 不改后端业务语义、数据库或发布环境。
- 不复制 uni-superone 的页面和产品交互；仅采用其共享契约调用与平台适配模式，按必要范围将业务调用迁移到 composable。
- 不新增与本次目标无关的业务功能，不执行发布合并或生产部署。
- 不新增测试框架；本期门禁聚焦类型、静态规则、构建和契约路径一致性。

## 改动范围

### 涉及仓库

- `business-repo/utools-superone`：`.gitmodules`、`src/contracts` gitlink、`src/utils/adapt/**`、契约 client 绑定入口、手写 API/types 清理、`src/repos/**` 合并至 `src/stores/**` / `src/composables/**` 并删除 Repo 目录、检查脚本、CI 和文档。
- `business-repo/frontend-contracts`：唯一协议事实源；本期按废弃决策删除 stock topic 协议枚举/OpenAPI 值，不新增臆造接口。
- `business-repo/utools-superone`：近期任务筛选 store、缓存迁移；记录父子关系的类型、Repo、Store、路由、详情视图；stock API、Repo、Store、Composable、视图、类型、路由、导航与样式。
- 参考 `business-repo/uni-superone/src/pages/log-detail/` 与 `src/composables/useRecentTaskList.ts`。
- 工作台：本方案、任务登记与阶段过程记录。

### 涉及库表

- 无。

### 涉及接口与契约

- 后端接口语义保持不变。任何客户端使用的 API method/path/Req/Resp 必须来自共享契约；缺漏回到 `frontend-contracts` 补齐，禁止客户端手写兼容定义。

## 实施方案

1. 将 `frontend-contracts` 作为 `src/contracts` 子模块接入，固定跟踪 `release`。
2. 对照 `uni-superone/src/contract.ts` 和 `src/utils/adapt/{http,storage}.ts`，在 uTools 建立同构契约 client 绑定及 uTools HTTP/DBStorage 适配器；通用 CacheManager 消费 StorageAdapter。
3. 审核全部 uTools API 调用与后端 OpenAPI。共享契约缺的已存在接口回唯一事实仓补齐并生成；废弃 stock 从 uTools 与契约仓一并删除。
4. 用契约仓 `create*Api` 工厂替代手写 API 方法及 `src/types/api/**` 协议副本。按 uni-superone 模式将有调用迁移到 composables，去掉纯透传 Repo/Store；保留必要的 uTools 本地数据/登录同步业务逻辑，但不保留平台判断在 adapt 之外。
5. 保留契约完整性检查、只读 lint、统一 `check` 和 CI；lint 当前存量基线与第三方压缩文件问题记录在方案，后续单独收敛，不自动格式化无关文件。
6. 更新 uTools `AGENTS.md` 与 README，规定契约唯一来源、adapt 边界、调用模式、分支发布流程。
7. 保持现有日志跟进和任务筛选功能，验证业务行为在迁移后未回退。

## 验收标准

- `src/contracts` 指向 `frontend-contracts`，Git 子模块分支配置为 `release`。
- uTools API 请求、Req/Resp 和枚举均由 `src/contracts` 提供；源代码不存在本地协议副本或手写 API path。
- uTools 业务侧不直接调用 `window.utools` 网络/存储接口；平台运行差异只存在于 `src/utils/adapt/`。
- 所有当前存量 API 调用均在共享协议仓有契约；新增后端接口进入共享仓后，uTools 通过更新子模块即可获得 client/type。
- `npm run check` 可串行执行所有门禁，`npm run lint` 不修改文件。
- GitHub Actions 使用 lockfile 安装并运行同一 `check` 命令。
- 文档明确 `master` 是集成分支、`release` 是发布分支和发布前门禁。
- uTools 日志列表只显示根记录，详情展示子记录，新增跟进携带当前记录 ID，跟进可继续嵌套。
- uTools 页面、代码和共享契约不再出现 stock 领域实现或兼容枚举。
- 筛选选择离开页面并重新进入后恢复；空/无效缓存显示为全部状态选中。
- `git diff --check` 无空白错误。

## 推荐实施顺序

工作台方案记录 → 子模块与 API 路径接入 → 脚本及 CI → 文档更新 → typecheck/lint/契约检查/build 与 diff 审查。

## 测试方案

### 功能测试

| 序号 | 场景 | 操作 | 预期结果 |
|---|---|---|---|
| 1 | 契约路径复用 | 运行 `npm run check:contracts` | 已有契约路径不再以字面量重复定义；缺失契约路径有清晰报告 |
| 2 | 日志跟进 | 创建一条跟进，再打开该跟进 | 请求携带 `parentLogId`；详情和子列表正确显示，可继续跟进 |
| 3 | 状态筛选恢复 | 选中部分状态后离开并重进 | 选中状态和任务过滤恢复；空/无效缓存变为全选 |
| 4 | 统一门禁 | 运行 `npm run check` | typecheck、lint、契约检查、build 依次完成并返回准确状态 |

### 回归测试

| 序号 | 场景 | 操作 | 预期结果 |
|---|---|---|---|
| 1 | uTools API 运行行为 | 对比改造前后请求调用 | HTTP method、参数、API 路径语义不变 |
| 2 | 删除有跟进的记录 | 删除包含多层跟进的本地/远端记录 | 本地级联删除；远端遵循已有服务端级联行为 |
| 3 | lint 不改文件 | 记录工作树状态后运行 `npm run lint` | lint 只报告问题，不自动修改源码 |

### 兼容性测试

| 序号 | 场景 | 预期结果 |
|---|---|---|
| 1 | 干净 clone 初始化子模块 | `git submodule update --init --recursive` 可获取契约；TypeScript 与构建可解析子模块源码 |
| 2 | 契约缺少后端接口 | 停止客户端实现；核验后端真实协议并先补唯一事实仓，再更新子模块消费。

## 风险与回滚

- 子模块未递归初始化会导致导入缺失；README 与 CI 会明确初始化方式，CI checkout 开启子模块。
- 仅将已在后端路由/OpenAPI 确认的接口纳入契约，不推断或发明接口语义。
- 回滚时恢复 API path 引用、子模块和门禁配置即可，不涉及数据变更。
- 跟进功能依赖共享契约已有的 `parentLogId` 和服务端已有级联删除语义；本地模式需单独实现级联删除。

## 落地记录

前端改造与 Repo 收敛已完成；阶段实现、迁移边界和验证结论见 `process/02-前端开发.md`。`npm run check`、主仓及 contracts 子模块 `git diff --check` 通过。uTools 插件环境的交互仍需手动验收；后端源码里仍存在 stock 常量/逻辑，需在后端发布链路同步清理，客户端与契约不恢复兼容定义。
