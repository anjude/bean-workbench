---
name: dev-flow-tools-repo
description: 需要查 backend-superone 或 uni-carbon-space 的目录约定、技术栈、常用命令、分支与部署链路，或要把 dev 合并到 test/release、执行 make push-all / nonlive / release 时使用；供所有开发阶段共享仓库上下文，不属于任何阶段。
metadata:
  short-description: 仓库上下文与分支部署
---

# 仓库上下文与分支部署

工具 skill，不占阶段号。方案设计、后端开发、前端开发、整体验证需要项目约定或推进分支时读取本文件，各阶段 skill 不重复维护这份内容。

## 仓与路径

| 仓 | 路径 | 角色 |
| --- | --- | --- |
| 工作台根 | `bean-workbench` | 跨仓协调目录，方案落在 `task/YYMMDD_{主题}/README.md` |
| 后端仓 | `business-repo/backend-superone` | Go 后端，以此为项目根目录 |
| 前端仓 | `business-repo/uni-carbon-space` | uni-app 前端，以此为项目根目录；同时是后端仓的 git 子模块 |
| 协议仓 | `business-repo/frontend-contracts` | OpenAPI YAML 与前端契约文件输出位置 |

在仓内执行时用相对路径，跨仓引用时用上表路径。

## 后端仓

### 目录约定

| 内容 | 路径 |
| --- | --- |
| 路由 | `app/api_service/*.go` |
| UseCase | `use_case/*.go` |
| DTO | `internal/domain/{domain}/{domain}_dto` |
| Entity | `internal/domain/{domain}/{domain}_entity` |
| Factory | `internal/domain/{domain}/{domain}_factory` |
| Service | `internal/domain/{domain}/{domain}_service` |
| Repo | 优先 `internal/repo`，domain 已有局部 repo 时沿用 |
| 表模型 | `internal/model/*_tab.go`，公共字段复用 `model.BaseTab` |
| 错误包 | `internal/infrastructure/ecode` |
| BizContext | `internal/infrastructure/bizctx` |
| 迁移脚本 | `scripts/migration`，SQL 文件在 `scripts/migration/sql/` |

### 技术栈

Go、Gin、GORM、MySQL、Viper、Wire、Logrus、JWT、Prometheus、pprof、Docker。

分层顺序：app → use_case → domain → repo → infrastructure。不跨层直接调用 app 或 middleware。

### 常用命令

| 命令 | 作用 |
| --- | --- |
| `make wire` | 运行 `wire ./...`，重新生成依赖注入 |
| `make lint` | golangci-lint，缺失时自动安装 v1.53.2 |
| `make lint-fix` | lint 并自动修复 |
| `make test` | `go test -short ./...`，默认快速测试 |
| `make test-integration` | `RUN_INTEGRATION_TESTS=1 go test ./...` |
| `make build` | `docker build -t superone .` |
| `make mock` | `go generate -run="mockgen" ./...` |
| `make gentab ENV=<test\|live>` | 执行默认建表，等价 `go run ./scripts/migration -env=<ENV>` |
| `make push-all <说明>` | 提交并推送前端子模块与后端主仓，commit 带 `yyMMdd` 前缀 |
| `make nonlive` | 把 dev 合并到 test；内部调 `push.bat`，仅 Windows 可用，见「平台差异」 |
| `make release` | 把 dev 合并到 release；同上 |

迁移脚本直连：

```bash
go run ./scripts/migration -action=exec-sql -sql-file=scripts/migration/sql/xxx.sql -env=test
```

macOS / Linux 的 bash、zsh 下直接照上面写，不加任何转义；Windows PowerShell 下要加 `--%` 避免参数被解析异常。迁移脚本默认环境必须是 `test`，执行 live 必须显式传 `-env=live`。

## 前端仓

### 目录约定

| 内容 | 路径 |
| --- | --- |
| 页面配置 | `src/pages.json` |
| 页面 | `src/pages/**/index.vue` |
| API 请求 | `src/apis/*.ts` |
| API 类型 | `src/types/api/*.ts`、`src/types/api.ts` |
| 业务类型 | `src/types/*.ts` |
| Store | `src/stores/*.ts` |
| Composable | `src/composables/use*.ts` |
| 通用组件 | `src/components/cu-*.vue` |
| 业务组件 | `src/components/business/*.vue` |
| 图标资产 | `src/static/icons/` |
| 样式入口 | `src/styles/index.css` |
| 请求封装 | `src/utils/request` |

### 技术栈

Vue 3、uni-app、TypeScript、Pinia、Vite、Tailwind CSS、Sass、vue-i18n、uni-ui。

数据流默认顺序：page → composable → store/api → request。复杂业务或项目已有同域 repo 时再引入 repo。

### 常用命令

| 命令 | 作用 |
| --- | --- |
| `npm run type-check` | `vue-tsc --noEmit`，前端必过门禁 |
| `npm run dev:h5` / `npm run dev:mp-weixin` | 本地起 H5 / 微信小程序 |
| `npm run build:h5` | H5 构建 |
| `npm run build:mp-weixin` | 微信小程序构建，产物用微信开发者工具预览或上传 |

## 协议仓

- OpenAPI YAML：`openapi/{domain}_api.yaml`，后端改接口时增量更新，只追加不整份重写。
- 前端契约：`src/` 下生成的可复制文件，由阶段 02 消费。

## 分支与部署

| 分支 | 作用 | 部署目标 |
| --- | --- | --- |
| `dev` | 日常开发基线，需求默认落这里 | 无 |
| `test` | 合并 `dev` 后自动部署 | nonlive |
| `release` | 合并 `dev` 后自动部署 | live |

`backend-superone` 默认开发分支是 `dev`；`uni-carbon-space`、`frontend-contracts` 默认 `master`。不在 `test` / `release` 上直接开发。

### 分支推进脚本的实际行为

Windows 下由 `push.bat` 完成，macOS / Linux 下按「平台差异」里的等价命令手工执行。行为一致：

1. `git fetch origin --prune`。
2. 在临时 worktree 里 checkout 目标分支，pull 最新，merge `origin/dev`，push。
3. 在另一个临时 worktree 里更新 `dev`。
4. 清理临时 worktree，**当前工作区保持不变**。

所以本地有未提交改动也能执行，未提交的改动不会被带进去。反过来说，改动还没 commit，推进后目标分支上不会有这次改动。

### 环境判断

- 用户说「发 nonlive」「推 test 环境」「配合测试环境验证」→ 推进 `test` 分支。
- 用户说「发 live」「上生产」→ 推进 `release` 分支。
- 用户只说「合并 test/release」但没有明确要求数据库写操作 → 只做分支推进，不自动执行对应环境的 DDL/DML。数据库的 `test` / `live` 是执行环境，与 Git 分支名是两套语义，需要单独判断，见 `dev-flow-0102-db-change-flow`。
- 用户说「推 nonlive / live」时，通常同时意味着要执行对应环境的数据库变更。先确认代码改动已提交，再走数据库执行流程。

### 授权边界

- 推进 `test`：用户明确要求即可执行。
- 推进 `release`：必须用户显式要求，且确认本次改动已在 nonlive 验证过。
- live 环境的 DDL/DML：必须用户显式授权，不由分支推进动作推断。

执行前确认：当前改动是否已 commit、是否有未解决的冲突、目标分支是否是用户预期的那一个。

### 平台差异

主开发环境是 macOS（Apple Silicon）。`backend-superone` 的脚本仍带 Windows 痕迹，遇到下面这些按此处理，不要照抄 Windows 命令。

| 场景 | macOS / Linux | Windows |
| --- | --- | --- |
| 迁移脚本参数 | 照常用 `-action=... -sql-file=... -env=...` | PowerShell 下要加 `--%` |
| `make nonlive` / `make release` | **不可用**，内部调 `push.bat`；用下面的等价命令 | 可用 |
| `make push-all` | 能跑，但 `DATE_PREFIX` 由 `powershell` 取日期，取不到时 commit 消息前缀为空 | 正常 |
| 换行符 | 保持 LF，不提交 CRLF 改动 | 同左 |

mac 上推进 `test` / `release` 的等价命令，`<branch>` 取 `test` 或 `release`：

```bash
git fetch origin --prune
git worktree add /tmp/superone-<branch> <branch>          # 本地没有该分支时改为：git worktree add /tmp/superone-<branch> -b <branch> origin/<branch>
git -C /tmp/superone-<branch> pull origin <branch>
git -C /tmp/superone-<branch> merge origin/dev
git -C /tmp/superone-<branch> push origin <branch>
git worktree remove /tmp/superone-<branch>
```

当前工作区保持不变，未 commit 的改动不会带进去。异常中断后检查 `git worktree list`，用 `git worktree remove --force` 清理残留。

## 命令可用性

| 命令 | 位置 | 说明 |
| --- | --- | --- |
| `brew` | `/opt/homebrew/bin/brew` | 已装，经 `/etc/paths.d/homebrew` 进 login shell 的 PATH，不在 `.zshrc` 里 |
| `go` | `~/sdk/go/bin/go` | 1.27.0，PATH 与 `GOPROXY` 声明在 `~/.zshrc` 末尾；该文件曾被 oh-my-zsh 模板覆盖过，排查 Go 问题先 `tail ~/.zshrc` |
| `python3` | `/usr/bin/python3` | 系统自带 3.9.6，工作台脚本按这个版本兼容 |
| `pwsh` | 无 | 没装。别写 PowerShell 命令，也别指望 `.ps1` 能跑 |

Agent 的执行环境是非 login 非交互 shell，不读 `/etc/paths.d` 也不读 `~/.zshrc`，**直接敲 `brew`、`go` 会报 command not found**。用绝对路径，或先执行：

```bash
export PATH="/opt/homebrew/bin:$HOME/sdk/go/bin:$PATH"
```

判断某个命令「有没有装」之前先排除 PATH 问题：用 `ls <绝对路径>` 或 `zsh -lc 'command -v <cmd>'` 复核，别只信 `command -v`——曾据此误判过「本机没装 brew」。

## 常见坑

- 目标分支合并失败：多半是 `dev` 落后于远端或有冲突，先 pull 再重跑，不要手工改 worktree 里的文件。
- 推进后线上没生效：先确认改动是否 commit 到了 `dev`。
- `test` / `release` 上出现工作区脏文件：优先怀疑分支切换、脚本或换行符归一化，不要假设是业务代码真实改动。
- 临时 worktree 残留：脚本正常退出会自动清理；异常中断时检查 `git worktree list`，手动 `git worktree remove --force` 清理。
- `go test` 冷缓存首次编译耗时长，多个包并行跑容易超时，优先串行。

## 禁止事项

- 不在未 commit 的情况下声称改动已发布。
- 不把本地未提交改动当作已合并内容。
- 不用分支推进代替 live 数据库授权。
- 不直接 push 到 `release`，必须走 `make release` 的合并流程。
