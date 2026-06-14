---
name: uni-test-build-flow
description: 当 uni-app 项目需求完成后需要运行 type-check、H5/小程序 build、检查 pages.json、审查改动范围、定位构建失败或做交付验收时使用。
metadata:
  short-description: uni-app 验证构建
---

# uni-app 验证与构建

本 skill 自包含。执行任务时以工作目录 `.` 为项目根目录，所有文件路径都使用相对目录。

## 验证顺序

1. `npm run type-check`
2. 涉及页面或样式时运行 `npm run build:h5`
3. 涉及微信小程序能力时运行 `npm run build:mp-weixin`
4. 涉及其他平台时运行对应 `build:mp-*`
5. 检查 `git diff --check`
6. 审查改动是否只覆盖本需求

## 常见检查点

- `src/pages.json` 是否是合法 JSON，新增页面路径是否与文件一致。
- API 类型是否从 `src/types/api.ts` 导出。
- API 实现是否从 `src/apis/index.ts` 导出。
- 页面是否直接调用 API；如果是，应下沉到 composable/store/repo。
- Store 是否维护本地缓存和 force refresh。
- Composable 是否统一处理错误和 toast。
- 样式文件是否在 `src/styles/index.css` 注册。
- 是否误改无关页面、无关格式化或依赖版本。

## 构建失败处理

- TypeScript 报错：优先修类型契约，不用 `any` 绕过，除非第三方平台类型缺失且已有同类写法。
- 页面路径错误：同步修 `src/pages.json` 和实际文件路径。
- 样式缺失：确认 `src/styles/index.css` import。
- 平台 API 报错：使用 uni-app 条件编译，保留非目标平台降级。
- 依赖缺失：先检查 `package.json` 是否已有可复用库，不主动新增依赖。

## 最终验收输出

- 已运行命令和结果。
- 未运行命令及原因。
- 页面入口和手工验收步骤。
- 已知风险或需要后端配合的接口。
