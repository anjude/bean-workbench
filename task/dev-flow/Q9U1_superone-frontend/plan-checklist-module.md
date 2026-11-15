# 清单（checklist）模块前端方案

## 背景

backup（uni-superone-backup）有一套完整的清单功能：清单 CRUD、执行（勾选 + 备注 + 总结）、执行历史与总结分享。当前 superone 前端（uni-superone）首页面板已预留「清单」位（`PANELS[1]`，占位组件），契约层 `checklistApi` 已生成接线（`src/contract.ts:30`），但页面与状态层是空白。本方案按当前 superone 风格（行式列表 + 分隔线、系统 actionSheet、composable 业务流、页面薄）重新设计该模块。

## 需求理解

把 backup 的清单能力以 superone 现有风格落地：首页清单面板 + 新建/编辑页 + 详情页（含执行历史）+ 执行页 + 执行记录页，全程复用已生成的 `checklistApi` 契约。

## 目标与边界

### 本期目标

- 首页「清单」面板：列表（置顶标记、时间、摘要）、下拉刷新、真分页加载、长按菜单（移至最前 / 编辑 / 删除，已置顶多一项取消置顶），底部主按钮「新建清单」进编辑页。
- 清单编辑页：新建 / 编辑共用（带 `id` 参数区分），标题 + 条目列表（增、删、上移、下移），标题上限 100、条目上限 50。
- 清单详情页：标题 / 元信息 / 条目预览 + 执行历史列表（时间倒序），⋯ 菜单（编辑 / 删除 / 分享海报）。
- 执行页：常驻执行标题与进度（x/y + 百分比 + 进度条）、逐条勾选 + 可展开 Markdown 备注、Markdown 整体总结、操作菜单（全部完成 / 全部清除 / 重置）、完成执行（未完成条目确认后自动跳过）；支持本地草稿与经执行历史进入续跑（传 `executionId`）。
- 执行历史行内操作：分享、编辑和删除执行记录。
- 执行记录页：统计（完成率 / 耗时 / 起止时间）+ 逐条总结 + 整体总结 + 分享总结海报（so-poster-share）。
- 修正契约枚举取值（见「涉及前端契约」）。

### 本期不做

- **分步执行模式 UI**：后端 `mode` 有 1=正常执行 / 2=分步执行两种，backup 的执行页也只接了总览一种（`execute-overview/index.vue:203` 硬编码 `ExecutionMode.Overview`）。本期执行页固定 `mode=1`，分步交互设计留到真有需求时再做。
- **清单搜索**：与主题面板一致不做；契约 `keyword` 参数保留，后续要补成本低。
- **编辑预览**：backup 的清单编辑页预览弹窗本期不做。
- **执行记录编辑模式外的状态机**：执行记录仅「进行中 → 已完成」，不支持把已完成改回进行中（backend `Complete()` 单向）。
- 后端、库表、接口路由：零改动（接口与表已存在且够用）。

## 改动范围

### 涉及仓库

- `business-repo/uni-superone`（主改动，纯前端）。
- `business-repo/frontend-contracts`（仅同步 openapi 枚举描述文案，一行注释级）。

### 涉及库表

无。`checklist_v2_tab`、`checklist_execution_record_tab` 已存在，不动。

### 涉及接口

无新增。消费已存在的 11 个 `/api/so/checklist/**` 接口（list / detail / create / update / delete + execution 的 list / detail / create / update / delete / history），鉴权沿用 JWT Bearer。前端调用面 `checklistApi` 已生成（`src/contracts/apis/checklist.ts`），不改签名。

### 涉及前端契约

**必须修正：枚举取值错误**（`src/contracts/types/checklist.ts:3-13`）。

证据链（已核实）：

- 后端常量 `constant/checklist.go:7-8,30-31`：`iota + 1`，即 mode 1=正常执行 / 2=分步执行，status 1=进行中 / 2=已完成。
- 后端实体逻辑依赖该取值：`execution_entity.go:181,186` 的 `IsCompleted()` / `IsInProgress()` 直接与常量比较；`NewChecklistExecutionRecord` 默认 status=进行中（119 行）。
- 后端 create DTO `execution_dto.go:32,38` 对 `mode` / `status` 有 `binding:"required"`——int 的 required 即非 0，**契约里的 0 值根本发不出去**（会直接被参数校验拒）。
- 后端 DTO 注释与 DB 注释写的 0-based 是过期注释，不作数；backup 客户端发 1/2（`enums.ts:117-125`），与常量一致，是对的。
- 当前 superone 无任何清单消费代码，改枚举无回归面（已 grep 确认）。

改法：

- `ExecutionMode`：`Normal: 1, StepByStep: 2`（对齐后端 String() 文案「正常执行 / 分步执行」）。
- `ExecutionStatus`：`InProgress: 1, Completed: 2`（替换现有 `Draft: 0, Finished: 1` 命名与取值）。
- `src/contracts/openapi/checklist_api.yaml` + `business-repo/frontend-contracts/openapi/checklist_api.yaml`：mode / status 字段描述改为 1-based 并注明「0 会被 binding:required 拒绝」。

### 涉及页面

全部在 `business-repo/uni-superone`：

| 文件 | 动作 | 说明 |
| --- | --- | --- |
| `src/pages.json` | 改 | 注册 4 个新页面路由 |
| `src/pages/index/index.vue` | 改 | 面板分派加 `panel.key === 'checklist'` 分支 + import |
| `src/components/business/biz-checklist-panel.vue` | 新增 | 首页清单面板，结构照 `biz-topic-panel.vue` |
| `src/pages/checklist-edit/index.vue` | 新增 | 新建 / 编辑共用 |
| `src/pages/checklist-detail/index.vue` | 新增 | 详情 + 执行历史 |
| `src/pages/checklist-execute/index.vue` | 新增 | 执行页（勾选 + 备注 + 总结） |
| `src/pages/checklist-execution-detail/index.vue` | 新增 | 执行记录（统计 + 总结 + 分享） |
| `src/composables/useChecklistList.ts` | 新增 | 面板列表：load / loadMore / moveToFront / unpin / remove |
| `src/composables/useChecklistForm.ts` | 新增 | 编辑页：加载、条目增删与排序、保存 |
| `src/composables/useChecklistDetail.ts` | 新增 | 详情页：清单实体 + 执行历史分页 |
| `src/composables/useChecklistExecution.ts` | 新增 | 执行页：进度状态机、create / update、完成 |
| `src/composables/useChecklistExecutionDetail.ts` | 新增 | 执行记录页：详情 + 统计计算 |
| `src/contracts/types/checklist.ts` | 改 | 枚举取值修正（上文） |
| `src/contracts/openapi/checklist_api.yaml` | 改 | 枚举描述同步 |

页面状态分支（硬门槛）：每个页面补齐 loading / 空数据 / 失败重试 / 请求中防重复提交；执行页与编辑页有本地态（未保存退出不拦截，与主题编辑一致）。

## 实施方案

1. **契约修正先行**：改 `types/checklist.ts` 枚举 + 两份 openapi yaml 描述。这是后续一切的前提。
2. **数据层**（composables）：五个 composable 只调 `checklistApi`、抛业务错误（toast 由页面或 composable 内统一处理，照 `useTopicList` 的先例：composable 抛错，页面 toast）。列表排序由后端给（`top DESC, create_time DESC`），前端不重排。执行进度由 `stepSummaries` 推导：`confirmTime` 有值且 `isSkipped` 不为真 = 已完成。
3. **面板**：照 `biz-topic-panel.vue` 抄骨架（eyebrow + 大标题 + 说明、三态、refresher、触底加载防抖 12px），摘要行取条目首条纯文本（`toPlainText`，60 字截断）。长按菜单顺序：移至最前 / （取消置顶） / 编辑 / 删除。事件：`checklist:changed`（编辑页、执行页保存后 `$emit`，面板监听重拉，照 `topic:changed`）。
4. **编辑页**：标题输入 + 条目行（内容输入框 + 删除 / 上移 / 下移 小按钮）+ 底部「添加条目」。校验：标题非空 ≤100、条目 1–50、单条内容非空。保存走 create（无 id）或 update（有 id），成功 toast 并 `$emit('checklist:changed')` 后返回。
5. **详情页**：头部（标题 / 置顶标 / 创建更新时间）+ 条目预览（前几条纯文本，更多折叠「共 N 条」）+ 执行历史行式列表（模式文案、状态、起止时间，点进执行记录页）+ 底部主按钮「开始执行」。⋯ 菜单：分享（海报：标题 = 清单名，note = 条目摊平，bullets = 条目数 / 更新时间）/ 编辑 / 删除。
6. **执行页**：顶部进度（x/y、百分比、进度条）；条目列表：勾选框 + 内容（Markdown 渲染）+ 展开备注编辑（so-md-editor 或纯文本输入，照 log-detail 的跟进输入）；底部整体总结输入 + 「完成执行」主按钮。操作菜单（系统 actionSheet）：全部完成 / 全部清除 / 重置。完成时未完成条目弹确认「N 条未勾选，将记为跳过」→ 确认后 `isSkipped=true` 一并提交：create（新执行）或 update（续跑），带 `status=Completed(2)`、`finishTime`、整体总结、stepSummaries。中途退出：已 create 的记录每次勾选变更即 update 落库（与 backup 一致，防丢进度）；续跑模式进入时先 getExecutionDetail 回填。
7. **执行记录页**：统计卡（完成率、耗时、开始 / 完成时间、模式、状态）+ 逐条总结列表（跳过标灰）+ 整体总结 + ⋯ 分享海报（标题 = 清单标题，note = 整体总结，bullets = 完成率 / 耗时）。未完成记录点底部按钮「继续执行」跳执行页续跑。
8. **样式**：全部走 `--so-*` 令牌、行式 + 分隔线（不引入卡片外框）、系统组件优先；图标沿用现有 SVG 资产，缺的在 `dev-flow-0204` 里补。

## 验收标准

- `npm run type-check` 通过。
- `npm run build:mp-weixin` 通过。
- 微信开发者工具实测（不接受 H5 替代，H5 与小程序组件行为已多次出现差异）：建清单 → 面板出现且置顶标记正确；长按四项菜单可用；编辑改标题 / 调序保存生效；开始执行 → 勾选 2 条 + 备注 + 完成（1 条自动跳过）→ 详情页执行历史出现该记录；点记录进执行记录页统计正确（完成率 2/3）；分享海报出图；删除清单需确认且列表移除。
- 契约枚举修正后，createExecution 实际请求体 `mode/status` 均为 1 或 2，不再触发 `binding:"required"` 报错。

## 推荐实施顺序

契约修正 → useChecklistList + 面板（首页可见）→ 编辑页 → 详情页 → 执行页 → 执行记录页 → 分享海报收尾 → type-check / build / 开发者工具实测。

## 测试方案

### 功能测试

| 序号 | 场景 | 操作 | 预期结果 |
| --- | --- | --- | --- |
| 1 | 新建清单 | 面板主按钮 → 编辑页填标题 + 3 条 → 保存 | toast 成功，返回面板出现新清单（最前） |
| 2 | 标题上限 | 编辑页输入 101 字标题 | 输入被截断在 100，保存成功 |
| 3 | 条目上限 | 添加第 51 条 | 「添加条目」不可用或 toast「最多 50 条」 |
| 4 | 条目排序 | 编辑页上移 / 下移 / 删除条目后保存 | 详情页条目顺序与编辑一致 |
| 5 | 编辑清单 | 长按「编辑」→ 改标题保存 | 面板与详情页标题更新 |
| 6 | 移至最前 / 置顶 | 长按「移至最前」；对已置顶项「取消置顶」 | 列表重排正确，置顶标记增删正确 |
| 7 | 删除清单 | 长按「删除」→ 确认 | 二次确认文案提示执行记录一并删除，确认后列表移除 |
| 8 | 开始执行 | 详情页「开始执行」→ 勾选条目 + 写备注 | 进度 x/y 与百分比实时更新 |
| 9 | 完成执行（有未完成） | 1 条未勾选点「完成执行」 | 弹确认「记为跳过」，确认后记录完成，完成率正确 |
| 10 | 执行历史 | 详情页查看历史 → 点记录 | 执行记录页统计 / 逐条总结 / 整体总结正确 |
| 11 | 续跑 | 未完成记录点「继续执行」 | 执行页回填勾选与备注，可继续并再次完成 |
| 12 | 分享 | 详情页 ⋯ 分享清单；记录页 ⋯ 分享总结 | 两张海报出图，内容正确 |
| 13 | 全部完成 / 清除 / 重置 | 执行页操作菜单三项 | 勾选态相应变化，进度同步 |

### 回归测试

| 序号 | 场景 | 操作 | 预期结果 |
| --- | --- | --- | --- |
| 1 | 主题面板不受影响 | 首页切主题面板，增删主题 | 行为与改动前一致（首页模板只加分支） |
| 2 | 记录长按菜单 | 主题详情页长按记录 | 5 项菜单（移至最前 / 置顶 / 切换主题 / 标记 / 删除）正常 |
| 3 | 详情页 ⋯ 菜单 | 记录详情页点 ⋯ | 编辑 / 复制 / 分享 / 删除正常 |
| 4 | 双主题 | 浅色 / 深色切换下看四个新页面 | 令牌全部走 `--so-*`，无硬编码色 |
| 5 | 下拉刷新与分页 | 面板下拉、滑到底 | refresher 正常收起，触底加载下一页，「没有更多了」收尾 |

### 兼容性测试

| 序号 | 场景 | 预期结果 |
| --- | --- | --- |
| 1 | 旧数据（backup 时期产生的执行记录） | 记录里 mode/status 已是 1/2，新前端按 1-based 读，展示正确 |
| 2 | 空清单（0 条目）执行 | 执行页进度 0/0，完成执行可直接提交整体总结 |
| 3 | 无网络 | 各页面错误态 + 重试按钮可用，不白屏 |

## 风险与回滚

- **枚举修正**：当前无清单消费代码，无回归面；唯一风险是 frontend-contracts 描述与后端 DTO 注释（0-based）继续误导后人，方案里已把两处注释同步改掉。
- **执行页中途退出**：采用 backup 同款「变更即落库」策略，create 后每次勾选 / 备注失焦都 update；风险是请求频率，条目 ≤50 可控。
- **小程序 actionSheet 6 项上限**：执行页操作菜单 3 项、长按菜单最多 4 项、⋯ 菜单 3 项，均有裕量。
- 回滚：全部改动在 uni-superone 前端 + 一份契约描述，无 DDL；git revert 即可。

## 落地记录

- 前端已按本方案完成：首页面板、清单新建/编辑、详情与执行历史、执行与续跑、执行记录总结和海报分享；五个 composable 承接接口状态与交互流程。
- 契约枚举已修正为 1-based，并同步 `business-repo/uni-superone/src/contracts` 与 `business-repo/frontend-contracts`。
- 验证：`npm run type-check` 通过。实现期间也运行过 H5 与微信小程序构建，均通过；微信开发者工具已载入新面板并显示真实列表。
- 页面交互、完整 CRUD / 执行闭环、海报出图与多端人工验收留待用户确认。
- 根据人工反馈追加：首页列表加执行入口并缩短行距；编辑条目、执行备注及整体总结统一切换为 `so-md-editor`；执行标题和进度固定在内部滚动区上方。已复跑 `npm run type-check` 并通过。
- backup 对照结论：本次反馈提出的本地草稿、执行标题、执行历史行内操作均已补齐；编辑预览按要求不做。
