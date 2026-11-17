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

### 用户明确要求新建或进入任务

「新建任务」和「进入任务」必须区分处理：用户明确要求新建任务时，创建新的任务目录；检查现有任务只用于编号、路由和路径避冲突，不得拿相似或连续的已有任务替代。调用 `wb-handoff` 完成建档、登记、当前会话绑定和改名后，再执行具体工作。用户说“进入 / 继续某个已有任务”或指定已有任务目录时，才按 `wb-handoff` 查询并绑定已有目录；如果用户只要求进入上下文，改名后停下来等待下一步，进入本身不是执行任务内容的授权。普通提及已有任务不触发切换；用户明确要求新建任务或进入 / 切换到任务时，按其指令绑定并改名，即使当前会话此前已经自动绑定过其他任务。

## 二、路由

命中明确业务需求时，进入对应业务仓并读取该仓自己的 `AGENTS.md` 入口说明；未命中时，只在工作台层面补充任务、知识库或规则。

| 关键词 | 路由 |
| --- | --- |
| `素材库`、`原始素材`、`local-source` | `source/README.md`，需要二次开发时先复制素材到目标任务或业务仓 |
| 后端上传图片、图片转 URL | 使用 `tools-image-upload`；公众号专属素材与发布仍走 `bn-tools-publish-flow` |
| IMA 笔记或知识库 | 使用 `tools-ima`；读取对应 notes 或 knowledge-base 模块说明后操作 |
| 鹅懂个啥测试、副本内容或素材维护 | 进入 `task/daily/QBF1_gknow-content-maintenance/` 并使用 `tools-content-maintenance`；内容与素材备份在 `business-repo/uni-gknow/docs/content/`，功能改造仍走 `dev-flow` |
| `鹅懂个啥`、`uni-gknow`、`gknow` | `business-repo/uni-gknow`；长期产品上下文见 `business-repo/uni-gknow/docs/README.md`；功能日常入口见 `task/daily/QB81_gknow/README.md`，内容维护见 `task/daily/QBF1_gknow-content-maintenance/README.md`；管理员内容工具见 `task/dev-flow/QAA1_gknow-content-studio/`，产品视频见 `task/dev-flow/QAF1_gknow-product-video/` |
| `小红书内容研究`、`小红书帖子预发布`、`MediaCrawler`、`XHS-Downloader` | 使用 `xhs-tools-content-research`；鹅懂个啥图文生成与样本学习上下文见 `task/dev-flow/QAA1_gknow-content-studio/` |
| `疯狂大鹅`、`crazy-goose` | 任务入口 `task/dev-flow/QB12_gknow-minigame/README.md`；Cocos Creator 客户端在 `business-repo/crazy-goose`，后端用 `business-repo/backend-superone` |
| `superone` | 先到 `business-repo/`，再按需求判断 `backend-superone`、`uni-superone`、`uni-carbon-space`、`frontend-superone`、`miniprogram-superone`、`frontend-contracts` 或 uTools 端 |
| Superone MCP 安装、扫码登录或私有 Skill 同步 | 使用 `superone-mcp-install`；服务端功能开发仍进入 `task/dev-flow/QB71_backend-superone-mcp/` |
| `后端`、`API`、`数据库`、`SQL` | `business-repo/backend-superone` |
| `前端`、`页面`、`uni-app` | `business-repo/uni-superone` |
| `Web`、`H5`、`Nuxt` | `business-repo/frontend-superone` |
| `原生小程序`、`微信小程序原生` | `business-repo/miniprogram-superone` |
| `投资平台`、`investment platform` | `business-repo/frontend-investment-platform` |
| 个人理财、仓位健康、投资日报、sell put、滚仓或权利金周目标 | 使用 `finance-tools-investment`；当前上下文为 `task/daily/QAQ1_health-sleep-sell-put/`。与理财内容创作、投资平台开发区分，不改业务仓或自动交易 |
| `uTools`、`桌面工具` | 按语义到 `business-repo/utools-superone`、`utools-bean-note` 或 `utools-bean-option` |
| `carbon`、`uni-carbon-space` | `business-repo/uni-carbon-space`；开发流程内读取 Carbon 品牌 references，SVG 资产按需调用 `dev-flow-tools-svg-assets` |
| `宣传片`、`功能演示视频`、`版本更新视频`、`产品视频` | 先定位产品仓与任务目录，再用 `dev-flow-tools-product-video` 制作；不因制作视频直接改业务代码 |
| `OpenAPI`、`契约`、`frontend-contracts`、`DTO 同步` | `business-repo/frontend-contracts` |
| `beannote`、`豆小匠 Note`、`理财自媒体`、`内容创作`、`选题池`、`文章复盘` | 内容主题进入 `task/beannote/topics/{主题编号}_主题/`，新主题按 `task/beannote/README.md` 的日期码加当日序号规则建题，旧目录保留原名；续写时按选题目录名绑定、自动改当前会话名；选题不登记开发任务。发布工具等日常代码需求进入 `task/dev-flow/QAH2_beannote-daily/`，可复用代码随 `.agents/skills/bn-tools-*/scripts/` 管理，主题产物仍在 `task/beannote`。辅助编辑与长期写作规则维护统一走 `bn-tools-edit-flow`，排版走 `bn-tools-format-flow`，素材上传、草稿箱和按授权发布走 `bn-tools-publish-flow`；内容决策层 skill 已归档 |
| 长期日常事项、持续跟进、非代码工作 | 先查 `task/daily/README.md` 与 `task/registry.md`，进入对应 `task/daily/{任务编号}_{slug}/`；小型连续开发可在 daily 上下文推进，专项项目可衍生或转入 `task/dev-flow/` 并互链 |
| `handoff`、`交接`、`收工`、`下次继续`、`换会话接着做`、`切新会话` | 对应任务目录的 `handoff/`（包括 `task/daily/{任务编号}_{slug}/handoff/`），走 `wb-handoff` |
| 查找或总结本机微信联系人、群聊、关键词和指定时间段的聊天记录 | 走 `wb-wechat-local`，只读本机数据源 |
| macOS 微信防撤回、WeChatIntercept 安装/修复或补丁升级失效 | 走 `wb-wechat-anti-revoke`，安装前备份对应 build 并核验运行时 hook |
| `便签` | 先查 `task/registry.md` 和 `kb/`；没有明确归属时不直接改业务仓 |
| `工作台`、`skill`、`知识库`、`自进化` | 只改工作台根级目录 |

## 三、开发类需求的硬路由

后端改动、前端页面、跨端功能这类开发需求：统一按 `dev-flow` 推进需求沟通、方案设计、实现迭代和交付；有独立目标与验收标准的专项使用 `task/dev-flow/{任务编号}_{主题}/` 建档，编号按工作台任务规则分配，同日多任务递增 36 进制序号。所有已有专项目录均已统一为新版编号。设计方案放任务目录 `plans/` 下的独立文档，由 README 索引。持续日常事项中的小型开发可继续使用 `task/daily/{任务编号}_{slug}/` 上下文，过程记录留在 daily 目录；需要单独交付时从 daily 衍生专项并互链。具体后端、前端、验证细则按需读取 references。

## 四、配套 references

| 文件 | 用途 | 何时读 |
| --- | --- | --- |
| `references/business-request-loop.md` | 业务需求闭环流程 | 命中业务需求，要从需求一路做到沉淀 |
| `references/business-generation-checklist.md` | 业务仓生成验收与沉淀清单，含 dev-flow 全 skill 路由表 | 进入业务仓前、生成后验收、子仓接入检查 |
| `references/task-readme.md` | 工作台任务 README 模板 | 新建或延续 `task/{任务编号}_slug/` 目录 |
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
