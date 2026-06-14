# 任务登记

## 热任务

| 任务 | 目录 | 资源范围 | 状态 |
| --- | --- | --- | --- |
| 工作台初始化 | `task/260614_workbench-init/` | 根目录、`docs/`、`.agents/skills/`、`knowledge-base/`、`script/` | 进行中 |
| Superone 多仓规则完善 | `task/260614_superone-workbench-migration/` | `business-repo/` 路由、Superone skills、协议仓路径、知识库索引 | 进行中 |
| uni-carbon-space 接入 | `task/260614_uni-carbon-space-onboarding/` | `business-repo/uni-carbon-space`、uni 路由、品牌特化 skill、知识库索引 | 进行中 |

## 冷任务

| 任务 | 目录 | 资源范围 | 状态 |
| --- | --- | --- | --- |
| 暂无 | - | - | - |

## 路由提示

- 提到 `superone`：优先查看 `business-repo/` 下的相关业务仓，再结合具体需求选择后端、前端或协议仓。
- 提到 `uni-carbon-space`、`carbon`：优先路由到 `business-repo/uni-carbon-space`，并叠加 `carbon-space-ui`、`carbon-icon-flow` 等品牌特化 skill。
- 提到 `frontend-contracts`、`OpenAPI`、`契约`：优先路由到工作台下的 `business-repo/frontend-contracts`。
- 提到 `便签`：先查热任务和知识库；如果没有明确业务仓，不要直接改业务仓，先定位需求归属。
- 提到 `工作台`、`skill`、`知识库`、`自进化`：默认只改工作台根级目录。
