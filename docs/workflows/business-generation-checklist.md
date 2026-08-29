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
2. 使用 `wb-0001-router` 判断目标仓库和可能受影响的协作仓。
3. 进入业务仓前确认需求是否明确；不明确时只更新工作台任务或痛点，不直接改业务仓。
4. 命中 Superone 业务时，按阶段选择最小 skill 组合：
   - 所有需求先过 `dev-flow-0000-plan-flow` 出方案，方案确认后才进入开发阶段；方案文档落 `task/YYMMDD_{主题}/README.md`。
   - 00 方案设计：
     - 需求理解、改动范围确认、方案产出与阶段派发：`dev-flow-0000-plan-flow`。
   - 01 后端开发，按执行顺序：
     - 领域层 entity、model、factory、repo、service + 字段设计与 DDL/DML SQL：`dev-flow-0101-domain-flow`。
     - 迁移脚本、test/live 执行与验证：`dev-flow-0102-db-change-flow`。
     - API、UseCase、Service、路由 + Wire 依赖注入：`dev-flow-0103-api-flow`。
     - OpenAPI YAML 与前端契约生成：`dev-flow-0104-contract-flow`。
   - 02 前端开发：交接物是 `dev-flow-0104-contract-flow` 输出的前端复制清单；原型与状态矩阵是硬门槛。
     - 产品原型与状态矩阵：`dev-flow-0201-archetype-flow`。
     - API 类型与请求封装、Store 与 Composable：`dev-flow-0202-data-flow`。
     - 页面、路由与生命周期、组件与样式审美：`dev-flow-0203-page-flow`。
     - SVG 资产、命中 `uni-carbon-space` 时的品牌图标：`dev-flow-0204-asset-flow`。
     - 命中 `uni-carbon-space` 时的品牌规范（全程叠加）：`dev-flow-0205-space-ui`。
   - 03 整体验证：
     - 门禁复核、后端验证命令与审查、前端 type-check/build、契约核对、方案回填：`dev-flow-0301-verify-flow`。
   - 工具层，不占阶段，按需调用：
     - 多仓目录约定、技术栈、命令、分支推进与部署：`dev-flow-tools-repo`。
     - 只读数据库排查与结构验证：`dev-flow-tools-db-query`。
   - 完整编号表见 `AGENTS.md`「当前 skill 编号表」。

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
