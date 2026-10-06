---
name: dev-flow-0104-contract-flow
description: 当后端接口、DTO、响应结构、枚举、字段语义或错误码发生可能影响客户端的变动时使用；同步更新唯一协议事实仓中的 OpenAPI 与共享契约，并明确各客户端如何同步消费。
metadata:
  short-description: 后端维护共享协议
---

# 后端共享协议维护

阶段 01 后端开发，执行顺序第 4 步，也是阶段 02 前端开发的交接点。

本 skill 面向多仓、多客户端协作。执行任务时优先以工作台根目录为协调目录；如果当前工作目录在业务仓内，先识别工作台根目录，再定位唯一协议事实仓。当前工作台的协议事实仓是 `business-repo/frontend-contracts`，所有客户端项目共用，不按平台复制出多份协议。

## 目标

后端开发完成接口或枚举变更时，同步更新唯一协议事实仓。所有前端客户端都以 Git 子仓引入并消费同一份契约；客户端只实现自己的传输封装与产品交互，不复制或重新定义接口、结构体和枚举。

## 触发条件

只要本次后端改动包含以下任一项，就必须执行本 skill：

- 新增、删除或修改 API 路由、HTTP method、path。
- 修改请求 DTO、响应 DTO、分页结构、字段名、字段类型、必填规则。
- 修改业务枚举、状态值、错误码、常量含义。
- 修改前端会展示或提交的字段语义、默认值、时间戳、金额、JSON 字段。
- 修改认证要求、登录态、权限、订阅消息等前端调用条件。

## 输出位置

### OpenAPI YAML

- 接口文档放在 `business-repo/frontend-contracts/openapi/{domain}_api.yaml`。
- 已有 domain 更新原文件；新 domain 新建文件。
- YAML 使用 OpenAPI 3.x，保留 `servers.url: /api/so`。
- schema 字段使用后端 JSON 字段名，通常为 snake_case。

### 共享契约目录

统一放在：

```text
business-repo/frontend-contracts/
  openapi/
  apis/
  types/
```

如果唯一协议事实仓或本次需要的子目录不存在，先确认工作台接入约定，再保持最小结构补齐；不得在客户端仓另建一份协议作为替代事实来源。共享契约应平台无关，不依赖某个客户端的页面、状态管理或运行时。

## 文件职责

- `openapi/{domain}_api.yaml`：接口契约源文件。
- `types/{domain}.ts`：共享请求/响应类型、业务结构和枚举；按仓库约定组织与导出。
- `apis/{domain}.ts`：仅放跨客户端稳定且不绑定传输运行时的路径等契约常量；HTTP 请求封装属于客户端实现，不进入共享契约。

## 生成规范

### 命名转换

- 后端 JSON/YAML 字段保持 snake_case。
- TypeScript 类型字段默认使用 camelCase，前端 request 层负责 snake_case/camelCase 转换。
- 如果目标前端没有自动转换层，额外生成 snake_case 版本或在注释中明确字段映射。

### 类型映射

- Go `int`、`int32`、`int64`、`uint32`、`uint64` -> TypeScript `number`。
- Go `string` -> TypeScript `string`。
- Go `bool` -> TypeScript `boolean`。
- Go slice -> TypeScript array。
- Go map/JSON -> 明确结构；无法确定时使用 `Record<string, unknown>`，避免裸 `any`。
- 时间戳字段使用 `number`，注释说明单位。
- 金额如果后端可能返回 string，TypeScript 类型写成 `number | string`，Repo 层再转换。

### 枚举

- 后端新增或修改枚举时，必须生成 TypeScript `enum` 或 `as const` 常量。
- 注释写清每个取值的业务含义。
- YAML schema 的 `enum` 必须同步。
- 前端契约枚举名要包含业务上下文，避免通用 `Status`、`Type`。

### API 常量

如果共享契约仓包含 API 常量：

- 常量必须与 OpenAPI path 和 operationId 一致。
- 不绑定某个客户端的 request、响应包装、缓存或业务逻辑。

## 工作流程

1. 从代码读取真实路由、DTO、Resp、枚举、错误码，不凭空写契约。
2. 更新 `business-repo/frontend-contracts/openapi/{domain}_api.yaml`：
   - paths
   - operationId
   - requestBody 或 query parameters
   - responses
   - components.schemas
   - enum 和 required
3. 确保 `business-repo/frontend-contracts` 及本次需要的子目录存在；不存在则创建。
4. 生成或更新协议事实仓中的共享 TypeScript 类型、枚举和适用的契约常量。
5. 如果本次改动影响多个 domain，按 domain 拆文件，不写一个超大文件。
6. 确认受影响客户端通过 Git 子仓引用该协议事实仓，并给出需要同步的 revision 和消费验证方式；不输出文件复制清单。

## 自动开发集成

在后端 auto 开发流程中：

- API/DTO/枚举改动完成后立即执行本 skill。
- 测试前先保证唯一协议事实仓的 OpenAPI 与共享契约已同步。
- 最终结果必须说明：协议事实仓是否更新、客户端如何同步到该修订、客户端是否存在重复定义。

## 阶段交接

本 skill 是阶段 01 的最后一步，也是阶段 02 的输入：

- 客户端更新协议子仓 revision 后进入阶段 02，由 `dev-flow-0202-data-flow` 从共享契约导入类型和枚举，并在本地实现请求传输层。
- 前端接通后进入阶段 03，由 `dev-flow-0301-verify-flow` 收口，其中会再次核对契约与代码是否一致。
- 不影响前端的改动跳过本 skill，直接进阶段 03。

## 验证

- YAML 可读性：检查缩进、`paths`、`components.schemas`、`$ref` 是否一致。
- 契约一致性：字段名、类型、必填、枚举、path、method 与代码一致。
- TypeScript 基本合法：避免重复导出、缺失 import、裸 `any`。
- `git diff --check`。

## 禁止事项

- 不只改代码而漏掉 YAML 和前端契约。
- 不把某个客户端私有业务逻辑写进共享契约仓。
- 不把某个客户端的页面、store、composable 或平台运行时请求封装放入共享契约仓。
- 不在客户端重新声明已有共享契约中的请求、响应类型或枚举。
- 不使用绝对路径。
