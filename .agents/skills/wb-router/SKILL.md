---
name: wb-router
description: 当用户主要需要建立工作台上下文、定位任务/知识库/业务仓，或维护工作台规则与路由时使用。功能开发和缺陷修复由 dev-flow 负责完整流程；仅在需要判断仓库或任务归属时由 dev-flow 调用本 skill。
---

# 工作台入口与路由

工作台的第一站：先建立工作台上下文，再决定需求进哪个仓、走哪条流水线。本 skill 只负责入口收敛和路由，不直接替代业务 skill。

## 一、建立上下文

1. 读取工作台根目录 `AGENTS.md`，理解工作台边界。
2. 读取 `task/registry.md`，判断是否命中热任务，获取路由提示。
3. 读取 `kb/README.md` 和相关子目录，确认业务仓或系统上下文。
4. 需求涉及业务仓时，先确认是否是明确业务需求；不是业务需求时，不改 `business-repo/`。

### 用户明确要求进入任务目录

当用户说“进入”某个已有任务目录，或明确要求把当前会话切换到某任务时，按 `wb-handoff` 的「会话绑定任务」规则处理：将任务目录绑定到当前会话、把会话标题改为目录末级名称，然后停下来等待用户下一步指示。进入目录本身不是开始执行任务内容的授权。每个会话只自动绑定一次；已绑定后用户再提及或输入其他任务目录时，不自动换绑，除非用户明确要求切换 / 重新绑定。

## 二、路由

命中明确业务需求时，进入对应业务仓并读取该仓自己的 `AGENTS.md` 入口说明；未命中时，只在工作台层面补充任务、知识库或规则。

| 关键词 | 路由 |
| --- | --- |
| `素材库`、`原始素材`、`local-source` | `source/README.md`，需要二次开发时先复制素材到目标任务或业务仓 |
| `鹅懂个啥`、`uni-gknow`、`gknow` | `business-repo/uni-gknow`；长期产品上下文见 `business-repo/uni-gknow/docs/README.md`；日常开发见 `task/dev-flow/261009_gknow-daily/README.md`；管理员内容工具见 `task/dev-flow/261010_gknow-content-studio/`，产品视频见 `task/dev-flow/261015_gknow-product-video/` |
| `superone` | 先到 `business-repo/`，再按需求判断 `backend-superone`、`uni-superone`、`uni-carbon-space`、`frontend-superone`、`miniprogram-superone`、`frontend-contracts` 或 uTools 端 |
| `后端`、`API`、`数据库`、`SQL` | `business-repo/backend-superone` |
| `前端`、`页面`、`uni-app` | `business-repo/uni-superone` |
| `Web`、`H5`、`Nuxt` | `business-repo/frontend-superone` |
| `原生小程序`、`微信小程序原生` | `business-repo/miniprogram-superone` |
| `投资平台`、`investment platform` | `business-repo/frontend-investment-platform` |
| 个人理财、仓位健康、投资日报、sell put、滚仓或权利金周目标 | 使用 `finance-tools-investment`；当前上下文为 `task/daily/health-sleep-sell-put/`。与理财内容创作、投资平台开发区分，不改业务仓或自动交易 |
| `uTools`、`桌面工具` | 按语义到 `business-repo/utools-superone`、`utools-bean-note` 或 `utools-bean-option` |
| `carbon`、`uni-carbon-space` | `business-repo/uni-carbon-space`；开发流程内读取 Carbon 品牌 references，SVG 资产按需调用 `dev-flow-tools-svg-assets` |
| `宣传片`、`功能演示视频`、`版本更新视频`、`产品视频` | 先定位产品仓与任务目录，再用 `dev-flow-tools-product-video` 制作；不因制作视频直接改业务代码 |
| `OpenAPI`、`契约`、`frontend-contracts`、`DTO 同步` | `business-repo/frontend-contracts` |
| `beannote`、`豆小匠 Note`、`理财自媒体`、`内容创作`、`选题池`、`文章复盘` | 内容主题进入 `task/beannote/topics/YYMMDD_主题/`，按 `task/beannote/README.md` 建题或续写，并按选题目录名绑定、自动改当前会话名；选题不登记开发任务。发布工具等日常代码需求进入 `task/dev-flow/261017_beannote-daily/`，可复用代码随 `.agents/skills/bn-tools-*/scripts/` 管理，主题产物仍在 `task/beannote`。辅助编辑与长期写作规则维护统一走 `bn-tools-edit-flow`，排版走 `bn-tools-format-flow`，素材上传、草稿箱和按授权发布走 `bn-tools-publish-flow`；内容决策层 skill 已归档 |
| 长期日常事项、持续跟进、非代码工作 | 先查 `task/daily/README.md` 与 `task/registry.md`，进入对应 `task/daily/{slug}/`；小型连续开发可在 daily 上下文推进，专项项目可衍生或转入 `task/dev-flow/` 并互链 |
| `handoff`、`交接`、`收工`、`下次继续`、`换会话接着做` | 对应任务目录的 `handoff/`（包括 `task/daily/{slug}/handoff/`），走 `wb-handoff` |
| `便签` | 先查 `task/registry.md` 和 `kb/`；没有明确归属时不直接改业务仓 |
| `工作台`、`skill`、`知识库`、`自进化` | 只改工作台根级目录 |

## 三、开发类需求的硬路由

后端改动、前端页面、跨端功能这类开发需求：统一按 `dev-flow` 推进需求沟通、方案设计、实现迭代和交付；有独立目标与验收标准的专项在 `task/dev-flow/YYMMDD_{主题}/README.md` 建档。持续日常事项中的小型开发可继续使用 `task/daily/{slug}/` 上下文，过程记录留在 daily 目录；需要单独交付时从 daily 衍生专项并互链。具体后端、前端、验证细则按需读取 references。

## 四、配套 references

| 文件 | 用途 | 何时读 |
| --- | --- | --- |
| `references/business-request-loop.md` | 业务需求闭环流程 | 命中业务需求，要从需求一路做到沉淀 |
| `references/business-generation-checklist.md` | 业务仓生成验收与沉淀清单，含 dev-flow 全 skill 路由表 | 进入业务仓前、生成后验收、子仓接入检查 |
| `references/task-readme.md` | 工作台任务 README 模板 | 新建或延续 `task/YYMMDD_slug/` 目录 |
| `references/task-review.md` | 工作台任务复盘模板 | 任务收口时写复盘 |

## 输出要求

- 给出命中的业务仓或工作台目录。
- 说明是否需要读取额外规则（项目上下文见 `dev-flow-tools-repo`）。
- 路由不清楚时，先补充任务登记或痛点记录，不要盲目改业务仓。

## 工作原则

- 默认把工作台作为能力沉淀层，而不是业务实现层。
- 业务需求完成后，判断是否需要更新 `task/`、`kb/`、`~/.agents/skills/` 或 `script/`；skill 就在工作台仓库里，`make commit` 一起提交，改动经 `~/.agents` 外链同步给所有接入方。
- 连续两轮没有识别清楚用户意图时，记录到 `task/pain-points.md`，并考虑优化路由或 skill。
- 工作台说明类文档只在 `docs/` 平铺；模板、清单和工作流跟着对应 skill 的 `references/` 走。
- 工作台文档使用中文，专业术语和业务术语可保留英文。
