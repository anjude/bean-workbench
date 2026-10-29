# 朋友对照玩法 · 预览与验证

这里使用真实Vue页面和业务逻辑，登录、Redis与微信原生能力由本机模拟，不会请求真实后端或修改线上数据。

## 检查

在工作台根目录运行：

```bash
node task/dev-flow/261009_gknow-daily/preview/goose-mirror/verify.cjs
```

脚本使用业务仓已有 TypeScript 与 Vue，模拟独立用户的本机存储和共享 Redis，检查多人独立提交、累计图鉴、题库版本、故障恢复和 TTL；不替代真实网络与微信端联调。

## 浏览器预览

```bash
node task/dev-flow/261009_gknow-daily/preview/goose-mirror/server.mjs
```

入口为 `http://127.0.0.1:5209/?user=A`，模拟Redis仅在预览服务器进程内存在。生成邀请后，通过浏览器验证脚本读取真实分享路径并以B身份作答。

```bash
NODE_PATH=/Users/bean/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules node task/dev-flow/261009_gknow-daily/preview/goose-mirror/verify_browser.cjs
```

运行依赖本机Chrome与已有Playwright。代表截图在 `ui/`，覆盖390宽浅色入口/题目/邀请首页/记录/结果、320宽深色题目/记录/结果。预览将rpx转换为浏览器CSS，导航和微信组件为模拟；实际小程序渲染以微信端为准。

## 微信端验收

1. 打开 `business-repo/uni-gknow/dist/build/mp-weixin`，进入正式入口模式；趣味问答分类选择新玩法。
2. A完成六题并发到群；B、C分别打开并填写，两人都能提交并看到匹配题数。
3. A回到小程序，确认图鉴显示2人；点击此图鉴直接进入玩法首页，进入“填写记录”能看到B/C昵称、填写时间和各自六题对照。
4. A刷新或重启后人数不增加；发起人重填后旧分享仍可填写，已收录历史仍在；同一朋友参与新一轮增加记录、人数去重。
5. 检查断网重试、草稿恢复、旧链接仍可填写和原生转发落点。

每个发起人的玩法 key 保存最新自评和朋友对照快照；领取后不删除远端数据，邀请按创建起七天到期，本机历史不随 Redis 到期删除。前端读改写未引入后端锁或并发保证。

未执行上传、发布或线上多账号测试。

## 最新规则

每个发起人的openid对应一个玩法key，value包含最新自评和每位朋友填写时的双方答案快照；B只看匹配题数，不保存本次记录。A本机保存历史；Redis按邀请创建起七天到期。多人/重复填写及浏览器模拟通过，真实微信多账号与Redis待验收。此前组合答卷key与删除规则已废止。
