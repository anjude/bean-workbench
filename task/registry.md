# 任务登记

## 热任务

| 任务                   | 目录                                                   | 资源范围                                                                                                | 状态  |
| -------------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------------------------- | --- |
| 工作台初始化               | `task/workbench/260614_workbench-init/`              | 根目录、`docs/`、`.agents/skills/`、`kb/`、`script/`                                                       | 进行中 |
| Superone 多仓规则完善      | `task/dev-flow/260614_superone-workbench-migration/` | `business-repo/` 路由、Superone skills、协议仓路径、知识库索引                                                     | 进行中 |
|                      |                                                      |                                                                                                     |     |
| uni-carbon-space 接入  | `task/dev-flow/260614_uni-carbon-space-onboarding/`  | `business-repo/uni-carbon-space`、uni 路由、品牌特化 skill、知识库索引                                            | 进行中 |
| beannote 内容库接入       | `task/workbench/260628_beannote-onboarding/`         | `task/beannote`、内容创作路由、知识库索引                                                                        | 进行中 |
| be 族 skill 四阶段重构     | `task/workbench/260829_be-skill-refactor/`           | `.agents/skills/be-*`、`AGENTS.md`、`docs/workspace.md`、`docs/workflows/`                             | 已完成 |
| dev-flow 跨端合族        | `task/workbench/260829_dev-flow-merge/`              | `.agents/skills/dev-flow-*`、原 `fe-*` 前端族、`AGENTS.md`、`docs/workspace.md`、`docs/workflows/`          | 已完成 |
| dev-flow 合并精简        | `task/workbench/260829_dev-flow-slim/`               | `.agents/skills/dev-flow-*`、`wb-*`、`AGENTS.md`、`docs/`、`task/registry.md`、`script/`                 | 已完成 |
| macOS 平台适配           | `task/workbench/260829_macos-adaptation/`            | `script/`、`Makefile`、`dev-flow-tools-repo`、`dev-flow-0301-verify-flow`、`docs/goals.md`              | 进行中 |
| skill 实体外置           | `task/workbench/260830_skills-externalize/`          | `~/.agents/skills/`、`.agents` 符号链接、`script/check-workbench.py`、`AGENTS.md`、`README.md`、`docs/`      | 已完成 |
| 任务交接 handoff skill   | `task/workbench/260914_wb-handoff-skill/`            | `.agents/skills/wb-handoff/`、`AGENTS.md`、`task/registry.md`、`script/check-workbench.py`、`wb-router` | 进行中 |
| Superone 后端重构（下线老功能） | `task/dev-flow/260927_superone-backend-refactor/`    | `business-repo/backend-superone`、`release-260927` tag、`version/release-260927` 分支                   | 进行中 |
| backend 日常开发 | `task/dev-flow/261009_backend-daily/` | `business-repo/backend-superone`（日常需求方案、开发与验证上下文） | 进行中 |
| Superone 前端开发（模块与主题） | `task/dev-flow/260930_superone-frontend/`            | `business-repo/uni-superone`、`backend-superone`（近期任务、物品；三态主题方案待确认；release 分支） | 进行中 |
| Superone 前端模块设计（主题/清单/计划/物品/扩展） | `task/dev-flow/261002_superone-modules/`  | `business-repo/uni-superone`（扩展入口、系统与签到按钮已实现；type-check/build 待验证） | 进行中 |
| uni-superone 日常优化 | `task/dev-flow/261007_uni-superone-daily-optimization/` | `business-repo/uni-superone`（持续收纳日常体验、交互、样式与维护优化） | 进行中 |
| Topic 记录嵌套（log 的 log，parent_log_id） | `task/dev-flow/261002_topic-log-nesting/` | `business-repo/backend-superone`、`business-repo/frontend-contracts`                                  | 已完成 |
| 前端引入子日志（跟进，记录详情页） | `task/dev-flow/261002_superone-sub-log/`  | `business-repo/uni-superone`、`business-repo/frontend-contracts`                                      | 进行中 |
| 测试服务器构建优化（8.155.38.83） | `task/workbench/261002_测试服务器构建优化/` | 测试环境服务器、`/workspace/test-backend-superone` 的 `deploy.sh` 与 `Dockerfile` | 排查完成，改动待确认 |
| topic 模块 P0 闭环（增删改 + 级联删除） | `task/dev-flow/261003_topic-crud/` | `business-repo/backend-superone`（删除逻辑）、`business-repo/uni-superone`（编辑页、记录详情页、首页面板长按） | 进行中 |
| uTools 发布与契约检查改造 | `task/dev-flow/261007_utools-release-contract-checks/` | `business-repo/utools-superone`、`business-repo/frontend-contracts`（只读消费）、发布门禁与工作台方案记录 | 进行中 |
| uTools Superone 重构 | `task/dev-flow/261007_utools-refactor/` | 一级辅助文件精简、死文件清理、Topic 页面 UI/UX 与通用右键菜单 | Topic 页面第一版已实现，待后续验收 |
| 鹅懂个啥小程序初始化 | `task/dev-flow/261009_edonggesha-init/` | `business-repo/uni-gknow`（开发与生产分支 `release`）、uni-superone 框架复用评估、品牌图片与小游戏素材盘点 | 仓库已接入，方案设计中 |

## 冷任务

| 任务 | 目录 | 资源范围 | 状态 |
| -- | -- | ---- | -- |
| 暂无 | -  | -    | -  |

## 路由提示

- 提到原始素材库或 `local-source`：先读 `source/README.md`，原始文件不直接修改。
- 提到「鹅懂个啥」或新娱乐小程序初始化：进入 `business-repo/uni-gknow`，先读 `task/dev-flow/261009_edonggesha-init/README.md` 与最新 handoff；开发与生产统一使用 `release` 分支。

- skill 编号：`dev-flow-*` 跨端开发（00 方案设计 / 01 后端开发 / 02 前端开发 / 03 整体验证）、`bn-*` 内容生产、`wb-*` 工作台基建；编号前两位是阶段号，后两位是阶段内序号；`*-tools-*` 是工具 skill，不占阶段号。完整编号表见 `AGENTS.md`。
- 提到 `backend-superone`、`uni-carbon-space` 的需求改动：先走 `dev-flow-0000-plan-flow` 出方案，方案落 `task/dev-flow/YYMMDD_{主题}/README.md`，确认后再按端派发后端（`dev-flow-0101` 起）或前端（`dev-flow-0201` 起）开发 skill，收口走 `dev-flow-0301-verify-flow`。
- 提到 `superone` 的分支推进、项目约定、命令速查：走 `dev-flow-tools-repo`；数据库只读排查走 `dev-flow-tools-db-query`。
- 提到 `superone`：优先查看 `business-repo/` 下的相关业务仓，再结合具体需求选择后端、前端或协议仓。
- 提到 `uni-carbon-space`、`carbon`：优先路由到 `business-repo/uni-carbon-space`，并叠加 `dev-flow-0205-space-ui`、`dev-flow-0204-asset-flow` 等品牌特化 skill。
- 提到 `frontend-contracts`、`OpenAPI`、`契约`：优先路由到工作台下的 `business-repo/frontend-contracts`。
- 提到 `beannote`、`豆小匠 Note`、`理财自媒体`、`内容创作`、`选题池`、`文章复盘`：优先路由到 `task/beannote`，再读取该仓自己的内容工作流和 skill。
- 提到 `便签`：先查热任务和知识库；如果没有明确业务仓，不要直接改业务仓，先定位需求归属。
- 提到 `handoff`、`交接`、`收工`、`下次继续`：走 `wb-handoff`，在任务目录的 `handoff/` 下写 `YYMMDD-HHMM_{slug}.md`；每个 `task/YYMMDD_{主题}/` 目录都应带一个 `handoff/`。
- 提到 `工作台`、`skill`、`知识库`、`自进化`：默认只改工作台根级目录。
- skill 实体在 `bean-workbench/.agents/skills/`，由工作台 git 跟踪，工作台的 `make commit` 能带走；`~/.agents` 是指向它的外链，其他项目经它读到同一套 skill。详见 `AGENTS.md` 的「跨项目共享」。
- 工作台文档位置：说明类在 `docs/`（平铺），模板与工作流在各 skill 的 `references/`，知识内容与知识库规范在 `kb/`，任务、痛点和上下文记录在 `task/`。
- 主开发环境是 macOS（Apple Silicon），没有 `pwsh`（`brew` 有，装在 `/opt/homebrew/bin/brew`）；结构检查走 `make check`（Python 脚本），不要写 PowerShell 命令。平台差异与业务仓 Windows 脚本的绕法见 `dev-flow-tools-repo`。
