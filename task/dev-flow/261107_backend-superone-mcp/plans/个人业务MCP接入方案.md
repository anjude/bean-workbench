# 个人业务接入 MCP 方案

## 目标和范围

让用户通过已登录的 Superone MCP 查询和管理现有个人业务数据。复用后端现有 Service、数据和权限，HTTP 原有接口继续作为现有客户端入口，MCP 是访问相同业务实现的另一种传输入口。

用户选择接入近期任务、主题、主题记录、清单、清单执行记录、物品及物品分类，包含此前清单列出的读、创建、更新、删除能力。目标、行程、Carbon 专属能力等未被选择，不纳入本次。工具名称以下为设计候选，按现有方法逐项映射；不新增表或数据迁移。

## 工具清单

| 对象 | MCP 工具 | 对应现有 Service 方法 |
| --- | --- | --- |
| 近期任务 | `list_recent_tasks`、`get_recent_task`、`create_recent_task`、`update_recent_task`、`delete_recent_task` | `IRecentTaskService` 的 `GetRecentTaskList`、`GetRecentTaskDetail`、`CreateRecentTask`、`UpdateRecentTask`、`DeleteRecentTask` |
| 主题 | `list_topics`、`get_topic`、`create_topic`、`update_topic`、`delete_topic` | `ITopicService` 的相应 `Topic` 方法 |
| 主题记录 | `list_topic_logs`、`get_topic_log`、`create_topic_log`、`update_topic_log`、`delete_topic_log` | `ITopicService` 的相应 `TopicLog` 方法 |
| 清单 | `list_checklists`、`get_checklist`、`create_checklist`、`update_checklist`、`delete_checklist` | `IChecklistService` 的相应 `Checklist` 方法 |
| 清单执行记录 | `list_checklist_executions`、`get_checklist_execution`、`list_checklist_execution_history`、`create_checklist_execution`、`update_checklist_execution`、`delete_checklist_execution` | `IChecklistService` 的 `GetExecutionList`、`GetExecutionDetail`、`GetExecutionHistory`、`CreateExecution`、`UpdateExecution`、`DeleteExecution` |
| 物品及分类 | `list_items`、`get_item`、`create_item`、`update_item`、`delete_item`、`list_item_categories` | `IItemService` 的相应 `Item` 方法及 `GetItemCategoryList` |

共 32 个候选工具。工具参数、返回值和已有 HTTP DTO 对齐，名称及说明写清必填项、枚举取值、Unix 时间单位、分页和更新语义。列表保留既有筛选：任务关键词/状态/优先级；主题与清单关键词；主题记录的主题 ID、类型、父记录；执行记录的清单、状态及历史时间范围；物品关键词、分类、状态和标签。不要暗示已有接口支持时间范围、跨主题全文检索等未提供的筛选。

## 接入方式

1. **身份与入口。** 复用 `/api/so/mcp/transport` 的 JWT 鉴权和 `handleTool`，取当前认证 `BizContext`；不从工具参数接收 OpenID。MCP 场景 JWT 保持现有路由范围限制，不用内部 HTTP 自调用绕过该限制。
2. **复用 Service。** `UseCase` 从 HTTP 请求上下文取得 DTO，不能直接拿 MCP 参数调用。参照现有 Skill 工具，将 MCP 输入转换成现有 DTO，调用同一个领域 Service，让 HTTP 和 MCP 共享权限、事务、默认值及业务规则。通过 Wire 在 `ApiGroup`/MCP 注册处注入近期任务、主题、清单和物品服务，避免业务逻辑复制到工具层。
3. **参数校验。** HTTP 的 `ShouldBindJSON/Query` 执行 `binding` 校验，直接调用 Service 不会经过这一层。MCP 在 SDK 完成 JSON 解码后，调用 Gin 的 `binding.Validator.ValidateStruct` 验证同一请求 DTO 的 `binding` 标签，复用 HTTP 使用的校验器及其注册规则；校验失败转为参数错误并阻止调用 Service。MCP 适配 DTO 如与 HTTP DTO 不同，先转换成 HTTP DTO 再校验，不能另维护一套标签解析器。SDK 的 JSON Schema 校验先于 handler，其必填、零值和可选字段行为可能与 Gin 不同；对照调节 schema 并用原始请求比较缺失、null、零值、空字符串、数组及非法类型，不把复用校验器误当作解析完全一致。现有 `CreateExecutionReq` 的 `mode` 和 `status` 注释允许 0，但 `binding:"required"` 对整数零值的行为必须先实测并与现有产品预期对齐，不能静默拒绝合法状态或擅自修改业务语义。
4. **权限和数据。** 逐个核对列表、详情及写操作的数据归属和 `CanEdit` 权限；测试其他账号传入 ID 时不能越权。MCP 输出以业务所需字段为准，核查现有 DTO 的 OpenID 等内部标识，避免无必要暴露。分页沿用实际 Service 行为，不能只靠 schema 声称具有限制。
5. **主题记录边界。** 现有 `TopicLog` 同时支持多种业务类型，其中 Carbon 类型涉及空间权限；`GetTopicLogList` 查询约定类型还会标记已读。用户已明确 Carbon 不开放。主题记录使用显式允许的业务类型白名单，至少排除 CarbonFeedback、CarbonAgreement 和 CarbonScale；未知或未来新增类型默认拒绝。列表逐项检查传入的类型；创建检查目标类型及父记录；详情、更新、删除根据服务端读取的真实记录类型和归属检查，不能信任客户端声明。批量列表混入任一不允许类型时整体拒绝，不进入查询或触发标记已读。个人业务允许的具体非 Carbon 类型结合本次已选功能核定，不能因排除 Carbon 自动开放反馈或公开分享。只有无副作用的查询才设置 `ReadOnlyHint`。
6. **修改与删除。** 各工具保持现有部分更新、清单项目替换和删除语义，不添加不存在的版本锁或批量事务。工具描述清楚删除和关联影响；用户可在客户端确认具体操作，客户端提示不是服务端强制确认。失败时返回业务错误，不报告成功或自动重试可能重复创建的操作。
7. **隐私和日志。** 记录工具名、耗时及结果，不记录 JWT、主题正文、清单内容和物品详情；检查现有 MCP 中间件、SDK 和 Service 日志的实际输出，确保不将私有内容写入日志。

## 文件和契约影响

- 后端 `app/api_service/mcp/`：按领域新增工具注册文件，复用 `handler.go`；补参数校验和工具注释、输入输出说明。
- 后端 `app/api_service/api_service.go`、`wire.go`、生成的 Wire 文件及 `use_case/wire.go`：装配上述现有 Service；如校验或共享业务规则需要调整，落在共享层并回归 HTTP，不另造并行实现。
- `internal/domain/{plan,topic,checklist,item}/`：先核查现有 DTO、权限及跨领域依赖，仅为消除真实不一致而调整共享校验或授权；不改变既有业务能力。
- `frontend-contracts`：HTTP 行为和 DTO 不变时无需改动 HTTP 契约；如为修复实际校验/行为问题修改契约，按影响同步。MCP 工具 schema 由服务端注册生成，补充面向客户端的工具说明和示例。
- 安装说明与 `superone-mcp-install`：更新工具清单与客户端用法，保留用户决定是否执行写操作的边界。

## 实施顺序和验收

1. 核对每个 Service/Repo 的用户权限、HTTP 绑定和真实枚举，明确个人主题记录的类型边界；确定执行记录零值校验和查询副作用。形成工具 schema 及示例。
2. 逐领域装配服务和工具，覆盖列表、详情、创建、更新、删除及历史/分类；工具 schema 必须与实际 DTO 和校验一致。
3. 针对 HTTP 与 MCP 运行同一组有效/无效输入对照；检查两个身份对彼此记录的列表、详情、更新、删除，包含主题记录的父子关系和非个人类型绕过尝试。
4. 在真实 test 服务按领域验证「创建 → 列表 → 详情 → 更新 → 读取 → 删除」；清单执行记录另验证历史、状态 0 和 1、时间筛选；主题记录验证根/子记录；物品验证分类及提醒字段。每次只清理由测试创建的数据，验证失败后的数据状态。
5. 用真实 MCP 客户端完成一次跨工具自然语言查询和一次经用户明确要求的写操作；测试分页、参数缺失、非法枚举、无权限、其他账号 ID、错误结果及日志不泄露内容。确认现有小程序 HTTP 行为无回归。编译和单测不视为目标环境验收。

## 待评审

- 32 个工具名称是否采用上述一一映射，还是由客户端体验决定少量合并；不改变用户选择的业务操作范围。
- Carbon 已明确不开放，包括 CarbonFeedback、CarbonAgreement 和 CarbonScale；非 Carbon 中哪些类型对应本次已选业务，需按调用方核实并列入白名单。执行记录零值校验实际规则及清单/主题删除的关联影响，需按代码和现有客户端确认后写入工具说明。
- 客户端写入前的确认体验由目标客户端决定；若需要服务端强制确认或审计，另定交互与存储方案。
