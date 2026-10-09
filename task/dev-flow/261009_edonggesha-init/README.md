# 261009 鹅懂个啥小程序初始化

## 目标

建立「鹅懂个啥」独立小程序的开发上下文，先完成产品定位、初始化方案与品牌图片归档，再开展项目初始化。

## 产品定位

- 名称：鹅懂个啥。
- 体验：开心玩，顺便认识自己。
- 内容方向：趣味测试（包括类似 MBTI 的性格玩法）和小游戏。
- 品牌形象：一只好奇、爱玩、也不装懂的鹅；产品表达保持轻松，不使用沉重的自我定义叙事。
- 长线愿景：借有趣的测试与互动，让人更理解自己和他人的相处方式，愿意走近彼此、互相接受；爱情是其中一个方向，不将产品限定为恋爱测试。

## 小程序介绍

> 鹅懂个啥？和一只好奇的鹅测测性格、玩玩小游戏。先玩个开心，顺便发现不一样的自己。

## 体验设定

- 核心顺序是先玩得开心，再从测试或游戏结果里得到一点关于自己的新发现。
- 2026-10-10 鹅BTI 首次实际体验反馈：用户认为「小现场 + 凭第一反应选择」有代入感；后续测试可沿用这种场景化表达，但应设计各自的情境主题、节奏与结果，不把不同测试做成同一题库的换皮。
- 趣味测试和小游戏并列呈现；品牌名称与主视觉不绑定单一玩法。
- 当前对外只使用「趣味测试」等表述；原计划的抽签类玩法暂不纳入当前产品范围，后续若恢复须按实际功能重新评估平台规则和类目。
- 「帮助全人类认清自我」「SI 时代迷失、找不到意义」是讨论产品时的玩笑式背景，不作为严肃的产品使命或对用户的承诺。
- 面向用户的文字保持轻巧、好奇、有幽默感；吉祥物以「懂个啥」的自嘲口吻陪用户探索。

## 微信服务类目准入

- 注册主体：个人主体。
- 2026-10-09 核对[微信官方小程序开放类目表](https://developers.weixin.qq.com/miniprogram/product/material/)：个人主体开放类目中没有与当前规划的趣味测试和小游戏相匹配的服务类目。
- `工具 > 信息查询`面向信息查询服务，不能用来代表本产品的实际内容；现阶段不建议为了提交审核而选不匹配的类目。
- 当前准入问题待解决：若保持上述产品方向，需评估符合资质的非个人主体及各玩法对应的微信类目和审核材料；最终以微信公众平台提交时显示的类目与要求为准。实际功能须与申报类目一致，仅调整文案不能替代准入审核。

## 注册形态判断

- 「鹅懂个啥」以趣味测试、结果展示和内容导航为主体，技术上拟复用 uni-app 页面框架，优先按普通小程序规划。
- 微信[小游戏开发指南](https://developers.weixin.qq.com/minigame/dev/guide/)将小游戏定位为游戏应用；[小游戏运营规范](https://developers.weixin.qq.com/minigame/product/)要求开发小游戏选择游戏类目，且选定后不能改为其他小程序类目。因此不把整个测试产品注册成小游戏。
- 若后续独立推出真正的游戏产品，再单独评估小游戏账号、类目和所需资质；当前计划中的游戏内容也需在实现前核对普通小程序平台规则。
- 注册形态建议不解除个人主体类目的准入卡点：当前不应为了上线测试功能而选择不匹配的服务类目。

## 范围

- 本任务记录独立小程序的初始化方案、品牌资源、技术复用判断及后续开发过程。
- 业务仓：`business-repo/uni-gknow`（GitHub：`git@github.com:anjude/uni-gknow.git`），开发与生产统一使用 `release` 分支。
- 技术框架参考 `business-repo/uni-superone`；UI 与 UX 独立设计。
- 本地素材库约 1.0 GB，存放测试与 H5 小游戏候选源码，供后续挑选、组合和二次开发；源码不纳入 Git。
- 原始素材位置：`/Users/bean/workspace/bean-workbench/source/local-source/h5-game-library/`（工作台共享目录，由根 `.gitignore` 忽略，不属于某一个任务）。目录职责见 `source/README.md`。
- 后续挑选或二次开发时，先将需要的内容复制到任务或业务仓工作目录，保持原始素材不变。
- 微信小程序头像资源已归档于 `assets/`。

## 初始化方案

### 目标与边界

- 本次将 `business-repo/uni-gknow` 初始化为 Vue 3 + TypeScript 的 uni-app 微信小程序工程，只支持微信小程序。
- 微信小程序 AppID：`wx5feedb4268569b68`（用户于 2026-10-09 提供）。
- 复用 `uni-superone` 的工程版本、目录分层、页面容器与导航栏的实现思路；组件改用 `gk-*` 前缀，视觉令牌独立定义。
- 首页只承载品牌介绍与「趣味测试」「小游戏」两个内容方向。玩法、题库、结果算法、用户体系和服务端接口本次不开发。
- 不复制 Superone 的 AppID、业务页面或品牌 UI；页面门禁按后续产品需求采用 `wbbb || admin` 规则。
- 门禁关闭时使用现有首页内容作为 demo；管理员或入口模式开启时使用独立的正式版首页占位，不展示 demo。
- 共享协议在 `business-repo/frontend-contracts` 唯一维护；`uni-gknow` 按 `uni-superone` 的配置挂载 `src/contracts` 子仓，跟随 `release` 分支，客户端通过 `@/contracts` 导入，不复制契约文件。

### 文件级改动

| 范围 | 落点 |
| --- | --- |
| 工程配置 | `business-repo/uni-gknow/package.json`、`vite.config.ts`、`tsconfig.json`、`.gitignore` |
| 小程序入口 | `src/main.ts`、`src/App.vue`、`src/pages.json`、`src/manifest.json`、`src/uni.scss`、`src/env.d.ts` |
| 通用能力 | `src/components/gk-page.vue`、`gk-header.vue`、`gk-loading-state.vue`、`gk-empty-state.vue`、`src/composables/useTheme.ts` |
| 视觉与首页 | `src/styles/**`、`src/pages/index/index.vue`、`src/pages/settings/index.vue`、`src/static/brand/avatar.png` |
| 使用说明 | `business-repo/uni-gknow/README.md`、`AGENTS.md` |

### 页面原型与状态

- 原型：轻量内容入口。首页先说明「开心玩，顺便认识自己」，再展示两类内容；当前均为筹备状态，不提供失效的跳转按钮。
- `gk-page` 支持 `ready`、`loading`、`empty`、`error` 四态及对应插槽；错误态提供重试事件。首页当前使用 `ready`，未来接入内容数据时复用状态分支。
- 原始头像从任务资产复制到业务仓；素材库只以文档路径引用，不接入工程构建。

### 验收与风险

- `npm run type-check` 与 `npm run build:mp-weixin` 可执行。
- 编译产物使用 gknow 自己的 AppID 与后端环境配置；页面门禁按 `wbbb || admin` 判断。
- 微信 AppID 已写入 `src/manifest.json` 的 `mp-weixin.appid`。
- 个人主体的服务类目准入仍按上文处理，工程初始化不代表可提交审核。

### 检查场景

| 类别 | 场景 | 预期 |
| --- | --- | --- |
| 功能 | 管理员关闭入口模式 | 管理员仍可访问正式页面 |
| 功能 | 非管理员关闭入口模式 | 显示首页 demo；测试与小游戏可实际试玩，设置页显示准备中 |
| 功能 | 非管理员开启入口模式 | 可访问首页、测试、游戏和设置页 |
| 功能 | 管理员或入口模式开启 | 首页展示正式版占位，不出现 demo 内容 |
| 功能 | 打开首页 | 显示鹅形象、产品介绍与两个内容方向 |
| 功能 | 页面处于加载、空、错误态 | 对应反馈可见；错误态可触发重试事件 |
| 回归 | 检索工程配置 | 不含 Superone AppID 和业务页面 |
| 兼容 | 微信小程序构建 | 可生成 `dist/build/mp-weixin` |

## 边界

- 新业务子仓接入时，按工作台规则同步检查 `business-repo/` 索引、路由、知识库与任务登记。

## 图片资源

| 文件 | 用途 | 状态 |
| --- | --- | --- |
| `assets/logo-concept.png` | 带品牌字样的透明背景 Logo 概念图 | 字样与视觉尚待正式设计校核 |
| `assets/avatar-source.png` | 无文字鹅头像高清源图 | 已生成 |
| `assets/avatar-144.png` | 微信小程序头像上传版，144 × 144 PNG，26 KB | 已按用户提供的尺寸与大小要求制作 |

![鹅懂个啥头像](assets/avatar-144.png)

## 当前状态

初始化工程、demo 游戏与测试、结果分享海报、契约请求基础设施、启动数据门禁和设置页均已落地；正式首页已改为品牌主视觉与可继续扩展的测试陈列区，首项接入第一版「鹅BTI」六场景测试及带小程序码的可选海报，微信小程序可构建。上架类目准入仍待解决。

第一款正式玩法暂定名为「鹅BTI」（谐音「2BTI」）；素材库与网上案例调研、候选玩法和首发验证假设见[《鹅BTI · 第一款正式玩法方向研究》](鹅BTI-方向研究.md)。

三个方向的具体体验、内容样片、首发与朋友回流阶段安排见[《鹅BTI · 三段式玩法方案》](鹅BTI-玩法方案.md)。

第一阶段四张鹅格结果卡与六道情境题见[《鹅BTI · 第一阶段内容样片》](鹅BTI-第一阶段内容样片.md)。可玩版已接入正式首页，聚焦测试趣味和带小程序码的可选结果海报；群聊操作与朋友猜测留给后续，分享和额外互动不作为看结果的条件。

## 落地记录

- `business-repo/uni-gknow` 已建立 uni-app + Vue 3 + TypeScript 工程、`gk-*` 页面组件、主题样式和品牌首页。
- 2026-10-09：`npm run type-check`、`npm run build:mp-weixin` 均通过；生成的 `dist/build/mp-weixin/project.config.json` 包含 AppID `wx5feedb4268569b68`。
- 已用微信开发者工具打开 `dist/build/mp-weixin`，iPhone 12/13 模拟器显示首页、品牌头像与两张筹备卡片；窄屏标题换行已调整。
- 本轮最终范围为微信小程序；早期方案中的 H5 预览已按用户最新要求移除。
- 启动门禁已接入微信登录、用户资料和系统信息接口；测试与小游戏本身仍使用本地数据，未改动数据库或协议仓。真机调试及平台审核尚未验证。
- 后续协作分工：Agent 只做类型检查与微信小程序编译，页面功能由用户验证；持续编译与一次性构建的命令见业务仓 `README.md`。

## 沉淀候选

- 从现有 uni-app 项目抽取可复用框架、同时保持新产品视觉独立的做法。
- H5 小游戏向微信小程序改造时反复出现的适配问题。

## 示例游戏方案：鹅眼快手

### 来源与改造

- 参考原始库 `source/local-source/h5-game-library/400多套h5微信朋友圈小游戏源码/games/zuiqiangyanli/` 的「记住目标位置、交换遮挡物、猜目标」规则。
- 参考同库 `games/shouzhi/` 的「限时连续点击」规则。
- 两段合为一个小程序示例游戏：先完成三轮找鹅，再进行 10 秒拍鹅掌挑战；按找鹅与连点成绩计分，结算时展示分级勋章、本局成绩和本地个人最佳。规则与界面重新实现，不复制原 H5 的代码、图片、统计、广告和分享链接。
- 原始库保持不变；该示例可作为后续游戏玩法改造的参考。

### 页面与状态

- 原型：沉浸式单页游戏，首页小游戏卡片是唯一入口。
- 页面：`src/pages/game/goose-quick/index.vue`；游戏状态与计时封装于 `src/composables/useGooseQuickGame.ts`；样式放 `src/styles/06-pages/_goose-quick.scss`；`src/pages.json` 注册路由；首页卡片改为可进入。
- 状态：介绍／找鹅展示／交换／等待猜测／揭晓／拍掌准备／10 秒计时／结算。交换时禁用选择，揭晓后自动进入下一轮；退出页面时清理计时器。结算主按钮收下成绩并回首页，重玩需明确点击次要按钮。
- 无网络、登录或服务端数据；失败回退为「再玩一次」，小程序生命周期离开页面时停止本轮计时。

### 验收与分工

- Agent 运行 `npm run type-check` 与 `npm run build:mp-weixin`，确认游戏路由和资源生成。
- 用户在微信开发者工具中验证实际页面、动画、触控和玩法手感；Agent 不代替用户验收页面功能。

| 用户验证场景 | 预期 |
| --- | --- |
| 首页点击「小游戏」 | 进入「鹅眼快手」介绍页 |
| 找鹅三轮 | 展示目标、交换杯位、允许猜测并揭晓 |
| 10 秒拍掌 | 连点计数并显示当前积分，时间结束进入结算 |
| 结束缓冲 | 时间到先显示「收手啦」提示，结算操作短暂拦截点击，避免连点误触 |
| 结算 | 展示勋章、本局积分、找鹅成绩和本地个人最佳 |
| 收下成绩或重玩 | 主按钮回首页；明确选择重玩后重置成绩并开始第一关 |
| 生成游戏海报 | 海报显示本局勋章、积分、找鹅与拍掌成绩，可分享或保存 |

### 落地记录

- 2026-10-09：已实现 `src/composables/useGooseQuickGame.ts`、`src/pages/game/goose-quick/index.vue`、`src/styles/06-pages/_goose-quick.scss`，并从首页小游戏卡片接入。
- `npm run type-check`、`npm run build:mp-weixin` 均通过；生成的 `app.json` 含 `pages/game/goose-quick/index`，构建包约 220 KB。
- 页面交互与手感按本项目分工留给用户在微信开发者工具中验证；本轮未运行模拟器。
- 2026-10-09：新增「今天你是哪款鹅」六题趣味性格测试，参考库中 `games/weidao/` 连续选择题后分流至多种结果的结构；题目和结果重新编写，代码位置见下方方案。
- `npm run type-check`、`npm run build:mp-weixin` 均通过；`dist/build/mp-weixin/app.json` 包含 `pages/quiz/goose-style/index`。
- 按项目分工，本轮没有在模拟器中代替用户验证题目交互。

## 性格测试示例方案：今天你是哪款鹅

### 来源与改造

- 参考原始库 `source/local-source/h5-game-library/400多套h5微信朋友圈小游戏源码/games/weidao/` 的连续选择题与多结果分流结构，目录标题为「你在别人眼中味道」。
- 改成 6 道日常偏好题，按选择汇总为四种轻松的「鹅系玩家」：探路鹅、观察鹅、气氛鹅、松弛鹅。
- 只参考交互结构，题目、结果文案和视觉重新设计；不复制旧测试的性别入口、远程图片、外链、追踪或分享代码。结果作为娱乐内容，不声称是严肃测评。

### 页面与状态

- 原型：单题逐步作答，完成后显示结果卡片，可重新测试或返回首页。
- 页面：`src/pages/quiz/goose-style/index.vue`；题目和结果数据放 `src/data/gooseStyleQuiz.ts`；计分与进度放 `src/composables/useGooseStyleQuiz.ts`；样式放 `src/styles/06-pages/_goose-style-quiz.scss`；`src/pages.json` 注册路由，首页趣味测试卡片接入。
- 状态：介绍、答题中（当前题/已选择）、结果；页面离开时清理自动跳题计时器。无网络与用户数据持久化。

### 用户验证场景

| 场景 | 预期 |
| --- | --- |
| 从首页进入趣味测试 | 显示介绍和开始入口 |
| 选择答案 | 进度前进，不重复记录一次答案 |
| 完成六题 | 根据答案显示一个鹅系结果 |
| 重新测试 | 题目进度和得分清零 |
| 生成结果海报 | 展示对应鹅系结果，并可发给朋友或保存到相册 |

## 分享海报

- 当前性格测试和小游戏的结果页均可生成结果海报，支持微信图片分享菜单和保存到相册。
- 性格测试海报展示鹅系结果、标签和介绍；小游戏海报展示勋章、积分、找鹅与拍掌成绩。
- 海报只在本地 Canvas 生成，不包含用户头像、二维码或外部服务依赖。
- 海报采用固定浅色底和高对比深色文字，不随页面深色主题切换；正文与数据标签字号适配手机预览。
- 用户验收：分别完成测试和游戏后生成海报，预览内容正确；可唤起微信图片分享菜单或保存图片。

## 共享契约接入

- 参照 `business-repo/uni-superone/.gitmodules`，在 `business-repo/uni-gknow/src/contracts` 挂载 `git@github.com:anjude/frontend-contracts.git`，跟随 `release` 分支。
- 通过现有 `@/* -> src/*` 别名从 `@/contracts` 或 `@/contracts/types/{domain}` 导入；新增接口消费时复用其中的共享类型、枚举和 API 路径，不在客户端复制协议。
- 当前页面没有接入后端 API，本次只完成协议子仓和项目约定接入；子仓固定到提交 `e701efc`。
- 验收：`git submodule status` 指向 `src/contracts` 的 `release` 修订；`npm run type-check` 与 `npm run build:mp-weixin` 通过。

## 契约请求基础设施

- `src/contract.ts` 将契约仓导出的 API 工厂绑定到 `HttpClient`；`src/apis/index.ts` 统一导出各域 client。
- `src/utils/request.ts` 统一处理基础 URL、query/body、snake_case/camelCase、HTTP/业务错误和请求拦截器；`src/utils/adapt/http.ts` 将 `uni.request` 归一为 Promise 适配器。
- `src/constant/config.ts` 复用 `uni-superone` 的 debug/develop/trial/release 后端地址映射，由 `App.vue` 的 `onLaunch` 按微信环境版本设置基地址。
- 可复用的运行时文件已整理到 `business-repo/frontend-contracts/templates/uni-app/src/`；该仓的 `docs/uni-app-client-integration.md` 记录新客户端挂载契约子仓、复制运行时模板、设置启动环境、选择 API 并后续同步的方法。模板不包含项目自己的 `src/apis/index.ts`；新项目按实际需要从 `@/contract` 选择导出，OpenAPI、共享 API 与类型通过子仓引用。
- 当前已确定沿用 Superone 的后端地址映射；启动时所需登录、用户资料与系统信息接口由下文启动门禁接入，玩法本身尚未接入业务 API。
- 验收：共享 API client 可通过 `@/apis` 导入；类型检查及微信小程序构建通过。

## 应用启动数据门禁

- 需求：gknow 与 uni-superone 一样，在应用启动时取得用户数据和系统数据；两项数据都成功后才展示任何页面内容。现有页面统一由 `gk-page` 包裹，它作为本产品对应 `cu-page` / `so-page` 的门禁容器，等待态和失败重试也由容器呈现。
- 请求顺序：先确保微信登录并取得可用 token，再并发请求 `userApi.getUser()` 与 `commonApi.getSystemInfo()`；任一失败则保持页面门禁关闭。遇到登录过期，清理 token、重新登录并重试一次。
- 数据归属：在 `src/stores/app.ts` 保存 `userInfo`、`systemInfo`、`ready` 与错误状态；`App.vue` 负责启动时初始化，`gk-page` 为页面挂载提供幂等兜底。不给页面各自重复请求用户和系统数据。
- 影响文件：`src/utils/adapt/login.ts`、`src/utils/auth.ts`、`src/utils/request.ts`、`src/stores/app.ts`、`src/App.vue`、`src/components/gk-page.vue`、`AGENTS.md`、`README.md`。
- 验收：`ready` 只有在用户与系统数据均有值时才变为真；加载中和失败时不渲染页面 header/主体；失败页可以重试；运行 `npm run type-check` 与 `npm run build:mp-weixin`。

## 设置页

- 原型：轻量个人设置页。首页左侧设置入口进入；页面由 `gk-page` 包裹并消费启动时已取到的用户和系统数据。
- 与 uni-superone 配置页对齐用户资料、分享主页、联系客服、系统链接、重新登录和主题功能；管理员可使用本地场景与服务器入口模式开关、管理系统链接、展开查询用户行为统计并通过触底加载分页用户列表。视觉与文案仍使用 gknow 自己的设计，不展示系统状态栏。
- 状态矩阵：应用数据加载或失败时沿用 `gk-page` 全局门禁；就绪时展示用户与系统信息；头像缺失时回退品牌鹅头像；头像上传 / 用户资料提交显示处理中和成功失败反馈；主题选择即时生效并沿用本地持久化；重新登录复用启动数据初始化流程。
- 不重复请求启动数据；管理员本地场景开关只改当前 store，入口模式开关更新服务器系统配置。
- 文件：`src/pages/settings/index.vue`、`src/styles/06-pages/_settings.scss`、`src/pages/index/index.vue`、`src/pages.json`、`src/styles/06-pages/_home.scss`、`src/styles/index.scss`、`src/utils/upload.ts`、`src/utils/adapt/upload.ts`、`src/stores/app.ts`。
