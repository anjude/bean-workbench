# uTools Superone 重构

## 背景

`utools-superone` 已完成一轮契约接入、Repo 收敛、发布检查与业务清理改造。本任务先精简一级辅助文件，再审查 `src/` 目录组织、遗留文件和契约类型复用方式。

## 需求理解

精简 `utools-superone` 一级目录辅助文件，保持开发/生产 API 环境选择一致、保留 Vue 组件自动导入和构建能力，并让 README 与当前功能一致。

## 目标与边界

### 本期目标

- 移除冗余的显式环境文件，提供有效的 `.env.example` 本地覆盖示例。
- 移除未使用的 API 自动导入插件及空生成声明，保留组件自动导入。
- 移除陈旧技术栈建议与误导性的旧产品介绍。
- 检查 `src/` 是否适合从按技术层分组逐步转成按业务功能组织。
- 清理有明确无引用证据的旧文件和本地重复类型，确认 API 枚举直接使用 `src/contracts`。
- 对照近期任务 `task/dev-flow/261007_utools-release-contract-checks/README.md`，避免重复其已完成的契约、Repo、发布门禁和业务功能范围。
- 不扩展到业务逻辑或页面架构重构，不触碰共享契约和后端。

### 本期不做

- 不扩展到业务逻辑或页面架构重构，不触碰共享契约和后端。
- 不执行发布、分支推进或数据库操作。
- 不批量迁移活跃源码目录；仅删除经过引用扫描确认无消费者的文件与类型。
- Vite 环境选择与配置保持现状，本阶段不调整。

### 后续实施：Topic 页面 UI/UX

- 目标：收紧 Topic 页面的间距、按钮和元信息，把选中主题、快速记录与记录内容作为视觉主线。
- 低频的主题/记录操作通过统一的可复用上下文菜单呈现；保留明显的创建、保存和记录详情入口。
- 参考 `business-repo/uni-superone` 的 SuperOne 品牌令牌与克制层级；适配 uTools 桌面交互，不照搬 uni-app 布局。
- 范围：`utools-superone/src/views/TopicList.vue`、`src/styles/07-pages/_topic-list.scss`、通用上下文菜单组件及必要的主题 composable。
- 状态：加载、错误/重试、空主题、无选中主题、空记录、有记录、菜单打开/关闭、操作中反馈均保留。
- 不改 API、共享契约、后端、Vite 环境或其他业务页面。

## 改动范围

### 当前确认范围

- `business-repo/utools-superone`：一级辅助文件；`src/types/`、`src/constants/`、请求 client 绑定、样式入口与图标字体目录中的确认废弃项；Vite 环境配置不在本次改动范围。
- 工作台：本任务方案、过程记录、交接记录及任务登记。

### 涉及库表、接口与契约

- 无；仅核对现有 `src/contracts` 消费关系，不改契约事实源。

## 实施方案

1. 移除 Vite 默认 MODE 可替代的 `.env.development` 与 `.env.production`，整理 `.env.example` 与 README。
2. 移除当前没有实际使用的 `unplugin-auto-import`，保留组件自动导入插件。
3. 删除过时的技术栈实施建议和陈旧产品简介。
4. 更新任务过程记录；运行门禁验证后记录结论。

## 验收标准

- TypeScript/Vite 配置不再引用 `unplugin-auto-import`，Vue 组件自动导入仍保留。
- 无环境变量覆盖时，dev 默认指向 develop，build 默认指向 release；`.env.example` 可复制为 `.env.local` 使用。
- README 不再声明已删除功能，过时技术栈文档已清理。
- 静态差异审阅完成；`npm run check` 通过后任务收口。
- 结构审查给出按功能组织的可行方案，已删除项均有源码引用扫描依据。
- 本工作台任务在 `task/registry.md` 中可路由。

## 当前状态

前一轮清理与门禁已完成；uTools 子仓提交 `eaec6c4` 已推送到 `release`。Topic 页面及记录详情/跟进 UI/UX 已实现，类型检查与生产构建通过；Vite 环境配置保持不动。

## 待确认

- 活跃源码目录未迁移；按功能组织的重构方案暂作后续建议。

## 沉淀候选

- 如果发现可跨 uTools 页面复用的重构规范，再评估沉淀到 uTools 仓说明或工作台 skill。
