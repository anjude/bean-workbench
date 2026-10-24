# 需求理解与范围确认

# 跨端方案设计

需求理解和范围确认发生在设计与开发之前；方案默认经用户确认后再进入实现。

项目上下文（目录约定、分支与部署、技术栈、构建命令）不在此处重复，需要时读取 `dev-flow-tools-repo`。

## 定位

本细则说明三件事：把需求理解清楚、把改动范围钉死、把后续阶段派发下去。不写业务代码，不执行 SQL，不跑验证命令。

## 需求解析

从需求描述中提取，缺什么问什么，不替用户发明业务规则：

- 动作：新增、修改、删除。
- 对象：业务对象名称、字段、状态流转。
- 约束：权限、幂等、分页、排序、过滤、默认值、历史数据处理。
- 边界：本期做什么，明确不做什么。
- 数据：是否涉及新增表、改字段、改索引、回填 DML。
- 接口：是否有对外 API，是否影响前端展示或提交。
- 端：只动后端、只动前端、还是跨端。跨端需求必须写清两段的交接物。
- 页面：新增页面、改已有页面，还是只改组件和样式。
- 状态：是否存在加载中、空数据、失败、权限不足等非 happy path 分支。

缺失但能从现有同类功能安全推断的规则，要在方案里写明推断来源，不要静默假定。

## 影响面定位

用 `rg` / `find` 定位最相近的现有实现，方案里的每一处改动都要有落点。

后端落点：

- 路由：`app/api_service/*.go`
- UseCase：`use_case/*.go`
- DTO：`internal/domain/{domain}/{domain}_dto`
- Entity：`internal/domain/{domain}/{domain}_entity`
- Factory：`internal/domain/{domain}/{domain}_factory`
- Service：`internal/domain/{domain}/{domain}_service`
- Repo：优先 `internal/repo`，domain 已有局部 repo 时沿用
- 表模型：`internal/model/*_tab.go`
- Wire：`use_case/wire.go`、`app/api_service/wire.go`、`internal/domain/**/wire.go`
- 契约：`business-repo/frontend-contracts/openapi/{domain}_api.yaml`

前端落点：

- 页面与路由：`src/pages.json`、`src/pages/**/index.vue`
- API 调用：`src/apis/*.ts`；共享 API 类型与枚举：项目接入的协议子仓目录（当前 uni-superone 为 `src/contracts`）
- 状态：`src/stores/*.ts`、`src/composables/use*.ts`
- 组件与样式：`src/components/cu-*.vue`、`src/components/business/*.vue`、`src/styles/index.css`

跨端边界：

- 接口与枚举只核对唯一协议事实仓及客户端子仓修订，不规划按平台复制契约。
- 平台运行时差异定位到客户端适配边界；页面层只承接确有产品需要的 UI、UX 与交互差异。

需要确认库表结构时，用 `dev-flow-tools-db-query` 只读查看，不在此阶段做写操作。
