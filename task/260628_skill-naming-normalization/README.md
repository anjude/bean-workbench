# skill 命名规范收敛

## 背景

工作台会持续接入多套功能和领域各异的 skill，若目录命名没有统一规则，后续会出现：

- 同一领域 skill 无法按前缀聚类
- 新旧 skill 混用品牌名、仓名、动作名，难以搜索和维护
- 业务仓内部的私有 skill 长期滞留，无法沉淀成工作台通用能力

`beannote` 接入后，暴露出一类典型问题：内容 skill 沉淀在 `business-repo/beannote/.workbuddy/skills/`，目录命名和内部路径都带有 `workbuddy` 品牌属性，不利于工作台复用。

## 目标

1. 在工作台 `AGENTS.md` 和 `docs/workspace.md` 中补充统一的 skill 命名规则。
2. 约定 `.agents/skills/` 统一使用 `{领域前缀}-{可选子域}-{能力后缀}` 的 kebab-case 命名。
3. 将 `beannote` 的内容 skill 迁移到工作台级 `.agents/skills/`，移除品牌化 skill 目录命名。
4. 保留业务仓 memory 和业务内容目录，但让入口文档优先指向工作台 skill。
5. 对历史品牌目录做收口时，将稳定规则蒸馏到项目文档，而不是继续保留品牌目录作为主入口。

## 当前命名约定

推荐前缀：

- `backend-*`
- `frontend-*`
- `uni-*`
- `content-*`
- `workbench-*`
- `carbon-*`

实践要求：

- 新增 skill 必须优先按领域归类，再补能力后缀
- 存量 skill 可渐进迁移，不强制一次性全量重命名
- 业务仓稳定复用的 skill 应迁移到工作台 `.agents/skills/`

## 本次迁移

- `article-review` -> `content-beannote-article-review`
- `content-creation` -> `content-beannote-creation-flow`
- `knowledge-base` -> `content-beannote-knowledge-base`

## 当前状态

进行中。
