---
name: uni-api-flow
description: 当 uni-app 项目需求涉及新增或修改后端接口调用、TypeScript API 类型、可选 Repo 数据封装、request 参数转换或接口错误处理时使用。
metadata:
  short-description: uni-app API/可选Repo
---

# uni-app API / 可选 Repo 开发

本 skill 自包含。执行任务时以工作目录 `.` 为项目根目录，所有文件路径都使用相对目录。

## 当前模式

- API 文件：`src/apis/{domain}.ts`。
- API 统一导出：`src/apis/index.ts`。
- API 类型：`src/types/api/{domain}.ts`。
- API 类型统一导出：`src/types/api.ts`。
- 业务实体类型：`src/types/{domain}.ts`。
- Repo 文件：`src/repos/{domain}-repo.ts`，可选。复杂领域、跨页面复用、需要集中字段转换/错误封装时使用；轻量业务可由 `composable/store` 直接调用 API。
- 请求入口：`src/utils/request`。
- 响应格式：`ApiResponse<T>`，字段为 `errCode`、`data`、`msg`、`detail`。
- request 层会把请求参数转 snake_case，把响应转 camelCase。

## 开发流程

1. 从需求或后端接口定义提取 method、path、Req、Resp、业务实体。
2. 在 `src/types/api/{domain}.ts` 定义命名空间 `{Domain}Api`。
3. 在 `src/types/api.ts` 导出新命名空间。
4. 在 `src/apis/{domain}.ts` 用 `request.get/post/put/delete` 封装接口，返回 `Promise<ApiResponse<Resp>>`。
5. 在 `src/apis/index.ts` 导出 `{domain}Api` 和必要类型。
6. 判断是否需要 Repo：
   - 需要：接口多、转换复杂、跨页面复用、已有同域 repo、需要集中错误/日志封装。
   - 不需要：轻量接口、单页面/单 store 使用、转换简单，直接在 store/composable 使用 api 和 mapper。
7. 如果需要 Repo，在 `src/repos/{domain}-repo.ts` 封装业务方法：
   - 检查 `response.errCode !== 0` 并抛出 `response.msg`。
   - 做字段默认值、后端 string/number 兼容转换。
   - 使用 `logger.logRequestStart/Success/Error` 记录。
8. 如果不需要 Repo，把字段转换集中放在 `src/types/{domain}.ts` 或 store/composable 的 mapper/helper 中，不要散落到页面。
9. 如果接口驱动 store 或页面，继续使用 `uni-state-flow` 和 `uni-page-flow`。

## 约束

- API 层只做 HTTP 调用，不写页面逻辑和缓存逻辑。
- Repo 是可选层，不为轻量接口机械新增。
- Repo 层不直接操作页面 toast；只抛错或返回业务数据。
- 未使用 Repo 时，store/composable 仍要集中处理错误和字段转换，页面不直接写重复转换逻辑。
- GET 参数可作为第二参数传给 `request.get`，沿用现有调用风格。
- 字段名在 TS 类型中使用 camelCase，request 层负责 snake_case 转换。
- 类型注释要标明与后端 Req/Resp 对齐。
- 不绕过 `src/utils/request` 直接调用 `uni.request`。

## 验证

- `npm run type-check`
- 如果改动 request 底层：补充 H5 或目标小程序平台 build。
