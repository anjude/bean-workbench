# 全项目 UI/UX 迁移 · 过程记录

- 任务目录：`task/dev-flow/261007_utools-refactor/`
- 阶段：02 前端开发
- 时间：2026-10-07

## 做了什么

- 将样式说明从 Topic 试点总结改成全项目规范，明确模块页、详情页、登录页的共享规则和业务边界：`business-repo/utools-superone/src/styles/README.md`。
- 扩展共享卡片规格，增加 compact/inset 两种密度；最近任务详情信息卡、记录编辑卡改用项目级 compact 卡片，详情描述启用 compact Markdown：`business-repo/utools-superone/src/styles/06-components/_cu-card.scss`、`src/views/PlanDetail.vue`。
- 压缩最近任务详情旧布局的留白、标题与记录操作控件尺寸：`business-repo/utools-superone/src/styles/07-pages/_plan-detail.scss`。
- 最近任务列表右键菜单迁移到 `CuContextMenu`，删除页面自绘菜单样式，并适配 composable 的关闭目标：`business-repo/utools-superone/src/views/PlanList.vue`、`src/styles/07-pages/_plan-list.scss`、`src/composables/usePlanManagement.ts`。
- 清理清单详情及列表对 Markdown 标题、段落、列表的重复深度覆盖，交由 `MarkdownViewer.cu-markdown--compact` 统一排版；全局 Markdown 编辑区内距收敛为紧凑规格：`business-repo/utools-superone/src/styles/07-pages/_checklist-detail.scss`、`_checklist-list.scss`、`src/components/MarkdownEditor.vue`。

## 得到的结论

- 用户澄清迁移范围是整个项目。Topic 仅是试点，不能以三个模块列表页已抽取共享样式作为全项目迁移完成：本轮覆盖所有适用页面，并保留登录页品牌布局等真实业务差异。
- 最近任务详情旧尺寸（20px 页面/卡片 padding、24px 标题、16-20px 区块间距）明显违背 uTools 有限纵向空间的密度目标，现使用共享卡片与紧凑间距。
- 最近任务列表的对象管理菜单与 Checklist/Topic 已有共享菜单职责一致，采用 `CuContextMenu`，状态变更菜单仍保留独立业务语义。
- 对 Markdown 内容的页面级重复 `:deep()` 样式会覆盖共享 Viewer 规则，应删除排版声明，仅保留内容结构和状态样式。

## 被推翻的判断

- “共享样式抽取并迁移到 Checklist/Plan 列表后，Topic UI/UX 迁移即可完成” → 被用户明确纠正：目标是全项目迁移；任务详情页、登录控件及其他共享组件同样需要审视：`README.md` 当前实施范围。

## 待核 / 没答上来

- `npm run typecheck` 通过。
- `npm run build` 通过，Vite 转换 1583 个模块并完成生产构建。
- `git diff --check` 通过。
- 不做浏览器检查，遵循用户此前明确要求。

## 2026-10-07 补充：统一主题与清单选择方块

- 排查发现两处虽然使用 `.cu-selectable-tab`，但置顶标记仍由页面各自定义：Topic 用 8px 圆点字符，清单用 🔝 emoji，导致内容占位、视觉大小和标签宽度不同；清单选择器容器另有 2px 垂直 padding。
- 新增共享 `cu-selectable-tab-wrap`、`cu-selectable-tab__indicator`、`cu-selectable-tab__label`，Topic 和清单使用同一容器结构与 6px 指示点，并移除各自的标记样式：`business-repo/utools-superone/src/styles/06-components/_cu-tag.scss`、`src/views/TopicList.vue`、`src/views/ChecklistList.vue`、两页样式文件。
- 复核 `npm run typecheck` 与 `git diff --check` 均通过；遵循用户要求未做浏览器检查。
- 后续复核发现两处仍挂有各自的 selector/page 类，分别覆盖 flex、滚动条和 gap，造成即使基础标签一致，选择方块所在容器仍可能不同。已移除这两页的专属选择器类，让 wrap、list、tab DOM 仅保留同一套 `cu-selectable-*` 类，页面只保留选择数据和事件差异；对应的历史页面样式一并删除。再次运行 `npm run typecheck` 和 `git diff --check` 均通过。
- 用户指出留白/margin 也有差异。进一步确认清单列表曾单独把 `.cu-module-page` 的纵向 `gap` 设为 `spacing-xs`，Topic 使用共享的 `spacing-sm`。已将全局模块页间距统一设为紧凑的 `spacing-xs`，并删除清单页覆盖；两页外层 padding 与响应式规则相同。修改后 `npm run typecheck`、`git diff --check` 均通过。

## 2026-10-07 补充：清单执行项交互与卡片层级

- 移除执行区域外层卡片，仅保留执行项自身卡片，避免卡片套卡片；调整执行区展示为单层内容列表：`business-repo/utools-superone/src/views/ChecklistList.vue`。
- 将复选框放到每项最左侧，点击条目内容区域即可切换完成状态；复选框本身、备注操作、链接和 Markdown 编辑器交互避免重复触发勾选。
- 将备注入口固定在条目内容行尾，并把单项 Markdown 编辑器的有效最小高度设为 64px（此前 `height=80` 但组件默认 `minHeight=200px`，导致实际输入框仍偏高）。
- `npm run typecheck` 与 `git diff --check` 通过；未进行浏览器检查。

## 2026-10-07 补充：清单备注常显双栏

- 按用户反馈取消每项的“备注”按钮和按需显示状态；检查项左侧区域显示复选框、序号与内容，右侧固定显示该项 Markdown 备注编辑器，占两栏布局的右半区：`business-repo/utools-superone/src/views/ChecklistList.vue`。
- 备注编辑器保持紧凑的 64px 初始/最小高度，最大高度 120px；点击备注编辑区不会触发行项目勾选。
- 调整执行项为单层卡片布局，CSS 显式覆盖通用卡片的 flex display，确保左右分栏生效：`business-repo/utools-superone/src/styles/07-pages/_checklist-list.scss`。
- `npm run typecheck` 和 `git diff --check` 通过；未进行浏览器检查。
- 用户进一步指定备注编辑器占每条检查项约 2/3 宽度，已将网格比例由 1:1 调为 1:2：`business-repo/utools-superone/src/styles/07-pages/_checklist-list.scss`。`npm run typecheck`、`npm run build` 与 `git diff --check` 通过。
- 用户进一步要求默认仅显示备注入口，点击后在右侧栏展开编辑器，并提高编辑器高度。已为无备注条目显示右栏“+ 添加备注”入口，已有备注继续直接显示编辑器；输入区高度/最小高度调整为 120px、最大高度 240px，左右 1:2 布局保持不变：`business-repo/utools-superone/src/views/ChecklistList.vue`、`src/styles/07-pages/_checklist-list.scss`。`npm run typecheck`、`npm run build` 与 `git diff --check` 通过。
- 用户指出编辑器还需要收起能力。已在展开状态增加“收起备注”入口；收起只改变可见状态，不清除备注内容，并将收起状态保存到清单执行缓存、切换清单时恢复：`business-repo/utools-superone/src/composables/useChecklistExecution.ts`、`src/views/ChecklistList.vue`。`npm run typecheck`、`npm run build` 和 `git diff --check` 通过。
- 用户要求空备注编辑器在失焦后自动收起。已监听编辑区域的 focusout；焦点离开备注栏时，若内容为空则收起并保存可见状态，若移动到备注栏内控件则不触发，已有内容也保持展开：`business-repo/utools-superone/src/views/ChecklistList.vue`、`src/composables/useChecklistExecution.ts`。`npm run typecheck`、`npm run build` 与 `git diff --check` 均通过。
- 用户复现点击“添加备注”后编辑器立即收起。原因是入口按钮被编辑器替换时，按钮自身 focusout 被当作编辑器失焦；现仅处理事件目标位于 `.markdown-editor-wrapper` 内的 focusout，再执行空备注收起判断：`business-repo/utools-superone/src/views/ChecklistList.vue`。`npm run typecheck`、`npm run build` 与 `git diff --check` 通过。
- 用户决定移除失焦自动收起逻辑，统一由“收起备注”按钮控制。已删除 focusout 监听和对应 composable 处理函数，添加备注后持续展开，只有显式点击收起才隐藏：`business-repo/utools-superone/src/views/ChecklistList.vue`、`src/composables/useChecklistExecution.ts`。`npm run typecheck`、`npm run build` 与 `git diff --check` 通过。
- 对照 uni-superone 清单详情历史列表，发现缺少执行名称、状态、开始时间、耗时、完成数。uTools 执行记录契约已含 `title/startTime/finishTime/status/stepSummaries`，无需改接口；现补充历史总数、标题/时间、状态标记、耗时、完成比例条，整张记录可点开详情并保留删除操作。进度统计按 `confirmTime` 且未跳过计算，并将详情列表类型改为直接消费 contract 类型：`business-repo/utools-superone/src/views/ChecklistDetail.vue`、`src/styles/07-pages/_checklist-detail.scss`、`src/composables/useExecutionHistory.ts`。`npm run typecheck`、`npm run build`、`git diff --check` 通过。
- 用户要求选择方块上下留出适度空间、执行标题/进度滚动时保持可见，并确认执行标题可编辑。共享选择器容器添加上下 2px 内距；执行标题进度区设为 sticky；执行名称按 uni-superone 同样可编辑，存入本地执行缓存并随完成记录提交，旧缓存缺标题时生成默认名称：`business-repo/utools-superone/src/styles/06-components/_cu-tag.scss`、`src/styles/07-pages/_checklist-list.scss`、`src/views/ChecklistList.vue`、`src/composables/useChecklistExecution.ts`。`npm run typecheck`、`npm run build`、`git diff --check` 通过。

- 用户指出清单执行完成预览弹窗不够紧凑。将弹窗宽度从 600px 收至 520px，压缩标题/时间/进度区、步骤行、备注与总结的间距和字号；步骤项取消卡片式边框和内边距，确定按钮改为 small：`business-repo/utools-superone/src/views/ChecklistList.vue`、`src/styles/07-pages/_checklist-list.scss`。`npm run typecheck`、`npm run build`、`git diff --check` 均通过；未做浏览器检查。
