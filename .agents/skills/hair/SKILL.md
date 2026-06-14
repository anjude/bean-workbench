---
name: hair
description: 个人 Agent 工作台入口 skill。用户提到 hair、使用这个工作台、沉淀 skill、知识库、自进化、任务登记、热任务、工作台路由、用工作台处理业务需求时使用。该 skill 会先读取 bean-workbench 的工作台规则、任务登记和知识库索引，再决定是否进入业务仓。
---

# Hair 工作台入口

## 使用步骤

1. 读取工作台根目录 `AGENTS.md`。
2. 读取 `docs/workspace.md` 理解工作台边界。
3. 读取 `task/registry.md` 获取热任务和路由提示。
4. 如需求涉及可复用知识，读取 `knowledge-base/README.md` 和相关子目录。
5. 如需求涉及业务仓，先确认是否是明确业务需求；不是业务需求时，不改 `business-repo/`。

## 工作原则

- 默认把工作台作为能力沉淀层，而不是业务实现层。
- 业务需求完成后，判断是否需要更新 `task/`、`knowledge-base/`、`.agents/skills/` 或 `script/`。
- 如果连续两轮没有识别清楚用户意图，记录到 `docs/pain-points.md`，并考虑优化路由或 skill。
- 对工作台文档使用中文，专业术语和业务术语可保留英文。

## 关键入口

- `AGENTS.md`：工作台总规则。
- `docs/self-evolution.md`：自进化机制。
- `task/registry.md`：热任务和冷任务。
- `knowledge-base/`：知识库。
- `.agents/skills/workbench-router/SKILL.md`：轻量路由 skill。
