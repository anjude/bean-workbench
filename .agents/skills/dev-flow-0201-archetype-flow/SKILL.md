---
name: dev-flow-0201-archetype-flow
description: 当 uni-app 或产品需求需要先判断页面属于哪种产品原型、确定信息架构与 CTA 节奏，并在实现前补齐页面状态、交互状态、数据状态和失败回退时使用。
metadata:
  short-description: 产品原型与状态矩阵
---

# 产品原型与状态矩阵

阶段 02 前端开发，执行顺序第 1 步。阶段编排见 `dev-flow-0000-plan-flow`，项目上下文见 `dev-flow-tools-repo`。

编码前的前置设计，两件事连着做：先确认「这是什么产品」，再确认「它有哪些状态」。执行任务时以工作目录 `.` 为项目根目录，路径用相对目录。

## 硬门槛

- 先出产品，再出页面；先补齐状态，再写 happy path。
- 只有 happy path 的页面视为未完成，状态矩阵没过不进入 `dev-flow-0203-page-flow`。
- 原型和状态的结论要能被页面、样式、数据层直接消费，不另起一套说法。

## 一、原型判断

### 默认原型

- dashboard / control center
- feed / timeline
- space / relationship
- detail / immersive
- config / settings
- onboarding / activation

### 判断规则

- 核心是概览、切换、概括和入口 → `dashboard`
- 核心是连续内容流和回看 → `feed`
- 核心是关系、共创、互动和双人空间 → `space`
- 核心是单对象深看和沉浸编辑 → `detail`
- 核心是偏好、管理、系统项 → `config`
- 核心是第一次理解和第一次行动 → `onboarding`

### 输出

1. 原型判断
2. 为什么是这个原型
3. 页面结构骨架
4. 主 CTA / 次 CTA
5. 不该出现的反模式

### 反模式

- 一个页面同时想当 dashboard、detail 和 feed
- CTA 没有主次
- 页面结构只按接口字段堆砌
- 看得出有模块，但看不出产品意图

## 二、状态矩阵

### 默认检查项

首次进入 / 有本地缓存 / 服务端空数据 / 服务端有数据 / 加载中 / 刷新中 / 提交中 / 失败 / 部分可用 / 周期切换 / 权限或资格不足。

### 输出字段

按表格或列表输出：场景、触发条件、UI 表现、数据来源、用户可做的动作、失败或下一步回退。

### 使用规则

1. 先列最小矩阵，不追求无限展开。
2. 某个状态不会出现时，明确说明为什么。
3. 多个状态共享同一 UI 骨架可以合并，但不能省略。
4. 只做 happy path 视为未完成。

### 特别关注

- 本地缓存和服务端数据切换时的体验
- 提交后是否有明确反馈
- 失败时是否还能继续下一步
- 周期型功能跨天、跨周后的显示

## 与其他 skill 协作

- 原型与状态确认后，进入 `dev-flow-0202-data-flow`（接口类型、store、composable）
- 落页面和样式交给 `dev-flow-0203-page-flow`
- 需要图标和空状态图时走 `dev-flow-0204-asset-flow`
- 命中 carbon 品牌项目时全程叠加 `dev-flow-0205-space-ui`
