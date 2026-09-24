---
name: wb-router
description: 工作台入口与路由 skill。用户提到 hair、使用这个工作台、沉淀 skill、知识库、自进化、任务登记、热任务，或提出 superone 需求、业务仓需求、前后端需求、文档需求，需要判断应进入哪个业务仓、哪个知识库、哪个任务上下文时使用。
---

# 工作台入口与路由

工作台的第一站：先建立工作台上下文，再决定需求进哪个仓、走哪条流水线。本 skill 只负责入口收敛和路由，不直接替代业务 skill。

## 一、建立上下文

1. 读取工作台根目录 `AGENTS.md`，理解工作台边界。
2. 读取 `task/registry.md`，判断是否命中热任务，获取路由提示。
3. 读取 `knowledge-base/README.md` 和相关子目录，确认业务仓或系统上下文。
4. 需求涉及业务仓时，先确认是否是明确业务需求；不是业务需求时，不改 `business-repo/`。

## 二、路由

命中明确业务需求时，进入对应业务仓并读取该仓自己的 `AGENTS.md` 入口说明；未命中时，只在工作台层面补充任务、知识库或规则。

| 关键词 | 路由 |
| --- | --- |
| `superone` | 先到 `business-repo/`，再按需求判断 `backend-superone`、`uni-superone`、`uni-carbon-space`、`frontend-superone`、`miniprogram-superone`、`frontend-contracts` 或 uTools 端 |
| `后端`、`API`、`数据库`、`SQL` | `business-repo/backend-superone` |
| `前端`、`页面`、`uni-app` | `business-repo/uni-superone` |
| `Web`、`H5`、`Nuxt` | `business-repo/frontend-superone` |
| `原生小程序`、`微信小程序原生` | `business-repo/miniprogram-superone` |
| `投资平台`、`investment platform` | `business-repo/frontend-investment-platform` |
| `uTools`、`桌面工具` | 按语义到 `business-repo/utools-superone`、`utools-bean-note` 或 `utools-bean-option` |
| `carbon`、`uni-carbon-space` | `business-repo/uni-carbon-space`，并叠加 `dev-flow-0205-space-ui`、`dev-flow-0204-asset-flow` |
| `OpenAPI`、`契约`、`frontend-contracts`、`DTO 同步` | `business-repo/frontend-contracts` |
| `beannote`、`豆小匠 Note`、`理财自媒体`、`内容创作`、`选题池`、`文章复盘` | `business-repo/beannote`；内容需求按交互回合走 bn 阶段 skill：先 `bn-0000-think-flow` 想清楚本质，再 `bn-0100-shape-flow` 定主题与要点，再 `bn-0200-express-flow` 成稿；项目上下文读 `bn-tools-content-context` |
| `handoff`、`交接`、`收工`、`下次继续`、`换会话接着做` | `task/YYMMDD_{主题}/handoff/`，走 `wb-handoff` |
| `便签` | 先查 `task/registry.md` 和 `knowledge-base/`；没有明确归属时不直接改业务仓 |
| `工作台`、`skill`、`知识库`、`自进化` | 只改工作台根级目录 |

## 三、开发类需求的硬路由

后端改动、前端页面、跨端功能这类开发需求：**先走 `dev-flow-0000-plan-flow` 出方案**，方案落 `task/YYMMDD_{主题}/README.md`，确认后再按端派发 `dev-flow-01*`（后端）或 `dev-flow-02*`（前端）。不进方案直接改业务仓代码视为越权。

## 四、配套 references

| 文件 | 用途 | 何时读 |
| --- | --- | --- |
| `references/business-request-loop.md` | 业务需求闭环流程 | 命中业务需求，要从需求一路做到沉淀 |
| `references/business-generation-checklist.md` | 业务仓生成验收与沉淀清单，含 dev-flow 全 skill 路由表 | 进入业务仓前、生成后验收、子仓接入检查 |
| `references/task-readme.md` | 工作台任务 README 模板 | 新建或延续 `task/YYMMDD_slug/` 目录 |
| `references/task-review.md` | 工作台任务复盘模板 | 任务收口时写复盘（文章复盘的旧写法在 `.agents/archive/bn-20260914/bn-0303-retro-flow/`） |

## 输出要求

- 给出命中的业务仓或工作台目录。
- 说明是否需要读取额外规则（项目上下文见 `dev-flow-tools-repo`）。
- 路由不清楚时，先补充任务登记或痛点记录，不要盲目改业务仓。

## 工作原则

- 默认把工作台作为能力沉淀层，而不是业务实现层。
- 业务需求完成后，判断是否需要更新 `task/`、`knowledge-base/`、`~/.agents/skills/` 或 `script/`；skill 就在工作台仓库里，`make commit` 一起提交，改动经 `~/.agents` 外链同步给所有接入方。
- 连续两轮没有识别清楚用户意图时，记录到 `task/pain-points.md`，并考虑优化路由或 skill。
- 工作台说明类文档只在 `docs/` 平铺；模板、清单和工作流跟着对应 skill 的 `references/` 走。
- 工作台文档使用中文，专业术语和业务术语可保留英文。
