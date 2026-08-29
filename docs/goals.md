# 目标管理

## 工作台长期目标

形成个人可持续进化的 Agent 工作台，通过 `skill`、知识库、任务记录和脚本提高业务仓代码与文档产出效率。

## 已达成阶段目标

1. 建立稳定的工作台目录结构。
2. 建立全局可触发的 `wb-0001-router` skill。
3. 建立轻量业务仓路由和跨仓编排能力。
4. 建立知识库、自进化和任务登记机制。
5. 把 skill 收敛为按阶段推进的族群编号体系（见 `AGENTS.md`）。
6. `docs/` 只保留说明类文档并平铺，模板与工作流下沉到对应 skill 的 `references/`；知识内容与知识库规范收在 `knowledge-base/`，记录类内容收在 `task/`。

## 当前阶段目标

1. 工作台脚本与结构检查跨平台：以 macOS（Apple Silicon）为主环境，不依赖 PowerShell。
2. 业务仓 Windows 脚本（`backend-superone` 的 `push.bat`、Makefile 里的 `powershell` 与 `cygpath` 调用）补齐 macOS 路径，推进分支不再手工拼命令。

## 验收标准

- Agent 能通过 `wb-0001-router` 进入工作台上下文。
- `task/registry.md` 能反映热任务和路由提示。
- 工作台结构能通过 `make check`（macOS 下直接可跑）。
- 新增业务经验能落到知识库、skill（含 `references/`）或脚本中的合适位置。
