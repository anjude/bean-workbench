# 260829 macOS 平台适配

## 目标

开发环境从 Windows 切到 macOS（Apple Silicon，darwin/arm64）。排查工作台与业务仓里的 Windows 依赖，把主环境视角改成 macOS，保证常用命令在 mac 上直接可跑。

环境事实（30 日凌晨核实过一遍，第一版结论有误，以此为准）：

| 项 | 状态 |
| --- | --- |
| `pwsh` / `powershell` | **没装**。`brew leaves` 只有 nvm、wechattweak、zsh-completions。PowerShell 脚本跑不了 |
| `brew` | **装了**，`/opt/homebrew/bin/brew` 6.0.19，经 `/etc/paths.d/homebrew` 进 login shell 的 PATH |
| `go` | 1.27.0，在 `~/sdk/go`，`.zshrc` 末尾 PATH + GOPROXY 配置完好 |
| `python3` | 系统 `/usr/bin/python3` 3.9.6；终端里没有其他 python。检查脚本两个版本都跑通 |

助手的 Bash 工具环境是非 login 非交互 shell，PATH 里没有 `/opt/homebrew/bin` 和 `~/sdk/go/bin`，直接敲 `brew`、`go` 会报找不到——要用绝对路径或先 export PATH。**判断命令有没有装之前先排除 PATH 问题**，这次就是这么误判的。

结论不变：`make check` 原来依赖 pwsh，在本机必挂。

## 范围

### 工作台（已完成）

| 项 | 处理 |
| --- | --- |
| `script/check-workbench.ps1` | 删除，重写为 `script/check-workbench.py` |
| `Makefile` 的 `check` target | `pwsh ... -File` 改为 `$(PYTHON) script/check-workbench.py`，带 python3 缺失提示 |
| `AGENTS.md` 第 72 行 | 脚本路径引用同步 |
| `wb-0001-router/references/business-generation-checklist.md` | 最小验证表里的 `script/check-workbench.ps1` 改为 `make check` |
| `wb-0101-skill-refactor/SKILL.md` | 同步清单与校验清单两处改用新脚本与 `make check` |
| `.gitattributes` | 补 `*.py text eol=lf` |
| `dev-flow-tools-repo` | 新增「平台差异」小节；`push.bat` 改为「分支推进脚本的实际行为」；Windows 编译/换行符表述改中性 |
| `dev-flow-0301-verify-flow` | 「Go test 性能注意」去掉 Windows 限定 |
| `docs/goals.md` | 已达成目标补 docs 平铺；当前阶段目标改为跨平台与业务仓脚本适配 |

### 新检查脚本能力

原 ps1 只做「必需文件是否存在」。新脚本 `script/check-workbench.py` 覆盖三项，把此前每次靠临时脚本手写的校验固化下来：

1. 必需文件存在性（29 项，含 business-repo 子仓 AGENTS.md，缺失时提示 submodule 未初始化）。
2. `.agents/skills/` 下目录名、`SKILL.md` 的 `name` 字段、编号规范三者一致。
3. 工作台 md 相对链接是否失效（跳过 `.git`、`node_modules`、`business-repo`、`dist`、`.workbuddy`）。

用法：`make check`，或 `python3 script/check-workbench.py [--root <path>] [--skip-links]`。
只依赖 Python 3 标准库，跨平台。负向测试已验证三项均能检出。

### 业务仓（未处理，需评估后单独做）

按工作台规则「非明确业务需求不直接改业务仓」，本次只排查不动手：

| 位置 | 问题 | 影响 |
| --- | --- | --- |
| `business-repo/backend-superone/Makefile:5` | `DATE_PREFIX := $(shell powershell -NoProfile -Command "Get-Date -Format yyMMdd")` | mac 上取不到值，`make push-all` 的 commit 消息日期前缀为空 |
| `business-repo/backend-superone/Makefile:8` | `SSH_HOME_EXPORT` 用 `cygpath -u "$USERPROFILE"`，mac 上 `USERPROFILE` 未定义、`cygpath` 不存在 | 落到 `HOME=""; export HOME;`，**会把 HOME 清空导致 SSH key 找不到**，push 失败 |
| `business-repo/backend-superone/push.bat` | `make nonlive` / `make release` 直接调 bat | mac 上不可用，分支推进走不通 |
| `business-repo/backend-superone/deploy.sh` | 未核查 | 待确认 |

`business-repo/` 其余 powershell 命中都在 `node_modules`、vditor dist、highlight.js 里，是第三方依赖噪声，与平台适配无关。

## 边界

- 不动业务仓代码与脚本，本任务只做工作台改造与问题排查。
- 历史任务文档（`task/260628_*`、`task/260829_*`）里 `script/check-workbench.ps1` 的字面引用按历史记录保留，未改写。
- 不在本任务内给业务仓补 macOS 脚本；等用户明确后再走 `dev-flow-0000-plan-flow`。

## 当前状态

工作台部分已完成，`make check` 在 mac 上跑通，三项检查全通过。业务仓部分待用户决定是否推进。

## 沉淀候选

- `dev-flow-tools-repo` 的「平台差异」小节：mac 上推进 test/release 的等价 git worktree 命令，后续可直接复用。
- 结构检查脚本：以后新增必需文件、skill 或 references，改 `script/check-workbench.py` 里的清单即可，不必再临时写校验脚本。
