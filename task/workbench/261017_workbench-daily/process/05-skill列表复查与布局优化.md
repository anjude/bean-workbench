# skill 列表复查与布局优化 · 过程记录

- 任务目录：`task/workbench/261017_workbench-daily/`
- 阶段：05 工作台 skill 维护
- 时间：2026-10-25

## 做了什么

- 复查 `.agents/skills/` 下 12 个在用 skill 的入口描述、职责边界、目录结构与相互引用。
- 收窄 `wb-router` 和 `bn-tools-writing-style` 的触发描述，明确开发流程、日常编辑与长期规则维护的分工。
- 明确开发阶段过程记录由 `dev-flow` 推进；`wb-handoff` 聚焦任务/会话绑定、跨会话交接和提交前过程记录核对，并新增过程记录模板 reference。
- 将 `dev-flow/references/` 整理成按任务阶段命名的子目录，新增总索引；为长文档加入目录，并同步工作台文档、路由清单和检查脚本。
- 修正旧路径、知识库目录名、skill 描述中的模板数量和仓库工具的阶段措辞。

## 得到的结论

- 当前 12 个 skill 数量合理，职责分成开发流程入口与独立工具、beannote 内容工具、工作台基建；不需要按数量继续合并。
- `dev-flow-tools-repo` 仍有用，承载多仓路径、技术栈、命令、分支和部署上下文，是跨流程共享能力。
- `make check`：必需文件、skill 命名和 Markdown 相对链接检查均通过。`task/workbench/261017_workbench-daily/README.md`、`AGENTS.md`、`.agents/skills/`、`script/check-workbench.py`。

## 被推翻的判断

- 之前认为 `dev-flow` references 按需读取已经足够；实际文件平铺且长文档缺少目录，会增加定位成本。改为阶段子目录 + 总索引 + 长文档目录。
- 之前将 `wb-handoff` 描述为每个开发阶段的过程记录入口，容易与 `dev-flow` 同时被宽泛触发。现由 `dev-flow` 推进开发过程记录，handoff skill 保留跨会话和提交前的横切职责。

## 待核 / 没答上来

- 无。后续可依据真实使用情况评估是否需要为 skill 选择建立独立触发样例检查；目前先完成人工边界复核。

## 2026-10-25 第 2 轮：合并辅助编辑与写作规则维护

- 用户确认合并后，将长期写作规则维护纳入 `bn-tools-edit-flow/SKILL.md`；`writing-rules.md` 与 `article-modules.md` 迁入其 `references/`，移除原 `bn-tools-writing-style` 入口及空目录。
- 保留单篇临时要求和长期规则更新的边界，长期规则必须有用户明确指令或确认依据。
- 同步排版、发布流程、工作台路由、AGENTS、工作台介绍、任务登记、检查脚本、长期记忆及活跃任务 README 的引用；历史过程记录保留旧名称以便追溯。
- 在用 skill 从 12 个变为 11 个，bn 族从 4 个入口收敛到编辑、排版、发布 3 个入口。
- 验证：`make check` 与 `git diff --check` 通过；活跃文档中无旧 skill 入口引用。
