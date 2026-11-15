# Topic 样式审计与项目级规则提炼

## 职责划分

| 样式/交互 | 归属 | 处理 |
| --- | --- | --- |
| 模块头部高度、导航不换行、模块间距 | 项目级 | Topic、检查清单、最近任务统一使用 `cu-module-page` / `cu-module-header` |
| 新建、编辑表单弹窗的最大高度、标题/正文/页脚留白 | 项目级 | `cu-dialog--compact` 应用于三模块及记录详情中的所有业务弹窗；检查清单弹窗宽度由 700px 收至 600px |
| 内容卡片边框、圆角、紧凑内边距、hover 边框、元信息行 | 项目级 | 新增 `cu-card--dense`、`cu-card--interactive`、`cu-card__meta`，用于主题记录、清单步骤/执行记录、任务记录和记录详情 |
| 卡片内 Markdown 字号、标题/段落/列表/代码块间距 | 项目级 | 新增 `MarkdownViewer` 的 `cu-markdown--compact` 变体，替换 Topic 和其他记录/步骤视图的重复深层 CSS |
| 选择/筛选标签的尺寸、间距、选中态 | 项目级 | Topic、检查清单、任务状态筛选共用 `cu-selectable-tab-list` / `cu-selectable-tab` |
| 创建入口按钮尺寸 | 项目级 | Topic、检查清单、最近任务统一使用检查清单原有 Element Plus `small` 按钮 |
| Topic 主题数据、记录流、主题/记录右键动作和快速记录 | Topic 特有 | 保留在 Topic 页面与主题 composable |
| 勾选、步骤顺序、执行进度、备注、执行结果 | 检查清单特有 | 保留在检查清单页面与执行 composable；仅视觉表面复用项目级卡片和弹窗 |
| 任务主从分栏、状态流转、任务描述自动保存 | 最近任务特有 | 保留最近任务业务结构；筛选标签和弹窗复用项目级规则 |

## 改动范围

- 项目级基础：`utools-superone/src/styles/01-settings/_variables.scss`、`src/styles/06-components/`、`MarkdownViewer.vue`。
- 消费者迁移：Topic、检查清单、最近任务以及清单/计划/记录详情中的卡片、弹窗、筛选控件和 Markdown 记录视图。
- 工作台沉淀：新增 `business-repo/utools-superone/src/styles/README.md`，说明项目规则与页面边界。
- 不改业务数据/API/契约，不改 Vite 环境。

## 验证

- `npm run typecheck` 通过。
- `npm run build` 通过（Vite 编译 1583 个模块）。
- `git diff --check` 通过；按用户要求未进行浏览器检查。
