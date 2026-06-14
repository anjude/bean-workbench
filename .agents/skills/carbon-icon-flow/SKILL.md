---
name: carbon-icon-flow
description: 当 carbon 相关需求涉及业务图标、空状态图形、功能入口小图标、SVG 资产生产、图标替换或图标组件接入时使用；它是 uni 通用 SVG 流程的 carbon 品牌特化版，要求图标符合碳基空间品牌调性，并能直接落到当前前端仓库。
metadata:
  short-description: carbon 品牌图标特化
---

# carbon 品牌图标特化

本 skill 不是通用 SVG 生产流程，而是 `uni-svg-flow` 的 carbon 品牌特化层。

## 触发前提

先按 `uni-svg-flow` 判断是否需要本地 SVG。确认需要后，再用本 skill 叠加 carbon 的语义和审美约束。

## 品牌基调

- 关键词：安静、私密、温度、微光、有机
- 默认气质：像夜里的小信号，而不是白天的大图标
- 默认风格：圆角线性 + 少量面填充 + 克制暖色

## 适合本 skill 的对象

- 空间
- 信号
- 火花
- 约定
- 刻度
- 邀请
- 此刻
- 反馈

## 约束

- 缩到 `18-28px` 仍可辨认
- 默认落到 `src/static/icons/carbon/`
- 优先复用 `src/components/cu-biz-icon.vue` 或等价薄封装
- 不做游戏化卡通，不做企业后台线框感
- 不把图标做成多色插画主视觉

## 验收

- 检查深浅主题可读性
- 检查真实页面中的情绪是否跑偏
- 至少运行一次 `npm run type-check`

## 与其他 skill 协作

- 通用 SVG 流程先参考 `uni-svg-flow`
- 页面和样式接入时，同时使用 `uni-component-style-flow`
- 品牌审美边界参考 `carbon-space-ui`
