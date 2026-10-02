# 02-21 主题详情页：从「落地页 hero」改回工具页

> 豆哥：「重新设计下主题详情页，现在的设计太过于夸张了，和superone的品牌调性不符」。

## 根因：把 carbon 的落地页视觉套到了功能详情页上

上一版详情页长这样：

| 元素 | 具体形态 |
|---|---|
| eyebrow | `TOPIC`，20rpx、字距 4rpx、主色 |
| 标题 | 44rpx bold（`--so-font-xxl` 量级） |
| 外壳 | 白卡 + 1rpx 边框 + `shadow-soft` |
| 操作组 | 「编辑 / 置顶 / 更多」三个 `so-btn-secondary` 胶囊 |
| 间距 | content 内边距 32rpx，块间距 32rpx |
| 结果 | `hero 卡 → 输入卡 → 日志区` 三层卡堆叠 |

这套东西来自 carbon 的 `p-agreement-detail` / 演示页那一脉：**它服务的是「讲清楚这是什么」，
不是「拿来干活」**。eyebrow + 巨标题 + 大卡是落地页的语言，放在一个每天要打开十次的工具页上就浮了。

**对照 backup 的 topic 详情页**——它一直是裸文本头（标题 + 更新时间）+ 一张输入卡 + 时间轴。
没有 eyebrow、没有巨标题、没有一排按钮。这才是工具页的写法，也是豆哥认可的线上形态。

## 改后的层次

```
导航
头部（无卡）：主题名 36rpx bold → markdown 描述 → 元信息行（置顶标签 + 创建于/更新于）
输入卡：唯一一张卡
记录区：分区标题「记录」+ 条数 → 细分隔线 → 时间轴
```

一个页面只剩一张卡。层次靠排版与细分隔线做，不靠多重卡片。

## 具体改动

**`pages/topic-detail/index.vue`**
- 删 `TOPIC` eyebrow（营销语汇，工具页不需要自我宣讲）
- 删三个占位操作按钮与 `ACTIONS` / `onTodo`（功能本来就只有「开发中」toast，纯占视觉）
- 置顶标签从 hero 右上角挪进元信息行，跟「创建于 / 更新于」排在一起，不再独占一行挂胶囊
- 注释改口径：层次靠排版与细分隔线，不靠多层卡片与重标题

**`06-pages/_p-topic-detail.scss`**
- `.p-topic-detail__hero` → `.p-topic-detail__head`：去掉边框 / 背景 / 阴影 / padding，只剩纵向 `gap: 12rpx`
- 标题 44rpx → `--so-font-lg`(36rpx) bold，`line-height` 放宽到 1.35
- 新增 `.p-topic-detail__meta-row`（置顶标签与时间戳同行）
- 「记录」分区标题 `--so-font-lg`(36rpx) bold `--so-text-primary` → `--so-font-md`(28rpx) medium `--so-text-secondary`，
  让位给内容本身
- content 内边距：上 32→24rpx，底部 64→48rpx（原先是为了托住 hero 的大卡）

## 沉淀的口径

**抄 carbon 只抄布局分区思路，不抄它的营销视觉。** 落地页那一套（eyebrow / 巨标题 / 大卡 / 胶囊按钮组）
只在真正需要"讲清楚这是什么"的页面上用；功能详情页按 backup 的工具页写法：

- 一个页面最多一张卡（给需要边框的输入区）
- 头部是裸文本，标题在 36rpx 上下就够
- 分区标题用 28rpx medium + `--so-text-secondary`，不跟正文抢重量
- 状态标签并入元信息行，不独占一行

## 验证

- `npm run type-check` 与 `npm run build:mp-weixin` 通过。
- 旧类 `__hero` / `__eyebrow` / `__hero-row` / `__actions` / `__action` 在源码与产物 `app.wxss` 中均为 0。
- 新类核对：`.p-topic-detail__head{display:flex;flex-direction:column;gap:12rpx}`、
  `.p-topic-detail__content{padding:var(--so-space-md) var(--so-space-lg) var(--so-space-xl)}`、
  `.p-topic-detail__section-title{font-size:var(--so-font-md);...color:var(--so-text-secondary)}`。

## 追加：卡片成组 + 与背景协调（豆哥二次纠）

> 「不行，弄个卡片吧，因为输入框是必有卡片的，你这弄的整个页面只有输入框有个白色背景卡片，
> 怪奇怪的，卡片可以和背景协调一点」。

上一节把大卡去掉是对的，但**去到只剩输入卡一张就过头了**——整页只有一处带底色的区块，
其余全是裸文本压在灰底上，视觉上就是「一个孤零零的白块」。

两层修正：

**① 卡片成组**：头部卡（标题 / 描述 / 元信息）+ 输入卡 + 记录卡，三张同一层表面。
卡片不是「要不要」的问题，是「成不成组」的问题。

**② 卡片与背景协调**：

| | 之前 | 现在 |
|---|---|---|
| 页面底 | `--so-bg-secondary` | `--so-bg-base` |
| 卡片 | `--so-bg-elevated` | `--so-bg-secondary` |
| 对比 | 灰底白卡（硬切） | 同色系差一档（柔和） |
| 投影 | `shadow-soft` | 无（投影留给浮层） |

浅色 `#ffffff / #f5f5f5`，深色 `#1a1a1a / #242424`，两个主题下都只差一档。

**不改 `.so-card` 统一件**——它同时被 profile / test-theme / 首页占位面板用着，改背景会让那些页
（页面底仍是 secondary）变成「灰底灰卡看不见」。只在 06-pages 里覆盖：

```scss
.p-topic-detail .so-card {
  background-color: var(--so-bg-secondary);
  box-shadow: none;
}
```

**卡内边距**：头部卡 / 记录卡 `--so-space-md`(24rpx)；输入卡保持 `--so-space-sm`(16rpx)——
它里面包的编辑框自带边框与内边距，再叠 24rpx 会显得嵌套太厚。

## 未动

`so-timeline`（按天分组 + 竖线 + 圆点）是内容渲染不是装饰，本轮没改。若豆哥觉得记录流本身也偏重，
下一步再收（可考虑去掉按天分组标题、圆点改更中性）。
