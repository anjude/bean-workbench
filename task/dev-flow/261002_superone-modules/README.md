# uni-superone 功能模块开发（首页 + n 模块切换 + 底部操作栏）

> 阶段：00 方案设计（dev-flow-0000-plan-flow）。**方案确认前不改业务代码。**
> 两个输入源：**功能从 `uni-superone-backup` 收集**，**前端设计思路从 `uni-carbon-space` 获取**。

---

## 背景

uni-superone 品牌骨架已完成：双模式主题（`--so-*` 令牌 + `.theme-light/.theme-dark`）、统一组件样式（`so-btn`/`so-card`/`so-cell`/`so-switch`）、页面门禁 `so-page`、契约以 submodule 消费、profile 页（照 carbon + backup 抄全）。

现在进入功能开发：把骨架升级为功能型小程序。豆哥定调——**前端设计（模块与布局）参考 carbon，功能范围对齐 backup 并做优化，实现不要只实现一半**（整模块交付，不留半成品）。

---

## 需求理解

一句话：把 uni-superone 做成「首页 + 多个模块（滑动/点击切换）+ 底部操作栏」的形态，模块切换与信息层级照 carbon 首页，业务功能照 backup 旧版逐模块复刻并优化。

---

## 目标与边界

### 本期目标

| 期 | 内容 | 状态 |
|---|---|---|
| P0 | 首页骨架：左侧 rail + swiper 懒挂载 + 底部操作栏 + 高度链 + `PANELS` 配置 | **已完成**（2026-10-02，type-check/build 通过） |
| P1 | **清单 checklist 五页闭环**：列表 / 详情 / 编辑 / 执行 / 历史 | 本期 |
| P2 | 计划 plan：近期任务闭环（OKR 不迁移） | 近期任务实现中；范围见 `task/dev-flow/260930_superone-frontend/plan-module-inventory.md` |
| P3 | 主题 topic：主题 CRUD + Markdown 日志时间轴（时间轴抽 `so-timeline` 复用） | 后续 |
| P4 | 物品 item | **已完成**（2026-10-06；详见 `task/dev-flow/260930_superone-frontend/process/02-26-item-module.md`） |
| P5 | 扩展：订阅、问答两个功能入口（仅入口占位，不实现功能） | **入口占位已落地**（2026-10-06；验证待补） |
| P6 | 内容流（feedback 4 / beanflow 6 / publicflow 7 三合一）+ 邀请 + 关于 | 后续 |

### 本期不做

- **不动后端、不动库表**（后端接口已存在，纯前端任务）。
- **不做投资 stock 模块**（2026-10-02 豆哥拍板砍掉；契约仓无 stock 域）。
- 不迁移 backup 的 `demo/` 三页、`static/temp_code/`（md-editor 36KB、chart 20KB、u-charts 7705 行）。
- 不迁移 backup `tool-config` 里 6 个 `developing` 占位项。
- 不引入新框架/新 UI 库（不引 uView、不引图表库）。

### backup 的坑，明确不继承

1. 6 个近乎同构的详情 composable（topic/item/stock/feedback/beanflow/publicflow）→ 合并为 `useTopicLogTimeline(topicType, ownerId)`。
2. 详情页内联的 `o-timeline` 模板复制 9 处 → 抽 `<so-timeline>` 组件（P3 落地）。
3. 分页两套协议（`loadMoreStatus` vs `hasMore + loadingMore`）→ 统一一套。
4. 下拉刷新两套写法（页面级 `onPullDownRefresh` vs `scroll-view` refresher）→ 统一 refresher。
5. `BaseEntity` 定义 3 份、`ExecutionMode` 定义 2 份 → 一律从 `@/contracts` 取，前端不复制类型。
6. 硬编码色值（`var(--theme)` 100+ 处、裸 `#ff9f0a`/`#666`/`#ff4757`）→ 一律走 `--so-*` 令牌。
7. `repos/` 层与 `apis/` 双数据路径 → 只用 `@/contract`。
8. `static/temp_code/` 死代码（md-editor 36KB、chart 20KB、7705 行 u-charts）→ 不迁移。
9. feedback / beanflow / publicflow 三页复制 → 合成「内容流」模块（P6）。
10. `wbbb` 之类无语义命名 → 沿用但不新增同类命名；新代码一律用可读命名。

---

## 改动范围

### 涉及仓库

| 仓库 | 角色 | 本期是否改动 |
|---|---|---|
| `business-repo/uni-superone` | 前端 | **是** |
| `business-repo/frontend-contracts` | 契约（submodule 挂在 `src/contracts`） | 否（仅消费，七个域已够用） |
| `business-repo/backend-superone` | 后端 | 否 |

### 涉及库表

**无。** 本期纯前端，不改表结构、不执行 DDL/DML。

### 涉及接口（P1 清单，全部已存在于契约）

鉴权统一走 `request` 层注入的 `Authorization: Bearer <token>`（登录过期由 `LOGIN_EXPIRED_CODE` 触发重登一次）。

| # | 方法 | 路径 | Req | Resp | 用途 |
|---|---|---|---|---|---|
| 1 | POST | `/api/so/checklist/list` | `GetChecklistListReq` | `GetChecklistListResp` | 列表（分页） |
| 2 | GET | `/api/so/checklist/detail` | `GetChecklistDetailReq` | `GetChecklistDetailResp` | 详情 |
| 3 | POST | `/api/so/checklist/create` | `CreateChecklistReq` | `CreateChecklistResp` | 新建 |
| 4 | POST | `/api/so/checklist/update` | `UpdateChecklistReq` | `UpdateChecklistResp` | 编辑（含置顶） |
| 5 | POST | `/api/so/checklist/delete` | `DeleteChecklistReq` | `DeleteChecklistResp` | 删除 |
| 6 | POST | `/api/so/checklist/execution/list` | `GetExecutionListReq` | `GetExecutionListResp` | 执行记录列表 |
| 7 | GET | `/api/so/checklist/execution/detail` | `GetExecutionDetailReq` | `GetExecutionDetailResp` | 执行详情 |
| 8 | POST | `/api/so/checklist/execution/create` | `CreateExecutionReq` | `CreateExecutionResp` | 开始/提交执行 |
| 9 | POST | `/api/so/checklist/execution/update` | `UpdateExecutionReq` | `UpdateExecutionResp` | 更新执行（勾选项/备注/完成） |
| 10 | POST | `/api/so/checklist/execution/delete` | `DeleteExecutionReq` | `DeleteExecutionResp` | 删除执行记录 |
| 11 | POST | `/api/so/checklist/execution/history` | `GetExecutionHistoryReq` | `GetExecutionHistoryResp` | 执行历史（按清单筛选） |

其余模块契约已就绪：plan 10 个（recent_task ×5 + goal ×5）、topic 10 个（topic ×5 + topic_log ×5）、item 7 个（含 category/list）、message-subscribe 5 个。

### 涉及前端文件（P1 清单）

| 文件 | 动作 | 说明 |
|---|---|---|
| `src/pages/index/index.vue` | 改 | 首个模块由 `biz-panel-placeholder` 换成 `biz-checklist-tab`（模板显式分派） |
| `src/components/business/biz-checklist-tab.vue` | 新增 | 清单模块面板：列表 + 下拉刷新 + 加载更多 + `defineExpose({ open })` |
| `src/components/business/biz-panel-placeholder.vue` | 保留 | 其余模块占位（P2+ 逐个替换） |
| `src/stores/checklist.ts` | 新增 | 清单列表状态与缓存（跨页共享：首页面板与详情页） |
| `src/composables/useChecklist.ts` | 新增 | 列表加载/分页/刷新/置顶/删除的业务流程 |
| `src/pages/checklist/detail/index.vue` | 新增 | 详情（Markdown 合并内容 + 执行历史 + 编辑/删除/执行入口） |
| `src/pages/checklist/edit/index.vue` | 新增 | 编辑（标题 + 最多 50 项，每项 Markdown，上移/下移/删除） |
| `src/pages/checklist/execute-overview/index.vue` | 新增 | 执行页（逐项勾选 + 备注 + 完成执行） |
| `src/pages/checklist/history/index.vue` | 新增 | 历史（清单筛选胶囊 + 执行记录列表） |
| `src/pages.json` | 改 | 注册 4 个新页面 |
| `src/styles/05-components/` | 按需 | 若出现第二处同类复用才收口（当前不预设） |

---

## 实施方案

### P5 扩展模块（入口占位已实现）

**原型判断：** `dashboard / launcher`。这是功能入口集合，不承载订阅或问答的数据流，也不做内容浏览。

**信息结构：** 首页 rail 新增唯一的「扩展」面板，内部纵向展示两个入口：「订阅」与「问答」。沿用现有 Superone 面板的标题、说明、行/卡片表面和 `--so-*` 主题令牌；入口视觉上清晰可辨，但标注「暂未开放」。

**交互边界：** 点击「订阅」或「问答」入口，只给出对应的「订阅功能暂未开放」/「问答功能暂未开放」轻提示，不跳转、不请求接口、不申请微信订阅授权、不创建或修改任何数据。首页底部主按钮保留统一布局，文案为「敬请期待」，点击只提示「扩展功能暂未开放」；不沿用现有「新建订阅」「提个问题」动作文案。

**文件级范围：**

| 文件 | 动作 | 说明 |
|---|---|---|
| `business-repo/uni-superone/src/pages/index/index.vue` | 改 | 将现有独立 `subscribe`、`flow` 面板项合并为 `extension`，文案为「扩展」；显式面板分派遵循小程序模板约束 |
| `business-repo/uni-superone/src/components/business/biz-extension-panel.vue` | 新增 | 只展示订阅、问答两个入口及暂未开放状态，不接入数据层 |
| `business-repo/uni-superone/src/components/business/biz-panel-placeholder.vue` | 保留 | 扩展已走显式分派；占位组件继续作为其他未实现模块的后备 |

**状态摘要：** 首次进入时展示静态入口；浅色/深色主题保持可读；点任一入口或底部按钮显示对应的暂未开放提示；不涉及加载、空数据、网络失败、权限和提交状态，因为本期没有数据请求或业务动作。

**验收：** 首页依次为主题、清单、计划、物品、扩展；扩展面板恰有订阅与问答两个入口；点击分别显示对应的暂未开放提示；底部主按钮显示「敬请期待」并只显示扩展暂未开放提示；不产生导航、网络请求或订阅授权弹窗；微信小程序模板无动态组件分派。

**资产与品牌：** 复用现有 `uni-icons` 与 Superone `--so-*` 令牌，不新增图像/SVG，不叠加 Carbon 品牌特化。

**本期不做：** 订阅列表/详情/增删改、微信订阅授权、问答浏览/发布/回答、相关页面、store/composable/API 接线及后端或契约改动。相关契约即使已存在也不消费。

### 四个业务模块的统一交互与视觉规则（2026-10-06 确认并落地）

- **详情页入口：** 主题、清单、计划、物品详情标题旁都提供可见编辑入口；低频动作统一收进「⋯」菜单。
- **删除：** 详情页「⋯」菜单和首页条目长按菜单均可删除，均明确二次确认；编辑页只负责字段修改与保存。
- **置顶：** 未置顶项显示「置顶」；已置顶项可「移至最前」或「取消置顶」，允许多条置顶并通过时间戳调整置顶顺序。
- **列表刷新：** 四个列表统一使用 scroll-view 下拉刷新、触底分页；筛选变化回到顶部并重置触底加载门槛，避免旧滚动位置误触发分页。
- **分页反馈：** 统一显示「加载中…」「继续上滑加载」「没有更多了」三种状态；失败时保留重试入口或提示。
- **表单：** 主题、计划、物品统一为单张表单卡、标签/字段节奏与分隔线、固定底部主保存按钮；清单继续使用适配多条排序内容的专属编辑结构。
- **视觉基调：** 延续 Superone「干净、克制、有层次」：32rpx 页面侧边距、轻量分隔线、主色小标签、主题令牌和圆角卡片；保留物品缩略图、清单执行入口、计划状态快捷操作等领域特有内容。
- **计划命名：** 首页 rail 为「计划」，面板标题为「近期任务」。
- **清单详情 CTA：**「开始执行」放在信息卡片右侧，位于「编辑 / ⋯」按钮下方；标题和日期信息在左侧，不固定在屏幕底部。
- **详情卡片操作：** 主题、清单、计划、物品详情的「编辑 / 更多」在内容右侧并排显示；每个入口内部为图标加文字，按钮尺寸与间距一致。
- **首页模块高度：** 四个可滚动业务面板统一填满首页 `swiper-item` 的 `100%` 高度，避免父级 swiper 与子级滚动区各自重复计算像素高度。
- **执行记录详情：** 记录状态右侧只放一个低强调度的「编辑」入口，打开对应执行记录编辑页。
- **首页转发：** 使用微信小程序原生右上角转发入口，分享标题、首页路径和分享卡片图片与 `uni-superone-backup` 保持一致。

**落地记录：** 已统一四个列表的置顶菜单、分页文案和列表行视觉；详情页补齐编辑/置顶/删除入口及清单下拉刷新；普通表单调整为一致的单卡结构。实现过程见 [`process/02-前端开发.md`](process/02-前端开发.md)。

### 首页左上角系统入口与签到（已实现）

**系统按钮样式：** 将首页左上角现有单人形图标改成 Carbon 首页的紧凑胶囊形式：齿轮图标 +「系统」文案、细边框、浮层底色、柔和阴影、轻磨砂与按压反馈。保留 Superone 的左侧位置、透明导航栏与 `.theme-light` / `.theme-dark` 令牌，不搬 Carbon 右侧布局或品牌色。按钮仍进入当前 `/pages/profile/profile`。

**签到按钮：** 紧邻系统按钮右侧，使用同一套胶囊视觉，文案按状态显示「签到」/「已签到」；处理中禁用并防重复点击。它承接 backup 的 `useDailyCheckin` 流程：微信小程序请求周报打卡模板授权，授权后调用现有 `userApi.subscribeMsg`（`msgType: WeeklyCheckin`）保存订阅，再将当天日期写入平台缓存；不新增后端接口或契约。现有 Superone 已有对应用户订阅 API、模板 ID 与枚举。

**行为修正：** backup 目前把“授权弹窗调用成功”直接当成用户已授权。实现时应检查微信返回的模板授权结果；用户拒绝时不调用保存接口、不写当天签到缓存，并允许重试。非微信端沿用 backup 的条件编译语义：跳过微信授权步骤，继续调用现有订阅接口。

**文件级范围（进入开发阶段后）：**

| 文件 | 动作 | 说明 |
|---|---|---|
| `business-repo/uni-superone/src/pages/index/index.vue` | 改 | 左侧插槽并排放「系统」与「签到」按钮；绑定签到文案、处理中/已签到禁用态 |
| `business-repo/uni-superone/src/styles/06-pages/_p-index.scss` | 改 | 按 Carbon 胶囊视觉整理导航按钮组与间距，沿用 `--so-*` 令牌 |
| `business-repo/uni-superone/src/composables/useDailyCheckin.ts` | 新增 | 管理当天签到缓存、授权、现有订阅接口调用、错误反馈与防重复提交 |
| `business-repo/uni-superone/src/utils/storage.ts` | 改 | 增加签到日期缓存键 |

**状态矩阵摘要：** 初次进入读缓存；缓存日期为今天则显示「已签到」且禁用；未签到点击后进入处理中；授权接受且接口成功则写缓存并提示成功；授权拒绝不写缓存并提示可重试；接口失败不写缓存并提示重试；处理中重复点击无副作用；跨日后首页再次显示时按当前本地日期刷新状态。浅色/深色主题下两个胶囊均需可读。

**验收：** 系统按钮外观与 Carbon 同类按钮一致且仍位于左上角，点击进入 profile；其右侧新增签到按钮。签到成功后当前日显示已签到，重复点击不再请求；拒绝授权和接口失败均不显示已签到，且可再次尝试；非微信构建不引用微信专属 API；不增加新后端接口/契约；H5 与微信小程序通过类型检查和构建。

**语义说明：** backup 将该流程称为「签到」，但实际动作是保存周报打卡订阅并记录本地当天状态，没有独立签到接口或服务端签到记录。本方案沿用这一既有含义。

### 其余阶段方案

### 一、原型判断（0201 硬门槛）

| 页面 | 原型 | 理由 | 主 CTA | 次 CTA |
|---|---|---|---|---|
| 首页 | `dashboard` | 核心是概览、切换、入口 | 底部主按钮（随模块变） | rail 切换、右上角「我的」 |
| 清单模块（首页内） | `feed` | 连续列表 + 回看 | 底部「新建清单」 | 卡片进详情、长按置顶 |
| 清单详情 | `detail` | 单对象深看 | 「执行」 | 编辑、删除、分享 |
| 清单编辑 | `detail`（沉浸编辑） | 单对象沉浸编辑 | 「保存清单」 | 预览、增删项、排序 |
| 执行页 | `detail` | 单对象分步完成 | 「完成执行」 | 全部完成/清除/重置 |
| 历史 | `feed` | 连续记录回看 | 无（筛选为主） | 进执行详情 |

**反模式自查**：首页不兼任 detail 和 feed（模块各司其职）；每页只有一个主 CTA；页面结构按产品意图组织，不按接口字段堆砌。

### 二、状态矩阵（0201 硬门槛，缺一视为未完成）

| 场景 | 触发条件 | UI 表现 | 数据来源 | 用户动作 | 失败/回退 |
|---|---|---|---|---|---|
| 首次进入 | 无本地缓存、首次 onShow | loading（骨架屏） | 请求 1 列表 | 等待 | 失败转 error + 重试 |
| 有本地缓存 | 二次进入，缓存未过期 | 先渲染缓存，再静默刷新 | `CacheManager` → 请求 | 可直接操作 | 刷新失败保留缓存 + 轻提示 |
| 服务端空数据 | 列表返回 `list: []` | 空态（文案 + 一个明确 CTA「新建清单」） | 请求 | 走 CTA | — |
| 服务端有数据 | 正常 | 卡片列表 | 请求 | 进详情/长按置顶 | — |
| 加载中 | 首帧/切模块 | 骨架屏 | — | 等待 | — |
| 刷新中 | 下拉 | 顶部 refresher | 请求 | 等待 | 失败 toast + 保留原列表 |
| 加载更多 | 触底 | 底部 loading / `no-more` | 请求（offset 累加） | 等待 | 失败「重试」按钮 |
| 提交中（新建/编辑/删除） | 点保存 | 按钮 disabled + loading | 请求 | 等待 | 失败就地提示（不 toast 了事） |
| 请求失败 | 非 0 errCode / 网络错 | error 态 + 重试按钮 | — | 点重试 | 可继续用缓存数据 |
| 登录过期 | `LOGIN_EXPIRED_CODE` | 静默重登一次后重试 | login adapter | 无感 | 重登失败 → 引导重新登录 |
| 权限不足 | 非管理员操作管理员项 | 不渲染该入口 | — | — | 不出现（入口不可见） |
| 删除二次确认 | 点删除 | `uni.showModal` 确认 | — | 确认/取消 | 取消即回退，无副作用 |

### 三、首页骨架（P0 已完成，作为后续模块的固定契约）

1. 切换三件套：`activeIndex` + `curSwiper` + `loadedPages: Set<number>`（懒挂载，首屏只挂 1 个）。
2. 点击 rail：先把 `swiperDuration` 置 0（点击不做滑动动画），300ms 后恢复 200。
3. 高度链：胶囊算导航高 → `swiperHeightPx = max(windowHeight - nav - 50, 200)` → 传模块 → 模块内 `scroll-height = max(navHeightPx - 16, 200)`。
4. 底部主按钮是「当前模块发布入口」的遥控器：点击调 `xxxRef.open()`，弹层由首页统一渲染、反受控 `:visible="!!ref?.composerVisible"`。
5. 刷新统一用模块内 `scroll-view` refresher，不用页面级 `enablePullDownRefresh`。
6. **小程序端不支持 `<component :is>`**，模块分派必须写显式分支（加模块在模板加一支）。

### 四、数据层（0202）

- 类型一律从 `@/contracts` 取，前端不再复制 `types/apis`。
- `stores/checklist.ts` 管跨页状态与缓存；`composables/useChecklist.ts` 管页面业务流程（加载/分页/刷新/置顶/删除）。
- 字段兼容转换与业务错误处理放统一 helper，不散在 `.vue`。
- **分页协议统一一套**（`hasMore + loadingMore`），不继承 backup 的 `loadMoreStatus` 双协议。

### 五、页面与样式（0203）

- 页面尽量薄，业务逻辑进 composable/store。
- 样式走 `--so-*` 令牌 + `05-components` 统一件，页面 scoped 只留布局/间距。
- 复用的时间轴在 P3 抽 `so-timeline` 组件；P1 不涉及。

### 六、资产与品牌（0204 / 0205）

- **资产主权**：图标继续用 `uni-icons`（项目已在用），不引入新图标库；空状态用文案 + 图标，不新增 SVG 资产。
- **品牌一致性**：本项目是 **superone 品牌（微信绿 `#07C160`）**，不是 carbon。carbon 只提供**布局与交互思路**（rail + swiper + 底部操作栏 + 主按钮遥控 + 反受控弹层），**不叠加 carbon 的品牌规范**（暖色、无红绿、深水意象等不适用）。

---

## 验收标准（可判定）

1. `npm run type-check` 通过；`npm run build:mp-weixin` 通过。
2. 首页：6 个 rail 项点击切换无卡顿；左右滑动切换正常；底部主按钮文案随模块变化。
3. 清单模块：列表能加载、下拉能刷新、触底能加载更多、空态有 CTA、失败有重试。
4. 清单五页闭环：列表 → 详情 → 编辑保存 → 执行 → 历史可见该次执行。
5. 状态矩阵中每一行都能在真机/模拟器上复现（尤其：缓存先渲染、失败可重试、删除二次确认）。
6. 浅色/深色双模式下全部页面可读（重点检查背景与文字对比度）。

---

## 推荐实施顺序

1. **0201 原型与状态矩阵**（本方案已产出，实现前逐页对齐一次）。
2. **0202 数据层**：`stores/checklist.ts` + `composables/useChecklist.ts` + 契约接线。
3. **0203 页面**：`biz-checklist-tab` → 详情 → 编辑 → 执行 → 历史，`pages.json` 注册。
4. **首页接线**：第一个模块由占位换成 `biz-checklist-tab`。
5. **0301 验证**：type-check / build / 真机走查状态矩阵。

---

## 测试方案

### 功能测试

| 序号 | 场景 | 操作 | 预期结果 |
|---|---|---|---|
| 1 | 清单列表加载 | 进首页，停在清单模块 | 骨架屏 → 列表渲染，条数与后端一致 |
| 2 | 下拉刷新 | 列表顶部下拉 | 触发刷新，列表更新，refresher 收起 |
| 3 | 触底加载更多 | 滑到底部 | 追加下一页；无更多时显示 `no-more` |
| 4 | 空态 | 用无清单账号进入 | 空态文案 + 「新建清单」CTA，点击进编辑页 |
| 5 | 新建清单 | 底部主按钮 → 填标题与 3 项 → 保存 | 列表新增该清单，toast 成功 |
| 6 | 编辑清单 | 详情 → 编辑 → 改标题 → 保存 | 详情与列表同步更新 |
| 7 | 删除清单 | 详情 → 删除 → 确认 | 二次确认后删除，列表移除；取消则无变化 |
| 8 | 置顶 | 列表长按 → 移至最前 | 该项排到首位，刷新后保持 |
| 9 | 执行清单 | 详情 → 执行 → 勾选 2 项 + 备注 → 完成执行 | 生成执行记录，历史页可见 |
| 10 | 执行历史 | 历史页 → 选清单筛选 | 只显示该清单的执行记录 |
| 11 | 底部主按钮随模块变 | 切到不同模块 | 按钮文案随模块变化，点击触发该模块 open() |
| 12 | 深浅色 | 切换主题 | 五个页面文字与背景对比度正常，无消失元素 |

### 回归测试

| 序号 | 场景 | 操作 | 预期结果 |
|---|---|---|---|
| 1 | 首页骨架 | 逐个点击 6 个 rail | 切换正常，未访问模块首次点击后懒挂载，无白屏 |
| 2 | 模块高度 | 真机与模拟器各看一次 | 列表可滚动、底部操作栏不遮挡内容 |
| 3 | profile 页 | 我的 → 主题切换 | 主题切换生效，管理员面板按权限显示 |
| 4 | 门禁 | 非管理员进入 | 按 `so-page` 规则展示演示/锁定态，不越权 |
| 5 | 登录过期 | 清 token 后请求 | 静默重登一次并重试成功；失败则引导重新登录 |

### 兼容性测试

| 序号 | 场景 | 预期结果 |
|---|---|---|
| 1 | 旧数据（清单无 `top` 字段） | 按 `top ?? 0` 处理，不影响排序与展示 |
| 2 | 执行记录 `status` 为历史值 | 按枚举映射显示，未识别值显示「未知」不崩溃 |
| 3 | 缓存结构与新版本不一致 | 解析失败时丢弃缓存直接请求，不白屏 |
| 4 | 长标题 / 50 项上限 | 标题省略号，项数超 50 时限制新增并提示 |

---

## 风险与回滚

| 风险 | 影响 | 应对 |
|---|---|---|
| 后端字段与契约不符（契约按 yaml 生成，内层可能退化 `unknown`） | 页面取不到字段 | 实现前用真账号打一次 `/api/so/checklist/list` 核对字段；不符则先补契约再写页面 |
| swiper 高度算错 | 列表不可滚动或白屏 | 严格照高度链实现；真机与模拟器各验一次 |
| 模块越做越多导致 rail 放不下 | 交互拥挤 | 模块数控制在 6 个内；超出时加「更多」入口（不在本期） |
| 一次做多页导致半成品 | 无法交付 | 严格按 P1 五页清单验收，缺一页不进入下一期 |

**回滚**：所有改动停在未提交工作区；出问题 `git checkout -- src/` 即可回到骨架状态（骨架本身已 build 通过）。

---

## 落地记录

- 2026-10-02：完成调研（backup 功能清单 + carbon 前端架构）、P0 首页骨架落地、本方案产出。
- 2026-10-06：按确认方案将订阅、问答合并为「扩展」面板，新增两个暂未开放入口；未接实际功能。之后按确认方案将首页左上角设置入口改为 Carbon 式「齿轮 + 系统」胶囊，并加入签到入口、微信订阅授权结果校验、现有订阅接口和本地当日缓存。过程记录见 [`process/02-前端开发.md`](process/02-前端开发.md)。
- 2026-10-06：按四模块统一交互规则调整列表菜单、详情入口、删除位置、置顶动作、加载文案和普通表单布局；类型检查、微信小程序构建与 H5 构建通过。过程记录见 [`process/02-前端开发.md`](process/02-前端开发.md)。

---

## 附录：SuperOne 视觉语言（风格基线，2026-10-02 建立）
页面照此执行，新增页面不另起风格。
**定位**：干净 · 克制 · 有层次。对标微信 / 滴答清单这类工具感产品，不玩酷炫、不做装饰性动画。
**分层逻辑**：靠「细边框 + 轻阴影」分层，不靠重色块。
- 页面底 `--so-bg-secondary`；卡片 `--so-bg-elevated` + `1rpx` 边框 + `--so-shadow-card`；浮层（底栏/弹层）`--so-shadow-float`。
- 圆角：卡片 lg(28rpx)、控件 md(20rpx)、胶囊 full。列表行无圆角、只有 1rpx 分隔线。
- 品牌主色 `#07C160`，主按钮渐变 `135deg #07c160 → #06a050` + 绿色投影 `0 6rpx 16rpx rgba(7,193,96,.28)`；次按钮描边。
- 排版记忆点：**eyebrow**（20rpx、字距 4rpx、主色）标模块属性，下面接 48–52rpx 粗体大标题，再接 24rpx 说明。
- 语义色只用 success / warning / error / info 四个，且只出现在图标与小标签上，不铺面。
- 动效：只做 `transition-fast` 的颜色/显隐过渡，不弹跳、不闪烁、不旋转。
- **反面清单**：不要大面积高饱和色块；不要重投影；不要一个页面两个强调色；不要让卡片与页面底同色（必须边框或阴影分层）。
**落地**：令牌 `--so-shadow-card`/`--so-shadow-float` 已在 `01-settings/_variables.scss`；`.so-card` 已带边框与阴影；`.so-btn-primary` 已带渐变与投影；风格预览页 `pages/test-theme/test-theme.vue` 是这套规范的活样板（品牌色/文字层级/表面层次/卡片列表行/按钮/圆角阴影六段）。

### 视觉语言修订（2026-10-02 晚）
- 豆哥：「渐变色是个什么鬼玩意，实在不行你就抄一下 carbon 的，然后改改颜色」。核查结果：**渐变就是 carbon 原样**——`.cs-btn-primary` 本身就是 `linear-gradient(135deg, var(--cs-glow), var(--cs-glow-dark))`。自造的是绿色投影，已删除。
- 阴影令牌改名对齐 carbon：`--so-shadow-card/float` → **`--so-shadow-soft`（0 12rpx 34rpx）/ `--so-shadow-deep`（0 18rpx 48rpx）**，且像 carbon 一样**随主题变化**（浅色墨绿调 rgba(24,38,30,.1/.16)、深色纯黑调 rgba(0,0,0,.28/.36)）。
- rail 选中态改回 carbon 写法：磨砂底 `--so-bg-elevated` + `--so-border-color` 边框 + 主色字 + `--so-shadow-soft`，不再用绿弱底+绿边。
- **原则修正**：视觉手法一律先抄 carbon 再换色，不自创（渐变、投影、光斑强度都不自己拍）。要改观感时先问，不要自己加料。

### 令牌挂载规则：小程序端禁用 `:root`（2026-10-02 真机事故）
- 现象：**真机浅色模式整体没颜色（网格、光斑、卡片、按钮全丢），深色模式正常，开发者工具模拟器正常**。
- 根因：浅色/静态令牌写在 `:root` 上。小程序渲染层没有 html 元素、不认 `:root`；**逗号选择器列表不是容错的**（CSS 规范：一个选择器不认识，整条规则被丢弃）→ 真机上整条浅色令牌规则被丢。深色是单选择器 `.theme-dark`，所以正常；开发者工具是 Chrome 内核认 `:root`，所以模拟器正常。
- 修法（照 carbon，carbon 全仓零 `:root`）：
  - 静态令牌 → `page, .theme-light, .theme-dark { }`
  - 浅色令牌 → `page, .theme-light { }`
  - 深色令牌 → `.theme-dark { }`（不挂 page）
- 连带：`page` 元素永远只拿得到浅色令牌，所以 **`page` 不能设主题背景**（深色会露白底），背景交给各页面根容器（so-page / index shell / profile shell）铺满提供。
- ~~同域的第二条：`background` 简写里的 `var()` 在真机不稳~~ —— **作废，是误判**。豆哥让回去查证：carbon 全仓 **110 处 `background: var(...)`**，页面容器就是 `background: var(--cs-page-bg)`，`.cs-btn-primary` 是 `linear-gradient(135deg, var(--cs-glow), var(--cs-glow-dark))`（渐变里直接嵌 var），线上真机正常。所以**不要为想象中的真机兼容性写硬编码兜底**，一律照 carbon 用 `background: var(...)`；`_button.scss` 里先前加的品牌绿兜底也已删除。

### 圆角与导航入口（2026-10-02 晚三）
- **`--so-radius-full: 50%` 不是胶囊，是正圆**。50% 是相对自身宽高的百分比，扁矩形上会渲染成**椭圆弧**（水平半径取宽一半、垂直半径取高一半），这就是「按钮圆弧太丑」的真因。carbon 的 50% 只用在**正方形**上（avatar / splash 圆点 / `.rounded-full`），胶囊药丸一律写死 **`999rpx`**（固定大值被 clamp 到短边一半 = 正圆角）。
  - 已全仓修正 5 处扁矩形误用：首页底栏主按钮、so-page 重试 / 切换场景按钮、profile 分享按钮、风格页主题按钮；保留 50% 的只有 `.round`、profile 头像、首页光斑（都是正方形）。
- **导航栏设置入口在左侧**（豆哥定）：右侧是微信原生胶囊的地盘（so-custom 已做 padding-right 避让），自己的操作走 `#left` 插槽。
- 底栏主按钮尺寸照 carbon 的 `.p-index__tabbar-action--primary`：`height 78rpx` / `min-width 190rpx` / `padding 0 24rpx` / `font-size 24rpx`（原先是 88rpx 高 + 30rpx 字 + 32rpx 留白，又矮又胖）。

### 首页布局与背景（2026-10-02 晚二）
- 豆哥：「首页导航栏都可以直接照抄用透明的，然后首页直接布局一个高级感点的背景设计 / 不要只盯着颜色，边距、布局这些更重要」。
- **导航栏透明态照抄 carbon 的 floating**：`so-custom` 的 `transparent` 改为**仍占一份导航高度**（原先做成不占位，会导致内容压到导航栏下），只去掉背景与边框，`rootHeight` 恒为 `customBar`。首页用 `<so-custom transparent class="so-index__nav">`，标题用主色。
- **背景层 `.so-index__backdrop`**（`absolute inset:0` + `pointer-events:none`，不参与布局）：两个品牌光斑（左上 420rpx 用 `--so-glow-strong`、右下 360rpx 用 `--so-glow-soft`，均带 180/160rpx 光晕与 `so-orb-breathe` 呼吸动画）+ 44rpx 网格线（`--so-grid-color`）。照 carbon 的 `p-index__backdrop` 三件套。
- **新增令牌**：`--so-page-bg`（两层径向光 + 竖向渐层，照 `--cs-page-bg`）、`--so-frost`（浮层磨砂面：导航胶囊 / 底栏 / rail 选中，半透明 + `backdrop-filter`）、`--so-frost-weak`（rail 未选中淡底，照 carbon 的 4% 白）。
- **边距与高度链严格对齐**（这轮的重点，比颜色优先）：
  - `.so-index-shell`：`height:100vh` + `overflow:hidden`；导航栏占位后，`.so-index` 高度 = `calc(100vh - var(--index-nav-height))`。
  - `.so-index` 纵向内边距 = **上 16rpx + 下 176rpx**（底部操作栏占位），左右 `--so-space-lg`(32rpx)；底栏左右同为 32rpx，与内容边缘对齐。
  - rail：`fixed` 左 32rpx、宽 108rpx、`top = 导航高 + 24rpx`；`.so-index__main` 左内边距 128rpx → 内容与 rail 留出约 20rpx 间隙。
  - 模块可视高度 `swiperHeightPx` 用**同一个数字**换算（视口 - 导航高 - 192rpx 转 px），不再各算各的；`biz-panel-placeholder` 改为直接用传入值（原来再减 16px，会与 CSS 不一致）。
  - swiper 高度改 flex（`flex:1; min-height:0`），与 carbon 一致，不再用 `calc(100vh - ...)`。
