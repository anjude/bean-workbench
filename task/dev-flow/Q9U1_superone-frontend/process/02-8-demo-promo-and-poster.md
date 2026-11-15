# 02-8 演示态宣传页（执行清单）+ 分享海报

> 豆哥：「演示页面我们也参考carbon的做法，弄一个执行清单的宣传页，增加导出分享海报的功能」。

## 调研：carbon 怎么做
- 演示/兜底页 = `cu-page.vue` 的 fallback（`reverse` 且非真实态时展示），结构：
  1. `hero-card`：eyebrow + 大标题 + 描述 + 纯 CSS 视觉 + 三项 stats
  2. `poster-card`：区块标题 + **页面上一个 DOM 版海报预览**（glow/grid/header/badge/facts/quote）
     + 「保存图片」按钮 + **离屏 canvas**（`position:fixed; left:-9999px; width:1080px; height:1680px; opacity:0`）
  3. 知识卡片列表
  4. 生活场景列表
  5. `admin-card`（管理员切换模式，仅 admin 可见）
- 海报能力 = `composables/usePosterShareCard.ts`：
  - `uni.createCanvasContext(canvasId, proxy)` + `ctx.draw()` + `uni.canvasToTempFilePath` 导出
  - `generate()`（绘制+导出）/ `generateAndShare()`（`wx.showShareImageMenu` 转发）/ `savePreviewImage()`（`saveImageToPhotosAlbum`）
  - 状态：`previewVisible` / `previewImagePath` / `generating`
  - 排版：标题按字数自适应字号、`buildWrappedLines` 逐字换行 + 超行省略、圆角矩形/光斑/pill 全手工画
  - 二维码是可选的（走后端 `generateMpQrcode`），没有就不画

## 与 superone 的差异（本期取舍）
- 契约里**没有生成二维码的接口**，`src/static` 也不存在 → 海报**不放二维码、不放封面图**，纯绘制（也符合 0204 不产资产的判断）。
- 颜色：canvas 不认 CSS 变量，海报内部写死品牌绿 + 中性色（carbon 的海报同样写死，不跟主题）。
- 页面部分（DOM）照旧走 `--so-*` 令牌，随浅/深主题变化。

## 原型判断
- **原型 = dashboard（展示型落地页）**：单页纵向滚动，无表单、无分页、无编辑。
- 页面不进门控（它本身就是 `so-page` 的演示态内容），不需要 `navTitle` 等页面能力。
- 只需要一个交互：生成海报 → 预览 → 保存 / 转发。

## 状态矩阵（0201 硬门槛）
| # | 状态 | 触发 | 界面表现 | 兜底 |
|---|---|---|---|---|
| 1 | 首次进入 | 演示态首页渲染 | hero + 海报预览卡 + 卖点 + 用法；离屏 canvas 已在 onMounted 预绘一次 | — |
| 2 | canvas 不可用 | `createCanvasContext` 返回空 | 按钮仍可点，生成时抛错 → toast「海报画布不可用」 | 页面其余部分不受影响 |
| 3 | 生成中 | 点「生成分享卡」 | `uni.showLoading(mask)` + 按钮禁用（`generating` 锁，防重复点） | 锁在 finally 释放 |
| 4 | 生成成功 | 导出拿到 tempFilePath | 关闭 loading，弹出预览层（图 + 保存/转发/关闭） | — |
| 5 | 生成失败 | 绘制或导出 reject | 关闭 loading，toast「生成失败」，`generating` 复位 | 不弹空预览层 |
| 6 | 保存成功 | 点「保存到相册」 | `saveImageToPhotosAlbum` 成功 → toast「分享卡已保存」 | — |
| 7 | 保存被拒（未授权） | 用户拒绝相册权限 | errMsg 含 auth → toast「请先允许保存到相册」 | 与「保存失败」区分文案 |
| 8 | 保存失败 | 其他错误 | toast「保存失败」 | — |
| 9 | 转发 | 点「转发给朋友」 | 微信小程序 `wx.showShareImageMenu`；失败 toast「图片转发失败」 | 非微信平台 toast「当前平台不支持图片转发」 |
| 10 | 重复点击 | 生成中再点 | 被 `generating` 直接 return，不重复绘制 | — |
| 11 | 关闭预览 | 点关闭/遮罩 | `previewVisible=false`，保留 `previewImagePath` 可再次打开 | — |
| 12 | 管理员 | `isAdmin` | 页面底部由 `so-page` 提供「切换场景」入口（不在宣传页内重复） | — |

## 实施
1. `src/composables/usePosterShare.ts`（新）：绘制 + 导出 + 预览 + 保存 + 转发。
2. `src/components/so-demo-page.vue`：重做为「执行清单」宣传页（hero / 海报卡 / 卖点 / 用法 / 预览层 / 离屏 canvas）。
3. 不改 `so-page.vue`（演示态入口与 admin 入口已在那儿）。

## 验证
- `npm run type-check` / `npm run build:mp-weixin` 通过。
- dist 里 `so-demo-page.wxml` 含 `<canvas canvas-id="...">`、`wxss` 含离屏样式与预览层。
- 真机：点生成 → 预览 → 保存相册（首次会弹授权）。

## 待核
- `uni.createCanvasContext` 是旧版 API（carbon 在用），若后续基础库弃用再迁 `type="2d"` + `CanvasRenderingContext2D`。
- 海报尺寸 1080×1440；如果觉得竖版太长可改 1080×1350。

## 落地记录
- 新增 `src/composables/usePosterShare.ts`：1080×1440、三个背景光斑 + 圆角卡 + 品牌竖线/kicker +
  自适应字号标题（逐字换行 + 超行省略）+ note + 要点行（主色圆点 + label/value）+ 分隔线 + 品牌 + 收尾。
  导出 `generate` / `savePreviewImage` / `sharePreviewImage` / `closePreview` 与 `previewVisible` /
  `previewImagePath` / `generating` 三个状态。
- 重写 `src/components/so-demo-page.vue`：hero（eyebrow + 56rpx 标题 + 描述 + 纯 CSS 的三条清单视觉）→
  海报卡（DOM 版预览 + 「生成分享卡」+ 离屏 canvas）→ 能做什么（4 条）→ 怎么用（3 步）→ 预览层
  （图 + 保存到相册 / 转发给朋友 + 关闭）。
- 与计划的两处偏差：
  1. `sharePreviewImage` 用**运行时探测 `globalThis.wx`**，没用 carbon 的条件编译 + 裸 `wx`
     —— 项目没装小程序类型包，裸 `wx` 让 `vue-tsc` 报 `Cannot find name 'wx'`。
  2. hero 没做 stats 三项：演示态没有真实数据可放，硬编数字就是编的，改成「能做什么 / 怎么用」两块实的内容。
- 验证：type-check + build:mp-weixin 通过；dist 里 `<canvas canvas-id="{{d}}">`（d = `superonePosterCanvas`）存在、
  `.so-demo__canvas` 为 `left:-9999px` 离屏、预览层 `so-demo__mask` 存在、`closeempty` 图标在 uni-icons 里合法。
