# Codex 压缩分支钩子 · 过程记录

- 任务目录：`task/workbench/261017_workbench-daily/`
- 阶段：03 钩子实现
- 时间：2026-10-24

## 做了什么

- 查阅 Codex Hooks 文档，确认 `PreCompact` / `PostCompact` 事件及 `/hooks` 信任要求：`https://learn.chatgpt.com/docs/hooks`
- 检查本机 app-server 协议 schema，确认 `thread/turns/list`、`thread/fork.lastTurnId`、`thread/name/set`、`turn/start` 可用于等待后分叉、命名和注入上下文。
- 更新 `script/codex-hooks/fork-before-third-compact.py`：前两次压缩由 `PostCompact` 计数；第三次 `PreCompact` 阻止压缩并启动后台续接程序；后台程序轮询旧轮结束或中断，从第一轮分叉，注入老会话 ID、工作目录、最近用户请求和最终答复/最近进展，改名后要求新会话等待用户输入。
- 更新 `wb-handoff` 与任务 README，说明 handoff 文件仍由旧会话按需维护、后台续接流程及桌面打开尚待验收。
- 执行 `python3 -m py_compile script/codex-hooks/fork-before-third-compact.py`，语法检查通过。

## 得到的结论

- 本机 app-server schema 支持创建首轮分支、改名和启动新 turn 注入交接文本：`script/codex-hooks/fork-before-third-compact.py`
- `PreCompact` 返回 `continue: false` 用于阻止第三次压缩；当前轮是否因此完全停止，仍待桌面实测确认。
- hook 需要用户在 Codex `/hooks` 页面审阅并信任后才会执行：`https://learn.chatgpt.com/docs/hooks`

## 被推翻的判断

- 原流程要求旧会话完成 handoff 后手动确认创建分支 → 用户明确要求第三次压缩时自动启动后台等待程序，因此改为后台轮询并自动续接：`script/codex-hooks/fork-before-third-compact.py`

## 待核 / 没答上来

- 未发现 app-server 的前台导航/打开 thread RPC；自动命名、注入与创建不等于桌面已切换到新会话。
- 尚未在真实压缩中验证 hook 信任后的完整桌面链路，尤其是 `continue:false` 对当前轮状态、最新可见内容读取、后台 fork、自动打开与新会话等待行为的影响。

## 2026-10-27 后续：已授权的定时任务迁移

- 投资任务用户确认会话续接时迁移其日报；钩子交接文字改为先读取正式任务与 wb-handoff，执行已授权且仍绑定旧会话的特定自动化迁移，核验后再等待输入。
- 实际更新由新会话的应用自动化工具完成，不通过未知 app-server RPC 或直接写 TOML。其他任务没有授权时保持只读取/等待，不迁移第三方会话的绑定，也不自动归档旧会话。
- 详细验收在 `task/daily/health-sleep-sell-put/process/13-会话续接与日报调度迁移.md`；真实第三次压缩触发仍待独立实测。
