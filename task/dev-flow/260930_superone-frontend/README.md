# Superone 前端开发

## 目标

推进 `business-repo/uni-superone`（Superone 通用 uni-app 前端）的开发。

首个具体开发范围**待豆哥指定**（当前仅知从空白预设起步，详见「边界」）。建此任务的动作本身已完成，范围确认后按 dev-flow 出方案再动手。

## 资源范围

- 主仓：`business-repo/uni-superone`
- 技术栈：uni-app（Vue 3 + TS + Pinia + Vite）、`@dcloudio/uni-app` 3.0、pinia 2、vue-i18n、marked、mp-html
- 当前状态：空白预设，仅 `src/pages/index/index.vue` 一个页面，`release` 分支、工作区干净、与 `origin/release` 同步

## 边界

- 本仓只改跨端前端（页面、组件、样式、路由、前端状态、基于现有接口的交互流程）。
- 一旦涉及参数、字段、枚举、错误码、权限等接口语义变化，或需新增服务端接口，必须回到工作台编排 `business-repo/backend-superone` 与 `business-repo/frontend-contracts`，不在本仓私自改协议。
- 纯前端任务，dev-flow 跳过 `01` 后端阶段；流程为 `00 方案设计 → 02 前端开发 → 03 整体验证`。

## 参考仓库（只读）

- `business-repo/uni-superone-backup` 是**旧版** superone 前端快照（被裁剪前的完整版本，含 `src/stores`、`src/apis`、`src/styles` 等 + `node_modules` + `.git`，约 301MB）。
- **仅供参照，禁止基于它开发，也不要改动或提交它。** 当前活跃开发仓是 `business-repo/uni-superone`（8 文件最小品牌骨架）。
- 该目录已在 workbench 根 `.gitignore` 中，不会被误提交。

## 待确认

- **开发范围**：豆哥后续指定首个功能/页面或基线架构目标。
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
- 待补：品牌色为中性占位，待规范替换；运行时主题切换（根容器挂 `.theme-light` / `.theme-dark`）待实现；分支仍在 `release`、改动未提交。

## 状态

- `260930` 建任务目录，范围待指定；样式基础（ITCSS + SCSS）已落地。

## 路由

- 需求明确后走 `dev-flow-0000-plan-flow` 出方案（落本目录 `README.md` 或方案文档），确认后派发 `dev-flow-0201` 起的前端开发 skill，收口走 `dev-flow-0301-verify-flow`。
- 仅前端文案/样式/交互/页面结构调整，且接口语义不变时，可直接在本仓处理。
