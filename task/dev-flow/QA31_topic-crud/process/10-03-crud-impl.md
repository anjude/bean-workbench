# 10-03 topic 增删改落地（后端 + 前端）

## 做了什么

### 后端（两个文件，已过 gofmt / build / vet）

`internal/repo/topic_repo.go`：

- 删掉 `Del` 重载。它名义上是 `BaseRepo.Del`，实际重写成「删主题 + 级联删该主题的日志」，
  但 `DeleteTopicLog` 也在调它 —— 那时 id 是**日志 ID**，第一步会执行
  `DELETE FROM topic_log_tab WHERE topic_id = <日志ID> AND topic_type = 1`，
  把「topic_id 恰好等于这条日志 ID」的主题下的全部日志删掉。
- 换成两个显式方法：`DeleteTopicLogsByTopicID`（按主题清日志）、
  `DeleteTopicLogWithChildren`（删一条 + 全部子孙）。
- `collectChildLogIDs` 用 BFS 逐层 `Pluck("id")` 收集，`maxLogDepth = 10` 防脏数据成环。

`internal/domain/topic/topic_service/topic_service.go`：

- `DeleteTopic` 事务内先清日志再删主题（原来靠 `Del` 内部事务，语义不变）。
- `DeleteTopicLog` 改调 `DeleteTopicLogWithChildren`。

权限语义按豆哥定的写进注释：**有父记录权限等同于有子记录权限——删父必删子，删子不动父**。
校验仍只在根记录上做（原有的 `ctx.CanEdit(log.Openid)` + `ensureSpaceLogAccessible`），
不逐条校验子孙 openid —— 逐条校验会重新制造孤儿，与需求目的冲突。

### 前端（type-check / build:mp-weixin 均通过）

| 文件 | 改动 |
|---|---|
| `src/pages/topic-edit/index.vue`（新） | 新建 / 编辑同页，带 id 进为编辑；名称 input 必填 ≤50，说明走 `so-md-editor` ≤2000，底部主按钮文案随态切「创建 / 保存」 |
| `src/pages/log-detail/index.vue`（新） | 读 `topic/log/detail` 取完整正文（列表的 `preview` 是截断的），页内编辑与删除 |
| `src/styles/06-pages/_p-topic-edit.scss`、`_p-log-detail.scss`（新） | 表单页与详情页样式，收在 06-pages |
| `src/pages.json`、`src/styles/index.scss` | 注册两页 + 接 06 层 |
| `src/components/business/biz-topic-panel.vue` | `open()` 从 toast 改跳新建页；列表项 `@longpress` 出 `showActionSheet`（置顶 / 编辑 / 删除） |
| `src/composables/useTopicList.ts` | 加 `toggleTop` / `remove`；`nextTop` 处理 top 是时间戳不是布尔 |
| `src/components/so-timeline.vue` | 条目可点，`emit('select', item)`；图片缩略图 `@tap.stop` 不让预览冒泡成跳转 |
| `src/pages/topic-detail/index.vue` | 导航栏右侧「更多」（编辑 / 删除主题），记录项点进 log-detail |

## 结论

- **跨页刷新走 `uni.$emit('topic:changed')`**：首页是 `navigateTo` 压住的存活页面，
  面板又是组件不是页面（拿不到 `onShow`），只能靠全局事件。编辑页 / 记录详情页发，
  面板与主题详情页收。面板在 `onMounted/onUnmounted` 配对，详情页用 `onUnload` 配对。
- **置顶不重拉整页**：`sorted` 是 computed，`toggleTop` 改本地项的 `top`，列表当场重排。
- **`rows` 是 `items` 的拷贝**（`{...item, descText}`），所以长按菜单里拿到的 item 不是
  `items` 里的原对象。置顶文案的「已置顶 / 已取消置顶」必须先存 `wasPinned`，
  否则读到的到底是旧值还是新值全看实现细节。

## 豆哥反馈后的第二轮改动

1. **「置顶」改「移到最前」**：排序是 `top DESC`，所以一律写当前时间戳——已置顶的还能再往前挪，
   不是二态切换。照 backup 的 `moveTopicToTop` / `handleMoveLogToTop`（两者都是 `top = now`）。
   取消要单独一项：`unpin`（`top = 0`），**只在已置顶时出现**。
   backup 的主题列表菜单只有「移至最前」一项，我们没有它的编辑/删除入口，所以菜单是
   `[移到最前, (取消置顶), 编辑, 删除]`。
2. **图片预览仍跳详情**：`@tap.stop` 在 uni-app 里就是 catch——产物确认编译成了 `catchtap`
   （`catchtap="{{url.c}}"`），但真机上没拦住。**不跟编译器较劲，改结构**：把 gallery 从
   `so-timeline__body` 里挪出来当兄弟节点，跳转热区只包正文。点图片压根不在热区里，
   跟冒泡机制无关。产物已核实：body 带 `bindtap`，gallery 是独立子树。
   副作用：hover 反馈也从整条 item 收到 body 上（整条变淡会让图片区跟着闪）。
3. **log 详情页改成与主题详情页同构**：头部卡（正文 + 元信息行）→ 写跟进卡（常驻输入框）
   → 跟进时间轴卡。编辑态整块收起跟进区（两个编辑区同屏，焦点和「保存 / 记下来」会打架）。
   跟进只在**根记录**下开一层（`parentLogId === 0`），UI 只做两层。
   跟进走 `topic/log/create` 传 `parentLogId`，列表走 `topic/log/list` 传 `parentLogId`。
4. **记录长按菜单**（`useTopicLogActions.ts` 新）：照 backup 的日志菜单，去掉「切换主题」
   （跨主题迁移不在本期）。菜单 = `[移到最前, (取消置顶), 标记/取消标记, 删除]`。
   composable 只管弹菜单 + 调接口 + toast，**返回是否改动了数据**，刷新由调用方决定
   （主题详情页 `load()`，记录详情页 `loadFollows()`）。
   本页自广播用 `selfBroadcasting` 标志位挡掉——`$emit` 是同步的，发完即撤。

## 豆哥第三轮反馈

1. **跟进放开到每一条记录**：原先按「UI 只做两层」只给根记录（`parentLogId === 0`）开跟进区，
   这是错的——后端 `parent_log_id` 支持任意层级，**每条记录都能被跟进**。去掉 `isRoot` 限制，
   跟进输入与跟进列表对所有记录都显示。`isRoot` 只留作标记：非根记录在元信息行加一枚「跟进」标签，
   让人知道自己在哪一层。删除确认文案也统一成「它的跟进会一起删掉」（任何一条都可能有跟进）。
2. **log 详情页样式补齐**：上一轮重写导页时把 class 从 `__body` 改成了 `__head` 系列，
   scss 没跟着改——`__head / __meta-row / __composer-card / __feed / __section-title /
   __divider` 等 11 个类全是裸的，padding 全丢，页面挤成一团。已按 topic-detail 的写法重写。
   **教训：06-pages 的 scss 与模板 class 要成对核对**，已加脚本核对（`re.findall` 对比两边），
   topic-detail 顺带核出一个多余的包裹层 `p-topic-detail__composer`（无样式且多余一层 flex item），已删。

## 豆哥第四轮反馈

- **log 详情页的编辑 / 删除不占视觉重点**：它们是低频操作，常驻底部双按钮把页面压成「表单页」。
  改法与主题详情页一致——收进导航栏右侧「更多」抽屉。**只有编辑态才升出底部 `[取消 | 保存]`**，
  那一刻保存确实是当前唯一的主任务，占重点站得住。
  content 的 padding-bottom 跟着分态：平时只留 `--so-space-lg`，编辑态才让出固定保存条的位置，
  免得日常浏览底下空一大块。

## 豆哥第五轮反馈

1. **时间轴改线性排序**：`so-timeline` 原本按天分组（自己加的，carbon 与 backup 都没做），
   实际把一个主题的记录切成好几块，每块内部还要重排一遍，扫读反而不如一条接一条。
   改回 backup 的**线性列表**，排序统一在读取出口：`top DESC, createTime DESC`
   —— 置顶排到**整列最前**，不是分组内的最前。
   去掉分组后日期信息不能丢，左列改成两行：上行 `10-05`、下行 `16:30`（左列 92rpx → 112rpx）。
   跟着清掉 `time.ts` 里失去调用者的 `formatDayLabel` / `dayKey`。
### 根因（前一节先写错了，这里更正）

**真根因：自定义组件 emit 了小程序原生事件名。**

`so-timeline` 对外 `emit('longpress', item)`，编译到 mp 就是 `bindlongpress`——
这是微信的**原生事件名**。微信把它当原生长按处理，父组件 `@longpress="onLogLongPress"`
收到的是**事件对象**而不是 emit 的 payload，`item` 直接变 undefined，取 `item.id` 全是空。
`select` 不是原生事件名，走自定义事件通道正常 —— 这解释了为什么点条目能进详情、长按却读不到 id。

修法：对外事件改名 `logMenu`，避��原生事件名。产物已核实：组件内仍是 `bindlongpress`，
父组件变成 `bindlogMenu`。

> 上一节我写「内联 `emit('longpress', item)` 编译后丢参数」，是**误判**——
> 内联与具名两种写法编译出来的事件映射结构是一样的（`e.o(fn, n.id)`），
> 我从 wxml 的 `item.f` / `item.g` 对称性上推断，证据不足就下了结论。以本节为准。

**通用规则：uni-app 自定义组件 emit 的事件名不能用 `tap` / `longpress` / `touchstart`
这类小程序原生事件名，重名会被微信按原生事件处理，payload 收不到。**

次生改进（不是根因，但值得留）：`run()` 里 id 在 await 之前就取成标量，
避免响应式对象跨 await 取字段；`requireId` 拦住残缺请求，别让 `JSON.stringify`
把 undefined 字段静默丢掉后由后端报一个指向错误的错。

### 菜单照 backup

backup `handleLongPress` 的菜单是 `[移至最前, 置顶/取消置顶, 切换主题, 标记, 删除]`。
去掉「切换主题」（跨主题迁移不在本期），其余四项照抄 ——
注意「置顶」是**常驻二态项**（`isPinned ? '取消置顶' : '置顶'`），
不是「只在已置顶时才出现」，我前一版擅自砍成后者，已改回。

排序规则照 backup 的 `store/topic-log.ts: sortLogs`：`top DESC → createTime DESC`，
置顶排整列最前。这与我们 `so-timeline` 读取出口的排序一致。

### 返回按钮点了没反应（不是记录页独有）

`so-custom` 的返回按钮在**所有页面都没渲染**（topic-detail / topic-edit / profile / log-detail 一样）。

根因：**无值布尔属性在 uni-app 编译到小程序时被丢掉**。
`<so-custom is-back>` 编译产物里标签上没有 `is-back`，props 里也没有这个键，
组件的 `wx:if="{{b}}"`（= `isBack`）恒为 false，返回按钮压根没进 DOM。
改成显式绑定 `:is-back="true"` 后，产物里出现 `e.p({"is-back":!0})`，按钮才出来。

同类一起修：首页 `<so-page reverse>` → `:reverse="true"`、`<so-custom transparent>` → `:transparent="true"`。
前者失效意味着首页在非真实态走不到演示页分支，后者失效意味着首页导航栏一直带背景和边框。

**规则：uni-app 自定义组件的布尔 prop 一律写 `:prop="true"`，别用无值写法。**
原生组件（如 `refresher-enabled`）不受影响，wxml 本身支持无值属性。

## 待核

- 真机冒烟未跑（本地只有 build）。重点看：长按菜单在真机上的触发、
  编辑器在编辑页里键盘弹起时底栏有没有被顶走、log-detail 编辑态保存后正文有没有正确回到展示态。
- 删除确认文案里的「跟进会一起删掉」目前是固定文案，拿不到实际条数
  （`TopicLogListItem` 没有 `child_count`，要精确得逐条查，N+1，方案里已定不显示）。

## 豆哥第四轮（更多按钮的位置 / 类名撞名）

- **「更多」从导航栏右侧挪进头部卡右上角**（豆哥：不要在 navigate title 右边放更多按钮）。
  `so-custom` 的 `#right` 插槽整块删掉；头部卡改成横向两栏：`__head-main`（flex:1; min-width:0）
  放标题/正文/元信息，`__more`（48rpx 方形热区，`margin: -6rpx -6rpx 0 0` 抵掉卡内边距）
  放 `uni-icons type="more"`。log-detail 的 `__more` 加 `v-if="!editing"`——编辑态头部卡是编辑器，
  且底部已有 [取消|保存]，那枚图标是多余的。
- **顺手核出 `__more` 撞名**：topic-detail 里列表末尾的「加载中…/没有更多了」提示也用了
  `p-topic-detail__more`，和新的图标按钮同名 → 两条规则（48rpx 方形热区 / 居中文字+32rpx 上下 padding）
  会互相污染。底部那个改名为 `__more-hint`。
- 类名核对脚本排掉噪声后三页零误差（剩下的 `editing` 是 `:class` 对象里的变量名，不是类名）。
  核对要点：全局组件类（`so-btn*`/`so-card`）定义在 05-components，不在页面 scss 里，要加白名单；
  `:class="{ 'x--y': flag }"` 这类对象写法要 strip 引号花括号再比对。
- type-check 与 build:mp-weixin 全绿。产物确认：页面 `index.wxss` 是空的（样式全部打进 `app.wxss`），
  查样式要查 `app.wxss`；wxml 里 `__head-main` 与 `__more` 是头部卡内的兄弟节点，`__nav-action` 已消失。

## 豆哥第五轮（详情页返回点了没反应）

复现路径：进主题页 → 长按 log 移至最前 → 点 log 进记录详情 → 点返回 → 无响应。

**先排除掉旧的那个坑**（别再往回掉）：`:is-back="true"` 在运行时是能落到 `isBack` 的，
不是编译期看一眼就下结论——链路是 `e.p({"is-back":true})` → 产物 `u-p="{{b}}"` →
uni-app `findComponentPropsData`（按 `"uid,propsId"` 从 propsCaches 取回原对象）→
Vue `setFullProps` 里 `camelize(key)` → `props.isBack`。dev / build 两份产物都已核对。
返回按钮 `bindtap → onBack`、页面栈、路由路径也逐项查过，都正常。

**真正的改动**：`onBack` 原来是先 `getCurrentPages?.()` 预判页面栈再决定 `navigateBack` / `reLaunch`。
`getCurrentPages` 是**裸全局调用**，而 uni-app 自己的运行时从头到尾没用过裸 `getCurrentPages`
（它用的是 `getApp` 和自己的页面栈，vendor.js 里 0 处）——一旦在组件作用域解析不到就是
**ReferenceError**，事件回调里被吞掉的表现恰恰是「点了没反应、控制台还干净」。
改成不预判：`uni.navigateBack({ delta: 1, fail: () => reLaunch(首页) })`。
navigateBack 自己知道能不能退，退不了走 fail，不再需要在前面猜页面栈。

**排查过程中顺带确认（都不是原因，别再查第二遍）**：
- 没有 `uni.showLoading({mask:true})` 残留（全局遮罩会吞掉所有点击，是最像的一种）——
  全仓只有 profile 传头像、usePosterShare 两处用，且都不在这条路径；`request.ts` 只在 `cfg.showLoading` 为真时弹，没有调用方传。
- 没有 `uni.addInterceptor` 或任何对 navigateBack / navigateTo 的包装。
- `--so-z-sticky` = 100 > `.so-md-editor__container` 的 10，导航栏不会被编辑器容器盖住；
  原生 `editor` 虽然无视 z-index，但几何位置在页面中部，与导航栏不重叠。
- `so-timeline` 的 `wx:key` 是 `item.id`（产物里 `n: item.id`），没有重复 key 导致的事件串台。
- dev 与 build 两份产物都是新的（时间戳与 src 同步），不是跑的旧包。

**待豆哥确认**：换完若仍无响应，那就是页面栈里压着两份 log-detail（返回键坏的那阵子累积的），
退一份看着跟没动一样。区分方法：进详情页后**连点两次返回**，或在控制台打 `getCurrentPages().length`。

## 豆哥第六轮（为什么 backup / carbon 从来没这问题）—— 照抄收尾

前两轮我都在自己的代码里推演，两次都错。豆哥一句「为什么backup和carbon都没有类似的问题」点破：
**别推演，去看能跑的参照实现**。backup 的 `cu-custom.vue` 与 carbon 的 `cu-custom.vue` 是同一份，
它们的返回按钮是这么写的：

```html
<view class="action" @tap="BackPage" v-if="isBack">
  <text class="cuIcon-back"></text>
</view>
```

**一层 view + 原生 `<text>`**。而我们的是：view(so-bar__left) → view(so-bar__actions) → view(so-bar__action) → `<uni-icons>`。
差异不在 prop、不在事件名，而在**导航栏里套了一个自定义组件 `uni-icons`**：
`uni-icons` 根节点是 `<text bindtap="{{e}}">`（自带事件绑定），且图标靠它自带的字体渲染——
字体没加载时那个位置就是一块空白，热区也随之塌掉。

**这次的改动（全部照抄，不自己发挥）**：
1. `so-custom` 返回/主页改成原生 `<text>`（`‹` / `⌂`），不再套 `uni-icons`。
   产物 `components/so-custom.json` 的 usingComponents 已变空，组件零依赖。
2. 去掉多余的 `so-bar__actions` 中间层（胶囊那套 `capsuleStyle` 一并删，没有页面用 isHome）。
3. `onBack` 换成 backup / carbon 的 `BackPage` 原文：`typeof getCurrentPages === 'function'` 守卫 +
   `__wxConfig.pages[0]` 兜底 + `uni.navigateBack({delta:1})`。
4. `.so-bar__action` 加 `min-width: 72rpx`（照 carbon 的 `.cu-bar .action`）——字符宽度由字体决定，
   不设下限热区会缩成一条缝。
5. 页面头部卡的「更多」也换掉 `uni-icons`（同样的风险），改用 `⋯`。

**⚠️ 更正前一轮写下的错误结论**：「无值布尔属性在 uni-app 编译到小程序时被丢掉」——**是错的**。
实测：`<so-custom is-back>`（无值）编译后同样进 `u-p`，值是 `{"is-back":!0}`，
与 `:is-back="true"` 的产物**完全一致**。当时我只看了 wxml 标签上没有该属性就下了结论，
没去看 `u-p`。两条写法没有差别，prop 传递从头到尾都不是这次问题的原因。
