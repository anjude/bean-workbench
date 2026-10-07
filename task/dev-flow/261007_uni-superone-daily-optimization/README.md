# 261007 uni-superone 日常优化

## 目标

集中记录并推进 `uni-superone` 的日常前端体验、交互、样式、稳定性与维护性优化，避免零散优化失去上下文。

## 范围

- 主仓：`business-repo/uni-superone`
- 按具体优化内容关联 `business-repo/frontend-contracts` 或 `business-repo/backend-superone`。
- 逐项记录目标、影响范围、实现与验证；涉及开发需求时按 dev-flow 完成方案、前端开发和整体验证。

## 边界

- 不把新的独立业务功能或跨端需求默认并入本任务；先判断是否应单独建任务。
- 若优化涉及 API、DTO、响应结构、错误码、枚举或数据语义，回到工作台编排后端与协议仓。
- 未经明确业务需求，不改其他业务仓。

## 当前状态

已完成；backend、frontend-contracts、uni-superone 代码均已提交并推送 release，test/live 数据库 DDL 与层级回填均已执行并核验。

## 沉淀候选

- 可复用的 uni-superone 优化模式与问题排查经验。
- 经多次验证后适合补入前端开发 skill 的流程或规范。

## 本轮优化方案（2026-10-07）

### 需求

1. 跟进最多三级，并确认前后端都能支持三级。
2. 缩小编辑记录页 Markdown 编辑器的初始高度。
3. Superone 详情页操作保持原有右上角位置和简洁视觉，不占描述正文空间。
4. 主题记录时间轴跨年时显示年份。

### 现状与判断

- `topic_log_tab.parent_log_id` 以自关联记录父子关系，数据库可表示多层结构；创建服务目前不验证父记录存在、所属主题一致或深度，实际允许任意层级。删除通过 BFS 收集后代，原实现最多扫描 10 层；本轮改为遍历全部后代并用 visited 集合防环。层级字段由迁移回填并在创建时维护。
- uni-superone 的记录详情页对任意记录都展示跟进编辑框，创建请求把当前记录 ID 作为 `parentLogId`；跟进列表可继续进入详情，因此 UI 也允许递归进入任意层级。三级在现有结构上可支持，但需在第三层隐藏创建入口，并由后端拒绝超深创建。
- 记录编辑器调用显式指定 `:height="320"`，组件默认 `height` 为 200，`autoHeight` 默认开启且该高度同时作为最小高度。因此只改组件默认值不会影响当前记录编辑页，需要同时调低该处显式高度（或移除该覆盖）。
- `so-timeline` 日期目前固定显示月-日；公共时间格式工具已有完整年月日格式。
- 页面级操作入口紧凑地放在详情卡片标题行右侧，采用低强调的轻量样式。

### 目标与边界

#### 本期目标

- 层级从 0 开始：根记录 level=0，第一层跟进 level=1，第二层跟进 level=2；最多三层，level=2 不可再创建子跟进。
- 后端在 `topic_log_tab` 持久化层级，创建时校验父记录存在、当前用户可访问、主题类型和主题 ID 一致，并拒绝生成第 4 级；详情响应直接返回字段，避免读取时查询祖先链。
- 对已有超过三级的历史记录按真实层级回填，保留浏览、编辑和删除能力，不再允许从 level=2 及更深记录创建新跟进。
- 记录编辑页编辑器初始高度从 320px 降到 160px；组件缺省高度从 200px 降到 120px，显式传高的其他场景不受影响。
- 主题、记录、物品、近期任务以及清单的执行/编辑/更多入口位于详情卡片右下角，与创建/更新时间 footer 同行，并沿用原按钮样式。
- 清单分享入口保留在“清单内容”标题行，不移入详情卡片 footer。
- 时间文案可缩短，为 footer 操作按钮留出空间；操作入口随卡片滚动，不固定在页面边缘。
- 时间轴在跨当前年份的记录上显示完整年月日，同年记录仍用月-日。

#### 本期不做

- 不迁移或删除已有超过三级记录的内容；仅回填层级字段，保留浏览、编辑和删除能力。
- 不改变记录的 Markdown 内容格式，不新增标题字段。
- 新增 `topic_log_tab.level` 字段；通过迁移 SQL 扩表，再运行回填 action 初始化历史数据。

### 改动范围

#### `business-repo/backend-superone`

- `internal/domain/topic/topic_service/topic_service.go`：创建跟进时验证父记录关系并计算/限制层级。
- `internal/domain/topic/topic_dto/topic_dto.go`、`topic_service.go`：直接返回持久化的实际层级，限制创建深度并校验父记录所属主题和可访问性。
- `internal/model/topic_log_tab.go`、`scripts/migration/sql/20261007_add_topic_log_level.sql`、`scripts/migration/backfill_topic_log_level.go`：增加字段并回填历史数据。
- 对应 topic service 测试：覆盖根记录 level=0、跟进 level=1/2 允许、level=3 拒绝，以及无效父记录/跨主题父记录拒绝。迁移测试覆盖正常层级、孤儿和循环关系。

#### `business-repo/frontend-contracts`

- `openapi/topic_api.yaml`：说明 `CreateTopicLogReq.parent_log_id` 的最大层级与父记录要求；详情响应新增 `level` 字段。
- `types/topic.ts`：为详情响应增加层级类型；客户端通过 `src/contracts` 子仓消费对应协议修订。

#### `business-repo/uni-superone`

- `src/pages/log-detail/index.vue`：依据当前记录层级隐藏第三级之后的跟进编辑卡；查看、编辑操作位于记录详情卡片右下角 footer。
- `src/pages/topic-detail/index.vue`、`src/pages/checklist-detail/index.vue`、`src/pages/item-detail/index.vue`、`src/pages/plan-task-detail/index.vue`：将操作入口放到详情卡片时间 footer 同行右侧。
- `business-repo/uni-superone/AGENTS.md`：沉淀详情卡片 footer 操作区约定，供后续页面复用。
- `src/components/so-detail-actions.vue`：提供详情页操作入口，沿用既有按钮样式。
- `src/components/so-md-editor.vue`：降低组件 `height` 缺省值。
- `src/components/so-timeline.vue`、`src/utils/time.ts`：根据记录年份格式化时间轴日期。
- footer 对齐样式分别落在 `src/styles/06-pages/_p-log-detail.scss`、`src/styles/06-pages/_p-topic-detail.scss`、`src/styles/06-pages/_p-checklist-detail.scss` 及物品/任务页内联样式；按钮外观沿用组件原样式。

### 原型与状态摘要

- 跟进仍是记录详情页中的递归子记录工作流；状态包括：level=0/1 可跟进、level=2 只读其已有子记录（若有）、超深历史记录可浏览但无新增入口、创建失败显示后端错误。
- 各详情页查看态操作入口位于对应详情卡片右下角，并与时间信息同行；记录编辑态取消/保存也位于卡片 footer 右侧。
- 页面不再为操作按钮预留屏幕底部空间；按钮随详情卡片自然滚动。
- 时间轴空、加载、失败分支不变，仅日期标签格式根据年份变化。

### 验收标准

1. 根记录 level=0、跟进 level=1/2 可创建；level=3 请求由后端拒绝，前端 level=2 不展示创建跟进入口。
2. 不存在的父 ID、其他主题或类型的父记录、不可访问父记录不能被用作跟进父节点。
3. 记录编辑页编辑器初始高度为 160px；未传高度的编辑器最小高度为 120px；传入高度的既有调用维持各自高度。
4. 主题、记录、物品、近期任务和清单执行/编辑/更多入口位于各自卡片右下角、与时间信息同行；清单分享仍在“清单内容”标题行。
6. 时间轴中当前年份日期显示月-日，其他年份显示 YYYY-MM-DD。

### 验收步骤

| 场景 | 操作 | 预期结果 |
|---|---|---|
| 跟进层级 | 根记录 level=0，连续创建到 level=2，再尝试创建 level=3 | level=0/1/2 成功；level=2 没有新建入口；直接请求 level=3 被后端拒绝 |
| 父记录有效性 | 用不存在、跨主题或不可访问的父 ID 创建跟进 | 请求被拒绝，不产生孤立或跨主题记录 |
| 编辑器高度 | 打开记录编辑页，并查看未显式传高度的编辑器 | 记录编辑页初始 160px；组件缺省 120px；显式高度调用维持原值 |
| 页面操作区 | 查看主题、记录、清单、物品和近期任务详情 | 操作入口在卡片右下角与时间信息同行；清单分享在“清单内容”标题行 |
| 跨年日期 | 查看包含当前年和往年记录的时间轴 | 当前年为月-日，往年显示年份 |

### 实施顺序

1. 数据库新增层级字段并回填现存数据；后端创建时写入层级、校验父记录关系并直接返回详情层级。
2. 更新 OpenAPI 语义说明并同步共享契约。
3. 前端按详情层级控制跟进入口，并将操作按钮放到卡片时间 footer；完成编辑器和时间轴日期优化。
4. 按受影响端进行整体验收并回填结果。

### 落地记录

- 后端跟进校验、持久化层级字段及历史数据回填脚本、超深后代删除遍历、OpenAPI/TypeScript 契约、uni-superone 页面和组件调整已完成。
- test：`weiyi_superone_db_test` 共 145 条记录（135 根记录），level 字段结构正确，根/子层级不一致与孤儿均为 0。
- live：`weiyi_superone_db` 共 1242 条记录（1207 根记录），level 字段结构正确，根/子层级不一致与孤儿均为 0。
- 代码已推送 release：backend `63f6dfe`、frontend-contracts `e701efc`、uni-superone `32b13aa`；release restriction 更新提交为工作台 `29a1280`。
- 验证：`go test ./internal/domain/topic/topic_service ./scripts/migration`、前端 `npm run type-check`、`npm run build:h5`、`npm run build:mp-weixin`；`go test ./...` 的 test 集成包因本机 Redis 不可用失败；完整结果见 `process/03-整体验证.md`。
