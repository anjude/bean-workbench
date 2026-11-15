# 鹅懂个啥大转盘配置化 · 交接

- 任务目录：`task/dev-flow/QB91_gknow-wheel-config/`
- 时间：2026-11-10 13:58
- 来源会话 ID：`01a1c3d7-7d11-7f82-b89f-9c21856d20d9`
- 状态：待确认
- 上一份：`handoff/261110-1325_test部署与微信验收.md`

## 这次到哪了

目标是让大转盘由后端维护，并让预计超过 500 项的「周末去哪逛」先筛选再查询；代码、test 表结构、首批数据和本地真实接口回归已完成，当前只剩 test 部署与微信端验收。

## 已完成

- wheel 增加 `option_mode`，增加筛选条件分页查询并同步契约 —— `business-repo/backend-superone/internal/domain/wheel/`、`business-repo/frontend-contracts/openapi/gknow_wheel_api.yaml`
- `where-to-go` 使用 `filter_first`，默认筛选深圳，城市单选、其他维度多选 —— `task/dev-flow/QB91_gknow-wheel-config/seed/first-batch.json`
- 小程序进入筛选优先 wheel 时直接展示筛选行，并按条件重建候选 —— `business-repo/uni-gknow/src/pages/tools/wheel/index.vue`
- test DDL 与 HTTP + DB 回归 —— `business-repo/backend-superone/scripts/migration/sql/20261110_add_gknow_wheel_option_mode.sql`、`autotest/wheel_test.go`

## 过程记录

- 需求与现状：见 `process/01-需求理解与现状盘点.md`
- 功能与系统设计：见 `process/02-功能与系统设计.md`
- 开发与验证：见 `process/03-开发与迭代.md` 的第 2、3 轮；筛选优先查询已通过本地真实服务验证。

## 未完成 / 下一步

1. 取得提交推送授权后，分别提交 `frontend-contracts`、更新 `uni-gknow` 的契约子仓指针、提交 `backend-superone` 与任务文档；后端按 `dev → test` 发布，做完的判断标准是 test 服务新路由可访问。
2. 部署后在 test 地址核验列表返回 `option_mode=1`、`option_total=56`；`where-to-go` 详情 options 为 0；按深圳查询返回 56 项，做完的判断标准是与 `autotest/wheel_test.go` 一致。
3. 在微信开发者工具验证默认深圳、城市单选切换、场景多选、发起查询后重建候选、本地操作日志和复制隔离，做完的判断标准是方案中的微信端验收项通过并回填落地记录。

## 关键决策与原因

- 超过 500 项时采用 `filter_first`：因为详情全量返回会让小程序请求和本地筛选变得不稳定；保留 `direct` 模式给小规模 wheel。
- 默认城市放 `content_json.default_filters`：因为后续定位只需覆盖同一筛选值，不把北京或深圳写死在前端。
- 城市和区县单选、标签多选：因为切换城市应替换地点范围，而不是把多个城市叠加进同一轮。

## 卡点与待确认

- 需要用户明确授权提交和推送；当前所有改动仍在工作区。
- 北京及其他城市内容尚未录入，当前可验证数据只有深圳 56 项。

## 环境与坑

- `WHEEL_API_BASE_URL=http://localhost:18080` 可连接本机 test 服务；`where-to-go` 当前版本为 5。
- `tags_json` 条件查询使用 MySQL `JSON_CONTAINS`，城市当前单一值下耗时约 200–300ms；数据量到数万项或需要距离排序时应改可索引地点/标签表。
- 后端全仓 `make test` 仍有一个既有 MCP 工具数量断言失败；wheel 受影响测试与 vet 通过。

## 关联产物

| 产物 | 路径 |
| --- | --- |
| 方案文档 | `task/dev-flow/QB91_gknow-wheel-config/plans/大转盘远程配置方案.md` |
| 首批配置 | `task/dev-flow/QB91_gknow-wheel-config/seed/first-batch.json` |
| 改动 | 三个业务仓与任务目录当前工作区 diff，尚未 commit |

## 下次建议调用的 skill

- `wb-router`：恢复任务归属与业务仓上下文
- `dev-flow`：继续 test 部署、微信端验收和收口
- `dev-flow-tools-repo`：按仓库规则提交、推进 test 与核对部署
