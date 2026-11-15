# 财务自由主题测试 live 发布

- 日期：2026-11-11
- 关联 beannote 主题：`task/beannote/topics/QAO2_你需要多少钱才能财富自由/`
- 测试 key：`financial-freedom-tradeoffs`
- 标题：为了财务自由，你把什么留到以后？
- 内容文件：`business-repo/uni-gknow/docs/content/assessments/financial-freedom-tradeoffs/content/assessment.json`

## 内容

测试围绕追求财务自由时的生活取舍设计 8 个情境题，结果分为「不想把生活只留给以后」「先给生活留出余地」「相信能走得久的节奏」「想尽快拿回选择权」四种倾向。结果用于自我观察，不评价对错。Logo 复用小程序已有的性格盲盒素材，没有新增图片。

## 发布与回读

用户授权发布到 live。使用 `tools-backend-auth` 按 backend-superone live 配置即时签发短时 JWT，通过管理 API 创建，再更新发布状态。首次创建为 version 1；发布更新后 version 2、`test_status=1`。

随后通过 live detail 和 assessment list 两个 API 回读：业务码均为 0，详情与已发布列表均可见该 key，题数为 8，结果 ID 为 `present`、`buffer`、`steady`、`accelerate`。未更新或覆盖其他测试，未部署小程序代码。

临时 OpenID 和请求文件已在调用后删除；凭证和 JWT 未保存到仓库或过程记录。
