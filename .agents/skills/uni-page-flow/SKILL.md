---
name: uni-page-flow
description: 当 uni-app 项目需求涉及新增或修改页面、pages.json 路由、生命周期、页面跳转、下拉刷新、空/加载/错误状态或页面验收时使用。
metadata:
  short-description: uni-app 页面开发
---

# uni-app 页面开发

本 skill 自包含。执行任务时以工作目录 `.` 为项目根目录，所有文件路径都使用相对目录。

## 当前模式

- 页面配置在 `src/pages.json`。
- 页面文件通常是 `src/pages/{feature}/index.vue`，编辑/详情页为 `src/pages/{feature}/edit/index.vue`、`src/pages/{feature}/detail/index.vue`。
- 页面使用 `<script setup lang="ts">`。
- uni 生命周期从 `@dcloudio/uni-app` 引入，例如 `onLoad`、`onShow`、`onPullDownRefresh`。
- 页面业务逻辑优先从 `src/composables/use*.ts` 获取。
- 页面容器优先使用 `<cu-page>`、`o-page-container`、`cu-page-container` 和 `p-{page}` 命名空间类。
- 碳基空间页面约定：除 `src/pages/profile/index.vue` 外，页面必须由 `<cu-page>` 包裹；首页使用 `<cu-page :reverse="true">`，其他页面使用普通 `<cu-page>` 不传 `reverse`。
- 空状态、加载状态优先复用 `cu-empty-state`、`cu-loading-state`。

## 新增页面流程

1. 确定页面路径、标题、导航样式、是否启用下拉刷新。
2. 在 `src/pages.json` 添加页面配置。
3. 新建 `src/pages/{feature}/index.vue` 或对应子页面。
4. 如果页面有业务数据，先设计 composable 和 store，再让页面消费。
5. 页面只保留模板、事件转发、生命周期绑定和少量展示状态。
6. 页面样式放入 `src/styles/06-pages/p-{feature}.css`，并在 `src/styles/index.css` 引入。
7. 所有跳转使用相对应用路径，例如 `/pages/{feature}/detail/index?id=${id}`。

## 修改页面流程

1. 先读页面对应 composable、store、api；如果项目已有同域 repo 再读取 repo。
2. 判断改动应放在页面、composable、store、api，还是可选 repo。
3. 下拉刷新必须在 `finally` 中调用 `uni.stopPullDownRefresh()`。
4. 跳转失败、异步失败要使用现有错误处理或 toast 习惯。
5. 修改列表渲染时保留稳定 key，必要时使用 `renderKey` 触发组件重渲染。

## 约束

- 不把 API 调用直接写在页面里。
- 不把复杂筛选、格式化、订阅、确认弹窗流程堆在 `.vue` 文件中。
- 页面文案使用中文时保持现有风格，专业词可保留英文。
- 小程序多端兼容场景使用 uni-app 条件编译，不写平台私有全局 API，除非已有同类代码。

## 验证

- `npm run type-check`
- 新增页面后检查 `src/pages.json` JSON 格式。
- 需要真实渲染时运行目标平台 dev/build。
