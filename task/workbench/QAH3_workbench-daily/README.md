# QAH3 工作台日常维护

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

- 主会话 `PostModelRequest` 检查当次输入 token 与模型窗口，达到 90% 时后台从旧会话第一轮结束位置分叉；旧会话继续回答，不等待旧会话当前轮结束。用量或窗口缺失时跳过，单次请求跨过阈值时可能先压缩。
- 新会话启动消息只包含来源会话 ID。先读来源会话的实际对话并继续尚未完成的用户目标；只有上下文不足时才查 handoff 补充任务状态，不向用户播报后台读取、置顶或导航过程。经验记录见 `process/07-续接状态核验与如实回报.md`。
- hook 创建新会话后会先自动置顶并核验，再注入来源 ID 启动首轮；接手侧仍按续接规则复核置顶并打开，保留脚本生成的会话名。只有后台操作失败、无法核实且与用户目标有关时才简短说明。按已授权记录处理特定自动化迁移。
- 续接标题中的任务目录名保留规范格式，如 `QA92_gknow-daily-续接-02`；脚本会修复旧会话标题中被省略的日期分隔下划线。
- 用户说「切新会话」时，先更新 handoff，再用 `script/codex-hooks/continue-session.py --manual` 触发同一流程；重复触发复用已创建的子会话。
- 脚本不代写 handoff；过程与验证见 `process/03-Codex压缩分支钩子.md`，执行规则见 `.agents/skills/wb-handoff/references/session-continuation.md`。
- 本机配置位于 `~/.codex/hooks.json`，状态/日志位于 `~/.codex/state/session-continuation/`。旧脚本路径保留兼容转调；新增或变更 hook 后按应用 `/hooks` 的实际信任状态启用。
- 已用模拟 app-server 和事件测试验证逻辑；真实 90% 事件、桌面置顶与打开链路仍需实际触发验收。

## 全量 skill 复查与布局优化

- 当时 `.agents/skills/` 的 11 个 skill 入口描述、职责边界、引用路径与长文档布局已复查；过程记录见 `process/05-skill列表复查与布局优化.md`。
- `dev-flow` references 已按任务阶段分目录并建立索引；日常编辑与长期写作规则维护、开发流程与 handoff 的职责已明确。
- 写作风格维护已并入 `bn-tools-edit-flow`，规则保留在其 `references/`，bn 族现有编辑、排版、发布三个入口。
- 验证：`make check` 通过。

## 微信防撤回 skill 内化

将本机原有防撤回安装说明纳入 `.agents/skills/wb-wechat-anti-revoke/`，并同步工作台清单和路由。安装、版本适配与回滚记录见 `process/10-微信防撤回skill内化.md`。

## 工具 skill 命名与图片上传

后续新增独立工具统一使用 `tools-{能力}`，已有族群工具保留原名；通用图片上传见 [tools-image-upload](../../../.agents/skills/tools-image-upload/SKILL.md)。变更依据与验证见 [可配置测试专项过程](../../dev-flow/QB84_gknow-configurable-assessment/process/02-功能与系统设计.md)。

## Superone MCP skill

新增 `tools-superone`，以「so」为唤起词，支持 Skill 管理、近期任务查询、清单创建和执行；已同步工作台 skill 清单、命名检查和任务路由。过程记录见 `process/15-Superone-MCP操作skill.md`。

## 回答依据与不确定性

已将「按证据和用户前提回答、区分推论与观测事实、只交代实质性不确定性、关键前提不明时求证」同步到通用回答规范与 beannote 写作规则。过程记录见 `process/18-回答依据与不确定性.md`。

## dev-flow 方案图示要求

所有开发方案都必须提供业务泳道图和系统时序图；简单需求用最少的真实参与方表达，不虚构节点。业务泳道图采用纵向角色列、横向阶段行的连续表格布局，列之间紧邻相接、共享边界且不留间隙；跨列箭头表示交接。规则同步见 `dev-flow/references/00-plan/solution-template.md` 与 `design.md`，过程记录见 `process/16-dev-flow方案双图必需.md`。

## 日常任务编号

新建长期日常任务使用 `task/daily/{任务编号}_{slug}/`，与独立任务共用日期码和当日序号；已有未编号日常目录迁移时保留内容并同步更新所有引用。规则见工作台 `AGENTS.md`、`task/README.md` 和 `task/daily/README.md`，过程记录见 `process/19-日常任务编号.md`。

## 全量任务编号统一

`task/workbench/`、`task/dev-flow/` 和 `task/beannote/topics/` 下的 42 个旧日期编号目录已迁移为统一新版编号，所有现有新版编号保持不变。目录内 README、任务索引、路由文档、工作台记忆和路径引用已同步；续接脚本只按新版任务目录定位和规范标题。过程记录见 `process/20-任务编号统一迁移.md`。
