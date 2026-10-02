# 02-14 topic 模块落地：列表 + 展示

> 豆哥：「第一个要做的功能是topic，把它挪到第一位，然后实现列表和展示功能」。
> 设计见 `task/261002_superone-modules/topic-module-design.md`（含 0201 状态矩阵）。

## 三个拍板（影响实现范围）
1. 列表项**不带**「最近一条日志预览」→ 只用 `topic/list` 已有字段，少一次请求。
2. 详情页操作组**放但置灰**：「编辑 / 置顶 / 更多」三个文字胶囊，点击 toast「xx开发中」。
3. **不要搜索框** → 面板头之外全是列表。

## 落地文件
| 文件 | 作用 |
|---|---|
| `src/pages/index/index.vue` | PANELS 把 topic 提到首位；swiper 里按 key 分派 topic → `biz-topic-panel` |
| `src/composables/useTopicList.ts` | 列表加载/刷新/触底，排序在读取出口 |
| `src/components/business/biz-topic-panel.vue` | 首页面板（行式列表 + 三态 + refresher） |
| `src/composables/useTopicDetail.ts` | detail 接口 + 日志分页（传 `Ref<number>`，onLoad 才拿到 id） |
| `src/pages/topic-detail/index.vue` | 详情页：hero（属性区）+ 按天分组时间轴 |
| `src/components/so-timeline.vue` | 按天分组 + 左列时间 + 伪元素竖线 + 图片 3 张 +N |
| `src/components/so-empty-state.vue` / `so-loading-state.vue` | 三态组件（照 carbon 结构，样式重写） |
| `src/utils/time.ts` | 秒级时间戳格式化（smart / date / clock / 分组标签） |
| `src/utils/layout.ts` | `getNavigationBarHeight()`，首页与详情页共用同一份 |
| `src/styles/06-pages/_p-topic-detail.scss` | 详情页样式（面板样式留在组件内） |

## 关键实现决策
- **排序只在读取出口**：`top` 是时间戳非布尔，按 `top DESC, createTime DESC`；日志按 `createTime DESC`。
  backup 的坑是只在本地增删时排、读取时不排。
- **真分页**：`offset = 已取条数`、`size 20`，`hasMore = 已取 < total`，三重守卫（loading / loadingMore / !hasMore）。
  不用 backup 的 `loadMoreStatus` 字符串，也不搞它那个不发请求的假加载更多。
- **首屏触底防抖**：`canLoadMore`（scrollTop > 12 才置 true），照 carbon 的 biz-scale-tab，否则一进页面就触发一次。
- **三态 v-if 顺序**：`loading && 空` → `error && 空` → `空` → 列表。loading 必须与「空」同时成立，刷新时才不闪加载屏。
- **详情页走 detail 接口**，不从列表 find（backup 靠反查，列表没拉过时整个头部消失）。
- **时间轴竖线用伪元素**（`::before` + `:last-child` 截断），不加 DOM；圆点默认中性色，只有 mark 位掩码命中才上语义色。
- **时间戳是秒级**（backup `new Date(ts*1000)` 验证过），统一在 utils/time 处理。

## 验证
- type-check + build:mp-weixin 通过。
- 产物：`pages/topic-detail/` 已生成、`app.json` 已注册、首页 wxml 有 `biz-topic-panel` 与 `biz-panel-placeholder` 两支分派、
  详情页 wxml 有 hero / so-timeline / so-empty-state。

## 怎么看到（重要）
`so-page` 有门禁：非真实态下首页走演示页、普通页显示「开发中」。所以要看 topic 列表与详情，
得先用管理员入口（演示页底部「切换场景」）切到真实态（wbbb=1），再回首页点主题进详情。

## 待办（下一轮）
1. 新建主题（面板 `open()` 目前是 toast「新建主题开发中」）。
2. 详情页操作组接线：编辑 / 置顶 / 更多（长按菜单：移至最前、切换主题、标记、删除）。
3. 写记录（详情页底部输入 → `createTopicLog`）。
4. 列表项若觉得信息不够，可补「最近一条预览」（`topic/log/list` 支持 topicIds 批量，接口本来就够）。
