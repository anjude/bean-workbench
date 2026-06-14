---
name: uni-product-archetype-flow
description: 当 uni-app 或产品需求需要先判断页面/功能属于哪种产品原型，再决定信息架构、CTA 节奏和页面骨架时使用；目标是避免一上来拼页面，先确认这是一个什么产品。
metadata:
  short-description: 产品原型判断
---

# 产品原型判断

本 skill 用于在编码前先判断产品原型。目标不是立刻产出页面，而是确认“这是什么产品骨架”。

## 默认原型

- dashboard / control center
- feed / timeline
- space / relationship
- detail / immersive
- config / settings
- onboarding / activation

## 输出格式

至少输出：

1. 原型判断
2. 为什么是这个原型
3. 页面结构骨架
4. 主 CTA / 次 CTA
5. 不该出现的反模式

## 判断规则

- 如果页面核心是概览、切换、概括和入口，优先 `dashboard`
- 如果核心是连续内容流和回看，优先 `feed`
- 如果核心是关系、共创、互动和双人空间，优先 `space`
- 如果核心是单对象深看和沉浸编辑，优先 `detail`
- 如果核心是偏好、管理、系统项，优先 `config`
- 如果核心是第一次理解和第一次行动，优先 `onboarding`

## 反模式

- 一个页面同时想当 dashboard、detail 和 feed
- CTA 没有主次
- 页面结构只按接口字段堆砌
- 看得出有模块，但看不出产品意图

## 与其他 skill 协作

- 原型判断后，再调用 `uni-state-matrix-flow`
- 落页面时交给 `uni-dev-flow` 和 `uni-component-style-flow`
