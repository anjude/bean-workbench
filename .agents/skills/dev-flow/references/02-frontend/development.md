# 前端开发细则

## 目录

- [产品原型与状态矩阵](#产品原型与状态矩阵)
- [硬门槛](#硬门槛)
- [一、原型判断](#一原型判断)
- [二、状态矩阵](#二状态矩阵)
- [与其他 skill 协作](#与其他-skill-协作)
- [数据层与状态管理](#数据层与状态管理)
- [契约与平台边界](#契约与平台边界)
- [当前模式](#当前模式)
- [分层职责](#分层职责)
- [一、接口层](#一接口层)
- [二、Store 与 Composable](#二store-与-composable)
- [错误处理](#错误处理)
- [约束](#约束)
- [验证](#验证)
- [页面、路由与样式](#页面路由与样式)
- [当前模式](#当前模式)
- [一、新增页面](#一新增页面)
- [二、修改页面](#二修改页面)
- [三、组件与样式](#三组件与样式)
- [约束](#约束)
- [验证](#验证)
- [设计参考](#设计参考)
- [Carbon 品牌 UI 规范](#carbon-品牌-ui-规范)
- [一句话](#一句话)
- [关键词](#关键词)
- [品牌目标](#品牌目标)
- [结构治理](#结构治理)
- [审美边界](#审美边界)
- [图标与资产语义](#图标与资产语义)
- [动效约束](#动效约束)
- [页面决策规则](#页面决策规则)
- [与其他 skill 协作](#与其他-skill-协作)



## 产品原型与状态矩阵

# 产品原型与状态矩阵

前端原型和状态矩阵。项目上下文见 `dev-flow-tools-repo`。

编码前的前置设计，两件事连着做：先确认「这是什么产品」，再确认「它有哪些状态」。执行任务时以工作目录 `.` 为项目根目录，路径用相对目录。

## 硬门槛

- 先出产品，再出页面；先补齐状态，再写 happy path。
- 只有 happy path 的页面视为未完成，状态矩阵没过不进入 `页面、路由与样式细则`。
- 原型和状态的结论要能被页面、样式、数据层直接消费，不另起一套说法。

## 一、原型判断

### 默认原型

- dashboard / control center
- feed / timeline
- space / relationship
- detail / immersive
- config / settings
- onboarding / activation

### 判断规则

- 核心是概览、切换、概括和入口 → `dashboard`
- 核心是连续内容流和回看 → `feed`
- 核心是关系、共创、互动和双人空间 → `space`
- 核心是单对象深看和沉浸编辑 → `detail`
- 核心是偏好、管理、系统项 → `config`
- 核心是第一次理解和第一次行动 → `onboarding`

### 输出

1. 原型判断
2. 为什么是这个原型
3. 页面结构骨架
4. 主 CTA / 次 CTA
5. 不该出现的反模式

### 反模式

- 一个页面同时想当 dashboard、detail 和 feed
- CTA 没有主次
- 页面结构只按接口字段堆砌
- 看得出有模块，但看不出产品意图

## 二、状态矩阵

### 默认检查项

首次进入 / 有本地缓存 / 服务端空数据 / 服务端有数据 / 加载中 / 刷新中 / 提交中 / 失败 / 部分可用 / 周期切换 / 权限或资格不足。

### 输出字段

按表格或列表输出：场景、触发条件、UI 表现、数据来源、用户可做的动作、失败或下一步回退。

### 使用规则

1. 先列最小矩阵，不追求无限展开。
2. 某个状态不会出现时，明确说明为什么。
3. 多个状态共享同一 UI 骨架可以合并，但不能省略。
4. 只做 happy path 视为未完成。

### 特别关注

- 本地缓存和服务端数据切换时的体验
- 提交后是否有明确反馈
- 失败时是否还能继续下一步
- 周期型功能跨天、跨周后的显示

## 与其他 skill 协作

- 原型与状态确认后，进入 `数据层与状态管理细则`（接口类型、store、composable）
- 落页面和样式交给 `页面、路由与样式细则`
- 需要图标和空状态图时走 `dev-flow-tools-svg-assets`
- 命中 carbon 品牌项目时全程叠加 `Carbon 品牌 UI 规范（见 development.md）`


## 数据层与状态管理

# uni-app 数据层：接口与状态

前端数据层与状态管理。项目上下文见 `dev-flow-tools-repo`。

执行任务时以工作目录 `.` 为项目根目录，所有文件路径都使用相对目录。

## 契约与平台边界

- 后端接口、请求/响应结构和枚举以唯一协议事实仓 `business-repo/frontend-contracts` 为准；所有前端项目通过 Git 子仓消费。
- 使用共享契约中的类型和枚举，不在客户端重复声明或按平台维护分支版本。协议变化回到事实仓更新，再由客户端同步对应修订。
- 客户端本地 `src/apis` 负责调用本项目统一 request 能力，不重新定义协议。
- 网络、存储、登录、上传等平台运行能力经项目适配边界（如 `utils/adapt`）提供统一接口。业务状态和页面不直接调用平台私有 API，也不散落平台判断；产品本身需要不同 UI/UX/交互时，差异留在对应呈现层。

## 当前模式

- API 文件：`src/apis/{domain}.ts`，统一导出 `src/apis/index.ts`
- API 类型：从项目接入的协议子仓导入（uni-superone 当前是 `src/contracts`），不复制到客户端自有 API 类型目录
- 业务实体类型：`src/types/{domain}.ts`
- Repo 文件：`src/repos/{domain}-repo.ts`，**可选**
- Store：`src/stores/*.ts`
- Composable：`src/composables/use*.ts`
- 请求入口：`src/utils/request`，响应格式 `ApiResponse<T>`（`errCode`、`data`、`msg`、`detail`）
- request 层把请求参数转 snake_case，响应转 camelCase

## 分层职责

- `src/stores/*.ts`：跨页面状态、缓存、列表排序、本地增删改、远端 CRUD 编排。
- `src/composables/use*.ts`：页面业务流程、生命周期辅助、确认弹窗、toast、格式化、导航。
- `src/repos/*-repo.ts`：可选层。复杂领域用于调用 API、检查业务错误、转换数据；轻量业务可由 store/composable 直接调用 API。
- `src/pages/**/*.vue`：展示和事件绑定。

## 一、接口层

1. 从需求或后端接口定义提取 method、path、Req、Resp、业务实体。
2. 从协议子仓导入请求/响应类型、业务结构和枚举；若契约缺失或不符，回到协议事实仓更新，不在客户端临时造一份。
3. 在 `src/apis/{domain}.ts` 使用本项目统一 request/transport 封装接口，并引用共享契约类型。
4. 在 `src/apis/index.ts` 导出客户端 API 实现；公共类型仍从协议子仓导出。
5. 判断是否需要 Repo：
   - 需要：接口多、转换复杂、跨页面复用、已有同域 repo、需要集中错误/日志封装。
   - 不需要：轻量接口、单页面/单 store 使用、转换简单。
6. 需要 Repo 时在 `src/repos/{domain}-repo.ts` 封装业务方法：
   - 检查 `response.errCode !== 0` 并抛出 `response.msg`。
   - 按契约和真实存量数据处理字段默认值或格式差异，不做推测性转换。
   - 使用 `logger.logRequestStart/Success/Error` 记录。
7. 不需要 Repo 时，字段转换集中放 `src/types/{domain}.ts` 或 store/composable 的 mapper/helper，不散落到页面。

## 二、Store 与 Composable

### Store

1. 使用 `defineStore('{domain}', () => {})` setup store。
2. 状态用 `ref`，派生状态用 `computed`。
3. 常见状态：列表、`isInitialized`、`isLoading*`、`error`。
4. 列表模块应提供 `load*(forceRefresh = false)`、`add*Local`、`update*Local`、`delete*Local`、`get*ById`、`reset`。
5. 远端变更成功后同步本地缓存，必要时重新排序。
6. 排序逻辑放 store，页面不重复排序。

### Composable

1. 命名使用 `use{Feature}`。
2. 从 store 暴露页面需要的 computed 状态。
3. 统一使用 `useErrorHandler` 做 `handleAsyncError`、`showSuccess`、`showError`、`showConfirm`。
4. 导航封装为函数，使用 `uni.navigateTo` 并处理 `fail`。
5. 格式化工具可放 composable，跨模块复用时放 `src/utils`。
6. 订阅、分享、授权等产品流程放 composable；平台 API 和兼容实现放项目适配层，composable 通过统一适配接口调用。

## 错误处理

- 使用 Repo 时：Repo 抛错，store 记录日志并继续抛错或回退状态。
- 不使用 Repo 时：store/composable 统一检查 `errCode`、转换字段和抛错，页面不重复处理接口响应。
- Composable 决定是否展示 toast、confirm 和 fallback message；页面不直接吞错。

## 约束

- API 层只做 HTTP 调用，不写页面逻辑和缓存逻辑。
- 不绕过项目统一 request / transport 适配直接调用平台网络 API。
- Repo 是可选层，不为轻量接口机械新增；Repo 层不直接操作页面 toast。
- 不引入新状态库，沿用 Pinia；不把大量业务逻辑塞进 `.vue` 页面。
- 共享契约已有的类型、枚举不得在客户端复制定义；字段映射由统一协议约定或集中转换层处理，不散落在页面。
- 页面和业务状态不得直接调用平台私有 API；在确有 UI/UX 差异时才按平台区分呈现。
- 不做无关重构、无关格式化、无关依赖升级。

## 验证

- `npm run type-check`
- 对列表增删改查，至少手工检查：初次加载、强制刷新、本地缓存更新、空状态、错误提示。
- 改动 request 底层时，补充 H5 或目标小程序平台 build。


## 页面、路由与样式

# uni-app 页面与组件样式

前端页面、路由与样式。项目上下文见 `dev-flow-tools-repo`。

本节把产品原型和状态矩阵落成可信的界面，不只是「把样式补齐」。执行任务时以工作目录 `.` 为项目根目录，路径用相对目录。

## 当前模式

- 页面配置：`src/pages.json`
- 页面文件：`src/pages/{feature}/index.vue`，编辑/详情页为 `edit/index.vue`、`detail/index.vue`
- 页面使用 `<script setup lang="ts">`，uni 生命周期从 `@dcloudio/uni-app` 引入
- 页面容器优先 `<cu-page>`、`o-page-container`、`cu-page-container` 和 `p-{page}` 命名空间类
- 碳基空间约定：除 `src/pages/profile/index.vue` 外页面必须由 `<cu-page>` 包裹；首页用 `<cu-page :reverse="true">`，其他页面不传 `reverse`
- 空状态、加载状态优先复用 `cu-empty-state`、`cu-loading-state`
- 通用组件 `src/components/cu-*.vue`，业务组件 `src/components/business/*.vue`
- 页面样式 `src/styles/06-pages/p-{page}.css`，组件样式 `src/styles/05-components/cu-{name}.css`
- 样式入口 `src/styles/index.css`，设计变量 `src/styles/01-settings/variables.css`

涉及常见业务页面或对象操作时，先读 [`ui-ux-handbook.md`](ui-ux-handbook.md)，按任务语义选择模式；具体产品规格和品牌规范优先于通用建议。

## 一、新增页面

1. 确定页面路径、标题、导航样式、是否启用下拉刷新。
2. 在 `src/pages.json` 添加页面配置。
3. 新建 `src/pages/{feature}/index.vue` 或对应子页面。
4. 页面有业务数据时，先设计 `数据层与状态管理细则` 的接口、store、composable，再让页面消费。
5. 页面只保留模板、事件转发、生命周期绑定和少量展示状态。
6. 页面样式放入 `src/styles/06-pages/p-{feature}.css`，并在 `src/styles/index.css` 引入。
7. 所有跳转使用相对应用路径，例如 `/pages/{feature}/detail/index?id=${id}`。

## 二、修改页面

1. 先读页面对应 composable、store、api；项目已有同域 repo 再读 repo。
2. 判断改动应放在页面、composable、store、api，还是可选 repo。
3. 下拉刷新必须在 `finally` 中调用 `uni.stopPullDownRefresh()`。
4. 跳转失败、异步失败使用现有错误处理或 toast 习惯。
5. 修改列表渲染时保留稳定 key，必要时用 `renderKey` 触发组件重渲染。

## 三、组件与样式

1. 先判断是页面局部样式、可复用组件样式还是业务组件。
2. 对照产品原型：这是控制台、时间流、空间、配置页还是沉浸详情。
3. 对照状态矩阵：至少确认空、加载、失败、有数据四种视觉骨架。
4. 页面样式新增 `src/styles/06-pages/p-{feature}.css` 并注册到 `src/styles/index.css`。
5. 可复用组件新增 `src/components/cu-{name}.vue` 和必要样式文件；业务组件加到 `src/components/business`，命名与业务对象一致。
6. 优先复用现有变量、`cu-*` 组件、`uni-icons` 和项目内资产。

### 默认审美检查

改样式前先判断：页面视觉重心在哪、主次 CTA 是否分层、信息密度是否过满、空/加载/错误态是否和正文态属于同一产品、页面是否像一个稳定母版。

### 平台设计原则

吸收 Material Design 与 Apple Human Interface Guidelines 的通用设计判断，不把两套平台视觉语言拼成一套：

1. **先定任务与层级**：明确用户来到页面要完成什么，让关键内容和主操作一眼可见；次要操作降级或延后，不靠堆按钮表达功能完整。
2. **让内容关系可见**：相关内容按语义分组，使用留白、对齐、分隔或容器表达归属。列表、网格、卡片、横滑货架按内容关系和浏览任务选型；不要因为当前项目数量少就先定死只适合少量项目的布局。横滑内容要露出后续项或明确提示可继续浏览。
3. **优先熟悉、稳定的交互模式**：导航、选择、确认、反馈等优先沿用用户熟悉的模式；自创交互必须解决明确的问题，并提供可理解的提示、反馈和退出/恢复路径。
4. **给重要信息和操作留空间**：避免为了塞进一屏而压缩字号、点击区域或信息层级。适配目标设备的屏幕、系统安全区、字体放大和文案长度；信息确实较多时用清晰滚动或渐进展示。
5. **状态和可访问性不只靠颜色**：交互控件有明确的可用、按下、禁用等反馈；空、加载、失败、成功和恢复方式完整。颜色之外还要有文案、形状、图标或位置线索，保证对比度、文字可读性和触控可用性。
6. **用真实页面迭代**：实现后在目标平台和代表性屏幕尺寸查看页面截图，检查视觉层级、分组、内容密度、裁切和实际触控路径。若页面看起来拥挤、分区关系不清、项目之间像从属关系或主操作不突出，应回到布局与信息架构重做，不以微调颜色、圆角或阴影代替解决结构问题。

Material 3 和 Apple HIG 是设计判断与平台适配的参考，不是要求所有端长得一样。按目标端和项目既有设计系统选用组件、导航、图标、动效和视觉令牌；不要默认混用 Material 专属组件与 Apple 专属视觉元素。项目产品规格与品牌规范优先，平台惯例用于让实现更自然、可理解。

### 反拼凑检查

页面结构、审美、状态、资产必须互相匹配。出现以下任一情况必须回退重排：

- 同页有多个互相竞争的视觉中心
- CTA 太多，用户不知道先点哪个
- 空状态和正文态像两个产品
- 页面信息块都成立，但合在一起没有主节奏
- 为了好看引入大量额外装饰，反而削弱可用性

## 约束

- 不把 API 调用直接写在页面里；不把复杂筛选、格式化、订阅、确认弹窗流程堆在 `.vue` 文件。
- 不把大量 scoped style 写进页面，优先放 ITCSS 文件。
- 用户明确给出文案、布局或交互规格时按规格实现，不把额外入口、额外确认、额外状态当成「优化」自动加入。
- 不新增孤立的一次性 UI 组件；不使用负 letter-spacing 或随 viewport 缩放字体。
- 不做一整页单色系视觉，颜色优先来自 CSS variables；文案不能溢出按钮、卡片和窄屏容器。
- 先满足结构和交互，再处理阴影、透明度和层次感；深浅色模式问题回到令牌层解决。
- 页面层不直接处理平台运行时差异，不直接调用平台私有 API；优先使用项目统一适配接口。只有产品 UI/UX/交互确需因平台不同而变化时，才在呈现层做平台区分。

## 验证

- `npm run type-check`
- 新增页面后检查 `src/pages.json` JSON 格式
- 页面结构、布局或样式有变化时，在目标平台 build 后做截图视觉验收；至少覆盖一个代表性屏幕尺寸，核对信息层级、内容分组、主操作、裁切和安全区
- 检查空、加载、错误、长文本、窄屏，以及浅色、深色、跟随系统三种主题模式

## 设计参考

- [Material Design 3 Foundations](https://m3.material.io/foundations/)：无障碍、内容设计、交互状态与布局基础。
- [Apple Human Interface Guidelines — Design principles](https://developer.apple.com/design/human-interface-guidelines/design-principles/)：熟悉性、一致性、清晰反馈、适应性、层级与迭代。
- [Apple Human Interface Guidelines — Layout](https://developer.apple.com/design/human-interface-guidelines/layout)：内容分组、视觉层级、留白、渐进展示与布局适配。


## Carbon 品牌 UI 规范

# 碳基空间品牌 UI 规范

Carbon 品牌 UI 规范；命中 Carbon 需求时全程生效。项目上下文见 `dev-flow-tools-repo`。

本节不只是配色和样式参考，而是 carbon 的品牌治理层。命中项目后先应用本节品牌规范，再实现页面并按需调用 `dev-flow-tools-svg-assets`，不要等页面写完再回过头调颜色。

## 一句话

关了灯的两个人的空间，有微光，有呼吸，但很安静。

## 关键词

- 夜空
- 萤火
- 细胞
- 星图
- 磨砂

## 品牌目标

carbon 的视觉要同时传达：

1. 私域感：这是两个人的地方，不是公共广场。
2. 温度感：有机、温暖、生物性，不是冰冷工具。
3. 安静感：表达克制，不吵不闹。

## 结构治理

看到 carbon 页面时，先检查：

- 页面是否有单一视觉重心
- CTA 是否足够克制
- 信息是否围绕“关系”和“空间”组织
- 空状态是否像在邀请进入，而不是在报错
- 页面是否像一个稳定空间，而不是功能清单

如果答案是否定的，先调结构，不先调颜色。

## 审美边界

允许：

- 深色或低照度背景
- 微光强调
- 大圆角
- 轻磨砂
- 缓慢呼吸型动效
- 留白驱动层次

不允许：

- 企业后台式线框堆叠
- 游戏化卡通符号泛滥
- 过多彩色标签和强对比按钮
- 为了“高级感”堆满透明度、阴影和模糊
- 同屏出现多个竞争视觉中心

## 图标与资产语义

- 图标应像“信号”或“坐标”，不是宣传插画
- 空状态图应像“邀请进入”，不是“系统没数据”
- 分享图、背景纹理、轻插画都应服务安静和私密，不服务热闹
- 业务图标默认走 `dev-flow-tools-svg-assets`

## 动效约束

- 核心词：呼吸，不是弹跳
- 只允许少量循环动效
- 优先 `opacity`、`transform`
- 交互反馈尽量小而明确
- 不为了情绪氛围打断主流程

## 页面决策规则

当多个方案都可行时，优先级如下：

1. 更像一个空间
2. 更安静
3. 更容易理解
4. 更少依赖外部资产
5. 更少打断用户

## 与其他 skill 协作

- 阶段编排由 `本开发流程入口` 派发
- 页面与样式执行交给 `页面、路由与样式细则`
- 图标和小资产交给 `dev-flow-tools-svg-assets`
