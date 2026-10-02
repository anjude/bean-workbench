# 前端引入子日志（跟进）· 方案文档

- 任务目录：`task/dev-flow/261002_superone-sub-log/`
- 日期：2026-10-02
- 归属：`business-repo/uni-superone`
- 承接：后端与契约已完成，见 `task/dev-flow/261002_topic-log-nesting/`（单表自引用 `parent_log_id`）

## 背景

后端给 `topic_log` 加了自引用 `parent_log_id`，一条记录下可以持续挂「跟进」。
superone 目前只有两层：主题详情 → 记录平铺，记录之间没有关系。本轮把它接进来。

## 契约已更新

`uni-superone` 的 `src/contracts` 子模块从 `fd71e31` 快进到 `4ff0289`（`261002 维护 topic 契约(parent_log_id)`）：

- `GetTopicLogListReq.parentLogId?` —— 不传/0 返根，传 X 返 X 的子
- `CreateTopicLogReq.parentLogId?`
- `TopicLogListItem` / `TopicLogDetailView` / `CreateTopicLogResp` 都带 `parentLogId`

`type-check` 通过（新增的是可选字段，不影响现有调用）。

## 接口能力边界（决定 UI 能做成什么样）

| 事实 | 对前端的约束 |
|---|---|
| 列表只返「纯根」或「纯某父的子」，不混 | 一层一次请求，分页 `total` 只数当前层级 |
| `TopicLogListItem` **没有 child_count** | 主题详情页拿不到「这条有几条跟进」，要拿只能逐条查（N+1） |
| `UpdateTopicLogReq` **没有 parentLogId** | 层级创建后固定，不能把跟进挪到别的记录下 |
| `DeleteTopicLog` **不级联** | 删掉根记录，它的跟进仍在库里但失去入口 → 孤儿数据 |
| 后端支持任意层级，方案写明「UI 先只渲染两层」 | 跟进下不再挂跟进 |

## 两个拍板（豆哥）

1. **入口形态 = 独立记录详情页**（`pages/log-detail`）。不选内联展开/半屏弹层：
   子记录要分页（size 20），独立页面天然承载；输入框常驻，不用每条维护展开态与分页状态。
2. **主题详情页先不显示跟进条数**。接口 `parentLogId` 只支持单个父，做不到批量汇总；
   条数只在记录详情页内显示（那里已知）。

## 信息架构

```
首页 → 主题详情（pages/topic-detail）→ 记录详情（pages/log-detail）
                                          ├── 这条记录本身（hero）
                                          ├── 写跟进（composer）
                                          └── 跟进列表（正序、分页）
```

**主题详情页改动最小**：只给时间轴的记录行加点击（跳记录详情），不加任何"跟进"角标。

## 记录详情页分区

照 `pages/topic-detail` 的骨架（shell → 自绘导航 → scroll-view → hero → 内容流）：

1. **hero**：`formatDate + formatClock` 的完整时间 + `so-markdown` 渲染正文。
   本轮**不放操作组**——编辑/删除还没做，放假按钮只会误导。
2. **写跟进**：收起是一条「写一条跟进」按钮，展开是 `so-md-editor`（autofocus 弹键盘）。
   位置在跟进列表**之前**，与主题详情页保持一致：不受列表长度影响，不用滑到底才能写。
3. **跟进列表**：行式（左列时间 + 右侧内容，1rpx 分隔线），**正序**（早→晚）。
   条数显示在区头「跟进 · 共 N 条」。

### 为什么跟进用行式而不是 so-timeline

`so-timeline` 是按天分组 + 倒序，适合"跨天的独立事件流"。跟进是同一件事的推进，
条目通常少、按发生顺序读才读得懂，按天分组只会多出无意义的分组头。行式与 `biz-topic-panel` 一脉。

### 排序正序

后端不保证顺序，统一在读取出口排（项目已有约定）。根记录保持倒序（最新在上），
**跟进正序**（先写的在前）——跟进是叙事推进，倒序会读反。

## 状态矩阵（0201）

| 场景 | 状态 | 展示 |
|---|---|---|
| 首屏取记录 | loading | `so-loading-state` |
| 首屏失败 / 记录不存在 / 被删 | error | 错误文案 + 重试 + 返回按钮（整页，不白屏） |
| 跟进为空 | empty | `so-empty-state`「还没有跟进」 |
| 跟进首屏加载中 | loading | 跟进区 loading（三态顺序：`loading && 空`） |
| 触底加载更多 | loadingMore | 底部「加载中…」 |
| 全部加载完 | done | 「没有更多了」 |
| 跟进加载失败 | error | 「加载失败」+ 重试（不影响已显示的记录） |
| 提交中 | submitting | 守卫防重复提交，不置灰按钮 |
| 提交失败 | toast | 直接显示后端 msg |

## 落地文件

| 文件 | 改动 |
|---|---|
| `src/pages/log-detail/index.vue` | 新增：hero + composer + 跟进列表 |
| `src/composables/useLogDetail.ts` | 新增：记录详情 + 跟进分页 + 写跟进 |
| `src/styles/06-pages/_p-log-detail.scss` | 新增，`index.scss` 接入 |
| `src/components/so-timeline.vue` | 记录行可点（`emit('select', item)`），图片点击加 `.stop` 防冒泡 |
| `src/pages/topic-detail/index.vue` | 绑定 `select` → `navigateTo /pages/log-detail/index?id=` |
| `src/pages.json` | 注册 `pages/log-detail/index` |

## 关键实现决策

- **路由只传 `id`**：`GetTopicLogDetail` 只要 id；创建跟进需要的 `topicId` / `topicType`
  在记录详情返回里都有，不用外部再传。
- **写完只刷跟进，不走全量 refresh**：`refresh` 会先清空列表再拉，空列表 + loading 会闪加载屏。
  与 `useTopicDetail.createLog` 同一个做法。
- **分页三重守卫**：`loading` / `loadingMore` / `!hasMore`，`offset = 已取条数`，照 `useTopicList`。
- **触底防抖**：`canLoadMore`（scrollTop > 12 才置 true），照 carbon 的 `biz-scale-tab`。

## 本轮不做

1. **删除记录**——后端不级联，删根会留下孤儿子记录。这是产品决策，不是实现细节：
   要么后端级联删、要么删除前提示、要么列表能筛出孤儿。待豆哥定。
2. **编辑记录**（`updateTopicLog` 已在契约里）。
3. **跟进下再挂跟进**——后端支持任意层级，UI 按方案只做两层。
4. **主题详情页显示跟进条数**——要后端加 `child_count`。若后面觉得入口太隐蔽再提。

## 验证

- `npm run type-check` + `npm run build:mp-weixin` 通过。
- 产物：`pages/log-detail` 已生成、`app.json` 已注册、主题详情页 wxml 带 select 跳转。
- 手测路径：真实态 → 首页主题 → 主题详情 → 点任一记录 → 记录详情 → 写一条跟进 →
  列表出现且正序 → 返回主题详情 → 再进同一条，跟进还在（说明 `parentLogId` 落库正确）。

## 怎么造数据验证父子关系

主题详情页目前只能建根记录（`parentLogId` 不传）。要确认跟进真写进了子层级，
在记录详情页写一条后，用 `topic/log/list` 不带 `parentLogId` 查一次——**跟进不应出现在根列表里**，
带 `parentLogId=根id` 查才出现。这一步能同时验证后端 `WHERE parent_log_id` 始终生效。
