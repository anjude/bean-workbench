# bean-workbench 工作台

这是个人 Agent 工作台，用于沉淀可复用的 `skill`、知识库、任务记录和工作流脚本。

工作台目标不是替代业务仓，而是在业务需求执行前提供路由和上下文，在需求完成后把可复用经验沉淀回 `skill`、知识库或脚本，形成持续进化闭环。

## 核心目录

- `.agents/skills/`：工作台内维护的 Agent skill 源目录。
- `docs/`：工作流、模板、架构规范、目标管理等工作台辅助内容。
- `knowledge-base/`：跨业务仓和系统可复用的知识库。
- `task/`：工作台任务、热任务、冷任务和任务上下文登记。
- `archive/`：工作台历史任务、过期规则和阶段性材料归档。
- `script/`：工作台常用脚本。
- `business-repo/`：业务仓集合，非明确业务需求不直接改动。

## 入口文档

- [Agent 规则](AGENTS.md)
- [工作台规范](docs/workspace.md)
- [自进化机制](docs/self-evolution.md)
- [知识库规范](docs/knowledge-base.md)
- [任务管理规范](docs/task-system.md)
- [工作流索引](docs/workflows/README.md)
- [模板索引](docs/templates/README.md)
- [架构规范](docs/architecture/README.md)
- [目标管理](docs/goals/README.md)
