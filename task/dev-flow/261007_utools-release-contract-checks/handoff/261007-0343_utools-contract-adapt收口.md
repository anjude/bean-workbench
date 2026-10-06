# uTools 契约与 adapt 改造 · 交接

- 任务目录：`task/dev-flow/261007_utools-release-contract-checks/`
- 时间：2026-10-07 03:43
- 状态：代码实现完成，待 uTools 插件环境手验
- 上一份：`261007-0235_utools功能同步收口.md`

## 这次到哪了

按用户纠偏落实契约唯一来源和 adapt 平台边界。uTools 消费 contract 生成的 API client；网络、存储、登录、插件生命周期、系统主题、上传/文件选择均有 adapt 实现。删除 uTools 手写 API/types 副本，并从 frontend-contracts 删除 stock topic enum 和 OpenAPI 值。没有客户端手写 API path 或 stock 兼容类型。

## 已完成

- 契约工厂入口：`business-repo/utools-superone/src/contract.ts`，使用 `create*Api(HttpClient)`。
- 平台适配：`business-repo/utools-superone/src/utils/adapt/`。
- 移除旧 `src/api/**`、`src/types/api/**` 协议副本；原业务 Repo/Store 不是新接口接入必需层。
- frontend-contracts 子模块 `codex/utools-contract-adapt` 修改 topic 协议；父仓同名分支。
- uTools stock 功能和契约 enum/OpenAPI 项均已删除。
- 阶段过程与主方案已更新。
- `npm run check`、`git diff --check`、子模块 `git diff --check` 通过；contract scanner 报告 9 个 API 域且客户端没有 `/api/so` 字面路径。

## 待做

1. 在 uTools 插件环境手验日志 parentLogId 跟进、删除级联和最近任务筛选持久化。
2. 复核 frontend-contracts 的 stock 移除是否与后端发布决策同步；若仍有后端 Stock 常量/行为，需在后端对应发布流程一起删干净，不能在前端恢复兼容枚举。
3. 如进一步要求把所有既有 Repo/Store 调用改造成 composable 直连契约 API，按具体业务流逐步迁移；它们当前不再承载协议定义。

## 分支与工作树

- uTools：`codex/utools-contract-adapt`，基于 `release`；未提交、未推送。
- contracts 子模块：`codex/utools-contract-adapt`；未提交、未推送。
- 保留此前工作树已有改动。

## 验证

最近一次完整 `npm run check` 在本轮平台 adapt 全部改动前后通过生产构建；locale 迁移后还需再跑一次完整检查确认。插件 UI 真实环境未运行。
