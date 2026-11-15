# topic 模块 P0 闭环（主题与记录的增删改 + 后端级联删除）

## 背景

topic 模块目前只接了 4 个接口（list / detail / log/list / log/create），只能「看」和「写」，
删不掉也改不了。豆哥拍板：

1. **删除孤儿问题在后端补**——删根记录要级联删掉它的所有跟进（子记录）。
2. **不做独立 topic 列表页**（首页面板已经是列表）、**不做搜索**（02-14 已拍板）、
   **长按与置顶放在首页面板完成**。
3. P0 开工。

## 需求理解

- 动作：新增、修改、删除。
- 对象：主题（topic）、记录（topic log，含跟进子记录）。
- 边界：本期只补齐增删改闭环，不做分享/复制/跨主题迁移/批量。
- 数据：不新增表、不改字段，`parent_log_id` 与 `idx_topic_log_parent` 已在
  `20261002_add_topic_log_parent.sql` 落库，本期只动删除逻辑。
- 接口：全部已存在（`topic/create|update|delete`、`topic/log/detail|update|delete`），
  **契约与前端契约仓都不用改**。
- 端：跨端。后端先改（前端删除功能依赖级联语义），再前端。

## 目标与边界

### 本期目标

- 后端：删除记录级联删除全部子孙；修掉 `TopicRepo.Del` 被删日志误用的问题（见下）。
- 前端：首页面板支持新建入口与长按菜单（置顶 / 编辑 / 删除）；主题编辑页；
  记录详情页（查看 + 编辑 + 删除）；主题详情页补回操作入口（编辑 / 删除）。

### 本期不做

- 独立 topic 列表页、搜索框
- 记录分享到海报、复制、跨主题迁移
- 批量选择与批量删除
- 主题「移至最前」（与置顶共用 `top`，只是取最大时间戳，语义重复）
- 记录置顶 / mark 标记的交互入口（`so-timeline` 已渲染 mark，交互留到下一期）

## 改动范围

### 涉及仓库

| 仓库 | 改动 |
|---|---|
| `business-repo/backend-superone` | 删除逻辑（repo + service） |
| `business-repo/uni-superone` | 页面、composable、组件 |
| `business-repo/frontend-contracts` | **不改**（接口与字段都已存在） |

### 涉及库表

| 表 | 改动 |
|---|---|
| `topic_log_tab` | 不改结构；删除时按 `parent_log_id` 递归收集子孙一并删除 |

### 涉及接口

| method | path | 改动 |
|---|---|---|
| POST | `/api/so/topic/log/delete` | 行为变更：级联删除子孙（Req/Resp 不变） |
| POST | `/api/so/topic/delete` | 行为不变（仍级联删该主题全部日志），但不再走重载的 `Del` |
| 其余 8 个 | — | 前端开始调用，后端不动 |

### 涉及文件

后端：

- `internal/repo/topic_repo.go` —— 拆出显式删除方法，去掉 `Del` 重载
- `internal/repo/repo.go`（`ITopicRepo` 接口）—— 加新方法声明
- `internal/domain/topic/topic_service/topic_service.go` —— `DeleteTopicLog` / `DeleteTopic` 改调新方法

前端：

- `src/pages/topic-edit/index.vue`（新）—— 新建 / 编辑主题
- `src/pages/log-detail/index.vue`（新）—— 记录详情 + 编辑 + 删除
- `src/pages.json` —— 注册两页
- `src/composables/useTopicEdit.ts`（新）或并入 `useTopicDetail`
- `src/composables/useTopicList.ts` —— 加置顶、删除
- `src/components/business/biz-topic-panel.vue` —— `open()` 跳新建；列表项长按菜单
- `src/pages/topic-detail/index.vue` —— 补操作入口（编辑 / 删除），记录可点进详情
- `src/components/so-timeline.vue` —— 记录项可点击（进详情）

## 实施方案

### 后端：删除语义拆开（含一个必须一并修的问题）

现状（`topic_repo.go:153-167`）：

```go
// Del 重写删除方法，实现级联删除主题记录
func (t *TopicRepo) Del(ctx *bizctx.BizContext, tab model.IBaseTab, id int64) *ecode.BizError {
	return ctx.Transaction(func() *ecode.BizError {
		// 1. 先删除主题记录（topic_type=1）
		if err := ctx.GetDB().Where("topic_id = ? AND topic_type = ?", id, constant.TopicTypeTopic).
			Delete(&model.TopicLogTab{}).Error; err != nil { ... }
		// 2. 再删除主题本身
		return bizctx.DeleteDataById(ctx, tab, id)
	})
}
```

`Del` 是为「删主题」写的（`topic_service.go:164`：`Del(ctx, topic, req.ID)`，语义正确）。
但 `DeleteTopicLog` 也调了它（`topic_service.go:363`：`Del(ctx, log, req.ID)`）——
此时 `id` 是**日志 ID**，第 1 步会执行
`DELETE FROM topic_log_tab WHERE topic_id = <日志ID> AND topic_type = 1`，
把「topic_id 恰好等于该日志 ID」的那个主题下的**全部日志删掉**。
两张表 id 各自自增，撞上是概率事件不是不可能事件，属误删。

修法：不再靠 `Del` 重载区分语义，拆成两个显式方法。

```go
// DeleteTopicLogsByTopicID 删除某主题下的全部记录（供删主题调用）
func (t *TopicRepo) DeleteTopicLogsByTopicID(ctx *bizctx.BizContext, topicID int64) *ecode.BizError

// DeleteTopicLogWithChildren 删除一条记录及其全部子孙（按 parent_log_id 逐层收集）
func (t *TopicRepo) DeleteTopicLogWithChildren(ctx *bizctx.BizContext, logID int64) *ecode.BizError
```

- `TopicRepo.Del` 删除重写，退回 `BaseRepo.Del`（按 id 单删）。
- 子孙收集用 **BFS 逐层**，`SELECT id FROM topic_log_tab WHERE parent_log_id IN (...)`，
  直到某层为空；UI 只做两层，但库里允许任意层级，按层收集更稳。层级加一个上限（如 10 层）防脏数据成环。
- 整段仍在 `DeleteTopicLog` 已有的 `ctx.Transaction` 内，保证原子。

### 级联删除的权限取舍（有风险，需豆哥确认）

**只校验根记录的删除权限，子孙随父删除，不逐条校验 openid。**

- 理由：留着子孙就是孤儿，与本需求目的冲突。
- 风险：carbon 共享空间场景下，A 建根记录、B 在下面跟进，A 删根会连带删掉 B 的跟进。
- 兜底：删除前给出二次确认文案（前端写清「会同时删除 N 条跟进」）。
- 若要改为「只删自己有权限的子孙」，会重新制造孤儿，不建议。

### 前端

1. **主题编辑页** `pages/topic-edit/`：新建与编辑同页（带 `id` 进为编辑）。
   名称必填、≤50；描述走 `so-md-editor`（≤2000）；底部主按钮文案随态切「创建 / 保存」。
2. **首页面板**：底部主按钮 `open()` 从 toast 改为跳新建页；列表项**长按**出菜单
   （置顶 / 编辑 / 删除），置顶走 `topic/update` 传 `top`（0 ↔ 当前秒级时间戳）。
3. **记录详情页** `pages/log-detail/`：读 `topic/log/detail`（列表接口 `preview` 是截断文本，
   详情要完整正文）；页内可编辑（`topic/log/update`）与删除（`topic/log/delete`）。
4. **主题详情页**：补回操作入口（编辑 / 删除），记录项可点进记录详情页。

## 推荐实施顺序

1. 后端：`TopicRepo` 拆方法 + 修 `DeleteTopicLog`（含单测/构建）
2. 后端：gofmt / build / vet
3. 前端：主题编辑页 + 首页 `open()` 接线 + 长按菜单
4. 前端：记录详情页（查看 / 编辑 / 删除）
5. 前端：主题详情页操作入口
6. 验证：type-check / build / 真机冒烟

## 验收标准

- 删一条有子记录的日志后，库里该日志与其全部子孙都不存在（无孤儿）。
- 删一条与任何 `topic_id` 同号的日志，其它主题的日志不受影响。
- 删主题仍级联删除其全部日志。
- 前端能新建 / 编辑 / 删除主题，能查看 / 编辑 / 删除记录。
- `npm run type-check` 与 `npm run build:mp-weixin` 通过；后端 `gofmt` / `go build` / `go vet` 通过。

## 测试方案

### 功能测试

| 序号 | 场景 | 操作 | 预期结果 |
|---|---|---|---|
| 1 | 删无跟进的记录 | 删一条 `parent_log_id=0` 且无子的记录 | 只删这一条 |
| 2 | 删有 2 条跟进的记录 | 建根 + 2 条跟进后删根 | 根与 2 条跟进全部删除 |
| 3 | 删有多层跟进的记录 | 根 → 子 → 孙 | 三层全删 |
| 4 | 日志 id 与某 topic_id 撞号 | 造一条 id 等于某 topic_id 的日志并删除 | 该 topic 下的日志不受影响 |
| 5 | 删主题 | 删一个有 3 条日志的主题 | 主题与 3 条日志全删 |
| 6 | 前端新建主题 | 首页主按钮 → 填名称 → 创建 | 列表出现该主题，返回上一页 |
| 7 | 前端编辑主题 | 长按 → 编辑 → 改名称 → 保存 | 列表与详情显示新名称 |
| 8 | 前端置顶主题 | 长按 → 置顶 | 该主题排到列表首位 |
| 9 | 前端删主题 | 长按 → 删除 → 确认 | 列表移除 |
| 10 | 查看记录详情 | 详情页点一条记录 | 展示完整正文（非 preview 截断） |
| 11 | 编辑记录 | 记录详情页改内容 → 保存 | 回到列表显示新内容 |
| 12 | 删记录（含跟进） | 记录详情页删除 → 确认 | 记录与其跟进一并消失 |

### 回归测试

| 序号 | 场景 | 操作 | 预期结果 |
|---|---|---|---|
| 1 | 首页主题列表 | 下拉刷新、上拉加载 | 分页正常 |
| 2 | 主题详情写记录 | 输入 → 记下来 | 列表新增且清空输入框 |
| 3 | Markdown 渲染 | 含标题/列表/代码块的记录 | 渲染正常 |
| 4 | 编辑器工具栏 | 聚焦后点粗体/列表/图片 | 生效 |
| 5 | 其它 topicType 的日志 | feedback / beanflow 等 | 不受删除改动影响 |

### 兼容性测试

| 序号 | 场景 | 预期结果 |
|---|---|---|
| 1 | 历史记录（`parent_log_id` 默认 0） | 删除行为与改动前一致 |
| 2 | 无子记录的记录 | 不受级联逻辑影响 |
| 3 | 前端契约未变 | 老版本前端不受影响 |

## 风险与回滚

- **风险 1**：级联删除连带删掉他人跟进（见上，需豆哥确认取舍）。
- **风险 2**：BFS 收集子孙在极端深链下多轮查询；已加层级上限（10）。
- **风险 3**：`Del` 语义变更可能影响其它调用方。已确认只有 `DeleteTopic` 与 `DeleteTopicLog` 两处调用，
  改后各自走显式方法，行为分别是「删主题及其日志」与「删记录及其子孙」。
- **回滚**：后端改 3 个文件，回滚到上一 commit 即可；无 DDL、无数据回填，不需要数据回滚。
  前端新增页面为纯增量，回滚不影响既有功能。

## 落地记录

- 2026-10-03 方案建立，待豆哥确认级联删除的权限取舍后开工后端。
- 2026-10-03 豆哥确认两条：① 传入的是 topic log 就算用 topicRepo，删的也是 topic log，
  拆成显式方法没问题；② **有父记录权限等同于有子记录权限，删父记录要删子记录，删子记录不能删父记录**。
- 2026-10-03 后端落地（repo 拆方法 + service 改调），gofmt / go build / go vet 全通过。
- 2026-10-03 前端落地：主题编辑页、记录详情页、首页面板长按菜单、主题详情页操作入口。
  type-check 与 build:mp-weixin 通过。真机冒烟未跑。
- 过程见 `process/10-03-crud-impl.md`。
