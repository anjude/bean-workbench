# 02-19 照搬 backup 编辑器（含 iconfont），再收主题与逻辑

> 豆哥：「你这实现根本就不对吧，你都可以直接复制相关文件过来，再做优化，实在不行就照搬backup的，
> 然后调一下主题啥的就好了」+「iconfont也拿过来」。

前三轮（02-15 直编源码 / 02-17 块级 Live Preview / 02-18 delta）都是我另起炉灶，
**没有一次是先让 backup 那套跑起来**。这次认了：整份复制，先跑通，再挑真问题改。

## 搬了什么

| backup | 落到 uni-superone |
|---|---|
| `cu-md-editor.vue` | `components/so-md-editor.vue` |
| `cu-md-editor-toolbar.vue` | `components/so-md-editor-toolbar.vue` |
| `utils/markdown.ts`（html↔md 正则那套） | `utils/md-html.ts`（改名，避开我们已有的 AST 版 `markdown.ts`） |
| `types/md-editor.d.ts` | `types/md-editor.d.ts`（只留 `EditorFormats`） |
| `app.globalData.editorManager` | `utils/editor-manager.ts`（模块级单例，类型齐全） |
| iconfont + 编辑器图标 CSS | `styles/07-vendors/iconfont.css`、`styles/07-vendors/md-editor.css` |

07 层此前只是占位注释，本轮接进 `styles/index.scss`（sass 1.90 能直接 `@use` 纯 `.css` 文件，
不用改成 `.scss`）。

## 改了什么（照搬之后暴露的真问题）

**1. 上传返回值接错了。** 项目里 `uploadImage()` 解完信封返回的是 `WxUploadResp` 对象，
地址在 `.url` 上；backup 的 `ImageUploadUtils` 直接给字符串。照搬会拿一个对象去 `insertImage({src})`。
已改成取 `resp.url`，取不到直接 reject。

**2. 补一处边界：最后 100ms 的输入。** `onInput` 挂 100ms 防抖再转 markdown，
理论上敲完字 100ms 内点「记下来」/失焦，最后几个字不在 `internalMarkdownContent` 里
（backup 同款代码，同一处；实际人手速很难踩到，所以线上没暴露）。
拆出 `commitInput()` / `flushInput()`，`onBlur` 与 `onComplete` 先 flush 再往下走。

**3. 响应式来源要显式写出来（不是 backup 的 bug，这条判断曾判错，已更正）。**
我一度以为工具栏的 `activeEditor` computed「永不失效、按钮会一直全灰」，并把它记成 backup 自带的 bug。
翻 backup 原文核对后**结论是错的**：backup 的 `app.globalData` 是 `reactive({...})`（`stores/app.ts` 原注释
「让全局数据具备响应性，以便页面 computed 能自动更新」），`app.globalData.editorManager = {...}` 赋值触发 add，
且深代理会把 manager 整个对象包成 proxy → `getActiveEditor()` 里读 `this.activeEditorId` 是被 track 的
→ `setActiveEditor` 写它就会让 computed 失效。**线上能正常使用，没有问题。**
本项目 app store 是 pinia、没有 globalData 这种可挂的 reactive 容器，所以我改成导出一个显式 `ref`
（`activeEditorId`）——响应式来源写在明处，不复制「恰好被深代理包住」这个隐式前提。
顺带去掉 `isActiveEditor` 这个挂在实例上的镜像标志（有 ref 就不需要）。

> 教训：**说「既有实现有 bug」之前必须把原文拉出来核到行**。backup 是线上跑着的代码，
> 推断出来的「bug」十有八九是我漏看了它的依赖链。

**4. 砍掉两条本项目用不上的分支。** 工具栏原本有「全局浮动工具栏（so-page 挂 `isGlobal`）」与
「内嵌（`embedded`）」两套定位逻辑，外加 iOS 判定、键盘高度、`isIndex` 贴底策略。
本项目 so-page 不挂全局工具栏，浮动那条路是死代码；一律内嵌之后键盘高度与 iOS 判定也没用了。
一并删掉，工具栏退化成「挂在编辑器下方、没聚焦就整体置灰」，425 行 → 约 200 行。
编辑器侧的 `embedded` / `isIndex` / `isActiveEditor` 相应删掉。
另外 `:has()` 选择器小程序不支持，那条规则换成普通写法。

**5. 弃用 API。** `uni.getSystemInfoSync()`（backup 用它判 iOS）随上面那条一起没了。

**6. 主题。** 编辑器 18 处 + 工具栏 24 处 carbon 令牌批量换成 `--so-*`
（`--bg-primary`→`--so-bg-elevated`、`--theme`→`--so-color-primary`、
`--gray-100/200/600`→`--so-bg-secondary`/`--so-divider-color`/`--so-text-muted`、
`--shadow-md`→`--so-shadow-deep` …），`cu-` 类名与 carbon 令牌残留清零。
组件名 `CuMdEditor`→`SoMdEditor`，根类 `md-editor`/`editor-container`→`so-md-editor`/`so-md-editor__container`。

**7. `:maxlength` 不是编辑器的 prop。** 主题详情页原来传它其实会被当透传属性丢到根 view 上，
什么都不做。改到 `onSubmit` 里用 `CONTENT_MAX` 校验（后端 `binding:"max=10000"`）。

## 没动的地方（backup 的能力边界，换不走）

原生 editor 标签白名单没有 `pre` / `code` / `blockquote`：代码块退化成纯文本、引用退化成段落、
表格退化成文本。改一条含这些结构的旧记录再保存会丢结构。**EditorContext 没有 focus 方法**，
只能让用户自己点编辑区，弹不了键盘。

## 验证

- `npm run type-check` 与 `npm run build:mp-weixin` 均通过。
- 产物 `app.wxss` 里 `@font-face`(alicdn) 与 11 个工具栏图标类（`icon-format-header-3` /
  `icon-zitijiacu` / `icon-fontbgcolor` / `icon-youxupailie` / `icon-wuxupailie` / `icon-indent` /
  `icon-fengexian` / `icon-charutupian` / `icon-undo` / `icon-redo` / `icon-reset`）逐个核对存在。
- `so-md-editor.wxml` 里 `<editor>` 的 id / placeholder / read-only / bindready / bindinput /
  bindstatuschange / bindfocus / bindblur 齐全（`editor` 是原生组件，json 里不需要声明）。

## 待真机确认

工具栏内嵌后只在编辑器下方，键盘弹起时不会自动顶上去（backup 在 iOS 上本来也是这个行为）。
如果真机上「键盘挡住工具栏」明显，再考虑加 `cursor-spacing` 或把编辑器放到页面顶部。
