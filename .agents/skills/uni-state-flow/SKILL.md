---
name: uni-state-flow
description: 当 uni-app 项目需求涉及 Pinia store、Composable 业务逻辑、页面状态、缓存、错误处理、toast/confirm、列表刷新或跨页面数据同步时使用。
metadata:
  short-description: uni-app 状态逻辑
---

# uni-app 状态与 Composable

本 skill 自包含。执行任务时以工作目录 `.` 为项目根目录，所有文件路径都使用相对目录。

## 分层职责

- `src/stores/*.ts`：跨页面状态、缓存、列表排序、本地增删改、远端 CRUD 编排。
- `src/composables/use*.ts`：页面业务流程、生命周期辅助、确认弹窗、toast、格式化、导航。
- `src/repos/*-repo.ts`：可选层。复杂领域用于调用 API、检查业务错误、转换数据；轻量业务可由 store/composable 直接调用 API，并把 mapper/helper 集中放置。
- `src/pages/**/*.vue`：展示和事件绑定。

## Store 开发

1. 使用 `defineStore('{domain}', () => {})` setup store。
2. 状态使用 `ref`，派生状态使用 `computed`。
3. 常见状态：列表、`isInitialized`、`isLoading*`、`error`。
4. 列表模块应提供：
   - `load*(forceRefresh = false)`
   - `add*Local`
   - `update*Local`
   - `delete*Local`
   - `get*ById`
   - `reset`
5. 远端变更成功后同步本地缓存，必要时重新排序。
6. 排序逻辑放 store，页面不重复排序。

## Composable 开发

1. 命名使用 `use{Feature}`。
2. 从 store 暴露页面需要的 computed 状态。
3. 统一使用 `useErrorHandler` 做 `handleAsyncError`、`showSuccess`、`showError`、`showConfirm`。
4. 导航封装为函数，使用 `uni.navigateTo` 并处理 `fail`。
5. 格式化工具可放 composable，跨模块复用时放 `src/utils`。
6. 订阅、分享、授权等平台能力放 composable，使用条件编译或失败降级。

## 错误处理

- 使用 Repo 时：Repo 抛错，store 记录日志并继续抛错或回退状态。
- 不使用 Repo 时：store/composable 统一检查 `errCode`、转换字段和抛错，页面不直接重复处理接口响应。
- Composable 决定是否展示 toast、confirm 和 fallback message。
- 页面不直接吞错。

## 验证

- `npm run type-check`
- 对列表增删改查，至少手工检查：初次加载、强制刷新、本地缓存更新、空状态、错误提示。
