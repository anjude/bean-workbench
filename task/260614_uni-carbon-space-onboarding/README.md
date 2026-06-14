# uni-carbon-space 接入

## 背景

工作台新增 `business-repo/uni-carbon-space` 业务仓，用于承载 carbon 品牌的 uni-app 前端需求。

## 目标

1. 将 `uni-carbon-space` 纳入 `business-repo/` 业务仓索引。
2. 让 `carbon` 相关需求可以明确路由到该仓，并叠加 `carbon-space-ui`、`carbon-icon-flow` 等品牌特化 skill。
3. 保持 `uni-*` 总控 skill 继续抽象为通用 uni 流程，不把 carbon 作为默认前提。

## 边界

- 本任务只更新工作台索引、路由和 skill 分层，不改业务仓页面实现。
- 品牌约束只放在 carbon 特化层，不回写到通用 `uni-dev-flow` 的默认逻辑。

## 记录

- `uni-dev-flow` 已从“默认 carbon 绑定”改成“通用 uni 抽象 + 可叠加品牌特化层”。
- `business-repo/uni-carbon-space` 已加入工作台子模块和业务仓索引。
