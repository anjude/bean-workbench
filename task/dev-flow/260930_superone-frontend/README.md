# Superone 前端开发

## 目标

推进 `business-repo/uni-superone`（Superone 通用 uni-app 前端）的开发。

当前前端范围：已完成首页品牌骨架、主题、清单和近期任务模块；本轮按 backup 与 Carbon/Superone 设计原则接入物品模块。近期任务决策见 [计划模块功能清单](plan-module-inventory.md)，物品模块决策见 [物品模块功能清单](plan-item-inventory.md)。

## 资源范围

- 主仓：`business-repo/uni-superone`
- 提醒消息跳转适配：`business-repo/backend-superone`（物品提醒默认进入路径，携带物品 `id`）
- 技术栈：uni-app（Vue 3 + TS + Pinia + Vite）、`@dcloudio/uni-app` 3.0、pinia 2、vue-i18n、marked、mp-html
- 当前状态：已接入主题、清单、近期任务和物品模块；前端 `release` 分支有未提交改动，本次未提交或推送。

## 边界

- 本任务主要改跨端前端（页面、组件、样式、路由、前端状态、基于现有接口的交互流程）；因提醒消息需指向新详情路由，后端只调整 Item 提醒消息的默认进入路径，不改 API 契约或其他订阅类型。
- 一旦涉及参数、字段、枚举、错误码、权限等接口语义变化，或需新增服务端接口，必须回到工作台编排 `business-repo/backend-superone` 与 `business-repo/frontend-contracts`，不在本仓私自改协议。
- 纯前端任务，dev-flow 跳过 `01` 后端阶段；流程为 `00 方案设计 → 02 前端开发 → 03 整体验证`。

## 参考仓库（只读）

- `business-repo/uni-superone-backup` 是**旧版** superone 前端快照（被裁剪前的完整版本，含 `src/stores`、`src/apis`、`src/styles` 等 + `node_modules` + `.git`，约 301MB）。
- **仅供参照，禁止基于它开发，也不要改动或提交它。** 当前活跃开发仓是 `business-repo/uni-superone`（8 文件最小品牌骨架）。
- 该目录已在 workbench 根 `.gitignore` 中，不会被误提交。

## 待确认

- **分支策略**：仓内现仅 `master` / `release` 两条分支，`uni-superone/AGENTS.md` 标注默认分支为 `release`；与 `backend-superone` 的 `dev → release` 约定不一致。需豆哥确认前端在哪条分支开发、是否新开 `dev` 分支。
- **与 uni-carbon-space 的关系**：carbon「边界」等能力归属 `uni-carbon-space`，本仓是「通用 uni-app 前端」，需确认两者是否共用代码或各自独立。

## 约定（参照 uni-carbon-space）

- superone 前端的**技术栈与编码写法参照 `uni-carbon-space`**（carbon 是已落地样板）。
- **样式必须支持浅色 / 深色双模式**，主题命名不能重复 carbon 的错误：
  - carbon 用 `day` / `night` 作主题标识，命名与接线被豆哥判定为**反向（已弄反）**。
  - superone 改用自解释的 **`.theme-light` / `.theme-dark`**，映射严格正确：`.theme-light` = 浅色令牌（浅底深字），`.theme-dark` = 深色令牌（深底浅字）。
  - 令牌统一用 `--so-*` CSS 自定义属性（静态令牌如间距/圆角/字号同时保留 SCSS 变量供工具类 `@each` 生成）；浅色为默认（`:root` 即浅色令牌），运行时在根容器挂 `.theme-light` / `.theme-dark`。
  - 禁用 `day` / `night` 主题命名，避免在 superone 重现 carbon 的反向错误。

## 进展

- `260930` 样式基础落地 + 双主题：新建 `src/styles/`（ITCSS + SCSS），参考 `uni-carbon-space/src/styles` 分层与 `App.vue` 接入。`App.vue` 一次性 `@use './styles/index'`；令牌改为 `--so-*` CSS 自定义属性，支持浅色/深色双模式（`.theme-light` / `.theme-dark`，浅色为默认，映射正确，**不用 carbon 的 day/night 反向命名**）；静态令牌（间距/圆角/字号）同时保留 SCSS 变量供工具类 `@each` 生成。`uni.scss` 不再注入令牌（CSS 变量经层叠全局可用，避免重复 `:root`）。本地 `sass 1.90.0` 编译 `index.scss`/`uni.scss` 均通过。详见 `process/02-1-style-foundation.md`。
- 约定：superone 技术栈与写法参照 `uni-carbon-space`（见上文「约定」段）。
- `2026-10-05`：近期任务接入首页计划面板，包含状态筛选、分页、置顶、任务 CRUD、详情、进展日志与任务快照记录；筛选状态缓存恢复；不做搜索和 OKR。过程记录见 [`process/02-25-recent-task-module.md`](process/02-25-recent-task-module.md)。
- `2026-10-06`：物品模块接入首页，包含简单分类/状态筛选、分页、物品 CRUD、置顶、图片上传、提醒设置和使用日志；物品提醒在微信小程序端请求订阅权限，拒绝授权仍保存设置并提示；后端默认订阅跳转携带物品 id。独立订阅展示/配置页不迁移。不做关键词搜索、标签编辑和 demo 初始化。过程记录见 [`process/02-26-item-module.md`](process/02-26-item-module.md)。
- 本任务当前变更尚未运行前端 type-check/build，也未做微信小程序真机验收；业务仓工作区还有此前未提交的主题、清单、近期任务改动，提交前需一并区分核对。
- 待补：品牌色为中性占位，待规范替换；分支仍在 `release`、改动未提交。三态主题已按下文方案实现，验证尚未运行。

## 三态界面主题方案与落地

### 现状与差异

- Carbon 的主题偏好是浅色、深色、系统三态；设置页点击主题行循环切换，并显示当前偏好标签。
- Superone 当前 `ThemeMode` 只有 `light` / `dark`。无缓存时只读取一次系统主题作为初值，用户切换后只保存显式浅/深模式；设置页使用二态 switch，没有「跟随系统」选项，也没有运行时同步系统主题变化。
- `test-theme` 预览页直接把 `theme` 当成已解析的明暗状态；增加 system 偏好后需改用解析后的主题状态。

### 目标与边界

- 主题偏好扩展为 `light` / `dark` / `system`；浅色和深色仍使用 `.theme-light` / `.theme-dark`，**不创建 `.theme-system`**，不引入 Carbon 的 `day` / `night` 命名。
- 浅色/深色偏好固定对应外观；系统偏好读取设备当前主题，并在系统主题变化时更新页面主题。
- 系统主题来源沿用 Carbon 的平台分层：微信小程序需在 `manifest.json` 开启 `mp-weixin.darkmode`，再读 `getAppBaseInfo().theme` 并监听 `uni.onThemeChange`；H5 读 `matchMedia('(prefers-color-scheme: dark)')` 并监听媒体查询变化；不支持读取/监听的平台回落浅色，并在页面重新显示时刷新。
- 旧缓存 `light` / `dark` 原样兼容；没有缓存或缓存值无效时采用 `system`，设备主题无法识别时回落浅色。
- 不改后端、接口、数据库、CSS 令牌语义、页面路由或业务数据。

### 产品原型与交互

- 原型：`config / settings`。修改个人本地显示偏好，不产生业务数据。
- 设置页「界面主题」改为 Carbon 式可点击行，副标题显示「当前浅色 / 深色 / 跟随系统模式」，尾部 chip 显示「浅 / 深 / 系统」。点击按「浅色 → 深色 → 跟随系统 → 浅色」循环。
- 主操作：点击主题行切换偏好；次操作：无。页面不再显示二态 switch。
- 反模式：把 `system` 直接映射成 CSS 类；把系统当前是深色误当成用户偏好 `dark`；系统偏好下监听到 OS 变化后仍不更新。

### 状态矩阵摘要

| 场景 | 显示与行为 |
|---|---|
| 首次进入/无缓存 | 偏好为 `system`，按设备当前主题渲染；无法读取时用浅色 |
| 旧缓存 `light` / `dark` | 保留显式偏好，不被设备主题覆盖 |
| 用户选择浅色/深色 | 固定渲染 `.theme-light` / `.theme-dark` 并持久化偏好 |
| 用户选择跟随系统 | 偏好持久化为 `system`，解析后只挂 `.theme-light` / `.theme-dark` |
| 系统主题发生变化 | 仅当偏好为 `system` 时更新解析主题与整页主题类；显式偏好不变 |
| 页面重新显示 | 重新读取系统主题，避免应用在后台期间系统外观变化导致过期 |

### 文件级范围

| 文件 | 动作 | 说明 |
|---|---|---|
| `business-repo/uni-superone/src/composables/useTheme.ts` | 已改 | 分离保存的 `ThemeMode` 与实际解析主题；默认 system、系统主题监听、标签与三态循环 |
| `business-repo/uni-superone/src/manifest.json` | 已改 | 开启微信小程序 `darkmode`，让系统主题 API 与变化监听可用 |
| `business-repo/uni-superone/src/App.vue` | 已改 | 应用从后台返回时刷新系统主题 |
| `business-repo/uni-superone/src/pages/profile/profile.vue` | 已改 | 设置页主题行改为 Carbon 式当前模式说明与状态 chip，移除二态 switch |
| `business-repo/uni-superone/src/pages/test-theme/test-theme.vue` | 已改 | 用解析主题决定预览明暗，保证测试页在 system 偏好下正确显示 |
| `business-repo/uni-superone/src/styles/06-pages/_p-profile.scss` | 已改 | 增加主题状态 chip 样式 |

### 验收标准

1. 设置页可循环选择浅色、深色、跟随系统，当前模式文案/chip 正确。
2. 重启后记住三种偏好；既有 `light` / `dark` 缓存仍有效；无缓存默认为 system。
3. system 模式下改变系统外观，Superone 实际主题类同步；light/dark 模式不受系统变化影响。
4. 全程只使用 `.theme-light` / `.theme-dark`，浅深令牌映射正确。
5. `npm run type-check`、`npm run build:h5`、`npm run build:mp-weixin` 通过；手动核对三种偏好、系统切换、旧缓存和浅深色设置页。

### 推荐实施顺序

1. `dev-flow-0201-archetype-flow`：本节已给出原型与状态矩阵，确认后进入数据/全局主题状态层。
2. `dev-flow-0202-data-flow`：改造 `useTheme` 偏好持久化、系统主题解析和监听。
3. `dev-flow-0203-page-flow`：修改 profile 主题选择行与 `test-theme` 预览。
4. `dev-flow-0301-verify-flow`：运行 H5/微信小程序检查并回填验收结果。

方案已由用户确认并实现；实际改动和未运行的验证记录见 `process/02-27-three-state-theme.md`。

## 状态

- `260930` 建任务目录；样式基础（ITCSS + SCSS）已落地。当前前端工作区包含未提交模块实现。

## 路由

- 需求明确后走 `dev-flow-0000-plan-flow` 出方案（落本目录 `README.md` 或方案文档），确认后派发 `dev-flow-0201` 起的前端开发 skill，收口走 `dev-flow-0301-verify-flow`。
- 仅前端文案/样式/交互/页面结构调整，且接口语义不变时，可直接在本仓处理。
