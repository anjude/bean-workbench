# 02-17 编辑器重做：块级 Live Preview（含图片与待办）

> 豆哥：「现在的编辑器实现，不是所见即所得，不行，而且功能也阉割了，图片、todo这些都没有」。

这是对 02-15 那版「直接编辑 Markdown 源码」的**否定**。存储格式（Markdown）没被否定，被否定的是编辑器形态。

## 为什么不改用原生 `<editor>`

字级别的所见即所得在小程序上只有原生 `<editor>`（Quill）能做到，但它不能用：

| 问题 | 后果 |
|---|---|
| 内部表示是 HTML | 要存 Markdown 就得 HTML→MD 反解，正是 backup 那条 ~20 条正则的老路（嵌套标签/GFM 表格必错，失败还把原始 HTML 写库） |
| 不支持待办复选框 | 恰恰是豆哥这次点名要的功能 |
| 不支持 GFM 表格 | 同上 |
| 各端表现不一致 | 同一个 HTML 在 iOS/Android/开发者工具渲染有差异 |

所以不能为了"看起来所见即所得"把存储格式赔进去。

## 采用的方案：块级 Live Preview

**光标离开哪一块，哪一块就渲染成最终样式**（Obsidian 的 Live Preview 就是这套）。

- 写 `- [ ] 买菜`，失焦后看到的是一个可点的复选框 + "买菜"，不是 `[ ] 买菜`。
- 标题、引用、代码、图片、分割线同理——非当前块一律是渲染结果，看不到 Markdown 痕迹。
- 只有**正在编辑的那一块**是输入框（键盘弹着的时候）。

这是小程序上能做的最好形态：没有 contenteditable，拿不到富文本选区。

## 落地

| 文件 | 作用 |
|---|---|
| `src/utils/md-blocks.ts`（新） | `MdBlock` + `parseBlocks` / `serializeBlocks` |
| `src/components/so-md-block.vue`（新） | 单块两态：渲染态 / 输入态，待办复选框、图片、分割线 |
| `src/components/so-md-editor.vue`（重写） | 块流 + 工具栏 + 字数 + 完成 |
| `src/utils/markdown.ts` | 新增 `parseInline`（块内行内渲染）；list 项带 `checked` |
| `src/components/so-markdown.vue` | list 渲染支持复选框（展示态只读） |
| `src/components/so-md-inline.vue` | `font-size` 改 `inherit` |

## 关键实现决策

- **块只是视图状态，存储仍是 Markdown 字符串**。多一层块模型是因为：渲染是一次性的（源码→画出来），
  编辑器要的是**可寻址、可局部修改**的结构——用户改的是"第 3 块"，改完要能拼回源码而不动其它块。
- **不用 isUpdating 标志位同步外部值**：`watch(modelValue)` 里比较 `v !== serializeBlocks(blocks)`，
  自己 emit 出去的值与当前序列化结果一致，不会来回抖。backup 那个标志位只要回调没触发就永久卡住输入。
- **回车分块，但只认"新敲出来的换行"**：块里本来就有软换行时（解析时合并的多行段落），
  一输入就拆会把用户正在编辑的段落切碎。做法是数 `\n` 个数，超过原有数量才在新增那个位置切。
  code 块不分块（代码要多行）。
- **行内标记只能追加到末尾**：textarea 拿不到选区（02-15 就有这条约束），工具栏插入占位词让用户改写。
  好在块编辑器里用户可以直接敲 `**粗体**`，工具栏只是辅助。
- **图片走已有的 `utils/upload.ts`**：`uni.chooseMedia` → `uploadImage()` → 插入 image 块。
  上传工具原本就在（token 注入、信封解析、登录过期重试都是现成的），没重造。
- **`uni.chooseMedia` 的类型没有 Promise**：`@dcloudio/types` 把它声明成返回 `void`，
  必须自己包一层 Promise（success/fail 回调）。
- **插入分割线/图片后自动补一个空块**，否则光标没地方落脚，没法接着写。

## 两个连带修掉的坑

1. **展示侧看不到待办**。marked 会识别 `- [ ] / - [x]` 并**把 `[ ] ` 前缀剥掉**，
   但 `task` / `checked` 要自己从 ListItem 上取——之前 flatten 只取文字，
   结果编辑器能写待办、详情页却渲染成普通列表（连 `[ ]` 都没有）。
   现在 `MdListItem` 带 `checked`，`so-markdown` 渲染复选框（展示态只读，勾选要进编辑器）。
2. **标题字号传不进去**。`so-md-inline` 原来把 `font-size` 写死，而小程序 scoped 下 `:deep()` 失效，
   父级改字号影响不到子组件。改成 `font-size: inherit`，基准字号由容器根（`.so-md` / `.so-mdb`）给，
   标题按 h1-h6 分级就能生效了。

## 验证

- `type-check` + `build:mp-weixin` 通过。
- 块互转冒烟（esbuild 打包 `md-blocks.ts` 跑 node）：8 个用例（混合、纯文本、空、待办、有序、
  代码围栏内空行、`#无空格`、行内图片）**二次往返全部稳定**。
- 展示侧冒烟：`- [ ] 买菜` / `- [x] 洗碗` / `- 普通项` 正确得到 `checked: false / true / undefined`。
- 产物：`so-md-block.*` 已生成、编辑器 json 引用了它、工具栏数据与上传链路（`utils/upload.js` +
  `contracts/apis/common.js` 的 `/api/so/common/wx_upload`）都在。
- 预览页 `test-theme` 的样例加了待办，编辑器的初始草稿也是多块（能看出块级效果）。

## 待办 / 边界

1. 展示侧的复选框**只读**。详情页想直接勾选要接 `updateTopicLog` 改 content，本轮没做。
2. 表格仍然只能手写（编辑器没有表格工具），`so-markdown` 渲染 GFM 表格是支持的。
3. 块内行内语法在编辑态仍显示源码（`**粗体**`），失焦才渲染——这是块级 Live Preview 的固有边界。
4. 图片只能单张插入，没有删除/替换（删要改块结构，等有需求再加）。
