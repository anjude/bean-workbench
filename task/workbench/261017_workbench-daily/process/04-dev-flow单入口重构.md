# dev-flow 单入口重构 · 过程记录

- 任务目录：`task/workbench/261017_workbench-daily/`
- 阶段：04 工作台 skill 重构
- 时间：2026-10-24

## 做了什么

- 对照历史 dev-flow skill 体系和工作台路由说明，确定以单个开发流程 skill 作为关键词入口，按需读取阶段 references。
- 将入口从 `dev-flow-0000-development-flow` 简化命名为 `dev-flow`，流程阶段编号只用于过程记录，不进入 skill 名称。
- 约定任务推进顺序为任务初始化、需求理解与沟通、功能与系统设计、开发反馈循环、部署总结与 handoff。
- 将跨流程且可独立调用的能力划入 `dev-flow-tools-*`；后端、前端和验证细则留作流程 references。

## 得到的结论

- 将原 11 个流程阶段 skill 收敛为一个入口和五份按需读取的流程细则；资产生产独立成工具，仓库上下文、只读数据库和产品视频工具保留。
- 流程入口：`.agents/skills/dev-flow/SKILL.md`
- 工具层：`.agents/skills/dev-flow-tools-*/SKILL.md`
- 全仓命名、路由和目录职责同步更新：`AGENTS.md`、`docs/workspace.md`、`task/registry.md`、`script/check-workbench.py`。
- `make check`：必需文件、skill 命名、Markdown 相对链接全部通过。

## 被推翻的判断

- 每个技术阶段需要一个独立 skill 才能组织开发 → 用户确认 skill 关键词触发可能导致单次操作匹配多个 skill；开发阶段细则更适合从唯一流程入口按需加载。

## 待核 / 没答上来

- 无
