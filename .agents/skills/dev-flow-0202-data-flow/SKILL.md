---
name: dev-flow-0202-data-flow
description: 当 uni-app 项目需求涉及新增或修改后端接口调用、TypeScript API 类型、可选 Repo 封装、request 参数转换、接口错误处理、Pinia store、Composable 业务逻辑、页面状态、缓存、toast/confirm、列表刷新或跨页面数据同步时使用。
metadata:
  short-description: uni-app 数据层（API 与状态）
---

# uni-app 数据层：接口与状态

阶段 02 前端开发，执行顺序第 2 步。阶段编排见 `dev-flow-0000-plan-flow`，项目上下文见 `dev-flow-tools-repo`。

执行任务时以工作目录 `.` 为项目根目录，所有文件路径都使用相对目录。

## 契约与平台边界

- 后端接口、请求/响应结构和枚举以唯一协议事实仓 `business-repo/frontend-contracts` 为准；所有前端项目通过 Git 子仓消费。
- 使用共享契约中的类型和枚举，不在客户端重复声明或按平台维护分支版本。协议变化回到事实仓更新，再由客户端同步对应修订。
- 客户端本地 `src/apis` 负责调用本项目统一 request 能力，不重新定义协议。
- 网络、存储、登录、上传等平台运行能力经项目适配边界（如 `utils/adapt`）提供统一接口。业务状态和页面不直接调用平台私有 API，也不散落平台判断；产品本身需要不同 UI/UX/交互时，差异留在对应呈现层。

## 当前模式

- API 文件：`src/apis/{domain}.ts`，统一导出 `src/apis/index.ts`
- API 类型：从项目接入的协议子仓导入（uni-superone 当前是 `src/contracts`），不复制到客户端自有 API 类型目录
- 业务实体类型：`src/types/{domain}.ts`
- Repo 文件：`src/repos/{domain}-repo.ts`，**可选**
- Store：`src/stores/*.ts`
- Composable：`src/composables/use*.ts`
- 请求入口：`src/utils/request`，响应格式 `ApiResponse<T>`（`errCode`、`data`、`msg`、`detail`）
- request 层把请求参数转 snake_case，响应转 camelCase

## 分层职责

- `src/stores/*.ts`：跨页面状态、缓存、列表排序、本地增删改、远端 CRUD 编排。
- `src/composables/use*.ts`：页面业务流程、生命周期辅助、确认弹窗、toast、格式化、导航。
- `src/repos/*-repo.ts`：可选层。复杂领域用于调用 API、检查业务错误、转换数据；轻量业务可由 store/composable 直接调用 API。
- `src/pages/**/*.vue`：展示和事件绑定。

## 一、接口层

1. 从需求或后端接口定义提取 method、path、Req、Resp、业务实体。
2. 从协议子仓导入请求/响应类型、业务结构和枚举；若契约缺失或不符，回到协议事实仓更新，不在客户端临时造一份。
3. 在 `src/apis/{domain}.ts` 使用本项目统一 request/transport 封装接口，并引用共享契约类型。
4. 在 `src/apis/index.ts` 导出客户端 API 实现；公共类型仍从协议子仓导出。
5. 判断是否需要 Repo：
   - 需要：接口多、转换复杂、跨页面复用、已有同域 repo、需要集中错误/日志封装。
   - 不需要：轻量接口、单页面/单 store 使用、转换简单。
6. 需要 Repo 时在 `src/repos/{domain}-repo.ts` 封装业务方法：
   - 检查 `response.errCode !== 0` 并抛出 `response.msg`。
   - 做字段默认值、后端 string/number 兼容转换。
   - 使用 `logger.logRequestStart/Success/Error` 记录。
7. 不需要 Repo 时，字段转换集中放 `src/types/{domain}.ts` 或 store/composable 的 mapper/helper，不散落到页面。

## 二、Store 与 Composable

### Store

1. 使用 `defineStore('{domain}', () => {})` setup store。
2. 状态用 `ref`，派生状态用 `computed`。
3. 常见状态：列表、`isInitialized`、`isLoading*`、`error`。
4. 列表模块应提供 `load*(forceRefresh = false)`、`add*Local`、`update*Local`、`delete*Local`、`get*ById`、`reset`。
5. 远端变更成功后同步本地缓存，必要时重新排序。
6. 排序逻辑放 store，页面不重复排序。

### Composable

1. 命名使用 `use{Feature}`。
2. 从 store 暴露页面需要的 computed 状态。
3. 统一使用 `useErrorHandler` 做 `handleAsyncError`、`showSuccess`、`showError`、`showConfirm`。
4. 导航封装为函数，使用 `uni.navigateTo` 并处理 `fail`。
5. 格式化工具可放 composable，跨模块复用时放 `src/utils`。
6. 订阅、分享、授权等产品流程放 composable；平台 API 和兼容实现放项目适配层，composable 通过统一适配接口调用。

## 错误处理

- 使用 Repo 时：Repo 抛错，store 记录日志并继续抛错或回退状态。
- 不使用 Repo 时：store/composable 统一检查 `errCode`、转换字段和抛错，页面不重复处理接口响应。
- Composable 决定是否展示 toast、confirm 和 fallback message；页面不直接吞错。

## 约束

- API 层只做 HTTP 调用，不写页面逻辑和缓存逻辑。
- 不绕过项目统一 request / transport 适配直接调用平台网络 API。
- Repo 是可选层，不为轻量接口机械新增；Repo 层不直接操作页面 toast。
- 不引入新状态库，沿用 Pinia；不把大量业务逻辑塞进 `.vue` 页面。
- 共享契约已有的类型、枚举不得在客户端复制定义；字段映射由统一协议约定或集中转换层处理，不散落在页面。
- 页面和业务状态不得直接调用平台私有 API；在确有 UI/UX 差异时才按平台区分呈现。
- 不做无关重构、无关格式化、无关依赖升级。

## 验证

- `npm run type-check`
- 对列表增删改查，至少手工检查：初次加载、强制刷新、本地缓存更新、空状态、错误提示。
- 改动 request 底层时，补充 H5 或目标小程序平台 build。
