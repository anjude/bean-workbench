# 02-6 真机没颜色：令牌挂在 `:root` 上被整条丢弃

## 现象
豆哥：「真机就是没有颜色」→ 追问后确认**只有浅色模式没颜色**（网格、光斑、卡片、按钮全丢），
**深色模式正常**，**开发者工具模拟器正常**。

## 排查
1. 先怀疑「真机不支持 CSS 变量」——被深色正常否决：变量在真机是工作的。
2. 对照 carbon 的 `styles/01-settings/variables.css`，发现结构差异：
   - carbon：静态组 `page, .theme-day, .theme-night`，浅色组 `page, .theme-day`，深色组 `.theme-night`，**全仓零 `:root`**。
   - superone：静态组 `:root`，浅色组 `:root, .theme-light`，深色组 `.theme-dark`。
3. 结论：小程序渲染层没有 html 元素、不认 `:root`。而 **CSS 的逗号选择器列表不是容错的**——
   一个选择器不认识，**整条规则被丢弃**。所以浅色令牌（含间距/圆角/字号/层级这些静态令牌）在真机全丢；
   深色是单选择器 `.theme-dark` 所以正常；开发者工具是 Chrome 内核认 `:root` 所以模拟器正常。
   三者表现完全对得上。

## 修法（照 carbon）
- 静态令牌 → `page, .theme-light, .theme-dark { }`
- 浅色令牌 → `page, .theme-light { }`
- 深色令牌 → `.theme-dark { }`（不挂 page）
- `_variables.scss` 头部写明「绝不能用 `:root`」及原因。

## 连带修的两处
1. `03-elements/_base.scss`：**`page` 不再设 `background-color: var(--so-bg-base)`**。
   page 永远只拿得到浅色令牌（深色令牌只在 `.theme-dark` 子树里），设了就是深色模式露白底。
   照 carbon：page 只定字体与前景，背景交给各页面根容器（so-page / index shell / profile shell）铺满提供。
2. ~~`background` 简写里的 `var()` 在真机不稳~~ —— **这条是我先前的误判，已作废**（见下）。
   当时也顺手把 var() 从简写改成具体属性并加了硬编码兜底，豆哥一句「你看 carbon 是用 background var 吗」
   把我打回去查证：**carbon 全仓 110 处 `background: var(...)`**，其中 `p-invite/p-feedback` 的页面容器就是
   `background: var(--cs-page-bg)`，`.cs-btn-primary` 更是
   `linear-gradient(135deg, var(--cs-glow), var(--cs-glow-dark))`，渐变里直接嵌 var，线上真机正常。
   → 兜底全部撤掉，与 carbon 保持一致：
   - `.so-index-shell` 回到 `background: var(--so-page-bg)`，删除实色兜底与 `.theme-dark` 兜底块
   - `.so-index__orb--brand/--soft`、`.so-demo`、`.so-bar`、`.so-bar__actions--capsule` 回到 `background: var(...)`
   - `05-components/_button.scss` 删除品牌绿硬编码兜底（`.so-btn-primary` 改成
     `background: linear-gradient(135deg, var(--so-color-primary), var(--so-color-primary-strong))`，
     `.so-btn-secondary` 去掉 color/border 双写）

## 结论
- **小程序端的全局令牌只能挂 `page` 和主题类，不能碰 `:root`**。uni-app 自己生成的
  `page{--status-bar-height:...}` 也是挂 page 的，可作佐证。
- 真机与模拟器的差异，先查「渲染引擎认不认这个选择器」，不要急着怀疑 CSS 变量本身。
- 「深色正常、浅色不正常 + 模拟器正常」这组症状，一眼就該想到选择器列表容错问题。
- **作废旧结论**：「真机对 `background` 简写里的 var() 支持不稳」是误判（当时观察到的按钮底色消失，
  真因就是 `:root` 丢令牌，不是 var 在 background 里的问题）。carbon 110 处 `background: var(...)`
  是反证。**不要为想象中的真机兼容性写硬编码兜底**——先回来看 carbon / 线上代码怎么用。

## 验证
- `npm run type-check` 通过；`npm run build:mp-weixin` 成功。
- `dist/build/mp-weixin/app.wxss`：`:root` 出现 0 次；三组令牌分别为
  `page,.theme-light,.theme-dark{...}` / `page,.theme-light{...}` / `.theme-dark{...}`；`page{...}` 只剩 uni 自己的窗口变量。
- `pages/index/index.wxss`：`.so-index-shell{...background-color:#f4f7f5;background-image:var(--so-page-bg)...}`。

## 待核
- 真机重新编译后目测浅色模式（需整包重编译 + 真机预览，别走热重载）。
- 深色模式下页面回弹/overscroll 区域可能露系统白底（`page` 已不设背景）；若明显再考虑
  `uni.setBackgroundColor` 跟随主题。
