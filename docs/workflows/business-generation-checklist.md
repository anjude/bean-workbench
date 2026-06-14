# 业务仓生成验收与沉淀清单

## 目标

让工作台在生成业务仓内容时，不只完成代码改动，还能稳定完成路由、验证、契约同步和经验沉淀。

## 使用时机

- 用户提出明确业务需求，需要进入 `business-repo/` 下的后端、前端或协议仓。
- 业务需求涉及 API、DTO、字段、枚举、错误码、页面状态、交互或跨仓联动。
- 需求完成后需要判断是否更新知识库、skill、脚本或任务登记。
- 工作台接入新的业务子仓时，需要执行全量检查，确认文档、引用、路由和 skill 是否都已同步。

## 生成前检查

1. 读取 `AGENTS.md`、`task/registry.md` 和 `knowledge-base/README.md`。
2. 使用 `workbench-router` 判断目标仓库和可能受影响的协作仓。
3. 进入业务仓前确认需求是否明确；不明确时只更新工作台任务或痛点，不直接改业务仓。
4. 命中 Superone 业务时，按需求选择最小 skill 组合：
   - 后端 API、UseCase、Service、路由：`backend-superone-api-flow`。
   - 后端领域、模型、Repo、Service：`backend-superone-domain-flow`。
   - 字段、DDL、GORM 表模型：`backend-superone-field-sql-flow`。
   - 数据库连接、迁移、表结构验证：`backend-superone-db-change-flow`。
   - Wire 依赖注入：`backend-superone-wire-flow`。
   - 后端测试、审查、格式化：`backend-superone-test-review-flow`。
   - 前端页面、组件、状态、接口、构建：按需使用 `uni-*` 系列 skill；如果命中 `uni-carbon-space`，再叠加 `carbon-space-ui`、`carbon-icon-flow`。
   - API 契约、DTO、枚举、错误码同步：`backend-frontend-contract-flow`。

## 子仓接入检查

当工作台接入新的业务子仓时，必须补齐以下内容：

1. `business-repo/` 子模块或目录接入
2. `knowledge-base/business-repo/` 索引和职责说明
3. `task/registry.md` 热任务与路由提示
4. 受影响的 `skill` 路由和品牌/协议特化层
5. 相关工作流、任务目录和必要的验证说明

如果其中任一项缺失，视为接入未完成。

## 任务目录合并

当本次工作只是已有任务的延续、修补或碎片化收口时，优先复用最近的任务目录，不要为每次小变动新开目录。只有任务目标和沉淀对象明显分离，才新建任务目录。

## 生成中检查

1. 只在明确业务需求下修改 `business-repo/`。
2. 优先遵循业务仓自己的 `AGENTS.md`、现有目录结构和代码风格。
3. 如果接口、DTO、响应结构、枚举、字段语义或错误码变化，必须同步 OpenAPI 和前端契约。
4. 如果前端页面有数据加载、提交、刷新、错误或空状态，必须补齐状态矩阵，不只实现 happy path。
5. 如果引入新流程或重复命令，优先考虑沉淀为工作台脚本，而不是只写在对话里。

## 生成后验证

按实际影响范围选择验证，不强行跑无关命令。

| 影响范围 | 最小验证 |
| --- | --- |
| 后端 Go 代码 | `gofmt`、相关包 `go test`、必要时 `wire ./...` |
| 数据库变更 | SQL 文件审查、test 环境结构或数据验证、必要时 migration dry run |
| API 契约 | OpenAPI YAML 校验、协议仓类型生成或 diff 检查 |
| uni-app 前端 | `npm run type-check`、必要时 `npm run build:h5` 或 `npm run build:mp-weixin` |
| 工作台文档或 skill | `script/check-workbench.ps1`，必要时按 skill 规范检查 frontmatter |

## 提交收口

工作台内容需要提交时，优先使用根目录 `Makefile` 的统一提交命令，而不是分别对单个文件或子仓提交。这样可以保证工作台索引、路由、skill 和任务记录一起收口。提交信息直接来自 `make commit` 后面的参数，多个参数按空格拼接。

## 沉淀判断

| 现象 | 沉淀位置 |
| --- | --- |
| 只是本次任务上下文 | `task/registry.md` 或对应任务目录 |
| 需求中出现稳定业务知识、系统约束或路径索引 | `knowledge-base/` |
| 同类操作两次以上复现并造成误判或返工 | `docs/pain-points.md` |
| 三次以上复现且流程稳定 | `.agents/skills/` |
| 重复命令、校验或文件扫描可机械执行 | `script/` |

## 最终回复要求

1. 说明改了什么和验证结果。
2. 如果没有运行某项关键验证，说明原因。
3. 如果发现可复用经验已经沉淀，说明沉淀位置。
4. 不把业务仓大段实现细节复制回工作台；只保留索引、约束和可复用结论。
