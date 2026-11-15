# 02-23 记录置顶标识补回 + 复制/分享迁移 + backup topic 模块迁移审计

日期：2026-10-05

## 记录置顶标识（已修复）

**问题**：so-timeline 只有排序（top DESC）没有置顶视觉标识；圆点语义色给了「标记」。
so-timeline.vue 原注释把 backup 的 index%2 交替装饰色和 dot-red 置顶语义混在一起，
连语义一起去掉了。

**修复**（照 backup 的语义分配，两状态各占一个通道）：

- 置顶 → 圆点变红 `so-timeline__dot--pin`，用 `var(--so-color-error)`（backup 是 #ff4757 硬编码，新项目走主题变量，暗色下自动换 #ef9a9a）
- 标记 → 正文右上角小旗标 `uni-icons flag-filled`，用 `var(--so-color-warning)`（backup 在卡片内 absolute 右上角，新设计无卡片，用 flex `align-self: flex-end` 压到同行右上角，不占正文行）
- 备份的 index%2 交替装饰色不沿用（插入一条后面全翻色）

type-check 通过。变更文件：`src/components/so-timeline.vue`。

## 复制 / 分享（已修复，进长按菜单）

审计里两个缺口「复制日志」「分享日志」，按用户要求都做进长按菜单（不做行内按钮）：

- **复制**：菜单加「复制」项（插在删除前，照 backup 顺序），直接拷 `log.content`——
  列表接口返回的是全文（截断的只有 preview 字段），与 backup 的 handleCopyLog 一致。
- **分享**：菜单加「分享」项，走海报。海报 DOM 依赖抽成新组件 `so-poster-share.vue`
  （离屏 canvas + 预览层，包掉 usePosterShare 的全部 DOM 依赖），宿主页摆挂件、
  把 ref 传进 `useTopicLogActions({ poster, topicName })`；没传 poster 的页面菜单不出「分享」。
  两页接线：topic-detail（`topicDetailPosterCanvas`，标题=主题名）+ log-detail
  （`logDetailPosterCanvas`，标题落「一条记录」）。canvas-id 逐页静态取，互不冲突。
- 复制 / 分享不改数据，`run()` 返回 false，调用方不触发刷新（原有契约不用动）。

验证：type-check 通过；浏览器实测两页长按菜单顺序 移至最前 / 取消置顶 / 标记 / 复制 / 分享 / 删除，
复制链路走到 `uni.setClipboardData`（隐藏文档下剪贴板 API 被浏览器拒绝，属测试环境限制），
分享生成 121KB 1080×1440 海报并弹预览层。变更文件：`src/components/so-poster-share.vue`（新增）、
`src/composables/useTopicLogActions.ts`、`src/pages/topic-detail/index.vue`、`src/pages/log-detail/index.vue`。

## backup topic 模块迁移审计（清单）

### 未迁移 / 有差距（截至本次修复后）

| 功能 | backup 位置 | 现状 |
| --- | --- | --- |
| 主题搜索 | 列表页搜索框，store 端 searchTopics | ❌ biz-topic-panel 明确不做（注释有记录）；后端契约已支持 keyword，要补成本低 |
| 时间线原地编辑 | 条目内切编辑器改内容 | ➡️ 改为跳 log-detail 完整编辑（升级，但步数 2→3） |
| 首页跨主题最近日志 biz-topic-logs | 首页组件：数据源标签 + 快速保存 + 跨主题日志流 + 刷新/管理 | ❌ 新首页是面板架构无对应物，属架构差异（新设计里这个形态没有位置） |

### 审计后回补

- 切换主题（日志跨主题迁移）：`useTopicLogActions` 长按菜单第 3 项「切换主题」（顺序照 backup：
  移至最前 / 置顶 / 切换主题 / 标记 / …），update 带 `topicId` 完成迁移。
  选择器用系统 `showActionSheet` 而非 backup 的 uni-popup——新项目没接 uni-popup，
  且 biz-topic-panel 已立下「系统件够用就不自绘浮层」的先例；候选为当前主题之外的
  全部主题（一次拉 100 条），置顶的名称前缀 📌，空列表 toast「没有其他主题可选」。
  切换成功返回 true，主题详情页整页重拉、log-detail 只重拉跟进，记录自动从新主题消失。
  type-check 通过。

### 回补后踩坑：微信 actionSheet 6 项上限（已修）

切换主题进菜单后，有海报挂件的页面菜单变 7 项，**微信小程序 `showActionSheet`
的 itemList 上限就是 6 项**，超出整个调用 fail、菜单一项都不出——H5 无此限制，
浏览器实测完全正常，小程序端直接失效。修法：

- 长按菜单固定 5 项：移至最前 / 置顶 / 切换主题 / 标记 / 删除（上限 6，留一个位置）
- 「分享」「复制」都挪出长按菜单，改到 log-detail 头部卡 ⋯ 菜单（编辑 / 复制 / 分享 / 删除）：
  - 分享经 `useTopicLogActions` 导出的 `share(log)` 走原有 so-poster-share 挂件；
    入参收窄为 `Pick<TopicLogListItem, 'content' | 'createTime'>`，详情视图也能直接传
  - 复制经 `copy(log)`，成败 toast 都收在函数里
- topic-detail 页的海报挂件随之撤掉（复制 / 分享不再从这页触发），`useTopicLogActions()`
  无参调用
- 教训：actionSheet 菜单项数是跨端硬约束，**加项前先数项数**；H5 验证不能替代
  小程序验证。type-check 通过，待小程序 devtools 实测。

### 已迁移且更好（不用补）

- 主题 CRUD / 置顶 / 移至最前 / 删除：biz-topic-panel 长按菜单全覆盖，真分页（backup 是 size:1000 假分页）
- 日志置顶 / 移至最前 / 标记 / 删除：useTopicLogActions 长按菜单
- 复制 / 分享日志：也进长按菜单（backup 复制在行内 footer、分享跳独立海报页）；
  海报依赖抽成 so-poster-share 挂件复用，不用像 backup 那样过 globalData 传参
- 排序统一在读取出口施加（backup 只在本地增删时排，读取不排，置顶是否生效看后端心情）
- 记录详情页 + 任意层级跟进：backup 没有，纯新能力
- 主题编辑校验：NAME_MAX 50 / DESC_MAX 2000，与后端 binding 对齐
- 主题置顶入口：backup 列表卡片有置顶按钮，新面板长按「移至最前」即置顶 + 已置顶给「取消置顶」，能力等价
