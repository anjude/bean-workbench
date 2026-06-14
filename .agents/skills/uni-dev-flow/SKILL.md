---
name: uni-dev-flow
description: 当用户输入 uni-app 项目需求描述，希望自动输出完整前端改动方案，或直接完成 Vue3/TypeScript 代码、接口、状态、页面、样式、构建验证闭环时使用；作为总控 skill 编排 uni 子 skill，并默认按商业级产品标准约束页面原型、状态完整性、资产主权和品牌一致性。
metadata:
  short-description: uni-app 商业级产品总控
---

# uni-app 商业级产品总控

本 skill 是 uni 项目的总控流程。目标不是“把页面做出来”，而是尽量一次性生成可上线、可扩展、少依赖外部条件的产品能力。

执行任务时以工作目录 `.` 为项目根目录，所有文件路径都使用相对路径。

## 项目上下文

- 技术栈：Vue 3、uni-app、TypeScript、Pinia、Vite、Tailwind CSS、Sass、vue-i18n、uni-ui。
- 页面配置：`src/pages.json`
- 页面：`src/pages/**/index.vue`
- API：`src/apis/*.ts`
- API 类型：`src/types/api/*.ts` 和 `src/types/api.ts`
- 业务类型：`src/types/*.ts`
- Store：`src/stores/*.ts`
- Composable：`src/composables/use*.ts`
- 组件：`src/components/cu-*.vue` 和 `src/components/business/*.vue`
- 样式：`src/styles/index.css`

按需求选择子 skill：

- 产品原型判断：`uni-product-archetype-flow`
- 状态矩阵补全：`uni-state-matrix-flow`
- 接口、类型、可选 Repo：`uni-api-flow`
- 页面、路由、生命周期：`uni-page-flow`
- Pinia、Composable、业务交互：`uni-state-flow`
- 组件、样式、视觉一致性：`uni-component-style-flow`
- uni 通用 SVG 资产、图标组件、空状态图形：`uni-svg-flow`
- 品牌特化图标、SVG 资产、图标接入：按项目品牌 skill 叠加对应特化层，例如 carbon 项目使用 `carbon-icon-flow`
- type-check、build、验收：`uni-test-build-flow`

如果项目存在明确品牌 UI skill，页面和资产决策时必须叠加该品牌 skill；`uni-dev-flow` 只负责通用 uni 抽象，不默认绑定任何单一品牌项目。

## 核心原则

1. 先生成产品，再生成页面。
2. 先补齐状态，再写 happy path。
3. 优先项目自有资产和轻组件，减少对外部框架、外部图标平台、外部视觉资产的依赖。
4. 页面结构、审美、状态和资产必须互相匹配，不能分别最优、整体拼凑。

## 默认工作流

### 1. 产品原型判断

开始编码前，先判断这次需求属于哪类产品原型，再决定页面骨架和信息层级。调用 `uni-product-archetype-flow`。

至少判断：

- dashboard / control center
- feed / timeline
- space / relationship
- detail / immersive
- config / settings
- onboarding / activation

禁止直接跳过原型判断进入页面实现。

### 2. 状态矩阵补全

开始实现前，先补最小状态矩阵。调用 `uni-state-matrix-flow`。

默认检查：

- 首次进入
- 有本地缓存
- 服务端空数据
- 服务端有数据
- 加载中
- 刷新中
- 提交中
- 失败
- 部分可用
- 周期切换
- 权限或资格不足

如果只存在 happy path，视为产品未完成。

### 3. 资产主权检查

默认检查这次需求是否过度依赖外部条件：

- 是否依赖 iconfont 或外部图标平台
- 是否依赖重 UI 框架才能成立
- 是否依赖外部插画、图片、纹理才能成立
- 是否能改为项目内 `SVG`、CSS、轻组件、自有样式实现

涉及图标、空状态图、组合图形时，调用 `uni-svg-flow`；如果项目有明确品牌语义，再叠加对应品牌的图标特化 skill。

### 4. 品牌一致性检查

有品牌 skill 时，必须检查：

- 页面结构是否符合品牌气质
- 信息密度是否符合品牌气质
- CTA 是否过多或过吵
- 图标、空状态、动效是否跑偏

如果项目存在品牌 UI skill，优先参考该品牌 skill；例如 carbon 项目参考 `carbon-space-ui`。

### 5. 工程实现

通过前 4 步后，再开始正常工程实现：

- 类型
- API
- Store / Composable
- 页面
- 样式
- 验证

## 标准阶段

1. 定位入口：确认是否新增页面、改已有页面、加 API、加 store、加 composable、改组件或样式。
2. 调用 `uni-product-archetype-flow`，输出页面原型、信息骨架、CTA 结构、常见风险。
3. 调用 `uni-state-matrix-flow`，输出最小状态矩阵并补齐缺口。
4. 检查是否存在资产主权问题；必要时调用 `uni-svg-flow` 或品牌特化资产 skill。
5. 设计数据流：默认优先 `page -> composable -> store/api -> request`；复杂业务或项目已有同域 repo 时再引入 repo。
6. 先补类型：请求/响应类型放 `src/types/api/*.ts`，业务实体放 `src/types/*.ts`。
7. 再补 API：API 只做请求；字段兼容转换、业务错误处理优先放在 store/composable 的统一 helper 中。
8. 再补 Store 和 Composable：Store 维护跨页面状态和缓存，Composable 维护页面业务流程。
9. 最后补页面和样式：页面尽量薄，样式放 `src/styles/06-pages/p-*.css` 或组件样式文件，并在 `src/styles/index.css` 注册。
10. 运行验证：至少 `npm run type-check`；涉及平台差异时补 `npm run build:h5` 或目标平台 build。

## 两种执行模式

### 方案确认模式

当用户表达“先出方案”“确认后执行”“评审方案”时使用。

输出内容必须包含：

- 产品原型判断
- 状态矩阵摘要
- 文件级方案
- 资产主权决策
- 品牌一致性注意点
- 验证命令

### 全自动模式

当用户表达“直接做”“自动完成”“不需要确认”“一次性完成”时使用。

默认顺序：

1. 原型判断
2. 状态矩阵补全
3. 资产主权检查
4. 页面和数据实现
5. 真实页面接入
6. 验证

## 自动开发约束

- 不引入新 UI 框架或新状态库。
- 不把大量业务逻辑直接塞进 `.vue` 页面。
- 不绕过 `src/utils/request` 直接调用 `uni.request`，登录或底层 request 机制本身除外。
- 不为轻量接口机械新增 Repo 层。
- 不做无关重构、无关格式化、无关依赖升级。
- 用户明确给出文案、布局或交互规格时，不把额外入口、额外确认、额外状态当成“优化”自动加入。
- 如果首屏关键体验依赖外部资源且可以项目内实现，优先改成项目内实现。
- 主题可读性问题优先回到设计令牌修正，避免页面级补丁越积越多。

## 最终输出

- 需求理解：一句话。
- 产品原型：一句话说明判断结果。
- 完成内容：按 API/类型、状态、页面、样式、资产、验证分组。
- 验证结果：列出命令和结论。
- 产品完整性风险：只列真实缺口，例如状态缺口、外部依赖残留、品牌一致性未收口。
