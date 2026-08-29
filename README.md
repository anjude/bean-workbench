# bean-workbench 工作台

这是个人 Agent 工作台，用于沉淀可复用的 `skill`、知识库、任务记录和工作流脚本。

工作台目标不是替代业务仓，而是在业务需求执行前提供全局路由、跨仓编排和上下文，在需求完成后把可复用经验沉淀回 `skill`、知识库或脚本，形成持续进化闭环。

## 核心目录

- `.agents`：跨项目复用的 skill 实体目录，随工作台一起提交；模板、清单和工作流放各 skill 的 `references/`。`~/.agents` 是指向它的外链，其他 Agent 工具和其他项目经它读到同一套 skill，详见 [AGENTS.md 跨项目共享](AGENTS.md#跨项目共享)。
- `docs/`：工作台说明类文档，平铺不分层。
- `knowledge-base/`：跨业务仓和系统可复用的知识库，含知识库规范与条目模板。
- `task/`：工作台任务、热任务、冷任务、任务上下文登记和痛点记录。
- `script/`：工作台常用脚本。
- `business-repo/`：业务仓集合，包含后端、前端、协议等独立业务仓；非明确业务需求不直接改动。

## 入口文档

- [Agent 规则](AGENTS.md)
- [工作台规范](docs/workspace.md)
- [自进化机制](docs/self-evolution.md)
- [任务管理规范](docs/task-system.md)
- [目标管理](docs/goals.md)
- [知识库规范与条目模板](knowledge-base/README.md)

## 子仓接入规则

当新增或接入业务子仓时，必须同步检查并更新：

1. `business-repo/` 目录与 `.gitmodules`
2. `knowledge-base/business-repo/` 的仓索引与职责说明
3. `task/registry.md` 的热任务与路由提示
4. 受影响的 `.agents/skills/` 路由或品牌特化 skill，以及其 `references/` 里的清单
5. 必要的沉淀任务目录

如果新增子仓会影响已有路由、品牌、契约或协作边界，先补工作台规则，再做业务仓接入。

工作台级可复用 skill 统一沉淀在 `.agents/skills/`，并遵守 `AGENTS.md` 中的命名规则；业务仓内的品牌化 skill 目录应在稳定后迁移到工作台级命名体系。

## 任务合并规则

新建任务目录前，先检查最近几个任务目录和 `task/registry.md`。如果是类似任务、零碎任务或同一上下文链条，优先合并到已有任务目录继续共用上下文，不要人为拆成多个孤立任务。

## 提交流程

工作台统一使用根目录 `Makefile` 的提交入口提交当前工作台全部变更：

- `make commit`
- `make commit feat xxx`

该命令等价于先 `git add -A`，再把 `make commit` 后面的参数按空格拼成提交信息执行 `git commit`；如果不带参数，默认使用 `chore: update workbench`。

skill 就是工作台里的普通文件，`git add -A` 会一起带走，`make check` 会单独列出 `.agents/` 下的改动，方便确认有没有漏。

`~/.agents` 外链本身不在 git 里（home 目录不受版本控制），换机器后重建一条：

```bash
ln -s /Users/bean/workspace/bean-workbench/.agents ~/.agents
```
