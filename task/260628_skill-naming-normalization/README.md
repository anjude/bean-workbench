# skill 命名规范收敛

## 背景

工作台会持续接入多套功能和领域各异的 skill，若目录命名没有统一规则，后续会出现：

- 同一领域 skill 无法按前缀聚类
- 新旧 skill 混用品牌名、仓名、动作名，难以搜索和维护
- 业务仓内部的私有 skill 长期滞留，无法沉淀成工作台通用能力

`beannote` 接入后，暴露出一类典型问题：内容 skill 沉淀在 `business-repo/beannote/.workbuddy/skills/`，目录命名和内部路径都带有 `workbuddy` 品牌属性，不利于工作台复用。

## 目标

1. 在工作台 `AGENTS.md` 和 `docs/workspace.md` 中补充统一的 skill 命名规则。
2. 约定 `.agents/skills/` 统一使用 `{族群前缀}-{四位序号}-{能力后缀}` 的编号式命名。
3. 将 `beannote` 的内容 skill 迁移到工作台级 `.agents/skills/`，移除品牌化 skill 目录命名。
4. 保留业务仓 memory 和业务内容目录，但让入口文档优先指向工作台 skill。
5. 对历史品牌目录做收口时，将稳定规则蒸馏到项目文档，而不是继续保留品牌目录作为主入口。

## 当前命名约定

族群前缀固定两位，序号按族群内开发顺序从 `0000` 递增：

- `be-*`：后端开发流水线
- `fe-*`：前端开发流水线，carbon 品牌特化层并入本族
- `cn-*`：内容生产线
- `wb-*`：工作台基建

实践要求：

- 序号按开发顺序分配，入口总控固定 `0000`，验收审查排在末尾
- 新增 skill 追加到族群末尾，插队时必须重排后续序号并同步全部引用
- 目录名、`SKILL.md` 的 `name`、文档引用三者必须一致
- 业务仓稳定复用的 skill 应迁移到工作台 `.agents/skills/`

## 本次迁移

### 第一批：内容线收归工作台

- `article-review` -> `content-beannote-article-review`
- `content-creation` -> `content-beannote-creation-flow`
- `knowledge-base` -> `content-beannote-knowledge-base`

### 第二批：全量归族编号（2026-08-29）

后端（`be`，阶段 `00` 设计 / `01` 开发 / `02` 交付）：

- `backend-superone-dev-flow` -> `be-0000-dev-flow`
- `backend-superone-domain-flow` -> `be-0001-domain-flow`
- `backend-superone-field-sql-flow` -> `be-0002-field-sql-flow`
- `backend-superone-db-change-flow` -> `be-0101-db-change-flow`
- `backend-superone-api-flow` -> `be-0102-api-flow`
- `backend-superone-wire-flow` -> `be-0103-wire-flow`
- `backend-frontend-contract-flow` -> `be-0201-contract-flow`
- `backend-superone-test-review-flow` -> `be-0202-test-review-flow`

前端（`fe`，carbon 品牌特化层并入本族）：

- `uni-dev-flow` -> `fe-0000-dev-flow`
- `uni-product-archetype-flow` -> `fe-0001-product-archetype-flow`
- `uni-state-matrix-flow` -> `fe-0002-state-matrix-flow`
- `carbon-space-ui` -> `fe-0003-space-ui`
- `uni-api-flow` -> `fe-0101-api-flow`
- `uni-state-flow` -> `fe-0102-state-flow`
- `uni-page-flow` -> `fe-0103-page-flow`
- `uni-component-style-flow` -> `fe-0104-component-style-flow`
- `uni-svg-flow` -> `fe-0105-svg-flow`
- `carbon-icon-flow` -> `fe-0106-icon-flow`
- `uni-test-build-flow` -> `fe-0201-test-build-flow`

内容（`bn`，用户拍板前缀用 `bn` 不用 `cn`）：

- `content-beannote-knowledge-base` -> `bn-0001-knowledge-base`
- `content-beannote-creation-flow` -> `bn-0101-creation-flow`
- `content-beannote-article-review` -> `bn-0201-article-review`

工作台（`wb`）：

- `hair` -> `wb-0000-hair`
- `workbench-router` -> `wb-0101-router`

### 编号规则调整

初版用单一连续序号（`be-0000` 到 `be-0007`），用户反馈四位编号应拆成两段：前两位是阶段号，后两位是阶段内序号，`xx00` 留给阶段总控。因此把连续序号重排为阶段式编号，并同步全仓引用。

同步范围：`SKILL.md` 的 `name` 字段与正文交叉引用、`AGENTS.md`、`docs/workspace.md`、`docs/workflows/`、`task/registry.md`、相关任务文档、`script/check-workbench.ps1`、工作台长期记忆。业务子仓 `business-repo/` 与历史日志按只读处理，未改写。

### 后续变更（2026-08-29）

本篇记录的 be 族编号在同日又被重构了一次，改为四阶段划分并新增工具层，be 的编号以 `task/260829_be-skill-refactor/` 为准：

- `be-0000-dev-flow` 拆为 `be-0000-plan-flow`，原总控删除。
- `be-0001-domain-flow` -> `be-0101-domain-flow`
- `be-0002-field-sql-flow` -> `be-0102-field-sql-flow`
- `be-0101-db-change-flow` -> `be-0103-db-change-flow`
- `be-0102-api-flow` -> `be-0104-api-flow`
- `be-0103-wire-flow` -> `be-0105-wire-flow`
- `be-0201-contract-flow` -> `be-0106-contract-flow`
- `be-0202-test-review-flow` -> `be-0301-test-review-flow`
- 新增工具层：`be-tools-project-context`、`be-tools-db-query`、`be-tools-branch-release`

本篇其余族群（`fe`、`bn`、`wb`）编号未变，仍然有效。

## 当前状态

编号迁移已完成，24 个 skill 全部归族并采用「阶段号 + 阶段内序号」。后续按 `AGENTS.md`「当前 skill 编号表」维护。be 族的四阶段重构另见 `task/260829_be-skill-refactor/`。
