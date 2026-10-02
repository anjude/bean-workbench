# 02-7 导航入口位置 + 胶囊圆角的椭圆弧 bug

## 背景
豆哥（在确认 `:root` 修复生效后）：「1. 首页的导航栏，设置按钮应该放到左侧 2. 新建清单的按钮圆弧太丑了，你看看carbon怎么弄的」。

## 做了什么
1. **导航栏设置入口移到左侧**
   - `pages/index/index.vue`：profile 入口从 `#right` 改到 `#left`（so-custom 已有 `#left` 插槽，落在 `.so-bar__left`）。
   - 理由：右侧是微信原生胶囊的地盘（so-custom 已经做了 padding-right 避让），自己的操作放左侧。
   - 标题仍是绝对定位居中（left 16px / right 胶囊避让），左侧按钮只占 8–42px，不遮挡。
2. **底栏主按钮照 carbon 的 `.p-index__tabbar-action--primary` 重做尺寸**
   - `height: 78rpx` / `min-width: 190rpx` / `padding: 0 24rpx` / `font-size: 24rpx`
   （原先是 `.so-btn` base 的 88rpx 高 + 30rpx 字 + 32rpx 横向留白，又矮又胖）。
3. **修胶囊圆角的椭圆弧 bug（真因）**
   - 原先写 `border-radius: var(--so-radius-full)`，而 `--so-radius-full: 50%`。
     **50% 是相对自身宽高的百分比**：在 184×74 这种扁矩形上，水平半径 = 92rpx、垂直半径 = 37rpx
     → 渲染成**椭圆弧**，看起来就是"怪怪的圆弧"。
   - carbon 的 `--cs-radius-full` 同样是 50%，但它只在**正方形**元素上用（avatar、splash 圆点、`.rounded-full`）；
     胶囊/药丸一律写死 `999rpx`（`.p-index__tabbar-action` 就是 999rpx），固定大值会被 clamp 到短边一半 = 正圆角。
   - 全仓扫出 5 处扁矩形误用，全部改成 `999rpx`：
     `pages/index/index.vue`（底栏主按钮）、`components/so-page.vue`（重试按钮、切换场景按钮）、
     `pages/profile/profile.vue`（分享按钮）、`pages/test-theme/test-theme.vue`（主题预览按钮）。
     保留 50% 的只有：`.round` 工具类、profile 头像（正方形）、首页光斑（正方形）。
   - `_variables.scss` 的 `$so-radius-full` 处加注释，写清「50% 只给正方形，胶囊用 999rpx」。

## 结论
- **`--radius-full: 50%` 不是"胶囊"，是"正圆"**。想做药丸必须写 `999rpx`。
- 看 carbon 不能只看它"有没有用圆角"，要看它**在什么形状的元素上用**——同样是 50%，
  用在正方形是对的，用在扁按钮上是 bug。

## 验证
- `npm run type-check` 通过；`npm run build:mp-weixin` 成功。
- `pages/index/index.wxml`：`u-s="{{['content','left']}}"`（左侧插槽生效）。
- `pages/index/index.wxss`：`.so-index__tabbar-action{...height:78rpx;min-width:190rpx;...border-radius:999rpx}`。
- 残留 `border-radius:50%` 只剩 orb（正方形）与 profile 头像（正方形）。

## 待核
- 真机目测：左侧设置按钮与标题的间距；底栏主按钮在 78rpx 高下是否还够点击（微信建议 ≥ 44px，78rpx ≈ 39px，
  但父级底栏本身 108rpx 高，整条可点区域够大）。
