# 近期任务模块 · 过程记录

- 任务目录：`task/dev-flow/260930_superone-frontend/`
- 阶段：02 前端开发
- 时间：2026-10-05

## 做了什么

- 对照 backup 的 plan/task 页面、日志 composable 与后端 plan DTO，确认近期任务接口支持搜索、状态过滤、分页、置顶和 CRUD；Topic log 支持 `RecentTask` 类型：`business-repo/uni-superone-backup/src/pages/plan/`、`business-repo/backend-superone/internal/domain/plan/plan_dto/recent_task_dto.go`、`business-repo/uni-superone/src/contracts/types/topic.ts`。
- 将已确认范围写入 `../plan-module-inventory.md`：只迁移近期任务；OKR 不迁移；不迁移 backup 未接入 UI 的复制辅助方法。初版曾补搜索入口，后按用户明确要求移除。
- 新增 `useRecentTaskList` 与计划面板：列表分页/刷新、状态筛选、任务状态快捷操作、置顶与删除；接入首页现有 rail/swiper 和底部「新建任务」动作。
- 新增近期任务编辑页和详情页：新建/编辑/删除、状态/优先级/截止日/逾期信息、Markdown 描述、进展日志分页/新增/删除/编辑跳转，以及把任务快照保存为日志。
- 在 `src/pages.json` 注册两页；更新任务 README 与 registry 的范围说明。
- 按后续明确要求移除任务关键词搜索，并将状态筛选缓存到 `CACHE_KEYS.RECENT_TASK_STATUS_FILTER`，下次挂载时恢复有效状态值；清理清单、任务 README 与本过程记录中的搜索范围描述。
- 2026-10-06：在近期任务详情卡片中显示除当前状态外的可流转状态按钮；提交中禁用按钮，成功后更新详情并广播列表刷新事件。

## 得到的结论

- 不需要改后端或 frontend-contracts：本轮调用均由现有 `planApi` 与 `topicApi` 契约覆盖。
- 任务删除接口只删除任务实体，没有同步删除 RecentTask 日志；确认文案说明日志之后无法再从该任务入口查看，避免宣称后端级联删除：`business-repo/backend-superone/internal/domain/plan/plan_service/recent_task_service.go`、`business-repo/backend-superone/internal/repo/recent_task_repo.go`。
- Carbon 只作为内容滚动、分页/刷新状态和克制层级的参考；实现继续使用 Superone `--so-*` 令牌与组件，不复制 Carbon 品牌语义。

## 被推翻的判断

- 起初按 backup composable 中存在搜索方法而补了列表搜索控件；豆哥明确近期任务不需要关键词搜索后，删除搜索入口与对应状态/防抖逻辑，仅请求空 keyword 满足现有契约。
- backup 的快照入口容易被误读为图片分享；核实 `handleSaveSnapshot` 后确认其实际行为是把 Markdown 快照创建为一条任务日志，因此按该行为迁移。

## 待核 / 没答上来

- 本轮按指示未运行 type-check、build 或人工小程序验收；实现尚未经过这些验证。
