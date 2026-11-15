# 02-11 自定义导航栏标题没居中

> 豆哥：「首页的navigate title没有居中」。

## 定位
- 标题定位在 `so-custom.vue` 的 `titleStyle`：`left:{x}px;right:{y}px;top:{statusBar}px;`。
- 原写法左边留 16px（有返回/主页时 96px），右边留 `胶囊右间距 + 胶囊宽 + 8`（实测约 105px）。
- 左右留白不对等 → 这个区间的中点落在屏幕中线**左侧**（375 宽屏上偏左约 44px），标题看着就不居中。
  容器内部有 `justify-content:center`，但居中是相对这个偏左的区间，不是屏幕。

## carbon 怎么做
- `.cu-bar .content`：`position:absolute; left:0; right:0; margin:auto; width:calc(100% - 440upx)`。
- 440upx 是**左右各 220upx**，即两侧留白对称 → 标题落在屏幕中线。
- 坑点记录：`.cu-custom .cu-bar` 上那个 `padding-right: 220upx` **管不到**标题——绝对定位元素的包含块是
  padding box，左右边界不受 padding 影响；真正让标题居中靠的是 `width` + `margin:auto` 的对称留白。

## 修法
`titleStyle` 改为两侧对称，留白取两侧占位的较大者：
```ts
const capsuleGap = capsuleWidth > 0 ? capsuleRight + capsuleWidth + 8 : 16
const actionGap = props.isBack || props.isHome ? 96 : 16
const gap = Math.max(capsuleGap, actionGap)   // left/right 都用同一个 gap
```
比 carbon 的固定 220upx 更贴合真机（用实测胶囊几何，不同机型自适应）。
非小程序环境 `capsuleWidth=0` → gap=16，仍然对称。

## 验证
- `npm run type-check` / `npm run build:mp-weixin` 通过。
- 需在真机/模拟器上确认：首页标题「SuperOne」落在屏幕中线，左侧设置按钮（68rpx 胶囊）不与标题重叠
  （对称 gap 约 105px，按钮连外边距约 50px，不会撞上）。

## 附带结论
- 微信胶囊在右侧，所以「居中」必须是**屏幕中线居中**，不是「可用区居中」。以后任何贴顶元素
  （标题、tabs）都按这个口径对齐。
