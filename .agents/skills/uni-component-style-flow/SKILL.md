---
name: uni-component-style-flow
description: 当 uni-app 项目需求涉及 Vue 组件、业务组件、cu-* 基础组件、页面样式、ITCSS 样式、视觉一致性、多端 UI 兼容或页面审美执行时使用；重点保证页面不是零散功能拼接，而是结构、密度、CTA 和状态都统一的产品界面。
metadata:
  short-description: uni-app 审美执行与组件样式
---

# uni-app 审美执行与组件样式

本 skill 负责把产品原型和状态矩阵落成可信的界面，不只是“把样式补齐”。

## 组件约定

- 通用基础组件：`src/components/cu-*.vue`
- 业务组件：`src/components/business/*.vue`
- 页面样式：`src/styles/06-pages/p-{page}.css`
- 组件样式：`src/styles/05-components/cu-{name}.css`
- 样式入口：`src/styles/index.css`
- 设计变量：`src/styles/01-settings/variables.css`

## 默认审美检查

开始改样式前，先判断：

1. 页面视觉重心在哪里。
2. 主 CTA 和次 CTA 是否清楚分层。
3. 信息密度是否过满。
4. 空状态、加载态、错误态是否和正文态属于同一产品。
5. 页面是否像一个稳定母版，而不是若干区块硬拼。

## 开发流程

1. 先判断是页面局部样式、可复用组件样式还是业务组件。
2. 先对照产品原型：这个页面是控制台、时间流、空间、配置页还是沉浸详情。
3. 再对照状态矩阵：至少确认空、加载、失败、有数据四种视觉骨架。
4. 页面样式新增 `src/styles/06-pages/p-{feature}.css` 并注册到 `src/styles/index.css`。
5. 可复用组件新增 `src/components/cu-{name}.vue` 和必要的组件样式文件。
6. 业务组件新增到 `src/components/business`，命名尽量与业务对象一致。
7. 优先复用现有变量、`cu-*` 组件、`uni-icons` 和项目内资产。

## 约束

- 不把大量 scoped style 写进页面，优先放 ITCSS 文件。
- 不新增孤立的一次性 UI 组件，除非页面复杂度足以支撑。
- 不为了“更像设计稿”牺牲产品一致性。
- 不使用负 letter-spacing 或随 viewport 缩放字体。
- 不做一整页单色系视觉，颜色优先来自 CSS variables。
- 文案不能溢出按钮、卡片和窄屏容器。
- 用户给出精确结构时，按结构映射 DOM，不做近似布局。
- 先满足结构和交互，再处理阴影、透明度和层次感。
- 浅色/深色模式问题优先回到令牌层解决。

## 反拼凑检查

出现以下任一情况，必须回退重排：

- 同页有多个互相竞争的视觉中心
- CTA 太多，用户不知道先点哪个
- 空状态和正文态像两个产品
- 页面信息块都成立，但合在一起没有主节奏
- 为了好看引入大量额外装饰，反而削弱可用性

## 验证

- `npm run type-check`
- 需要视觉验收时运行 `npm run dev:h5` 或目标平台 build
- 检查空、加载、错误、长文本、窄屏和深浅主题表现
