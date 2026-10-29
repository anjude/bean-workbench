# 261017 工作台日常维护

## 目标

集中记录工作台的日常维护事项，让零散修补、检查结果和后续交接共用一个上下文。

## 范围

- 工作台根目录文档、`task/`、`kb/`、`.agents/skills/` 和 `script/` 的日常维护。
- 本目录的 `process/` 记录每次维护的经过与结论；`handoff/` 记录需要跨会话接续的状态。

## 边界

- 已有独立目标的专项任务继续使用各自任务目录。
- 没有明确业务需求时，不改动 `business-repo/` 中的业务仓。

## 当前状态

进行中，作为工作台日常维护入口。

## 沉淀候选

- 反复出现的问题先登记到任务或知识库；稳定可复用后再升级为 skill 或脚本。

## dev-flow 单入口重构

将开发流水线收敛为一个入口 skill；需求与设计、后端、前端、验证与交付的细则按需放入 references；跨流程可独立调用的能力保留为 tools。过程记录见 `process/04-dev-flow单入口重构.md`。

## Codex 会话续接钩子

- 第一次 `PreCompact` 后台从旧会话第一轮结束位置分叉，返回 `continue: true`；旧会话继续压缩与回答，不等待旧会话当前轮结束。
- 新会话只收到老会话 ID 与读取 handoff 的指令；读取 `wb-handoff` 续接规则后置顶并打开，沿用命名规则，按已授权记录处理特定自动化迁移，再等待用户输入。
- 用户说「切新会话」时，先更新 handoff，再用 `script/codex-hooks/continue-session.py --manual` 触发同一流程；重复触发复用已创建的子会话。
- 脚本不代写 handoff；过程与验证见 `process/03-Codex压缩分支钩子.md`，执行规则见 `.agents/skills/wb-handoff/references/session-continuation.md`。
- 本机配置位于 `~/.codex/hooks.json`，状态/日志位于 `~/.codex/state/session-continuation/`。旧脚本路径保留兼容转调；新增或变更 hook 后按应用 `/hooks` 的实际信任状态启用。
- 已用模拟 app-server 和事件测试验证逻辑；真实首次压缩、桌面置顶与打开链路仍需实际触发验收。

## 全量 skill 复查与布局优化

- `.agents/skills/` 当前 11 个 skill 的入口描述、职责边界、引用路径与长文档布局已复查；过程记录见 `process/05-skill列表复查与布局优化.md`。
- `dev-flow` references 已按任务阶段分目录并建立索引；日常编辑与长期写作规则维护、开发流程与 handoff 的职责已明确。
- 写作风格维护已并入 `bn-tools-edit-flow`，规则保留在其 `references/`，bn 族现有编辑、排版、发布三个入口。
- 验证：`make check` 通过。
