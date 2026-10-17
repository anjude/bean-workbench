---
name: dev-flow-0203-page-flow
description: 当 uni-app 项目需求涉及新增或修改页面、pages.json 路由、生命周期、页面跳转、下拉刷新、Vue 组件与业务组件、cu-* 基础组件、页面样式、ITCSS 样式、视觉一致性、多端 UI 兼容或页面审美执行时使用。
metadata:
  short-description: uni-app 页面与组件样式
---

# uni-app 页面与组件样式

阶段 02 前端开发，执行顺序第 3 步。阶段编排见 `dev-flow-0000-plan-flow`，项目上下文见 `dev-flow-tools-repo`。

本 skill 把产品原型和状态矩阵落成可信的界面，不只是「把样式补齐」。执行任务时以工作目录 `.` 为项目根目录，路径用相对目录。

## 当前模式

- 页面配置：`src/pages.json`
- 页面文件：`src/pages/{feature}/index.vue`，编辑/详情页为 `edit/index.vue`、`detail/index.vue`
- 页面使用 `<script setup lang="ts">`，uni 生命周期从 `@dcloudio/uni-app` 引入
- 页面容器优先 `<cu-page>`、`o-page-container`、`cu-page-container` 和 `p-{page}` 命名空间类
- 碳基空间约定：除 `src/pages/profile/index.vue` 外页面必须由 `<cu-page>` 包裹；首页用 `<cu-page :reverse="true">`，其他页面不传 `reverse`
- 空状态、加载状态优先复用 `cu-empty-state`、`cu-loading-state`
- 通用组件 `src/components/cu-*.vue`，业务组件 `src/components/business/*.vue`
- 页面样式 `src/styles/06-pages/p-{page}.css`，组件样式 `src/styles/05-components/cu-{name}.css`
- 样式入口 `src/styles/index.css`，设计变量 `src/styles/01-settings/variables.css`

涉及常见业务页面或对象操作时，先读 [`references/ui-ux-handbook.md`](references/ui-ux-handbook.md)，按任务语义选择模式；具体产品规格和品牌规范优先于通用建议。

## 一、新增页面

1. 确定页面路径、标题、导航样式、是否启用下拉刷新。
2. 在 `src/pages.json` 添加页面配置。
3. 新建 `src/pages/{feature}/index.vue` 或对应子页面。
4. 页面有业务数据时，先设计 `dev-flow-0202-data-flow` 的接口、store、composable，再让页面消费。
5. 页面只保留模板、事件转发、生命周期绑定和少量展示状态。
6. 页面样式放入 `src/styles/06-pages/p-{feature}.css`，并在 `src/styles/index.css` 引入。
7. 所有跳转使用相对应用路径，例如 `/pages/{feature}/detail/index?id=${id}`。

## 二、修改页面

1. 先读页面对应 composable、store、api；项目已有同域 repo 再读 repo。
2. 判断改动应放在页面、composable、store、api，还是可选 repo。
3. 下拉刷新必须在 `finally` 中调用 `uni.stopPullDownRefresh()`。
4. 跳转失败、异步失败使用现有错误处理或 toast 习惯。
5. 修改列表渲染时保留稳定 key，必要时用 `renderKey` 触发组件重渲染。

## 三、组件与样式

1. 先判断是页面局部样式、可复用组件样式还是业务组件。
2. 对照产品原型：这是控制台、时间流、空间、配置页还是沉浸详情。
3. 对照状态矩阵：至少确认空、加载、失败、有数据四种视觉骨架。
4. 页面样式新增 `src/styles/06-pages/p-{feature}.css` 并注册到 `src/styles/index.css`。
5. 可复用组件新增 `src/components/cu-{name}.vue` 和必要样式文件；业务组件加到 `src/components/business`，命名与业务对象一致。
6. 优先复用现有变量、`cu-*` 组件、`uni-icons` 和项目内资产。

### 默认审美检查

改样式前先判断：页面视觉重心在哪、主次 CTA 是否分层、信息密度是否过满、空/加载/错误态是否和正文态属于同一产品、页面是否像一个稳定母版。

### 平台设计原则

吸收 Material Design 与 Apple Human Interface Guidelines 的通用设计判断，不把两套平台视觉语言拼成一套：

1. **先定任务与层级**：明确用户来到页面要完成什么，让关键内容和主操作一眼可见；次要操作降级或延后，不靠堆按钮表达功能完整。
2. **让内容关系可见**：相关内容按语义分组，使用留白、对齐、分隔或容器表达归属。列表、网格、卡片、横滑货架按内容关系和浏览任务选型；不要因为当前项目数量少就先定死只适合少量项目的布局。横滑内容要露出后续项或明确提示可继续浏览。
3. **优先熟悉、稳定的交互模式**：导航、选择、确认、反馈等优先沿用用户熟悉的模式；自创交互必须解决明确的问题，并提供可理解的提示、反馈和退出/恢复路径。
4. **给重要信息和操作留空间**：避免为了塞进一屏而压缩字号、点击区域或信息层级。适配目标设备的屏幕、系统安全区、字体放大和文案长度；信息确实较多时用清晰滚动或渐进展示。
5. **状态和可访问性不只靠颜色**：交互控件有明确的可用、按下、禁用等反馈；空、加载、失败、成功和恢复方式完整。颜色之外还要有文案、形状、图标或位置线索，保证对比度、文字可读性和触控可用性。
6. **用真实页面迭代**：实现后在目标平台和代表性屏幕尺寸查看页面截图，检查视觉层级、分组、内容密度、裁切和实际触控路径。若页面看起来拥挤、分区关系不清、项目之间像从属关系或主操作不突出，应回到布局与信息架构重做，不以微调颜色、圆角或阴影代替解决结构问题。

Material 3 和 Apple HIG 是设计判断与平台适配的参考，不是要求所有端长得一样。按目标端和项目既有设计系统选用组件、导航、图标、动效和视觉令牌；不要默认混用 Material 专属组件与 Apple 专属视觉元素。项目产品规格与品牌规范优先，平台惯例用于让实现更自然、可理解。

### 反拼凑检查

页面结构、审美、状态、资产必须互相匹配。出现以下任一情况必须回退重排：

- 同页有多个互相竞争的视觉中心
- CTA 太多，用户不知道先点哪个
- 空状态和正文态像两个产品
- 页面信息块都成立，但合在一起没有主节奏
- 为了好看引入大量额外装饰，反而削弱可用性

## 约束

- 不把 API 调用直接写在页面里；不把复杂筛选、格式化、订阅、确认弹窗流程堆在 `.vue` 文件。
- 不把大量 scoped style 写进页面，优先放 ITCSS 文件。
- 用户明确给出文案、布局或交互规格时按规格实现，不把额外入口、额外确认、额外状态当成「优化」自动加入。
- 不新增孤立的一次性 UI 组件；不使用负 letter-spacing 或随 viewport 缩放字体。
- 不做一整页单色系视觉，颜色优先来自 CSS variables；文案不能溢出按钮、卡片和窄屏容器。
- 先满足结构和交互，再处理阴影、透明度和层次感；深浅色模式问题回到令牌层解决。
- 页面层不直接处理平台运行时差异，不直接调用平台私有 API；优先使用项目统一适配接口。只有产品 UI/UX/交互确需因平台不同而变化时，才在呈现层做平台区分。

## 验证

- `npm run type-check`
- 新增页面后检查 `src/pages.json` JSON 格式
- 页面结构、布局或样式有变化时，在目标平台 build 后做截图视觉验收；至少覆盖一个代表性屏幕尺寸，核对信息层级、内容分组、主操作、裁切和安全区
- 检查空、加载、错误、长文本、窄屏，以及浅色、深色、跟随系统三种主题模式

## 设计参考

- [Material Design 3 Foundations](https://m3.material.io/foundations/)：无障碍、内容设计、交互状态与布局基础。
- [Apple Human Interface Guidelines — Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles/)：熟悉性、一致性、清晰反馈、适应性、层级与迭代。
- [Apple Human Interface Guidelines — Layout](https://developer.apple.com/design/human-interface-guidelines/layout)：内容分组、视觉层级、留白、渐进展示与布局适配。
