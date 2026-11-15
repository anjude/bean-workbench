# 02-20 编辑器视觉修正：令牌按数值平移，不按名字

> 豆哥：「先保留内嵌的做法，但是现在的问题是编辑器这个交互还是太丑了，
> 可以参考下，主要是一些按钮、默认高度这些，可以参考下backup怎么设计的，或者参考下carbon的理念」。

## 根因：跨仓库照抄时把令牌当同名同值用了

上一轮照搬 backup 时做的是**按令牌名替换**：`--radius-lg` → `--so-radius-lg`、`--spacing-lg` → `--so-space-lg`。
名字对得上，**数值差了一倍多**：

| backup 令牌 | 实际值 | 我们同名令牌 | 实际值 |
|---|---|---|---|
| `--radius-sm` | 6rpx | `--so-radius-sm` | 12rpx |
| `--radius-md` | 8rpx | `--so-radius-md` | 20rpx |
| `--radius-lg` | 12rpx | `--so-radius-lg` | **28rpx** |
| `--radius-xl` | 16rpx | `--so-radius-xl` | 40rpx |
| `--spacing-md` | 16rpx | `--so-space-md` | 24rpx |
| `--spacing-lg` | 20rpx | `--so-space-lg` | **32rpx** |
| `--font-md` | 28rpx | `--so-font-md` | 30rpx（接近，保留） |

后果最重的一条：工具栏按钮是 60rpx 的方块，backup 给它 12rpx 圆角（圆角方块），
我给了 28rpx——**几乎等于边长的一半，视觉上接近圆形**。整排工具从「一排工具按键」变成「一串徽章」。
编辑区边框圆角同理（backup 12rpx → 我们 28rpx）。这就是「丑」的主因。

## 修正原则

**照抄样式时令牌按数值换算，不按名字对号。**

- backup 的 md/lg/xl（8 / 12 / 16rpx）在我们的尺度里统一落 `--so-radius-sm` (12rpx)
- backup `--spacing-lg`(20rpx) → `--so-space-md`(24rpx)；`--spacing-md`(16rpx) → `--so-space-sm`(16rpx)
- 颜色继续走我们的 `--so-*`（本来就是同一套语义）

## 具体改动

**`components/so-md-editor.vue`**
- `.so-md-editor` 根圆角 `--so-radius-md` → `--so-radius-sm`
- `.ql-container` padding `--so-space-lg` → `--so-space-md`，圆角 `--so-radius-lg` → `--so-radius-sm`
- `.loading-overlay` 圆角 `--so-radius-xl` → `--so-radius-sm`

**`components/so-md-editor-toolbar.vue`**
- 高度 100rpx → 88rpx（放 60rpx 的按钮，上下各 14rpx）
- 横向 padding `--so-space-lg` → `--so-space-md`
- `.toolbar-item` 圆角 `--so-radius-lg` → `--so-radius-sm`
- `.complete-button` 圆角补 `--so-radius-sm`，横向 padding 16 → 20rpx
- **未聚焦的置灰方式换掉**：原来整条 `opacity: .55`，看着发脏；改成「按钮底透明 + 图标 `--so-text-disabled`」，
  聚焦后底再浮出来。碳(carbon)的做法一向是这种克制分层，不是整体压暗。

**`pages/topic-detail/index.vue` + `06-pages/_p-topic-detail.scss`**
- 展开态**收进一张 `so-card`**：照 backup 的 topic 详情页（`cu-card` + header「记录想法」+ `uni-icons compose`）。
  原来是一个 200px 高的裸露编辑框直接摆在页面上，很散。
- **高度显式传 `:height="80"`**：backup 详情页传的是 `:height="30"`（约一行），按我们的字号放大到两行。
  组件默认值仍是 backup 原样的 200，没人用默认——之前是我们没传，白吃了一个大方块。
- 「取消」从编辑器下方的独立按钮挪到卡片 header 右侧的纯文字，跟 backup 一致（它在工具栏里只有「保存」）。
  旧的 `.p-topic-detail__compose-cancel` 样式删除。

**`pages/test-theme/test-theme.vue`**：补 `:height="120"`，预览页不再吃默认 200。

## 追加：写记录改常驻输入框（豆哥指令）

> 「不需要点击写一条吧，直接默认展示输入框」。

去掉「写一条 → 展开」这道入口，`composing` / `onCompose` / `onCancel` 全部删除，
进详情页直接是一张「记录想法」卡 + 常驻编辑器。**这本来就是 backup 的 topic 详情页的形态**
（它一直是常驻 `cu-card`，没有入口按钮），我上一版加的那道入口是自己多出来的。

连带删掉的还有「取消」按钮——常驻之后没有取消语义；保存成功只需要 `draft = ''`，
编辑器的 `watch(modelValue)` 会同步 `clear()`，不需要再收起。

SCSS 删 `__compose-btn` / `__composer-cancel`，保留 `__composer`（上间距）/ `__composer-card` /
`__composer-head` / `__composer-title`。

**交互口径**：记录类输入框默认展开，不加「写一条」这类入口按钮——少一次点击，也少一套展开/收起状态。

## 验证

- `npm run type-check` 与 `npm run build:mp-weixin` 通过（含常驻输入框那版）。
- 产物核对：`components/so-md-editor.wxss` 的 `.ql-container` 是 `padding:var(--so-space-md)` +
  `border-radius:var(--so-radius-sm)`；`components/so-md-editor-toolbar.wxss` 的 `.toolbar-item` 是
  `border-radius:var(--so-radius-sm)`，`is-disabled` 变体只剩 transparent + `pointer-events:none`，无 opacity。
- `app.wxss` 里新增 `.p-topic-detail__composer-card/-head/-title`，旧类 `_compose-btn` / `_composer-cancel` 归零；
  源码里 `composing` 零残留。

## 待真机确认

- 80rpx 的初始高度在真机上够不够放下 placeholder（不同基础库的 editor 内部 padding 有差异）。
- 未聚焦时按钮底透明的处理，在深色主题下图标会不会太淡（`--so-text-disabled` 深色值）。
