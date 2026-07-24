# 项目长期记忆

## 公众号内容生产
- 用户运营一个微信公众号，内容方向偏**商业/科技/战略思考**（如"护城河"主题）。
- 上上一篇《科技不是护城河》阅读仅 4，用户怀疑标题差或被限流。结论：限流概率低（无敏感词），更可能是标题太抽象/书面化或送达问题。
- 用户偏好**高点击标题**，方向：痛点实操 / 案例拆解 / 反常识观点 / 数据清单四类原型。
- 已沉淀可复用 skill：`content-wechat-article-flow`（用户级 ~/.workbuddy/skills/），覆盖选题→写作→发布清单。
- 文章成稿存工作区根目录，命名如 `技术不是护城河续篇-痛点实操版.md`，文末固定附"发布防低阅读清单"。

## carbon 项目（uni-carbon-space，情侣空间小程序）
- 原"留白"模块显示名改为**"一隅"**（用户拍板），内部 key `play` 不变，英文眉标 "Quiet Corner" 保留。一隅是轻入口+认真内容的聚合容器（含 QQ农场/默契问答/小游戏/边界）。
- "边界"模块（个人使用说明书）采用**两份模型**：每人写自己的底线/喜欢/不喜欢，对方只读且可表态（懂了 / 还需磨合）。**已于 2026-07-11 落地前后端代码**（前端页 `pages/boundaries/index.vue` + `useBoundary` composable + `biz-play-tab.vue` 入口卡片；后端 5 接口 list/create/update/react/delete 走 `/api/so/carbon/boundary/*`，权限：作者可改删、对方可表态、不可对自己表态、非成员拒绝）。设计文档 `docs/feature/2026-07-11_边界功能方案.md`、功能设计 `docs/功能设计文档.md「7. 边界」`。
- **carbon 品牌调性硬约束（做所有模块都要守）**：定位=两人留痕/回看/确认关系形状的空间，**不是效率工具、不是冲突解决工具**；明确避免：已读未读、强提醒、催回复、任务式推进、过重积分。配色 token 仅暖色（米白 #f5f0ea + 琥珀 glow #f0a050），**无红/绿独立色**，关系状态用"点亮 vs 未点亮"而非红绿对比。文案克制、口语化、不审问；"边界"=空间的深水区，概念锚定"个人使用说明书"（"我是台需要说明书的设备"比"底线"更软、更不审问）；须柔软地做成交换卡片/慢问题。**文案红线：避免普世口号式**（如"每个人都需要一份说明书"把抽象概念当标语），用第一人称、具体的、克制的口语；自嘲可，喊口号不可。

## carbon 文档与 dev-flow 规范（易踩错，已踩过）
- **需求/设计文档必须放 `business-repo/uni-carbon-space/docs/feature/`**，命名 `YYYY-MM-DD_功能名方案.md`（如 `2026-05-24_约定功能方案.md`）。**不要放 `docs/` 根目录**，也**不要拆成「前端设计文档」「后端设计文档」两份**——现有范式是**一篇合并文档**同时含「前端改动点」和「后端改动点」，末尾带「测试方案」（功能/回归/兼容性三张表）。
- **dev-flow 两个都在项目级 `.agents/skills/`**：前端用 `uni-dev-flow`（方案确认模式要求输出：产品原型判断/状态矩阵/文件级方案/资产主权/品牌一致性/验证命令）；后端用 `backend-superone-dev-flow`（要求：业务理解+验收/受影响接口表字段/DDL/OpenAPI YAML/末尾强制「测试方案」三表）。两者都要在同一篇 feature doc 里体现。
- 兄弟模块设计文档是最好模板：`docs/feature/2026-05-24_约定功能方案.md`（关系模块）、`docs/feature/2026-05-30_刻度功能MVP方案.md`。后端分层按 `backend-superone`：表模型 `internal/model/carbon_*_tab.go`、DTO `internal/domain/carbon/carbon_dto`、UseCase `carbon_use_case.go`、Router `app/api_service/api_service.go`、API 契约 `frontend-contracts/openapi/carbon_api.yaml`（与 uni-carbon-space 同级，此前不存在，2026-07-11 首次创建该目录并补 boundary 契约）。
- **carbon_api.yaml 维护约定（用户拍板 2026-07-12）**：该文件是边界模块契约的空白起点（git 无历史、非覆盖原有），**只增量 append 新接口**——`paths:` 加 path、`components.schemas:` 加 schema，**不整份重写**。以后任何 carbon 新接口都在此文件上增量维护，使其作为碳基空间契约基线。
- **carbon_api.yaml 缩进坑（2026-07-12 踩过）**：`components:` 必须是**第 0 列**的顶层键（与 `paths:`/`info:` 同级），其下 `securitySchemes:`/`schemas:` 在 2 列、schema 名在 4 列。在 `paths:` 末尾追加新接口时，若以「上一条 path 的 `description: success` + `  components:`」做锚点插入，容易把 `components:` 误留在 **2 列**，使其被解析为 `paths` 的子节点、顶层丢失 `components` 键、所有 `$ref` 仍只是字符串不报错但结构非法。插入后务必确认 `components:` 在第 0 列；用 `yaml.safe_load` 跑一遍 `list(d.keys())` 含 `components` 即为合法。

## carbon 后端表迁移约定（已踩坑）
- carbon 业务表**不走** `scripts/migration/config.go` 的 `tablesToCreate`（那是 user/spot/trip 等非 carbon 表），而是**单独的 DDL 文件** `scripts/migration/sql/YYYYMMDD_*.sql` + 命令：`go run ./scripts/migration -action=exec-sql -sql-file=<path> -env=test`（bash 下不要用 README 里的 `--%`，那是 PowerShell 语法）。
- `verify-carbon` 校验的表清单是 `scripts/migration/exec_sql.go` 里的 `carbonTables` 切片——**新增 carbon 表后须手动把表名加进去**，否则 verify 不覆盖、连表是否建成功都看不到。2026-07-11 已为 `carbon_boundary_tab` 加上。
- test 库是共享远程库（脚本里写死 `8.155.38.83/weiyi_superone_db_test`），建表真实生效，属外部写操作；执行前须向用户确认（用户授权"继续"后才执行）。
- **后端 DTO 校验坑（已踩）**：gin 的 validator 对数值类型，把 `0` 当零值，`binding:"required"` 会拒绝 `0`。任何**含合法 0 值**的整数字段（如 reaction 取消态=0、status 默认态=0）不要用 `binding:"required"`；改用 `binding:"gte=0"` 或去掉 required，让业务层 `isValidXxx` 兜底校验。2026-07-12 边界 `ReactBoundaryReq.Reaction` 因此导致"取消表态"报 param error，已改为 `gte=0`。

## beannote 内容（豆小匠）
- 选题池在 `business-repo/beannote/02_topic_pool/`，每篇按「选题卡」格式（模板与阶段调性见用户级记忆 + content-beannote-creation-flow skill）。
- 投资认知内容方向（2026-07-22 用户强调整）：反对口号/说教式，要科学、平实、可操作。重点讲清"测量方法 + 背后的道理"，必要处给阈值但**不要公式堆砌**；老实交代指标局限（能证伪不能证明），不夸大。不要泛泛而谈的"劝人"文。
- 进行中主题「什么情况下我们认为一个人在股市能稳定挣钱」：已收敛出可操作科学版（备净值数据 → 基础四数 → 夏普/索提诺/卡玛+阈值 → 统计显著性 t≈夏普×√年数 → α/β 回归 → 尾部风险一票否决 → 分段持续性）。待用户确认是否落选题卡。
