# 主题（topic）模块设计：列表 + 展示

> 豆哥：「我们第一个要做的功能是topic，把它挪到第一位，然后实现列表和展示功能。你看看界面怎么设计，
> 可以参考backup和carbon的设计，然后参考下业内优秀的范例」。

本轮范围：**只做列表与展示**（新建、编辑、删除、日志录入后置）。
首页 rail 顺序已改为 topic 第一（`pages/index/index.vue` 的 `PANELS`）。

## 一、契约事实（决定设计上限）

| 能力 | 接口 | 字段 |
|---|---|---|
| 主题列表 | `POST /api/so/topic/list` | `{offset,size,keyword}` → `{total,list:[{id,topicName,description,createTime,updateTime,top}]}` |
| 主题详情 | `GET /api/so/topic/detail?id=` | 同 list item（**没有日志条数、没有统计**） |
| 日志列表 | `POST /api/so/topic/log/list` | `{topicIds[],topicTypes[],offset,size}` → `{total,list:[{id,topicId,topicType,content,preview,extraData{imageUrls[]},mark,top,createTime}]}` |

两个关键约束：
1. **列表接口不返回任何"活跃度"信息**（无条数、无最近更新）。要么接受，要么多拉一次 log 接口补。
2. **log 列表支持 `topicIds[]` 批量传** —— 一次请求就能拿到多个主题的日志，本地分组即可算出
   「每个主题最近一条的 preview」。这是列表能做成"内容流"而不是"文件夹列表"的技术前提。

`top` 是**时间戳**不是布尔（backup 已验证），排序用 `top DESC, createTime DESC`；`mark` 是**位掩码**。

## 二、信息架构

```
首页 rail「主题」（首屏第一个面板）
  └ biz-topic-panel（scroll-view，高度由首页算好）
      ├ 面板头：eyebrow TOPIC + 标题「主题」+ 一行说明
      ├ 搜索行（keyword → 接口，防抖 300ms）
      └ 主题列表（行式，分隔线，非卡片外框）
          点一行 → pages/topic-detail/index?id=
                                                  ↓
详情页 so-page → shell → so-custom(isBack) → scroll-view
  ├ hero：eyebrow + 主题名 + 描述 + 元信息（创建/更新）+ 操作组
  └ 日志区：按日期分组的时间轴
```

## 三、列表（首页面板）设计

**行式不用卡片外框**（carbon 主流做法：`padding 22rpx 0` + `border-bottom: 1rpx solid --so-divider`）。
理由：面板宽度被左侧 rail 挤窄，卡片外框会浪费横向空间，行式能塞进更多信息。

单条信息层级（从上到下）：

```
标题行   置顶标记（📌 仅 top>0） + 主题名（30rpx/600）        右侧：更新时间（22rpx/muted）
副文本   描述（26rpx/secondary，1 行截断）
最近一条 最近日志 preview（24rpx/muted，1 行截断，无则显示「还没记录」）
```

- **要不要"最近一条"**：建议做。它是 flomo 卡片流的精髓——列表里看到的是内容，不是文件夹名。
  代价：进面板时多一次 `log/list` 请求（topicIds 批量，size 200），本地分组取每个主题最新一条。
  **条数不显示**（批量拉取下不精确，显示会误导）。
- **置顶**：`top>0` 的排在前面，行首给一个小标记；长按的「移至最前」本轮不做。
- **搜索**：keyword 走服务端（契约支持），防抖 300ms；清空即恢复全量。
- **三态**：`loading && 空` → loading；`空 && 非搜索` → 空态（提示去建主题）；`空 && 搜索中` → 「没有匹配的主题」。
  照 carbon 的 v-if 顺序，避免刷新时闪 loading 屏。
- **分页**：`{offset: list.length, size: 20}`，`hasMore + loadingMore` 双状态（不用 backup 的 `loadMoreStatus` 字符串），
  触底 `lower-threshold="80"` + 首屏 `canLoadMore` 防抖（carbon 的 biz-scale-tab 做法）。
- **刷新**：面板内 scroll-view 的 refresher，不用页面级下拉（首页是 swiper，页面级刷新会打架）。
- **主按钮**：底部「新建主题」本轮给 toast（新建不在本轮范围，下一轮补）。

## 四、详情页设计

分区顺序照 carbon 详情页骨架：`shell → so-custom(isBack) → scroll-view → hero → 日志区`。

**hero**（照 carbon 的 `__hero` 结构 + Notion 的"属性区在上"）：

```
eyebrow「主题」                                      右侧：置顶状态胶囊（top>0 时）
主题名（44rpx/600，最多 2 行）
描述（26rpx/secondary，有则显示）
元信息：创建于 X · 更新于 Y
操作组：[编辑] [更多]        ← 本轮：置灰/toast，或只留一个「编辑」占位
```

**日志区**：

```
区头：eyebrow「记录」+ 「这个主题下写了 N 条」
分隔线
按日期分组（今天 / 昨天 / 具体日期）
  日期头（22rpx/muted，粘住分组首行）
  日志条目 ×N
     左侧时间列（HH:mm，24rpx/muted，固定宽）+ 竖线（伪元素，末项截断）
     右侧内容：正文（28rpx/1.55，最多 6 行）、图片缩略图（3 张 + `+N`，112rpx）
```

- **按日期分组**：carbon 没做（它每条挂日期徽标），backup 也没做（纯扁平）。
  但 flomo / Notion / 系统相册都按天分组，长列表下这是能否"扫读"的关键，本轮做。
- **时间轴竖线用伪元素**：照 carbon 的 `biz-scale-tab`（`::before` + `:last-child::before` 截断），不加 DOM。
- **详情走 `topic/detail` 接口**，不从列表反查（backup 的坑：列表没拉过时整个头部消失）。
- **图片**：`extraData.imageUrls` 前 3 张 + `+N` 蒙层（carbon 的 `biz-agreement-log-card` 做法）。
- **markdown**：日志正文是纯文本渲染（无 markdown 组件，superone 没装 mp-html/marked；backup 有但本轮不引入）。
- **没有编辑入口**：详情页只读，底部不放输入框（"记录"下一轮做）。

## 五、业内参考（只取结构性做法）

| 来源 | 借鉴点 | 落到哪 |
|---|---|---|
| flomo | 卡片流直接显示正文预览，列表是"内容"不是"文件夹"；标签代替层级目录 | 列表项带最近一条 preview；主题扁平不嵌套 |
| flomo | 内容按时间轴排列 | 详情页日志按时间倒序 + 按天分组 |
| Notion | 详情页顶部属性区（标题/描述/时间）与下方内容流分离 | hero + 日志区两段式 |
| Things 3 | 列表项右侧放"何时"而非"多少"，详情顶部大标题 + 元信息行 | 列表右侧更新时间；hero 大标题 + 元信息 |
| 系统设置 / carbon | 行式列表靠 1rpx 分隔线，不用外框；右侧不放箭头也能点 | 主题列表行式 |

不做的：flomo 的每日回顾/随机漫步/热力图（超出本轮且要额外数据）、Notion 的多视图切换（契约只有一种查法）。

## 六、与 backup / carbon 的取舍

**保留（backup）**
1. `top` 时间戳 + `mark` 位掩码两个字段设计（比布尔高明）。
2. 排序 `top DESC, createTime DESC` 放在读取出口统一施加（backup 只在本地 mutation 时排，读时不排，是 bug）。
3. 三态判断 `loading && 空` / `空` / 列表，错误态带重试。

**丢掉（backup）**
1. 详情页 `topic = topics.find(...)` 反查 → 改走 detail 接口。
2. 假分页（`size:1000` 全量 + `handleLoadMore` 不发请求）→ 真分页 + hasMore。
3. 时间轴圆点按 `index%2` 交替颜色（纯装饰，插入一条后面全翻色）→ 统一中性色，只有"有标记"才给语义色。
4. 日志列表两套不通用样式 → 详情一套 `<so-timeline>`，后续模块复用。

**不照抄（carbon）**
1. 两个状态组件的 CSS 有 bug（`cu-loading-state` 类名前缀错配、`cu-empty-state` 根本没引样式）→
   照结构与 props，**样式在 superone 重写**（`so-empty-state` / `so-loading-state`）。
2. 琥珀暖色整套、backdrop 光斑呼吸动画 → superone 是工具感，用微信绿，装饰克制。
3. carbon 没有 markdown 渲染器，日志正文纯文本，照它。

## 七、状态矩阵（0201 硬门槛）

| # | 状态 | 触发 | 界面表现 | 兜底 |
|---|---|---|---|---|
| 1 | 面板首屏加载 | 首次 mount | loading 骨架（`loading && 空`） | — |
| 2 | 面板空（从未建过） | total=0 且无 keyword | 空态「还没有主题」+ 说明 | — |
| 3 | 面板有数据 | list>0 | 行式列表，置顶在前 | — |
| 4 | 下拉刷新 | refresher | 不闪 loading 屏，原地替换数据 | 失败 toast，保留旧数据 |
| 5 | 触底加载 | scrolltolower | 底部「加载中」；`hasMore=false` 后显示「没有更多了」 | loadingMore 守卫防重入 |
| 6 | 首屏误触发底 | 一进页面就触底 | `canLoadMore`（scrollTop>12 才置 true）挡掉 | — |
| 7 | 搜索中 | 输入 keyword | 防抖 300ms 后请求，列表替换 | — |
| 8 | 搜索无结果 | total=0 且有 keyword | 「没有匹配的主题」+ 清空按钮 | 与"空"区分文案 |
| 9 | 列表请求失败 | 网络/服务端错误 | toast + 错误态（带重试） | 保留上一次数据 |
| 10 | 细节：最近一条预览 | log 接口失败 | 预览行不渲染，列表其余照常 | 不影响主流程 |
| 11 | 详情首屏 | 进入 id | hero 骨架 + 日志 loading | — |
| 12 | 主题不存在 / 被删 | detail 失败或空 | 整页错误态 + 「返回」 | 不白屏 |
| 13 | 详情日志空 | total=0 | 「还没有记录」区（不带 action，本轮不能写） | — |
| 14 | 详情加载更多 | scrolltolower | 同 5；按天分组头在新增数据里继续合并 | — |
| 15 | 详情刷新 | refresher | 重拉 detail + 日志 | — |
| 16 | 日志含图片 | imageUrls | 3 张缩略图 + `+N` | 单图也走同一套 |
| 17 | 置顶主题 | top>0 | 列表排在最前 + 行首标记；详情显示置顶胶囊 | — |

## 八、落地文件清单

| 文件 | 说明 |
|---|---|
| `src/components/business/biz-topic-panel.vue` | 首页面板（列表 + 搜索 + 三态 + 分页） |
| `src/composables/useTopicList.ts` | 列表加载/搜索/分页/置顶排序/最近一条聚合 |
| `src/pages/topic-detail/index.vue` | 详情页（hero + 分组时间轴） |
| `src/composables/useTopicDetail.ts` | detail 接口 + 日志分页 + 按天分组 |
| `src/components/so-empty-state.vue` / `so-loading-state.vue` | 三态组件（照 carbon 结构，样式重写） |
| `src/components/so-timeline.vue` | 时间轴条目（dot/线/内容），后续模块复用 |
| `src/styles/06-pages/_p-topic-detail.scss` | 详情页样式（面板样式在组件内） |
| `src/pages.json` | 注册 `pages/topic-detail/index` |

## 九、已拍板的三个取舍（豆哥 2026-10-02）

1. **列表项不带"最近一条预览"** → 只用 `topic/list` 已有字段：置顶标记 + 名称 + 描述 + 更新时间。
   少一次请求，列表保持轻量；后续觉得信息不够再补（接口本来支持）。
2. **详情页操作组放，但置灰提示** → hero 底部排「编辑 / 置顶 / 更多」三个文字胶囊，点击 toast「功能开发中」，
   界面结构先完整，等下一轮做新建/编辑时一次性接上。
3. **不要搜索框** → 面板顶部只留面板头（eyebrow + 标题 + 说明），把纵向空间全给列表。
   `keyword` 能力保留在契约里，条目多了再开。
