# 02-16 写记录：Markdown 编辑器接上第一个业务

> 豆哥：「你选一个业务实现，用一下markdown编辑器看看」。

## 为什么选「写记录」而不是「新建主题」

候选有三个（接口都在 `src/contracts/apis/topic.ts`）：新建主题 / 编辑 description / 写记录。

选**写记录**（`createTopicLog`），理由是闭环最短：

- 日志正文 `content` 本来就是最主要的 Markdown 字段，上一轮 `so-timeline` 已经改走 `so-markdown` 渲染
  → **编辑器写进去、时间轴立刻渲染出来**，同一屏能同时验证"写"和"读"。
- 另外两个要么主体是纯文本（新建主题的名称），要么只改一个字段（description），编辑器都只是配角。

## 交互

详情页 `hero → 写一条 → 记录列表`。

- **收起态**：一条「写一条」按钮。
- **展开态**：`so-md-editor`（autofocus 直接弹键盘）+ 一条「取消」。
- 点「记下来」→ `createTopicLog` → 成功清空草稿、收起、toast「已记录」；失败 toast 后端 msg。

**「写一条」放在记录区之前，不在列表末尾**：日志分页 20 条，放末尾要滑到底才能写；
放前面一进页面就能写，展开时下面的列表被推下去，不会被遮挡。

## 落地文件

| 文件 | 改动 |
|---|---|
| `src/composables/useTopicDetail.ts` | 新增 `createLog(content)` |
| `src/pages/topic-detail/index.vue` | composer 区块 + `composing` / `draft` / `submitting` 三个状态 |
| `src/styles/06-pages/_p-topic-detail.scss` | `__composer` / `__compose-btn` / `__compose-cancel` |

## 关键决策

- **写完只刷日志，不走 refresh**：`refresh()` 会先清空 `logs` 再拉，列表空 + loading 会闪一下加载屏。
  `createLog` 内部成功后调 `loadLogs(true)`（reset 语义是"替换成第一页"），列表不为空就不闪。
  代价是若之前已加载多页会回到第一页——写完一条本来就该看到最新的，合理。
- **不构造本地插入**：`CreateTopicLogResp` 缺 `preview` / `top` / `updateTime`，硬拼一个 `TopicLogListItem` 是脏数据。
  多一次请求换数据干净，值。
- **`mark` 不传**：后端 `CreateTopicLogReq.Mark` 是 `omitempty`，0 时 `NewTopicLog` 用默认值（后端注释写明）。
  前端不替后端决定默认标记。
- **`maxlength = 10000`**：后端 `content` 是 `binding:"max=10000"`，前端同上限，写超了不会白提交一次。
  收成常量 `CONTENT_MAX`，不写魔法数。
- **不做"写完滚到顶部"**：scroll-view 的 `scroll-top` 设 0 若已是 0 不触发，要绕 hack。toast 够用，不为小体验引入第二套机制。

## 验证

- `npm run type-check` + `npm run build:mp-weixin` 通过。
- 产物：详情页 wxml 有 composer 区块；`so-md-editor` 的 props 正确序列化
  （`autofocus:true` / `placeholder:"记一笔，支持 Markdown"` / `complete-button-text:"记下来"` / `maxlength`）。
- 后端接口确认存在：`app/api_service/api_superone.go:25` `topicApi.POST("/log/create")`。

## 怎么测

1. 演示页底部「切换场景」切到真实态（wbbb=1）——`so-page` 门禁下非真实态看不到真实内容。
2. 首页点「主题」→ 进任一主题详情。
3. 点「写一条」→ 键盘弹起，工具栏 B / I / H / • / 1. / 引 / 码 / 链 / — 逐个点一下，
   看语法是否插在光标处、光标是否落在中间。
4. 切「预览」看渲染，再切回编辑。
5. 点「记下来」→ 列表顶部应出现刚写的那条，且 `**粗体**` / `- 列表` 等语法已渲染。

## 待办

1. 新建主题（面板 `open()` 仍是 toast）。
2. 详情页操作组接线：编辑（description 走 `updateTopic`）/ 置顶 / 更多。
3. 记录还没做编辑与删除（`updateTopicLog` / `deleteTopicLog` 都在）。
4. `extraData.imageUrls` 没接——编辑器目前纯文本，图片只能靠 Markdown 的 `![]()`。
