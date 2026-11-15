# 02-5 首页布局与背景层（透明导航 + 背景设计 + 边距体系）

## 背景
豆哥：「首页导航栏都可以直接照抄用透明的，然后首页直接布局一个高级感点的背景设计 /
不要只盯着颜色，边距、布局这些更重要」。
前一轮把视觉手法（渐变、投影、阴影令牌）已经回落到 carbon，这一轮解决**结构与留白**：
导航栏形态、背景层、以及「高度链和边距各算各的」这个隐患。

## 做了什么
1. `components/so-custom.vue`
   - `transparent` 语义改为**照 carbon 的 floating**：仍占一份导航高度（`rootHeight` 恒为 `customBar`），
     只去掉背景与边框。原实现是「不占布局高度」，会让内容从屏幕顶部铺起、压在导航栏下面。
2. `styles/01-settings/_variables.scss` 新增四个令牌（浅/深各一份）
   - `--so-page-bg`：两层径向光 + 竖向渐层（照 carbon 的 `--cs-page-bg`），绿系换成品牌绿。
   - `--so-frost`：浮层磨砂面（导航胶囊 / 底部操作栏 / rail 选中），半透明 + `backdrop-filter`。
   - `--so-frost-weak`：rail 未选中淡底（照 carbon 的 `rgba(255,255,255,.04)`）。
   - （上一轮已有 `--so-grid-color` / `--so-glow-strong` / `--so-glow-soft`。）
3. `pages/index/index.vue` 重写布局
   - 新增 `.so-index__backdrop`（`absolute inset:0`、`pointer-events:none`）：
     两个品牌光斑（左上 420rpx `--so-glow-strong`、右下 360rpx `--so-glow-soft`，各带 180/160rpx 光晕 +
     `so-orb-breathe` 呼吸动画）+ 44rpx 网格线 `--so-grid-color`。照 carbon 的 `p-index__backdrop` 三件套。
   - 导航栏改 `<so-custom transparent>`，标题用主色；右侧入口胶囊改用 `--so-frost` + 模糊。
   - 容器 `.so-index`：`height: calc(100vh - var(--index-nav-height))`，纵向内边距 上 16rpx + 下 176rpx（底栏占位），
     左右 32rpx；底栏左右同 32rpx，与内容边缘对齐。
   - rail：左 32rpx、宽 108rpx、`top = 导航高 + 24rpx`；`.so-index__main` 左内边距 128rpx。
   - swiper 高度改 flex（`flex:1; min-height:0`），与 carbon 一致，去掉 `calc(100vh - ...)`。
4. 高度链对齐：`swiperHeightPx = 视口 - 导航高 - 192rpx(转 px)`，与 CSS 的纵向内边距用同一个数；
   `biz-panel-placeholder` 改为直接用传入高度（原先再减 16px，会和 CSS 差一截）。

## 结论
- **透明导航 ≠ 不占位**。carbon 的 floating 只是去掉背景边框，高度照留，内容从导航栏之下开始；
  之前自己发明的「不占布局高度」是错的，会直接让内容压到栏下。
- **边距和高度链必须用同一个数**：容器写 16+176rpx，模块高度就得按 192rpx 换算，
  否则 scroll-view 比可视区高几十 px，内容会被底栏切掉一截。抽成 `CONTAINER_V_PADDING_RPX` 常量两边共用。
- 背景「高级感」来自**层次**（渐层底 + 光斑 + 网格 + 磨砂浮层）而不是颜色本身；
  豆哥明确说边距/布局比颜色重要，所以这轮先把 margins 和高度链理顺，颜色只做碳抄绿换色。

## 被推翻的判断
- 上一轮把 rail 选中态定为 `--so-bg-elevated`（不透明白）。有背景层之后不透明白块会显得「贴」在背景上，
  改回 carbon 的磨砂半透明 `--so-frost` + `backdrop-filter`。
- `so-custom` 的 `transparent` 原注释「透明悬浮态不占布局高度」——是照 cover 页的想象写的，
  carbon 里没有这种用法，已改。

## 验证
- `npm run type-check` 通过；`npm run build:mp-weixin` 成功。
- `dist/build/mp-weixin/app.wxss` 含 `--so-page-bg` / `--so-frost` / `--so-frost-weak`（浅深两份）。
- `dist/.../pages/index/index.wxss` 含 `.so-index__backdrop` / `orb--brand` / `orb--soft` /
  `.so-index__grid`（`inset:0` 已被编译成 top/right/bottom/left，小程序端安全）/ `@keyframes so-orb-breathe-*`。
- `dist/.../pages/index/index.wxml` 里 `<so-custom class="so-index__nav data-v-...">` 确认父级 scoped 命中。

## 待核
- 真机/模拟器目测：透明导航下的状态栏对比度（项目约定未接 `setNavigationBarColor`，深色模式状态栏仍是 black）。
- `backdrop-filter` 在部分 Android 基础库不生效时的观感（退化为半透明纯色，可接受）。
- 首页在演示模式下走的是 `so-page` 的 `#demo` 插槽，要用管理员开关切到真实模式才看得到这套布局。
