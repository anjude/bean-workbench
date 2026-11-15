# QB81 鹅懂个啥日常

## 目标

集中跟进「鹅懂个啥」小程序的日常反馈、体验优化、缺陷修复和维护。

## 范围

- 业务仓：[uni-gknow](../../../business-repo/uni-gknow/README.md)；产品定位、角色和品牌资料见[产品文档](../../../business-repo/uni-gknow/docs/README.md)。
- 小型连续改动在本任务推进，按需使用 `dev-flow`。有独立目标和验收标准的事项进入专项任务，方案和过程留在各自目录。

## 当前状态与待办

- 2026-11-08：已实现并推送功能埋点首版。test 库已建表，本地接口已连接真实 test MySQL 验证；共享契约已发布，小程序子模块已固定到新契约。待将后端 `dev` 推进到 `test` 并部署，再用微信体验版对账。
- 2026-11-09：5 个理财副本 test 草稿的目录封面已统一为外层「理财副本」Logo，版本 3，仍未发布；微信体验版显示待确认。
- 2026-11-09：性格盲盒列表中的 3 个 test 草稿 Logo 已改为外层盲盒图标；配置版本分别为 stock-methods v7、goose-bti v6、finance-personality v8，仍未发布。测试开始页和结果海报共用该 Logo。
- 2026-11-09：探索页四个分类内层列表的卡片 Logo 已增加四周留白，底色能从四边露出；类型检查和微信小程序构建通过。微信开发者工具当前打开的是 `crazy-goose`，尚未查看本页截图。
- 2026-11-09：副本结束页已增加“分享给好友”按钮；复用已有小程序分享回调，可分享当前副本并保留来源统计。类型检查和微信小程序构建通过。
- 2026-11-09：test 中 3 个测试与 8 个副本均已发布；按用户确认在 live 创建副本表，并将 3 个测试与 8 个副本同步至 live，核对数量、发布状态、版本及内容。详见[发布与 live 同步记录](process/03-test发布与live同步.md)。
- 既有方案、过程、交接和未结事项见[原日常开发记录](../../dev-flow/QA92_gknow-daily/README.md)。

## 方案

- 测试、副本内容与素材维护见[鹅懂个啥内容维护](../QBF1_gknow-content-maintenance/README.md)，项目内备份入口为 [内容备份](../../../business-repo/uni-gknow/docs/content/README.md)。
- [功能埋点](plans/功能埋点.md)：gknow 的事件口径、共用上报接口和事件表，以及按项目和业务查询与验收的方式。

## 关联专项

- [副本配置化](../../dev-flow/QB82_gknow-story-config/README.md)：后端管理发布与版本，副本 JSON 由前端定义并由后端不透明存取。
- [可配置测试](../../dev-flow/QB84_gknow-configurable-assessment/README.md)
- [恋爱副本](../../dev-flow/QAV1_gknow-love-copy/README.md)与[公司副本](../../dev-flow/QB11_gknow-company-copy/README.md)
- [疯狂大鹅微信小游戏](../../dev-flow/QB12_gknow-minigame/README.md)
- [小红书图片工坊](../../dev-flow/QAA1_gknow-content-studio/README.md)与[产品宣传样片](../../dev-flow/QAF1_gknow-product-video/README.md)
