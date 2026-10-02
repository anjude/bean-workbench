# 项目长期记忆

## skill 实体位置
- 实体在 `bean-workbench/.agents/skills/`；`~/.agents` 是指向它的外链，其他工具经它读同一套 skill。换机器重建外链即可。
- 坑：Python `Path.rglob` 与 Bash `grep -r` **不跟随符号链接目录**，校验脚本要自写递归或单独 `cd ~/.agents` 再跑；改目录结构后必须做负向测试。
- 代价：skill 改动全局生效；只在台内试用先 `git stash push -- .agents`。

## skill 编号体系（2026-08-29 定稿，27→18）
- 格式 `{族群前缀}-{阶段号}{阶段内序号}-{能力后缀}`；工具 skill 用 `{前缀}-tools-{后缀}`，不占阶段号；`xx00` 为阶段入口，具体从 `xx01` 起。
- 族群：`dev-flow-*` 跨端开发、`bn-*` beannote 内容生产（**前缀是 bn 不是 cn**）、`wb-*` 工作台基建。**bn 族群 2026-09-24 全部归档**，`.agents/skills/` 下已无 bn。
- **`wb-*` 是唯一例外（2026-09-14 豆哥定）**：不跑流水线，直接 `wb-{能力}`（`wb-router`/`wb-skill-refactor`/`wb-handoff`）；`check-workbench.py` 用独立正则 `WB_NAME_RE`，带编号的 `wb-0102-handoff` 判不合规。旧名只在历史任务文档残留。
- dev-flow 四阶段：`00` 方案设计（必过）/`01` 后端/`02` 前端/`03` 整体验证（必过）。纯前端跳 01，纯后端跳 02。
  - `0000-plan-flow` 唯一入口；`0101-domain-flow`（只设计不连库）→`0102-db-change-flow`（唯一写入口）→`0103-api-flow`→`0104-contract-flow`；`0201-archetype-flow`（原型+状态矩阵，硬门槛）→`0202-data-flow`→`0203-page-flow`→`0204-asset-flow`→`0205-space-ui`；`0301-verify-flow` 收口+回填；工具 `tools-repo`/`tools-db-query`（只读）。
  - bn 三层（2026-09-13 重构，已归档）：`00` 只答「到底是什么」、`01` 只答「这次讲哪几点」、`02` 只答「怎么讲给人听」。反馈归层：观点/事实错→00；讲偏/漏讲→01；AI 味/像提纲→02。
  - **重构原则（豆哥定）**：skill 只给框架和步骤，不写细、不搞机械写文规范。模板类 references 已删，只留 `表达红线.md`、`公众号草稿发布-本地配置.md`、`manifest模板.yaml`。
  - 槽位格式 `{阶段号}-{阶段内序号}-{槽位名}-{主题}`：`01-1-问答录`/`01-2-素材`/`01-3-大纲`/`02-1-公众号`/`02-2-小红书`。**`source/` 放第三方原文**（文件头写来源 URL/口径/抓取时间，表格照抄不加工），结论进槽位文件。
  - 目录骨架原由 `bn-0000-init-flow` 唯一定义（已随 bn 归档），下一代开建时定义处跟着新 skill 走。
- 合并粒度：同阶段总是一起走的合并，超 300 行才拆；读写边界、品牌特化资产不合并。
- 方案文档落 `task/YYMMDD_{主题}/README.md`，不往业务仓 `docs/feature/` 新增。编号表在 `AGENTS.md`；目录名/`SKILL.md` 的 `name`/文档引用三者一致，改完跑 `make check`。
- 旧名对照（查历史文档用）：`be-*`/`fe-*`→`dev-flow-*`；`content-beannote-knowledge-base`→`bn-0001`、`content-beannote-creation-flow`→`bn-0101`、`content-beannote-article-review`→`bn-0201`；`hair`→`wb-router` 一脉。历史文档旧路径刻意保留。

## skill 写法偏好
- **规则用正面表述**（2026-09-19 豆哥定）：写「要做什么」，少写「不要做什么」；走偏信号写成「在做的事 → 回到哪」对照表。
- **别把单次顺手行为固化成 skill 规则**（2026-09-23 豆哥"太机械了"）：门槛是「不写就会反复做错」，不是「这次做对了值得记」。好做法留在 working memory，skill 保持骨架。

## 代码复杂度偏好（2026-10-02 豆哥"你把我的程序弄得很复杂"）
- **一套设计只解决一个问题，不叠加第二套解法**。事故：login 改走 adapt/http 原语层后环已自断，却又加 `setAuthRefresher` 端口 + `boot/auth.ts` + `main.ts` import 去"解耦"同一个环。已全删（request 直接调 `getLoginAdapter().login()`）。
- 提新抽象前先画依赖方向：若加完新方案后删掉老方案仍成立，老方案多半早该删。
- 「要不要留缝」默认**不留**：直接调用 > 端口+接线文件；只有跨端/跨项目替换真发生才上升为端口。
- 顺手清：声明后从未使用的字段、只剩一个调用者的中间方法。

## 工作台目录约定
- `docs/` 只放说明类，当前仅 `workspace.md`。要照着填的材料进 skill 的 `references/`，并在 `SKILL.md` 列「配套 references」表。
- `kb/` 取代原 `knowledge-base/`（2026-09-30 迁移）；`task/registry.md` 登记任务。
- **`handoff/` + `process/` 两层（2026-09-21 豆哥加）**：handoff 是「我从哪接着干」（一屏快照，最新一份）；process 是「怎么被想清楚的」，一个阶段一份 `{阶段号}-{环节名}.md`，记做了什么/结论/被推翻的判断/待核，纵向只增不改。handoff 只引用 process 路径。**process 是 topic 维度的**：工作台 task 目录与 beannote 选题目录两边都建。

## 环境：macOS（2026-08-29 起）
- darwin/arm64，无 pwsh；brew 在 `/opt/homebrew/bin/brew`，Go 1.27.0 在 `~/sdk/go`（PATH 与 GOPROXY 写在 `.zshrc` 末尾）。
- **助手 Bash 的 PATH 不完整**（不读 `/etc/paths.d`/`.zshrc`）：直接敲 `brew`/`go` 会 command not found，用绝对路径或先 `export PATH="/opt/homebrew/bin:$HOME/sdk/go/bin:$PATH"`。判断「没装」前先排除 PATH。
- `make check` 调 `script/check-workbench.py`（标准库）：必需文件 + skill 命名一致性 + md 相对链接失效，均已负向测试。
- 业务仓 `backend-superone` 仍是 Windows 脚本，非明确需求不动。
- **分支约定（2026-09-28 豆哥定）**：dev 开发、就绪合 release；**不另开 `version/*` 推远程**；**开发阶段不擅自 commit，保持未提交工作区，等豆哥说"提交/合 release"再动**（助手两次越界已纠正）。重构前可打 tag 作基线（如 `release-260927`，保留）。
- **父仓 bump 子模块指针的例外（2026-09-30）**：子仓改动**已 push 远端**才可 bump；`ahead` 未推或未提交的不 bump。

## 引用同步排查坑
- Grep 工具默认跳过点开头目录，扫不到 `.agents/skills/`；全仓同步用 `grep -rn --exclude-dir=business-repo --exclude-dir=.git --exclude-dir=node_modules`。
- 活跃文档（`AGENTS.md`、`SKILL.md`+`references/`、`docs/`、`task/registry.md`、脚本）必须改名；历史任务文档保留旧名。

## carbon 项目（uni-carbon-space）
- 「留白」显示名改**「一隅」**（key `play` 不变）。「边界」= 个人使用说明书，2026-07-11 已落地（`/api/so/carbon/boundary/*` 5 接口）。
- 品牌硬约束：两人留痕/回看的空间，非效率或冲突解决工具；避免已读未读/强提醒/催回复/任务式推进；配色仅暖色（米白 #f5f0ea + 琥珀 #f0a050），**无红绿独立色**；文案第一人称、具体、克制，禁口号。
- 方案文档：`docs/feature/YYYY-MM-DD_功能名方案.md`，**一篇合并**含前后端改动点+测试三表，不拆两份。
- `frontend-contracts/openapi/carbon_api.yaml` 只**增量 append**；`components:` 必须在第 0 列。
- 迁移：carbon 表不走 `tablesToCreate`，用 `scripts/migration/sql/YYYYMMDD_*.sql` + `go run ./scripts/migration -action=exec-sql -sql-file=<path> -env=test`；新增表须手动加进 `exec_sql.go` 的 `carbonTables`。test 库是共享远程库，写操作须用户「继续」授权。
- gin validator 坑：含合法 0 值的整数不用 `binding:"required"`，改 `gte=0` + 业务层兜底。

## uni-superone 前端
- **对外名「豆流便签」，superone 只是内部工程名**（2026-10-02 豆哥定）。判断口径=用户看不看得见：看得见的（演示页文案、分享海报品牌行、分享标题、`pages.json` 的 navigationBarTitleText）用「豆流便签」；看不见的（`so-*` 前缀、storage key `superone:*`、logger `[superone]`、`superoneHttpClient`、manifest name、test-theme 调试页、契约/后端仓名）沿用 superone。首页**不挂导航栏标题**（豆哥定）。品牌名在演示页与 `usePosterShare` 各收一个 `BRAND_NAME` 常量。
- `business-repo/uni-superone`：通用 uni-app 前端（Vue3+TS+Pinia+Vite），`release` 分支为默认。纯前端任务跳 dev-flow 01。`uni-superone-backup`：旧版快照，**仅供参照，禁止基于它开发/提交**。
- **技术栈与写法以 carbon 为样板**。双模式主题：令牌 `--so-*`，主题类 `.theme-light`/`.theme-dark`（浅底深字/深底浅字，映射正确；**carbon 的 `day`/`night` 接线反了，不重复该错误**）。
- **品牌主色 = 微信绿 `#07C160`**（2026-09-30 拍板）。深色保持同绿不提亮，仅表面变深。切换由 `src/composables/useTheme.ts` 接管（模块级单例：读偏好→默认跟系统→用户可切，持久化到 CacheManager THEME 键）。**原生 chrome 用自定义导航栏 `so-custom.vue` 覆盖**（index 已 `navigationStyle: custom`），不引入 `darkmode`/`theme.json`/`setNavigationBarColor`；`pages.json` 的 `navigationBarTextStyle` 暂不处理。
- **页面门禁架构**：`so-page.vue` 是统一门禁（对标 carbon 的 `cu-page`）。优先级：未就绪→loading / 失败→error(重试) / 已就绪且 `isReal`→真实 slot / 非真实：`reverse`(首页)→`#demo`(默认 `so-demo-page.vue`)，普通页→`#locked`。`themeClass` 挂 so-page 根容器。`stores/app.ts` 是系统配置+用户信息唯一数据源（`init()` 在 App onLaunch 幂等调），`isReal = wbbb || isAdmin`。演示态的切换入口照 carbon 的 `p-page__admin-card`：**长在演示内容里**（`v-if isAdmin` 的「切换场景 {{ wbbb }}」按钮，在首页演示分支底部），**不用全局悬浮件**。
- **项目形态定调（2026-10-02 豆哥定）**：前端设计/布局**参考 carbon 首页**——**首页 + n 个模块（滑动/点击切换）+ 底部操作栏**；**功能范围对齐 backup 旧版并做优化**；**实现不要只实现一半**（整模块交付：列表+详情+编辑闭环）。方案文档 `task/dev-flow/261002_superone-modules/README.md`。
  - **首页骨架照抄 carbon 的 6 条机制**：① 切换三件套 `activePanel`+`curSwiper`+`loadedPages:Set`（懒挂载）；② 点击切换 duration 置 0、`@change` 后 300ms 恢复 200；③ **高度链** capsule → `navHeightPx=max(windowHeight-nav-50,200)` → 传模块 → `scroll-height=max(navHeightPx-16,200)`（不照抄必白屏）；④ 底部主按钮是「当前模块发布入口」遥控器，点击调 `xxxRef.open()`；⑤ 弹层由首页统一渲染、反受控 `:visible="!!ref?.composerVisible"` + `@close="ref?.close()"`；⑥ 刷新用模块内 `scroll-view` refresher，不用页面级 `enablePullDownRefresh`。
  - **模块清单（契约可用性）**：checklist ✅ / plan(任务+OKR) ✅ / topic(含日志时间轴) ✅ / item ✅ / message-subscribe ✅ / 内容流（feedback+beanflow+publicflow = topic-log 的 topicType 4/6/7 变体，合成一个模块）✅ / **stock ❌ 契约无此域**（待核后端是否有 `/api/so/stock/*`，否则砍掉）/ invitation、about 后置。
  - **方案走 dev-flow skill**：方案文档按 `dev-flow-0000-plan-flow` 模板落 `task/YYMMDD_{主题}/README.md`（当前 `task/261002_superone-modules/README.md`）；**功能从 backup 收集**（checklist/plan/topic/item/message-subscribe/内容流），**前端设计从 carbon 取**（rail+swiper+底部操作栏+主按钮遥控+反受控弹层+高度链）。**跳过阶段 01**（纯前端、不动库表）；0201 原型+状态矩阵是硬门槛（只有 happy path 视为未完成）；0204 不产资产（用 uni-icons）；**0205 不叠加**（carbon 只给布局与交互思路，本项目是微信绿 superone，不适用 carbon 品牌规范）。
  - **backup 的坑不继承**：6 个同构详情 composable 合并为 `useTopicLogTimeline(topicType, ownerId)`；`o-timeline` 内联模板抽 `<so-timeline>`；分页两套协议统一；刷新两套写法统一；`BaseEntity` 等类型一律从 `@/contracts` 取；硬编码色值全部走 `--so-*`；`repos/` 层与 `static/temp_code/` 死代码不迁移。
- **SuperOne 视觉语言（2026-10-02 建，新增页面照此执行）**：**一切视觉手法先抄 carbon 再换色，不自创**（曾自造"绿色投影"被豆哥骂"渐变色是个什么鬼玩意"；实际渐变是 carbon 原样 `.cs-btn-primary`，被否的是我加的投影）。① 页面底 `--so-bg-secondary`，卡片 `--so-bg-elevated` + 1rpx 边框 + `--so-shadow-soft`，浮层（底栏/弹层）`--so-shadow-deep`；阴影令牌**与 carbon 同名同义且随主题变**（浅色墨绿 rgba(24,38,30,.1/.16)、深色纯黑 rgba(0,0,0,.28/.36)）；② 圆角：卡片 lg(28)、控件 md(20)、胶囊 full，列表行无圆角只有分隔线；③ 主色 `#07C160`，主按钮 `135deg #07c160→#06a050` 渐变（carbon 原样），**不加彩色投影**，次按钮描边；④ 排版记忆点 **eyebrow**（20rpx、字距 4rpx、主色）+ 48–52rpx 粗体大标题 + 24rpx 说明；⑤ 语义色只上图标与小标签，不铺面；⑥ 动效只做 `transition-fast` 的颜色/显隐过渡。反面清单：自造投影/光效、大面积高饱和色块、一页两个强调色、卡片与页面底同色。风格预览页 `pages/test-theme/test-theme.vue` 是活样板。
- **首页布局与背景（2026-10-02 晚，豆哥「不要只盯着颜色，边距、布局这些更重要」）**：① **`so-custom` 的 `transparent` = carbon 的 floating：仍占一份导航高度**（`rootHeight` 恒 `customBar`），只去背景边框；曾自造成「不占布局高度」会让内容压到栏下。② 背景层 `.so-index__backdrop`（absolute inset:0 + pointer-events:none）= carbon `p-index__backdrop` 三件套：两个品牌光斑（左上 420rpx `--so-glow-strong` / 右下 360rpx `--so-glow-soft`，180/160rpx 光晕 + `so-orb-breathe` 呼吸动画）+ 44rpx 网格 `--so-grid-color`。③ 令牌：`--so-page-bg`（两层径向光+竖向渐层，照 `--cs-page-bg`）、`--so-frost`（浮层磨砂：导航胶囊/底栏/rail 选中，半透明+backdrop-filter）、`--so-frost-weak`（rail 未选中淡底=carbon 的 4% 白）。④ **边距/高度链必须同一个数**：`.so-index` 高 `calc(100vh - var(--index-nav-height))`、纵向内边距 上 16rpx + 下 176rpx（底栏占位）、左右 32rpx（底栏同宽对齐内容边）；rail 左 32rpx 宽 108rpx top=导航高+24rpx；main 左内边距 128rpx；swiper `flex:1;min-height:0`（照 carbon，不用 calc）。`swiperHeightPx = 视口-导航高-192rpx(转px)` 用常量 `CONTAINER_V_PADDING_RPX` 与 CSS 共用，模块**不再额外减 16px**（否则内容被底栏切一截）。
- **小程序端令牌只能挂 `page` 与主题类，禁用 `:root`（2026-10-02 真机事故）**：浅色+静态令牌原写在 `:root` 上 → **真机浅色整体没颜色，深色正常，模拟器正常**。原因是渲染层没有 html、不认 `:root`，而**逗号选择器列表不是容错的**（一个选择器不认识整条规则被丢弃）；深色是单选择器 `.theme-dark` 故正常，模拟器是 Chrome 内核认 `:root` 故正常。照 carbon（全仓零 `:root`）改为：静态 `page,.theme-light,.theme-dark` / 浅色 `page,.theme-light` / 深色 `.theme-dark`。连带：① **`page` 不能设主题背景**（page 永远只拿浅色令牌，深色会露白），背景交给页面根容器铺满。② **作废旧结论「真机对 `background` 简写里的 var() 不稳」**——那是误判（真因就是 :root 丢令牌）。豆哥让我回查 carbon：carbon 全仓 **110 处 `background: var(...)`**，`p-invite/p-feedback` 的页面容器就是 `background: var(--cs-page-bg)`，`.cs-btn-primary` 是 `linear-gradient(135deg, var(--cs-glow), var(--cs-glow-dark))` 渐变里直接嵌 var，线上真机正常。**不要为想象中的兼容性写硬编码兜底**（`_button.scss` 的品牌绿兜底已删），照 carbon 用 `background: var(...)`。
- **`--so-radius-full: 50%` 是正圆不是胶囊（2026-10-02「按钮圆弧太丑」）**：50% 是相对自身宽高的百分比，扁矩形上会渲染成**椭圆弧**（水平半径=宽一半、垂直半径=高一半）。carbon 的 50% 只用在**正方形**（avatar/splash 圆点/`.rounded-full`），胶囊药丸一律写死 **`999rpx`**（被 clamp 到短边一半=正圆角，`.p-index__tabbar-action` 就是）。已修 5 处扁矩形误用（底栏主按钮、so-page 重试/切换场景、profile 分享、风格页主题按钮），保留 50% 的只有 `.round`、头像、光斑。看 carbon 要看它**在什么形状的元素上用**，不只是"有没有用"。
- **首页导航栏：设置入口走 `#left` 插槽**（豆哥定），右侧是微信原生胶囊的地盘（so-custom 已做 padding-right 避让）。底栏主按钮尺寸照 `.p-index__tabbar-action--primary`：78rpx 高 / 190rpx 最小宽 / padding 0 24rpx / 24rpx 字。
- **页面样式归 `src/styles/06-pages/`，文件名 `p-*` 开头（2026-10-02 豆哥定，照 carbon 的 p-index.css）**：`.vue` 里不放 `<style>`。`_p-index.scss` / `_p-profile.scss` / `_p-test-theme.scss` 已在 `styles/index.scss` 接入。**类名前缀不变**（`so-index__*` / `profile__*` / `preview__*`，项目前缀是 so-，不改成 carbon 的 p-）。代价：失去 `data-v` 隔离 → **靠唯一前缀防冲突**，页面间不能撞类名；好处是 JS 注入的样式变量、给组件根传的 class 不用再靠 `:deep()`。组件样式（so-page/so-custom/so-demo-page）仍在组件内 scoped（属 05-components，不是页面层）。
- **`wx` 等端原生全局对象的声明在 `src/types/platform.d.ts`**（与 backup / carbon 同一份，迁移时漏了才补回来）：声明 `wx`(login/restartMiniProgram/showShareImageMenu)、`my`、`swan`、`tt`、`__wxConfig`。`@dcloudio/types` 不含这些；carbon 之所以裸写 `wx.login` 不报错，是因为**它压根不跑 type-check**（`package.json` 无 tsc 脚本）。superone 跑 `vue-tsc`，用到裸 `wx` 就先在这文件补（按需补，别引 `@types/wechat-miniprogram` 之类完整包，会与 `@dcloudio/types` 重复声明打架）。**注意别自己另建 wx 的 d.ts**——两个 `const wx` 会重复声明冲突。
- **演示态 = 「执行清单」宣传页 + 分享海报（2026-10-02 建，照 carbon 的 p-page__fallback）**：`so-demo-page.vue` 结构 = hero（eyebrow+56rpx 标题+描述+纯 CSS 清单视觉）→ 海报卡（**DOM 版预览，所见即所得** + 「生成分享卡」+ 离屏 canvas）→ 能做什么 → 怎么用 → 预览层（保存/转发/关闭）。海报能力在 `composables/usePosterShare.ts`（照 carbon 的 `usePosterShareCard`）：1080×1440、自适应字号标题 + 逐字换行省略、`generate`/`save`/`share`/`preview` 状态机。**两条约定**：① 页面上用 DOM 画一份、离屏 canvas 画一份，两份内容保持一致；② canvas 必须 `position:fixed; left:-9999px`（不占布局）。**不放二维码也不放封面图**（契约无生成码接口、项目无 static 目录，纯绘制）。canvas 不认 CSS 变量 → 海报颜色写死（carbon 同）。
- **页面外壳约定（2026-10-02 豆哥定）**：**所有页面必须包在 `<so-page>` 下，例外只有 profile 页**——自挂 `themeClass` 的 shell（同 carbon profile 的 `p-system-config-shell`），不进门控。原 settings 页 2026-10-02 已并入 profile 删除（跟 carbon 一致，只留一个设置类页面）。
- **统一样式体系（2026-10-02 建，参考 carbon 的 `05-components/button.css`）**：高复用外观进 `src/styles/05-components/`，页面 scoped 只留布局/间距。现有件：`_button.scss`（`.so-btn` + `-primary`/`-secondary` + `:active` + `[disabled]`，品牌绿保留 `#07c160` 硬编码兜底再叠 `var()`）、`_card.scss`（`.so-card` = elevated 表面+radius-lg，`.so-card--pad` 加内边距）、`_cell.scss`（列表行：icon+文本+右侧插槽，参考 carbon `p-system-config__item`，hover 用 `hover-class="so-cell--hover"`）、`_switch.scss`（原生 `<switch>` 尺寸统一；**color 属性写死 `#07c160` 不用 var()**，原生属性对 CSS 变量支持不稳且主色深浅同值）。
- **profile 页**（2026-10-02 建，**逐条照抄** `uni-carbon-space/src/pages/profile/index.vue` + `uni-superone-backup/src/pages/profile/index.vue`，不包 so-page）：用户信息卡（仅 wbbb===1：头像可换/昵称内联编辑/分享主页/注册时间）+ 菜单卡（联系客服 open-type=contact、链接菜单读 `systemConfig.linkMenu`、重新登录、界面主题 switch）+ 管理员面板 `v-if isAdmin`（**切换场景** = 只改本地 `systemConfig.wbbb` / **入口模式** = `setWbbb` 写服务器 / 用户行为统计 / 链接管理 / 用户列表分页）。**命名照抄 carbon+backup，不自造词**（曾自造「真实模式」被豆哥否）。
- **演示/真实切换照 carbon，不做全局悬浮件（2026-10-02 豆哥定）**：`so-admin-switch.vue`（全局悬浮胶囊）已删除。carbon 的 `cu-page.vue` 把入口放在**演示/兜底内容里**（`v-if="admin"` 的「切换模式 {{ wbbb }}」按钮）；superone 对应地放在 `so-page.vue` 的 reverse 演示分支底部 `.so-page__admin-card`，文案「切换场景 {{ wbbb }}」，调 `store.setWbbb()`（与 profile 管理员面板共用同一 action，不新增状态源）。普通页的 `#locked` 态不给入口（同 carbon）。
- 抄页面前先核对契约能力能否对上（`userApi.updateUser/getUserList`、`commonApi.updateSystemInfo(wbbb|linkMenu*)/getUserBehaviorStats`、`uploadImage`、`CacheManager.remove(TOKEN)`+`getLoginAdapter().login()`）；superone 无 `cu-input`/`cu-empty-state`/webview 页，用原生 `input` 与占位文案替代。
- **uni switch 的坑**：`@change` 事件签名是 `Event`（没有 `SwitchChangeEvent` 类型），自定义 `{detail:{value}}` 参数过不了 type-check；写法 `function onXxx(e: Event)` + 函数内 `(e as unknown as { detail: { value: boolean } }).detail.value`。
- ~~**真机 vs 模拟器渲染差：原生 button 对 `background` 里的 var() 支持不稳**~~ → **作废（2026-10-02 证伪）**：浅色下「按钮白字落白底消失」的真因是令牌挂在 `:root` 上被整条丢弃，不是 var 在 background 里的问题。carbon 110 处 `background: var(...)` + 渐变内嵌 var 线上正常。**不要为想象中的真机兼容性写硬编码兜底**，先回查 carbon 怎么用。
- **小程序端不支持动态组件**：模板里写 `<component :is>` 编译直接报错 `is not supported`。模块分派要按 key 写成显式分支（加模块在模板加一支），别指望配置数组 + 动态组件。
- **工具类定义缺口要靠脚本扫**：比对「模板用到的 `so-*`」与「styles 里定义的 `so-*`」——2026-10-02 据此扫出 `.so-bg-elevated`/`.so-text-disabled` 有引用无定义（首页卡片实际无背景色，这才是浅色不可见的真因，而非"白卡白底"）。
- **契约以 git submodule 挂在 `uni-superone/src/contracts`**（契约仓无 src 层，根即 `index.ts`）。**submodule 必须挂在 `src/` 内**：uni 插件自带 `@`→src 别名且优先级高于用户 alias，挂仓库根会解析失败；tsconfig paths 能过，**必须真跑 `build:mp-weixin`** 才暴露。验证要防 tree-shake 假阳性（临时在 `main.ts` 使用并 grep dist 特征串，测完还原）。
- 前端不再复制 `src/types`/`src/apis`，一律从 `@/contracts` 取。`.gitmodules` 用 `branch = release`；契约仓只留 `package.json`+`tsconfig.json`。契约侧出 `HttpClient`（返回 `ApiResponse<T>` **信封**），各端注入 `createXxxApi(http)`。**改契约要先提交并推 `frontend-contracts`**，superone 侧单独提交。
- **契约仓目录**：根为 `index.ts`+`types/`+`apis/`+`request/`+`openapi/`+`scripts/gen.mjs`。`types/<domain>.ts` 类型与枚举合一；`openapi/*.yaml` 9 个全保留（豆哥明确不删），apis 当前只生成 user。**生成器边界**：yaml 的 200 是 `StandardResponse` 信封、`data` 无内层类型，全量生成会丢精度，故只取路径/方法/operationId/请求体 schema 名，内层绑手写类型，绑不上退化 `unknown`；扩域往 `main()` 的 yaml 列表加。
- **导航栏「居中」= 屏幕中线居中**（2026-10-02 修标题偏左）：微信胶囊在右侧，标题容器左右留白必须**对称**（`gap = max(胶囊占位, 左侧动作占位)`，left/right 同值），不能「左留一点、右留整个胶囊宽」——那样容器内部 `justify-content:center` 居中在偏左区间。carbon 的 `.cu-bar .content` 是 `width:calc(100% - 440rpx) + margin:auto`（左右各 220rpx）。坑：bar 上的 `padding-right` 管不到绝对定位的标题（包含块是 padding box，边界不受 padding 影响）。
- **小程序 UI 文案也套豆哥的禁用清单**（2026-10-02）：无「你」、无破折号、无「不是…而是…」、不排比不煽情，给具体年份/数字/条款。写名人案例时**不编造其未公开的东西**（如巴菲特没有公开清单原件，只能写他可核查的条式用法）。
- **已知技术债（暂不改）**：request ↔ login 静态环（Rollup 报 Circular chunk）。运行期安全（`noRetry: true` 挡递归）。根因是 `request.ts` 底部自注册 `setAuthRefresher`；解法是把注册移到启动处、删掉对 login 的 import。

## beannote 内容（豆小匠）
- **行为规范只在 skill 里，不写进业务仓文档**（2026-09-08 定）：`docs/` 只描述「项目是什么样」（`项目说明.md`/`账号定位.md`/`content-playbook.md`）。
- 目录：`topics/`（唯一生产区，一篇一目录）/`knowledge-base/`/`data/`/`docs/`。**每篇一个 `manifest.yaml`**（唯一状态源：`status`/`conclusion`/`decisions`/`blockers`/`slots`/`next`；`status` 须与目录名前缀一致），改完重跑 `business-repo/beannote/script/gen_index.py` 重建 `topics/索引.md`。
- 一篇一目录 `topics/{状态前缀}{日期}_{主题}/`：无前缀=在制、`done-`=已发布、`drop-`=已归档；路径建后不变，只在发布/废弃时同层改名。**月份归档**：`topics/` 根只放当前月，跨月按选题记录日搬进 `topics/YYYY-MM/`。
- 槽内固定前缀：`01_选题卡` `02_脚本` `03_正文` `04_发布稿` `05_检查清单` `06_复盘` + `assets/`；缺哪号=卡在哪步。最小充分：公众号 01/04/05，小红书 01/02/03/05，06 有反馈才写。
- 历史复盘里的旧路径（`02_topic_pool/TODO_*`）保留不回改。`docs/content-playbook.md`（账号定位）优先级高于 skill 旧规则。
- 投资认知内容：反口号说教，讲清「测量方法+背后道理」，给阈值不堆公式，老实交代局限。标题偏好：痛点实操/案例拆解/反常识/数据清单。
