# bean-workbench 工作台

这是个人 Agent 工作台，用于沉淀可复用的 `skill`、知识库、任务记录和工作流脚本。

工作台目标不是替代业务仓，而是在业务需求执行前提供全局路由、跨仓编排和上下文，在需求完成后把可复用经验沉淀回 `skill`、知识库或脚本，形成持续进化闭环。

## 核心目录

- `.agents/skills/`：工作台内维护的 Agent skill 源目录。
- `docs/`：工作流、模板、架构规范、目标管理等工作台辅助内容。
- `knowledge-base/`：跨业务仓和系统可复用的知识库。
- `task/`：工作台任务、热任务、冷任务和任务上下文登记。
- `archive/`：工作台历史任务、过期规则和阶段性材料归档。
- `script/`：工作台常用脚本。
- `business-repo/`：业务仓集合，包含后端、前端、协议等独立业务仓；非明确业务需求不直接改动。

## 入口文档

- [Agent 规则](AGENTS.md)
- [工作台规范](docs/workspace.md)
- [自进化机制](docs/self-evolution.md)
- [知识库规范](docs/knowledge-base.md)
- [任务管理规范](docs/task-system.md)
- [工作流索引](docs/workflows/README.md)
- [业务仓生成验收与沉淀清单](docs/workflows/business-generation-checklist.md)
- [模板索引](docs/templates/README.md)
- [架构规范](docs/architecture/README.md)
- [目标管理](docs/goals/README.md)

## 子仓接入规则

当新增或接入业务子仓时，必须同步检查并更新：

1. `business-repo/` 目录与 `.gitmodules`
2. `knowledge-base/business-repo/` 的仓索引与职责说明
3. `task/registry.md` 的热任务与路由提示
4. 受影响的 `.agents/skills/` 路由或品牌特化 skill
5. 相关 `docs/workflows/` 工作流和必要的沉淀任务目录

如果新增子仓会影响已有路由、品牌、契约或协作边界，先补工作台规则，再做业务仓接入。

## 任务合并规则

新建任务目录前，先检查最近几个任务目录和 `task/registry.md`。如果是类似任务、零碎任务或同一上下文链条，优先合并到已有任务目录继续共用上下文，不要人为拆成多个孤立任务。

## 提交流程

工作台统一使用根目录 `Makefile` 的提交入口提交当前工作台全部变更：

- `make commit`
- `make commit feat xxx`

该命令等价于先 `git add -A`，再把 `make commit` 后面的参数按空格拼成提交信息执行 `git commit`；如果不带参数，默认使用 `chore: update workbench`。
