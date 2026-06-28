# 业务仓知识库

这里按业务仓沉淀系统理解、上下文入口、常见约束和复用经验。

## 业务仓索引

- `backend-superone`：后端业务仓，位置为 `business-repo/backend-superone`。
- `uni-superone`：uni-app 前端业务仓，位置为 `business-repo/uni-superone`。
- `uni-carbon-space`：carbon 品牌 uni-app 前端业务仓，位置为 `business-repo/uni-carbon-space`。
- `frontend-contracts`：前后端协议仓，位置为 `business-repo/frontend-contracts`。
- `frontend-superone`：Nuxt / Web 前端业务仓，位置为 `business-repo/frontend-superone`。
- `miniprogram-superone`：微信原生小程序业务仓，位置为 `business-repo/miniprogram-superone`。
- `frontend-investment-platform`：投资相关 Web 前端业务仓，位置为 `business-repo/frontend-investment-platform`。
- `utools-superone`：uTools Superone 桌面工具仓，位置为 `business-repo/utools-superone`。
- `utools-bean-note`：uTools 便签/笔记工具仓，位置为 `business-repo/utools-bean-note`。
- `utools-bean-option`：uTools option 工具仓，位置为 `business-repo/utools-bean-option`。
- `beannote`：豆小匠 Note 内容管理库，面向理财自媒体的选题、生产、知识沉淀、素材、发布和复盘流程，位置为 `business-repo/beannote`。
- `bt`：后端相关辅助工具仓，位置为 `business-repo/bt`。

## 默认分支约定

- `backend-superone` 默认分支为 `dev`。
- `uni-superone` 默认分支为 `master`。
- `uni-carbon-space` 默认分支为 `master`。
- `frontend-contracts` 默认分支为 `master`。
- `frontend-superone` 默认分支为 `master`。
- `miniprogram-superone` 默认分支为 `master`。
- `frontend-investment-platform` 默认跟踪分支为 `release`。
- `utools-superone` 默认分支为 `master`。
- `utools-bean-note` 默认分支为 `main`。
- `utools-bean-option` 默认分支为 `master`。
- `beannote` 默认分支为 `master`。
- `bt` 默认分支为 `master`。

## Superone 编排关系

- 工作台是 Superone 多仓协作的全局入口，负责判断需求应该落到后端、前端、协议仓，还是只沉淀到知识库或 skill。
- `backend-superone` 负责服务端实现、数据模型、领域规则、接口和验证。
- `uni-superone` 负责跨端前端页面、状态、交互和接口消费。
- `uni-carbon-space` 负责 carbon 品牌下的跨端前端页面、状态、交互和接口消费。
- `frontend-contracts` 负责 OpenAPI、前端类型、枚举和 API 契约文件。
- `frontend-superone`、`miniprogram-superone`、`frontend-investment-platform` 和 `utools-*` 负责各自端侧实现。
- `bt` 作为辅助工具仓，不承担 Superone 主业务后端职责。
- 涉及接口、DTO、枚举、错误码和字段语义变化时，由工作台编排后端实现与协议仓同步。
- 已迁入工作台的业务仓不再通过 `backend-superone/submodule/*` 访问；旧 submodule 路径不保留兼容入口。

## 路由提示

- 提到 `frontend-contracts`、`OpenAPI`、`契约`、`DTO 同步`：优先路由到 `business-repo/frontend-contracts`。
- 提到 `beannote`、`豆小匠 Note`、`理财自媒体`、`内容创作`、`选题池`、`文章复盘`：优先路由到 `business-repo/beannote`，再读取该仓自己的内容工作流和 skill。
- 进入任一业务仓后，优先读取该仓根目录 `AGENTS.md`。

## 写入边界

这里只记录知识索引和稳定结论，不复制业务仓大段源码或文档。
