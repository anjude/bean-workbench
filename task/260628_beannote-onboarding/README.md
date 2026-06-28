# beannote 内容库接入

## 背景

`beannote` 是豆小匠 Note 内容管理库，面向理财自媒体内容生产，覆盖选题池、单篇生产、数据复盘、知识库、素材、账号定位、发布归档和历史归档。

## 目标

1. 将 `git@github.com:anjude/beannote.git` 接入工作台 `business-repo/beannote`。
2. 在工作台知识库中补充 `beannote` 的仓位、职责和默认分支。
3. 在任务登记和路由 skill 中补充内容创作、理财自媒体、选题和文章复盘相关路由。
4. 保持接入边界清晰：本任务只更新工作台索引与子仓引用，不改 `beannote` 业务内容。
5. 将 `beannote` 内部可复用 skill 迁移到工作台 `.agents/skills/`，移除 `.workbuddy` 品牌目录依赖。

## 范围

- `.gitmodules`
- `business-repo/beannote`
- `knowledge-base/business-repo/README.md`
- `task/registry.md`
- `.agents/skills/workbench-router/SKILL.md`
- `.agents/skills/content-beannote-article-review`
- `.agents/skills/content-beannote-creation-flow`
- `.agents/skills/content-beannote-knowledge-base`

## 路由提示

- 提到 `beannote`、`豆小匠 Note`、`理财自媒体`、`内容创作`、`选题池`、`文章复盘` 时，优先进入 `business-repo/beannote`。
- 进入后优先读取该仓自己的 README 和内容工作流 skill。
- `beannote` 与 `utools-bean-note` 职责不同：前者是内容生产资料库，后者是 uTools 便签/笔记工具仓。
- `beannote` 的通用内容 skill 统一沉淀到工作台 `.agents/skills/`，不再保留 `.workbuddy/skills` 品牌命名。
- `beannote` 的项目稳定规则沉淀到 `docs/content-playbook.md`，不再依赖 `.workbuddy/memory/` 作为主入口。

## 验证记录

- 远端 `HEAD` 指向 `master`。
- 子模块路径为 `business-repo/beannote`。

## 当前状态

进行中。
