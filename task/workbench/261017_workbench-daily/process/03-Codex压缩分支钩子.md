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

## 2026-10-29 规则调整：首次压缩前后台续接

### 做了什么与取舍

- 用户要求首次压缩前分叉，旧会话继续压缩和回答；实现为 `PreCompact` 非阻断地启动后台程序并始终返回 `continue: true`，删除完成压缩次数门槛与 PostCompact 计数注册。
- 新入口 `script/codex-hooks/continue-session.py` 从旧会话第一轮结束位置分叉，已有结束的首轮时不等待当前轮。首轮仍在进行时仅后台等待首轮结束。
- 续接消息只包含老会话 ID 与读取 handoff、遵循 wb-handoff 续接规则的指令。近期请求仅用于保留原命名习惯，不再作为新会话消息上下文；旧会话答案/进展也不再注入。
- `wb-handoff/references/session-continuation.md` 定义接手后置顶并打开新会话、读取 handoff、保留已授权的特定自动化迁移并等待用户输入；手动「切新会话」先更新 handoff，再用 `--manual` 启动同一流程。
- 自动和手动入口按旧会话 ID 共享状态、复用已创建子会话。改名失败可继续；续接消息提交结果不明时标记待核，不重复分叉或重发。
- handoff 模板新增来源会话 ID，便于仅凭老 ID 定位任务；同步路由、任务登记、检查脚本与本机 hooks.json。旧脚本保留转调入口，兼容已加载旧路径的会话。
- 只读连接验证发现本机没有旧脚本依赖的共享控制套接字；新增独立 stdio app-server 备用连接。实测可读取当前会话首轮且状态为 completed，沿用本机 MCP 配置；独立服务会保持到新会话接手轮结束才关闭，不安装/重启常驻服务。

### 验证

- `/usr/bin/python3 -m unittest discover -s script/codex-hooks/tests -v`：12 项通过，覆盖首次事件、旧会话不中断、锁不阻塞、自动/手动去重、首轮分叉、最小注入、命名递增、改名恢复、提交结果不明与独立服务生命周期。
- `make check` 与 `git diff --check` 通过。
- 本机 `thread/turns/list` 只读读取当前会话首轮信息成功；本次没有创建真实续接会话。

### 待核

- 真实首次压缩的 hook 信任与事件触发、新会话的桌面应用工具置顶/打开、自动化授权迁移仍需实际链路验收；桌面工具只读调用本次未在等待窗口内返回，未据此宣称桌面操作成功。
