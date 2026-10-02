# 02-15 Markdown 展示与编辑器

> 豆哥：「要开始引入markdown展示和编辑器了，可以在backup看到，我们试一下能不能优化下实现，然后改成用vue3实现」。

## backup 那条路为什么不能照抄

调研（`uni-superone-backup`）结论：

| backup 做法 | 问题 |
|---|---|
| 用 uni-app 原生 `<editor>`（Quill） | 编辑器内部存的是 **HTML**，不是 Markdown |
| ~20 条手写正则 `htmlToMarkdown` 转回 Markdown | 嵌套标签、GFM 表格必错；**失败时返回原始 HTML**，直接把脏数据写进库 |
| `marked` → HTML 字符串 → 正则打 class → `rich-text` 渲染 | `rich-text` 里组件 scoped 样式进不去，`:deep()` 在小程序侧失效，样式只能写死；marked 输出一变正则就崩 |
| 工具栏用「字符串方法名派发」+ 全局单例反查 vm | 类型全丢 |
| `types/md-editor.d.ts` | 完全过时，0 引用 |
| `isUpdatingFromExternal` 只在回调里复位 | 回调不触发就永久卡住输入 |

**核心判断**：输入是 Markdown、存的就该是 Markdown。中间不经过 HTML，就不需要 HTML→MD 这层脆弱转换。

## 本轮实现

| 文件 | 作用 |
|---|---|
| `src/utils/markdown.ts` | `marked.lexer` → AST → 摊平成 `MdBlock[]`；`parseMarkdown()` / `toPlainText()` |
| `src/components/so-markdown.vue` | 块级渲染：heading / paragraph / list / blockquote / code / table / hr |
| `src/components/so-md-inline.vue` | 行内片段渲染：text / image，bold / italic / del / code / link |
| `src/components/so-md-editor.vue` | **直接编辑 Markdown 源码**的编辑器：编辑/预览切换 + 工具栏 + 字数 + 完成 |
| `src/components/so-timeline.vue` | 日志正文改走 `<so-markdown>` |
| `src/pages/topic-detail/index.vue` | hero 描述改走 `<so-markdown>` |
| `src/components/business/biz-topic-panel.vue` | 列表摘要走 `toPlainText()`（去掉语法符号，单行省略） |
| `src/pages/test-theme/test-theme.vue` | 风格预览页挂上渲染样例 + 编辑器，模拟器里直接能试 |

## 关键实现决策

- **不做 HTML 中间态**：`marked.lexer` 只取 AST，输出的是纯数据（`MdFragment[]` / `MdBlock[]`），
  Vue 组件照数据渲染。marked 换版本只影响 `markdown.ts` 一个文件，渲染层不动。
- **行内标记摊平一层**：`flatten()` 递归展开 strong/em/del/link/code，`**粗体里带 *斜体* 和 \`代码\`**`
  能正确得到 `bold`、`bold+italic`、`bold+code` 三种片段（已冒烟验证）。
- **不渲染原始 HTML**：`html` token 当纯文本显示。小程序富文本注入面太大，不值得为它开一个口子。
- **编辑器不做「选中包裹」**：小程序 textarea 拿不到选区，改成在光标处插入语法片段并把光标放进中间
  （`prefix + hint + suffix`，`cursor = at + prefix.length + hint.length`）。
- **`setOptions` 放模块级**：backup 在 computed 里反复 `setOptions`，改的是全局单例，还重复执行。
- **解析失败退化成纯文本段落**：不把异常抛到渲染层。
- **列表摘要一次性算好**（`rows` computed），不放模板里逐项 parse——滚动重渲染会重复解析。
- **字号全走 `--so-*` 令牌**：h1→xl / h2→lg / h3→md / h4-6→sm，正文 md。标题一律加粗（`#` 本身就是层级，
  不依赖用户再敲 `**`）。
- **段落不给 `display:flex`**：让 `<text>` 片段保持行内流动。flex 会把每个片段变成独立盒子，
  长句容易整段跳到下一行。`word-break: break-all` 挂在 `.so-md` 根部（可继承），防长串撑破容器。

## 验证

- `npm run type-check` 通过，`npm run build:mp-weixin` 通过。
- 解析冒烟（esbuild 打包 `markdown.ts` 后用 node 跑）：覆盖 主题描述（含 `---` 与 `*` 列表）、
  粗体+行内码+链接、嵌套强调、引用、代码块、GFM 表格、分割线、有序列表、纯文本、原始 HTML、空串、删除线+图片 —— 全部符合预期。
- 产物：`components/so-markdown.*`、`so-md-inline.*`、`so-md-editor.*` 已生成；
  `pages/topic-detail/index.wxml`、`components/so-timeline.wxml`、`pages/test-theme/test-theme.wxml` 均有引用。

## 坑（本轮新踩）

- **BSD grep 的 `\|` 交替不生效**，必须 `grep -E`。这轮又踩了一次（查产物引用时误以为没生成）。

## 待办

1. 编辑器还没接业务：`createTopic` / `createTopicLog` 接口都在（`src/contracts/apis/topic.ts`），
   下一轮「新建主题」和「写记录」直接用它。
2. `so-markdown` 目前不支持嵌套列表（`toBlock` 里 list 只取每项的文字部分）——日志类内容用不到，真需要再加。
3. 详情页操作组「编辑」若要接编辑器改 description，走 `updateTopic`。
