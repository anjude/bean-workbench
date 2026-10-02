# 02-1 样式基础（ITCSS + SCSS）

- 时间：2026-09-30
- 阶段：dev-flow 02 前端开发（首个落地动作）
- 做了什么：
  - 新建 `src/styles/`（ITCSS 分层，SCSS 版），参考 `uni-carbon-space/src/styles` 的分层结构与 `App.vue` 接入方式。
  - 分层：`01-settings`(令牌+混合) / `02-generic`(normalize) / `03-elements`(base) / `04-objects`(layout) / `05-components`(占位) / `06-pages`(占位) / `06-utilities`(flex/spacing/text/colors) / `07-vendors`(占位)。占位目录用 `.gitkeep` 保留。
  - 令牌用 SCSS 变量 `$so-*`（用户拍板：编译期、零运行时、暂不做换肤）。品牌色用中性占位值，待 superone 品牌规范替换。
  - spacing/text 工具类用 `@each` 映射生成，减少样板。
  - 接线：`App.vue` 全局 `<style lang="scss">` 一次性 `@use './styles/index'`（原 `@import`，为消除 Dart Sass 弃用警告改 `@use`）；`uni.scss` 注入 `01-settings` 的写法后已移除（见补充：组件改用 `var(--so-*)`，CSS 变量经层叠全局可用，避免重复 `:root`）。
- 结论：完整 ITCSS 骨架就位，基础样式可用。
- 验证：本地 `sass 1.90.0` 编译 `index.scss` 与 `uni.scss` 均通过；`index.scss` 输出含 normalize/base/layout/全部工具类，`uni.scss` 仅输出 uni 内置变量、无多余 CSS。
- 待核 / 待定：
  - 分支策略：改动仍在 `release` 分支、未提交；等豆哥确认前端在哪条分支开发（uni-superone `AGENTS.md` 标默认分支 `release`，与 backend 的 `dev→release` 不一致）。
  - 品牌色：当前中性占位，需豆哥给 superone 品牌规范后替换 `01-settings/_variables.scss`。
  - 与 uni-carbon-space 关系：未定（carbon 能力在 uni-carbon-space，本仓是通用前端）。
- 补充（同阶段 · 双主题改造）：令牌层由静态 SCSS 变量改为 `--so-*` CSS 自定义属性以支持浅/深双模式；主题类用 `.theme-light` / `.theme-dark`（浅色默认、映射正确：浅底深字 / 深底浅字），**规避 carbon 的 `day`/`night` 反向命名**。静态令牌（间距/圆角/字号）仍保留 SCSS 变量供 `@each` 生成工具类。`uni.scss` 移除对 settings 的 `@use`，避免 `:root` 块被注入每个组件导致重复 CSS；组件改用 `var(--so-*)`。`_base` / `_colors` / `_text`(颜色类) / `_layout` 已切到 `var(--so-*)`，并在 `_text.scss` 删掉与 `_colors.scss` 重复的颜色类。编译复验通过（`:root` / `.theme-light` / `.theme-dark` 三块齐全）。
