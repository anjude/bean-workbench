# 261015 uTools Bean Option 日常维护

## 目标

集中承接 `utools-bean-option` 的日常维护需求，让问题、方案、改动、验证和交接上下文持续可查。

## 范围

- 主仓：`business-repo/utools-bean-option`，包括桌面端页面、交互、本地工具逻辑、插件入口与构建维护。
- 任务记录：本目录的 `README.md`、`process/` 和 `handoff/`。
- 具体需求涉及其他业务仓时，再按实际依赖确认影响范围。

## 边界

- 本目录是日常维护入口；已有明确目标的专项任务继续使用各自目录。
- 新的开发需求仍先走 `dev-flow-0000-plan-flow` 形成方案，按涉及阶段实施并完成 `dev-flow-0301-verify-flow` 验证。
- 当前只建立任务上下文，尚无具体维护项或业务仓代码改动。

## 当前状态

进行中。首个维护项“汇率换算货币列表重新进入后消失”已完成代码修复与静态验证，待 uTools 插件内实际退出重进验收。

## 沉淀候选

- 可复用的 uTools 插件维护和排错经验，稳定后沉淀到知识库或相关 skill。
- 重复出现的检查与构建步骤，评估是否适合脚本化。

## 汇率换算货币列表记忆（2026-10-15）

### 背景与需求理解

用户添加货币后，退出并重新进入汇率换算，新增货币消失。期望插件记住当前货币列表及其顺序，添加或删除后重新进入仍保持该列表。

### 现状与原因

- `business-repo/utools-bean-option/src/views/FxConverter.vue` 中的 `rows` 每次组件创建都固定初始化为 CNY、USD、EUR、JPY、HKD、GBP。
- 当前 `fx_rate_cache_v1` 只保存汇率和更新时间；`handleConfirmAdd`、`handleRemove` 只修改内存数组，没有持久化。
- `business-repo/utools-bean-option/src/utils/storage.ts` 已封装 uTools `dbStorage`，汇率缓存已使用；`business-repo/utools-superone/src/utils/adapt/storage.ts` 也以 `dbStorage` 保存插件数据，可参考其存储边界。

### 目标与边界

#### 本期目标

- 添加、删除货币后立即保存当前货币代码及顺序；重新进入时恢复。
- 首次进入或缓存不可用时继续显示原有默认货币列表。
- 恢复时过滤未知代码和重复代码；合法空列表不作为持久化结果，因为页面至少保留一行。

#### 本期不做

- 不保存输入金额、小数位设置或汇率数据以外的页面状态。
- 不迁移现有汇率缓存键及内容，不改汇率抓取逻辑。

### 改动范围

- 业务仓：`business-repo/utools-bean-option`。
- 文件：`src/views/FxConverter.vue`，新增独立的货币列表缓存键，组件初始化时读取，添加和删除后写入；继续使用现有 `src/utils/storage.ts` 的 uTools `dbStorage` 封装。
- 库表、接口、共享契约：无。此功能只涉及插件本地存储。
- 页面状态：首次使用显示默认列表；有有效缓存显示保存的列表；缓存损坏或代码过期时过滤并回退到默认列表；存储失败时当前会话仍可操作。
- 资产与品牌：无改动。

### 实施方案

1. 将默认货币代码列表定义为常量，用它创建初始 `rows`。
2. 增加独立缓存键，仅存 `CurrencyCode[]`，避免将响应式行对象、金额和汇率写入持久化数据。
3. `onMounted` 时先读取并校验保存的代码列表，再按原顺序创建行；缺失或校验后为空时保留默认列表。
4. 添加和删除成功后保存 `rows` 中的代码数组；汇率缓存加载和刷新仍按现有流程执行。

### 验收标准与测试方案

| 场景 | 操作 | 预期结果 |
| --- | --- | --- |
| 添加后重进 | 添加新货币、退出插件、重新进入汇率换算 | 新货币和列表顺序保持 |
| 删除后重进 | 删除一个货币、退出并重新进入 | 被删货币不再显示，剩余顺序保持 |
| 首次使用 | 清空新增列表缓存后进入 | 显示原有六种默认货币 |
| 旧数据兼容 | 仅有现存 `fx_rate_cache_v1` 汇率缓存 | 汇率照常读取，货币列表显示默认项 |
| 异常缓存 | 缓存含未知或重复代码 | 仅恢复已支持的唯一代码；无有效代码则回退默认列表 |
| 汇率回归 | 刷新汇率、输入金额换算 | 当前货币列表保留，汇率和换算正常 |

静态验证：在 `business-repo/utools-bean-option` 运行 `npx vue-tsc --noEmit` 和 `npm run build`。uTools 进出插件的实际持久化行为需在插件运行环境验收。

### 风险与回滚

- `dbStorage` 写入失败时，当次操作仍在页面内可见，但无法跨重进保留；实现时应避免写入异常中断交互。
- 回滚时移除新增列表缓存读写即可，原 `fx_rate_cache_v1` 不受影响。

### 落地记录

已修改 `business-repo/utools-bean-option/src/views/FxConverter.vue`：将货币代码及顺序保存至独立的 `fx_currency_list_v1`，添加、删除后立即写入，进入汇率页面时恢复；无有效缓存时保留默认列表。原汇率缓存与抓取流程未改。

子仓 `release` 已提交：`ff82ea2 261015 修复汇率货币列表缓存`。

验证结果：

- `npm run build`：通过；构建仍提示既有 `follow.svg` 路径与大包体积警告。
- 当前依赖组合的 `npx vue-tsc --noEmit` 无法启动：`vue-tsc@1.8.27` 与 `typescript@5.8.2` 不兼容。
- 使用同工作台 `utools-superone` 已安装的 `vue-tsc@2.2.12` 全仓检查：存在原有 `src/utils/request.ts` 引用不存在的 `~/router` 错误。
- 使用上述检查器仅检查 `src/views/FxConverter.vue` 及其引用：通过；临时检查配置已移除。
- `git diff --check`：通过。尚未在 uTools 插件内执行退出重进的手工验收。

## 参照 uTools Superone 重构的工作量评估（2026-10-15）

### 现状对比

| 维度 | Bean Option | uTools Superone |
| --- | --- | --- |
| 基础技术 | Vue 3、TypeScript、Vite、Element Plus | 同样使用 Vue 3、TypeScript、Vite、Element Plus |
| 规模 | `src` 约 47 个文件，3 个主要页面 | `src` 约 215 个文件，包含多个业务模块 |
| 应用组织 | `App.vue` 条件切换 3 个工具，页面承担较多状态逻辑 | Vue Router、Pinia、Composable、适配层与分层样式 |
| 本地存储 | 直接使用 `dbStorage`，部分设置使用 `localStorage` | `CacheManager` 统一入口及 uTools/浏览器存储适配 |
| 质量门禁 | 只有 `dev`、`build` 脚本 | 类型检查、lint、契约检查、构建等组合命令 |

### 建议范围与粗估

以下为单人开发的初步估算，含改动和基础验证，不含等待产品反馈的时间：

| 范围 | 主要内容 | 估算 |
| --- | --- | --- |
| 只修货币列表记忆 | 沿用现有 `dbStorage`，补列表读写和回归验证 | 0.5～1 天 |
| 对齐基础架构 | 统一存储适配与缓存入口、引入页面路由、拆分页面状态、补类型检查和构建门禁，保留现有视觉 | 3～5 天 |
| 全面靠齐 Superone | 再迁移样式体系、状态管理、国际化、代码规范，并梳理旧 API/model 与页面组件 | 1～2 周，需先确定哪些能力确实要保留 |

### 建议实施顺序

1. 先修货币列表记忆，单独完成持久化闭环与 uTools 实机验收。
2. 再统一 `storage` / `localStorage` 的平台适配和缓存使用，确认滚动计算器历史、主题、汇率缓存的现有数据能读回。
3. 按实际页面复杂度引入 Router、状态拆分及检查命令；Pinia、i18n 和 Tailwind 仅在明确需要跨页共享、语言切换或新样式体系时加入。

### 主要风险与决策点

- 已有滚动计算器数据、历史记录、主题和汇率缓存属于真实存量；变更存储键或格式时必须先设计兼容读取与迁移，并单独确认写入范围。
- `src/api/`、`src/model/` 有未被当前三个页面引用的文件；清理它们应先核对插件入口和外部使用，不能凭目录名直接删除。
- uTools Superone 的后端协议、登录流程和业务 Store 不适合直接复制到本地计算工具。

当前仅完成评估，没有开始重构，也没有修改业务仓代码。

## 子模块默认分支调整（2026-10-15）

- 工作台 `.gitmodules` 将 `business-repo/utools-bean-option` 的跟踪分支从 `master` 改为 `release`。
- 子仓本地从 detached HEAD 切到跟踪 `origin/release` 的 `release` 分支；切换时两者指向相同提交，原有未提交改动保留。
- 已从远端抓取 `release` 并核对，本地 `release` 与 `origin/release` 无领先或落后提交。
- `kb/business-repo/README.md` 已同步分支说明；GitHub 仓库的网页默认分支设置未调整。

## 子仓提交与推送（2026-10-15）

- `utools-bean-option` 的 `release` 已推送到 `origin/release`，包含缓存修复提交 `ff82ea2` 和旧 `.cursor/rules/` 清理提交 `6aafd73`。
- 工作台子模块指针更新到 `6aafd73`；GitHub 仓库网页默认分支设置未改动。
