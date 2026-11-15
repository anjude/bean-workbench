# 02-18 编辑器改用原生 editor（backup 方案）+ delta 优化

> 豆哥：「你还不如直接用backup的方案呢」→「我们用backup的方案，不用 todo，你看下还有什么可以逻辑优化的」。

方向回到 backup：**微信原生 `<editor>`**，真所见即所得。待办不做（`format('list','check')` 是支持的，但豆哥不要）。

## 跟 backup 的差别：四处逻辑优化

外壳照 backup（原生 editor），改的是它内部那几条最脆的逻辑。

| backup 做法 | 本轮做法 |
|---|---|
| `setContents({ html })`，html 由 `marked.parse` 生成 | `setContents({ delta })`，delta 由已有的 `parseMarkdown` 结果直接构造 |
| `e.detail.html` → ~20 条正则 `htmlToMarkdown` | `e.detail.delta` → `deltaToMarkdown`，纯结构化遍历 |
| `isUpdatingFromExternal` 标志位（回调不触发就永久卡输入） | 比较「delta 往返后的值」，没有标志位 |
| 全局 `app.globalData.editorManager` 单例 + 字符串方法名派发 + 反查 vm | editorCtx 就在组件里，工具栏内联 |
| 图片插入本地临时文件，提交阶段替换 `data-local` | **先上传拿网络地址再插入**，没有替换这一步 |

**为什么要换成 delta**：微信官方 editor 文档原文——「通过 setContents 接口设置内容时，解析插入的 html 可能会由于一些非法标签导致解析错误，**建议开发者在小程序内使用时通过 delta 进行插入**」。走 delta 之后整条链路不出现 HTML 字符串，也就不需要那层正则。

## 落地

| 文件 | 作用 |
|---|---|
| `src/utils/md-delta.ts`（新） | `markdownToDelta` / `deltaToMarkdown` |
| `src/components/so-md-editor.vue`（重写） | 原生 editor + 内联工具栏 + 字数 + 完成 |
| `src/utils/markdown.ts` | 删掉 `parseInline`（块编辑器没了，无调用者） |
| `src/components/so-md-block.vue`、`src/utils/md-blocks.ts` | **删除**（02-17 的块编辑器，换方案后无调用者） |
| `src/pages/topic-detail/index.vue` | 去掉 `autofocus`（EditorContext 没有 focus 方法，弹不了键盘） |

## delta 的两个约定（踩过的点）

1. **块级属性挂在块尾的换行上**，行内属性挂在文本上（Quill delta 的约定）。
   例如标题：`{insert:'标题'}` + `{insert:'\n', attributes:{header:2}}`。
2. `header` 的取值微信文档写成 `H1 / H2 / h3 / H4 / h5 / H6`（大小写混排），
   解析时用正则取数字兼容，生成时统一传数字。

另外**块之间要补空行**：delta 不记录段落间距，直接 `join('\n')` 会把标题和正文挤成一段，
语义就变了。列表项之间紧排，其余块之间空一行。

## 代价（微信 editor 的能力边界，backup 也一样）

editor 支持的标签白名单里**没有 `pre` / `code` / `blockquote`**，所以：

- **代码块退化成纯文本块**（内容保留，围栏丢失）
- **引用退化成普通段落**
- **表格退化成一段文本**
- 分割线的 delta 表示不固定，退化成空行

编辑一条含代码块/引用/表格的旧记录再保存，这些结构会丢。这是原生 editor 的硬限制，
backup 也有，换不走。

另一个：**EditorContext 没有 focus 方法**，只能让用户自己点编辑区，没法自动弹键盘。

## 验证

- `type-check` + `build:mp-weixin` 通过。
- delta 往返冒烟（esbuild 打包跑 node）：标题、行内（粗体/斜体/链接）、无序、有序、混合（含图片）、
  纯文本、空串、软换行 —— 全部正确，混合用例**逐字还原原文**。另模拟了一份 editor 风格的
  delta（header/list/bold/image）验证反向解析正确。
- 产物：`so-md-editor.wxml` 里 `<editor>` 带 id / placeholder / read-only / bindready / bindinput /
  bindstatuschange / bindfocus / bindblur，工具栏数据与上传链路都在。
- **一个虚惊**：产物里 editor 被 `<block wx:if="{{r0}}">` 包着，而组件 js 里没有 `r0`。
  对照 backup 的产物——**结构完全一致**（同样是 `r0`、同样 js 里没有），
  最后在 `common/vendor.js`（uni-app 运行时）找到 `r0=1`。是框架行为，不是 bug。

## 怎么测

风格预览页 `test-theme` 挂了编辑器：选中文字点 B / I / U / S，点 H1/H2/H3 变标题，
有序/无序列表，插入图片走完整上传链路，↶/↷ 撤销重做。
