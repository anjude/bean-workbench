---
name: backend-frontend-contract-flow
description: 当后端接口、DTO、响应结构、枚举、字段语义或错误码发生可能影响前端的变动时使用；同步更新 OpenAPI YAML，并生成可复制到多个前端项目的 TypeScript 接口、结构体、枚举和 API 契约文件。
metadata:
  short-description: 后端生成前端契约
---

# 后端前端契约生成

本 skill 面向工作台多仓结构。执行任务时优先以工作台根目录为协调目录；如果当前工作目录在 `business-repo/backend-superone` 内，必须先识别工作台根目录，再把契约输出到工作台的协议仓。

## 目标

后端开发完成接口或枚举变更时，同时生成前端可直接使用的契约文件。前端开发只需要复制契约目录中的对应文件到前端项目，即可按同一套接口、结构体、枚举进行开发，减少口头对接。

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

### 前端契约目录

统一放在：

```text
business-repo/frontend-contracts/
  openapi/
  src/apis/
  src/types/api/
  src/types/models/
  src/types/enums/
```

如果 `business-repo/frontend-contracts` 或其中子目录不存在，必须先创建目录，再生成文件；不要因为目录缺失而跳过契约输出。目录创建应保持最小结构，只创建本次需要的子目录。

文件设计为可复制到前端项目。所有 TypeScript 文件使用相对项目内常见别名 `@/` 时，必须确保目标前端已有相同别名；否则优先生成无运行依赖的类型、枚举、常量文件。

## 文件职责

- `openapi/{domain}_api.yaml`：契约源文件，供前端或工具读取。
- `src/types/api/{domain}.ts`：请求/响应类型，命名空间 `{Domain}Api`。
- `src/types/models/{domain}.ts`：业务实体结构体。
- `src/types/enums/{domain}.ts`：枚举值、状态值、类型常量。
- `src/apis/{domain}.ts`：可选；当目标前端使用同类 request 封装时，生成 API wrapper。

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

### API wrapper

如果生成 `src/apis/{domain}.ts`：

- 只封装 HTTP 调用，不写业务缓存和页面逻辑。
- 方法名与 OpenAPI `operationId` 保持一致。
- 返回 `Promise<ApiResponse<Resp>>` 或目标前端已有统一响应类型。
- path 必须与后端路由一致，例如 `/api/so/{domain}/list`。

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
4. 生成或更新 TypeScript 契约文件。
5. 如果本次改动影响多个前端 domain，按 domain 拆文件，不写一个超大文件。
6. 最终输出“前端复制清单”，列明从 `business-repo/frontend-contracts` 复制哪些文件到前端哪些相对目录。

## 自动开发集成

在后端 auto 开发流程中：

- API/DTO/枚举改动完成后立即执行本 skill。
- 测试前先保证 `business-repo/frontend-contracts/openapi` 和契约文件已同步。
- 最终结果必须说明：OpenAPI 是否已更新、前端契约文件是否已生成、前端需要复制哪些文件。

## 验证

- YAML 可读性：检查缩进、`paths`、`components.schemas`、`$ref` 是否一致。
- 契约一致性：字段名、类型、必填、枚举、path、method 与代码一致。
- TypeScript 基本合法：避免重复导出、缺失 import、裸 `any`。
- `git diff --check`。

## 禁止事项

- 不只改代码而漏掉 YAML 和前端契约。
- 不把前端项目私有业务逻辑写进公共契约目录。
- 不把某一个前端项目的页面、store、composable 放入公共契约目录。
- 不使用绝对路径。
