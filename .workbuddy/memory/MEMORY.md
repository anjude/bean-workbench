# 项目长期记忆（bean-workbench）

## 工程结构
- 多子模块工程。业务仓：`backend-superone`（Go+Gin+GORM）、`uni-superone`（微信绿"豆流便签"前端）、`frontend-contracts`（契约源：openapi yaml + types + apis，以 git submodule 挂 `uni-superone/src/contracts`）。
- 测试库硬编码共享远程库，DDL/写操作须用户"继续"逐项授权；迁移 `go run ./scripts/migration -action=exec-sql -sql-file=<path> -env=test`。
- 分支：dev 开发、就绪合 release；**开发阶段不擅自 commit，保持未提交工作区**，等"提交/合 release"再动。子仓改动须 push 远端后才可 bump 父仓子模块指针。

## 环境
- macOS arm64。助手 Bash PATH 不完整：`go` 用 `~/sdk/go/bin/go`，`brew` 用 `/opt/homebrew/bin/brew`；判"没装"前先排除 PATH。
- `make check` 跑 `script/check-workbench.py`（必需文件 + skill 命名一致 + md 相对链接失效）。backend-superone 仍是 Windows 脚本，非明确需求不动。

## skill
- 实体在 `.agents/skills/`，`~/.agents` 是指向它的外链；改动全局生效，台内试用先 `git stash push -- .agents`。
- 编号 `{前缀}-{阶段号}{序号}-{后缀}`；`dev-flow-*` 四阶段 00→01→02→03（必过 00 与 03）；`wb-*` 是唯一不跑流水线的例外（wb-router/skill-refactor/handoff）；`bn-*` 已归档。
- 写法：正面表述、只给框架与步骤、不把单次顺手行为固化成 skill 规则。

## 代码复杂度（豆哥定）
- 一套设计只解决一个问题，不叠加第二套解法；"要不要留缝"默认不留（直接调用 > 端口+接线）；提新抽象前先确认删掉老方案仍成立；顺手清未使用字段/单调用者中间方法。
- **backup 是线上跑着的代码，默认按「它是对的」处理**（2026-10-02 豆哥纠）。说「既有实现有 bug / 有缺陷」之前必须把原文拉出来**核到具体行**，确认它的依赖链真的断了；推断出来的「bug」基本是我漏看了某个隐式前提（如 `reactive()` 深代理提供的响应式）。判断错了要在 process 文档与记忆里明确更正，不能悄悄改口径。

## 目录与文档约定
- **走 dev-flow 的开发需求，方案文档一律落 `task/dev-flow/YYMMDD_{主题}/README.md`**（不是 `task/` 根；`task/dev-flow/README.md` 只做索引，`task/registry.md` 是完整登记表）。建目录前先核对这两个索引，别照 SKILL.md 里可能泛化的写法直接建。不往业务仓 docs/ 新增。活跃文档改名须同步 `AGENTS.md`/SKILL.md/引用并跑 `make check`。
- `handoff/` 是一屏快照（最新一份）；`process/` 是 topic 维度思考过程（做了什么/结论/被推翻判断/待核），纵向只增不改。

## carbon / 边界
- 暖色品牌（米白 #f5f0ea + 琥珀 #f0a050），无红绿独立色；两人留痕空间，禁已读未读/强提醒/催回复/任务式推进。

## uni-superone 前端（豆流便签）
- 微信绿主色 #07C160；令牌 `--so-*`，主题类 `.theme-light`/`.theme-dark`。视觉/布局以 carbon 首页为样板（rail+swiper+底部操作栏+主按钮遥控+反受控弹层+高度链），不自创。
- **首页高度链**（塌陷过两次，改这块必查）：`.so-index` 必须 `display:flex; flex-direction:column`，否则子元素 `.so-index__workspace` 的 `flex:1` 静默失效 → swiper 撑不开 → 模块面板被裁成空白（不报错）。完整链：so-index(flex column, 100vh-nav) → workspace(flex1) → main(flex1) → swiper(flex1) → swiper-item(100%) → 面板 scroll-view(px)。**用 flex:1 的地方父级必须真是 flex 容器**。
- **关键真机坑**：① 令牌只能挂 `page` 与主题类，**禁用 `:root`**；② `page` 不设主题背景，背景交给页面根容器；③ 用 `background: var(...)`，不要为想象中的兼容性写硬编码兜底；④ 不支持动态组件 `<component :is>`；⑤ 弃用 `uni.getSystemInfoSync()`，改用 getWindowInfo/getAppBaseInfo/getDeviceInfo。
- 页面包 `<so-page>` 门禁（profile 除外）；原生全局对象声明在 `src/types/platform.d.ts`（用到裸 `wx` 在此补，别另建 d.ts）。详细设计见 `task/261002_superone-modules/` 与 process 文件。
- **契约子仓更新**：`uni-superone/src/contracts` 是 uni-superone 自己的子模块（release 分支），不是父仓的直接子模块——父仓 `git submodule status` 看不到它。更新方式：`cd business-repo/uni-superone/src/contracts && git fetch origin release && git merge --ff-only origin/release`，改完 uni-superone 会多一个「M src/contracts」待提交。**查契约前先确认这个指针**，别只看父仓。
- **子日志（跟进）四条接口边界**（2026-10-02）：① 列表只返「纯根」或「纯某父的子」，分页 total 只数当前层级；② `TopicLogListItem` **无 child_count** → 父层列表拿不到子条数，要拿只能逐条查（N+1），所以主题详情页不显示跟进数；③ `UpdateTopicLogReq` **无 parentLogId** → 层级创建后固定，不能挪；④ `DeleteTopicLog` **不级联** → 删根记录会留下孤儿子记录（仍在库、但失去入口），删除功能因此没做。后端支持任意层级，UI 只做两层。
- **登录只在「响应返回未登录码」时触发**（2026-10-02 豆哥定）：`utils/request.ts` 的 `handleLoginExpired` 命中 `LOGIN_EXPIRED_CODE(-100004)` 才 `reloginOnce()` 换 token 并重放（并发去重）。**任何地方都不要主动调 `getLoginAdapter().login()`**（`stores/app.ts` 的 init 里那次已删除）。
- **topic 模块（首个功能，2026-10-02）**：首页 PANELS 首位，面板 `biz-topic-panel`（行式+分隔线、无搜索、三态+refresher+canLoadMore 防抖）+ 详情页 `pages/topic-detail/index`（hero 属性区 + `so-timeline` 按天分组、竖线用伪元素、圆点只有 mark 位掩码命中才上语义色）。三态组件 `so-empty-state`/`so-loading-state`（照 carbon 结构、样式重写，carbon 那两个 CSS 有 bug）。时间收在 `utils/time.ts`（**后端时间戳是秒级**）；`getNavigationBarHeight()` 收在 `utils/layout.ts`。**要看 topic 必须先切真实态**——`so-page` 门禁下非真实态首页走演示页、普通页显示「开发中」。
- **topic 契约约束**：`topic/list` 只给 id/名称/描述/时间/top（无条数无统计）；`topic/detail` 同 item；`topic/log/list` 支持 `topicIds[]` 批量（要「最近一条预览」就靠它，但条数不精确别显示）。`top` 是**时间戳非布尔**，`mark` 是**位掩码**；排序统一在读取出口（top DESC + createTime DESC）。
- **markdown 两条路，别混**：① **展示**走 AST 不碰 HTML——`utils/markdown.ts` 用 `marked.lexer` 摊平成 `MdBlock[]` → `so-markdown`/`so-md-inline` 渲染（存储与展示全是 Markdown，`html` token 当纯文本）。② **编辑器**走 backup 原生 `<editor>` 的 HTML 往返——`utils/md-html.ts` 的 `markdownToHtml`/`htmlToMarkdown`。编辑区内是 HTML，出编辑区立刻是 Markdown，两者不交叉。
- **编辑器是照搬 backup 的**（2026-10-02 豆哥三次否掉我另起炉灶的三次实现后拍板）：`so-md-editor.vue` + `so-md-editor-toolbar.vue` + `utils/md-html.ts` 都是从 backup 整份复制后改主题改 bug。**教训：要改既有实现，先整份搬过来跑通，再谈优化。** 图标字体与编辑器皮肤在 `styles/07-vendors/`（iconfont.css / md-editor.css），已接入 `index.scss`。
- **编辑器三个已修的坑**：① `uploadImage()` 返回的是 `WxUploadResp` 对象，地址在 `.url`，不是字符串（backup 的 `ImageUploadUtils.uploadImage(): Promise<string>` 直接给 URL，两边签名不同）；② 敲完字 100ms 内点完成/失焦会丢最后几个字，**完成/失焦前必须先 flush**（`commitInput`/`flushInput`）；③ 工具栏的 `activeEditor` 要依赖显式响应式数据——本项目 app store 是 pinia，没有 backup 那种 `reactive(globalData)` 可挂，所以 `editor-manager` 导出 `activeEditorId` **ref**。
- **编辑器管理器是模块级单例** `utils/editor-manager.ts`（替代 backup 的 `app.globalData.editorManager`）。工具栏不接 props，全部状态从「当前激活编辑器实例」读，按钮直接调实例同名方法；本项目**没有全局浮动工具栏**，一律内嵌在编辑器下方。
- **原生 editor 的能力边界（换不走，backup 也有）**：支持标签里**没有 pre/code/blockquote** → 代码块退化成纯文本、引用退化成段落、表格退化成文本、分割线退化成空行（编辑旧记录再保存会丢这些结构）。**EditorContext 没有 focus 方法**，不能自动弹键盘。待办 `format('list','check')` 支持但豆哥不要。
- **markdown 排版两条**：段落/引用/列表内容**不要 `display:flex`**，让 `<text>` 片段保持行内流动（flex 会把每个片段变独立盒子，长句整段跳行）；`word-break:break-all` 挂 `.so-md` 根部靠继承防长串撑破。
- **跨仓照抄样式：令牌按数值换算，不按名字对号**（2026-10-02 教训）。backup 的 `--radius-sm/md/lg/xl` = 6/8/12/16rpx，我们的 `--so-radius-sm/md/lg/xl` = 12/20/28/40rpx，**同名差一倍以上**。曾把 backup 的 `--radius-lg`(12rpx) 直接换成 `--so-radius-lg`(28rpx)，60rpx 的按钮方块被圆成近圆形，整排工具看着像一串徽章。正确映射：backup 那套 md/lg/xl 统一落 `--so-radius-sm`(12rpx)，backup `--spacing-lg`(20rpx)→`--so-space-md`(24rpx)，`--spacing-md`(16rpx)→`--so-space-sm`(16rpx)。
- **功能页不要套落地页视觉**（2026-10-02 豆哥纠「太夸张，和品牌调性不符」）。曾给主题详情页套了 carbon 的 hero：eyebrow + 44rpx 巨标题 + 卡片阴影 + 一排胶囊占位按钮 + 三层卡堆叠。superone 的调性是干净克制、**靠细边框+轻阴影分层、不靠重色块**，对标微信/滴答清单的工具页。做法：分区标题用 28rpx medium + text-secondary，不与正文抢重量；状态标签并入元信息行，不独占一行。**抄 carbon 只抄布局分区思路，不抄它的营销视觉。**
- **卡片层级：页面 `--so-bg-secondary`、卡片走 `.so-card` 默认（elevated）**，即移动端主流的「灰底白卡」。**不要反着做「白底灰卡」**（2026-10-02 试过，豆哥一句「好丑，好割裂」）。要「协调」靠的是：同层级卡片 **去投影**（投影留给浮层）+ **块间距收紧**（16rpx，让多张卡读作一组而不是几块飞板），不是靠反转明暗。
- **卡片必须成组**（2026-10-02 豆哥纠「整个页面只有输入框一张白卡怪奇怪的」）：页内卡片 ≥2 张且同一层表面（主题详情页 = 头部卡 + 输入卡 + 记录卡）；去掉多余的某张可以，但**去到只剩一张就过头了**。卡内边距：普通卡 24rpx；**包着自带边框的编辑器那种卡用 16rpx**，否则嵌套太厚。需要覆盖卡片外观时只在 06-pages 里写 `.p-topic-detail .so-card`，不动 `.so-card` 统一件本身（会影响 profile/test-theme/首页占位面板）。

## beannote（豆小匠）
- 行为规范只在 skill，文档只描述项目本身。`topics/` 一篇一目录 + `manifest.yaml` 状态源；槽位 `01_选题卡`…`06_复盘`。投资认知：反口号说教，讲测量方法+背后道理，给阈值不堆公式。

## 测试服务器 8.155.38.83（backend-superone 部署机）
- 已配免密（`ssh root@8.155.38.83`，id_ed25519）。hostname `milk2025`，Ubuntu 22.04。
- **规格极小**：2 vCPU、内存 **1673 MB**、**swap 0**（`swappiness=0`）、磁盘 40G、**直读仅 27.7 MB/s**。常驻 supervisor 8 个服务 + docker 5 容器（mysql 单容器 418MB 占整机 25%）。
- **构建失败的真因不是 CPU 不够**（静置 100% idle）：磁盘慢 + 无 swap 抖动 + `deploy.sh` 的 `run_with_timeout 300` 太短。温缓存 `go build` 实测 >10 分钟，超时必被 SIGTERM 杀掉。
- **⚠️ 全量重编会把这台机器打崩**（2026-10-02 亲测，无 swap 时）：改 `CGO_ENABLED` 等会改变构建缓存键 → 缓存全失效 → 全量重编 → 内存耗尽 → **系统挂死重启**（journal 断写 9 分钟，内核无 OOM 记录因为抖到写不出日志）。**已有 2G swap 后不再复现**。
- **加完 swap 的实测耗时**：冷构建（独立 GOCACHE 全空）**222s**、缓存失效后首次 126s、**增量 11s**。产物 54.96MB→38.27MB。`deploy.sh` 超时定在 **600s**。提速最大头是 **`CGO_ENABLED=0`**（去掉 gcc 外部链接，原 link 单步就 10 分钟以上），不需要 `-p 1`。
- **Dockerfile 目前没在跑**：`superone:latest` 镜像创建于 18 个月前，无任何容器用它；superone 实际由 supervisor 起宿主机二进制。`make build` 那条 docker 路是休眠状态。
- **重启后 superone 不会自恢复**：supervisord 开机即拉所有程序，docker 的 MySQL 还没就绪 → superone 报 `dial tcp 127.0.0.1:3306: connect: connection refused`，重试耗尽转 FATAL 不再自拉。已装自愈兜底：`/usr/local/bin/so-recover.sh`（等 supervisorctl 可用 → 等 3306 端口最多 7.5 分钟 + 20s → 重启 5 个依赖 DB 的服务 → 复核，仍有 FATAL 再拉一次），由 crontab `@reboot` 触发，日志 `/var/log/so-recover.log`。
- **每日凌晨 3:06 自动重启**（豆哥要求）：crontab `6 3 * * * /usr/sbin/reboot`（`/usr/sbin/reboot` 是 systemctl 的软链；时区 Asia/Shanghai）。**这条能安全运行全靠上面的 `@reboot` 自愈，两者必须成对存在**——没有自愈，每次重启都会让线上服务挂到人工介入。
- 部署两路径：`make build` → docker build；`deploy.sh test` → 宿主机 `go build` + `supervisorctl reload`（失败发企微告警）。`deploy.sh` 里已无 `go mod tidy`。
- **新增依赖不需要上服务器跑 `go mod download`**（已实测）：Go 1.16+ 默认 `-mod=readonly`，`go build` 会自动下载 go.mod 里已声明的模块，但不会自动补写 go.mod。依赖由开发者本地 `go get` 后连同 `go.mod`/`go.sum` 一起提交即可。漏提交会明确报错（`no required module provides package xxx` / `missing go.sum entry`），不会静默带病上线。
- 已知待改项：删掉每次部署的 `go mod tidy`、超时 300→1800、加 2G swap、宿主机 `CGO_ENABLED=0`（Dockerfile 才是 0）、宿主机 Go 1.21.4 升到 1.24.5（go.mod 要求 1.24）、`go build` 加 `-ldflags="-s -w"`、Dockerfile 基础镜像换 1.24-alpine 且 `go.mod`/`go.sum` 要先于源码 COPY。详见 `task/workbench/261002_测试服务器构建优化/`。
- **远程排障坑**：① `pkill -f "<pattern>"` 会匹配承载命令的 shell 自身导致 SSH 断连（exit 255），先取 PID 再 kill；② 内存被打爆时 **TCP 能连、ping 通，但 sshd 不发 banner**（`Connection timed out during banner exchange`），此时应等待内存释放而非反复重连，恢复后用 `uptime` 的 "up N min" 判断是否重启过。
- 装 Go 不用联网下 tarball：模块缓存里的 `golang.org/toolchain@v0.0.1-goX.Y.Z.linux-amd64` 就是完整 SDK，`cp -r` 到 `/usr/local/go` 后 `chmod -R u+w` 即可（toolchain 模块文件默认只读）。
