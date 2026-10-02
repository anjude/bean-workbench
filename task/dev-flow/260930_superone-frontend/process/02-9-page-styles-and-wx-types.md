# 02-9 页面样式收进 06-pages + 补 wx 类型声明

> 豆哥：「把css从页面挪到itcss的文件夹里，有个专门的page文件夹，命名记得以p开头」；
> 「wx 没有全局类型声明（carbon 那边有类型包）。这个可以在superone也弄一下吗」。

## 一、页面样式收进 06-pages（照 carbon）
carbon 的页面样式全在 `src/styles/06-pages/*.css`（`p-index.css`、`p-system-config.css`、`p-invite.css`…），
`.vue` 里不放样式；superone 的 `06-pages/` 之前只有 `.gitkeep`，样式都堆在页面的 `<style scoped>` 里。

### 做了什么
- 新建三个页面样式文件（文件名照 carbon 以 `p-` 开头）：
  - `src/styles/06-pages/_p-index.scss`（首页，230 行）
  - `src/styles/06-pages/_p-profile.scss`（我的页，225 行）
  - `src/styles/06-pages/_p-test-theme.scss`（风格预览页，171 行）
- 三个页面的 `<style scoped>...</style>` 整块删除（index 407→176 行、profile 788→562 行、test-theme 322→150 行）。
- `styles/index.scss` 接入三份（原来 06 页面是「占位目录」的注释）。
- 类名前缀不变：`so-index__*` / `profile__*` / `preview__*`（项目前缀是 `so-`，不改成 carbon 的 `p-`）。

### 代价与约定（挪出 scoped 必须知道）
- 失去 `data-v-xxx` 隔离 → **命名靠唯一前缀防冲突**，页面间不能撞类名。
- 好处：`--index-nav-height` 这类由 JS 注入的样式变量、跨组件根节点（如给 `so-custom` 传的
  `.so-index__nav`）不用再靠 `:deep()` 或父级 scope 传递，写起来更直接。
- 组件样式（`so-page` / `so-custom` / `so-demo-page`）仍在组件内 scoped，不动——
  它们属于 05-components 层，不是页面层。

### 验证
- `type-check` + `build:mp-weixin` 通过。
- `dist/.../pages/*/*.wxss` 三个文件都是 **0 字节**（页面不再自带样式）。
- `dist/.../app.wxss` 含 `so-index-shell` / `profile__body` / `preview__swatch`（样式已收进全局层）。

## 二、wx 全局类型声明（**已按豆哥提醒改用 backup 的做法**）
- 豆哥：「你看看backup有没有wx的type文件，我记得应该有这个包可以下的」。
- 查证：**backup 和 carbon 都有 `src/types/platform.d.ts`**，是同一份手写声明（wx / my / swan / tt / __wxConfig），
  superone 迁移时漏了。所以我上一轮自己写的 `src/types/wechat.d.ts` 是重复造轮子，已删除
  （两个 `const wx` 会重复声明冲突）。
- 现在：`src/types/platform.d.ts` 照抄 backup/carbon 那份，只在 wx 里补了海报用的
  `showShareImageMenu`（`declare global` + `export {}` 写法不变）。
- 细节：`showShareImageMenu` 声明为**必选**（不是 `?`）——它只在 `#ifdef MP-WEIXIN` 块里调用，
  编译期已保证平台；`restartMiniProgram` 是可选，因为它要运行时降级。声明成可选的话，
  调用处会被 TS 要求判空（`TS2722: Cannot invoke an object which is possibly 'undefined'`）。
- 上一轮「carbon 没有类型包」这句仍然成立（它没有 npm 类型包、也不跑 type-check），
  但它**有手写的 platform.d.ts**——这才是一脉相传的正解。
- 事实核查：**carbon 并没有类型包**——它 `tsconfig` 的 `types` 和 superone 一样是 `["@dcloudio/types"]`，
  而 `@dcloudio/types` 里根本没有 `wx` 的声明。carbon 之所以不报错，是因为它**没有 type-check 脚本**
  （`package.json` 里搜不到 `tsc`/`type-check`），裸 `wx.login(...)` 一直没被检查到。
- superone 跑 `vue-tsc`，所以写裸 `wx` 会报 `Cannot find name 'wx'`（上一轮海报转发已经踩到）。
- 做法：新增 `src/types/wechat.d.ts`（全局 d.ts，`tsconfig` 的 include 已含 `src/**/*.d.ts`），
  **只声明项目真正用到、且 uni 没封装的 API**（目前只有 `showShareImageMenu`），用到一个补一个。
  没引 `@types/wechat-miniprogram` 这类完整包——避免与 `@dcloudio/types` 重复声明打架。
- 配套：`usePosterShare.ts` 的转发改回 carbon 原样的「条件编译 + 裸 `wx`」写法
  （上一轮为了过 type-check 临时改成了 `globalThis.wx` 运行时探测，现在可以还原）。

## 结论
- **页面样式归 06-pages，组件样式留在组件里**，这是 ITCSS 分层的本意；carbon 就是这么分的。
- 抄 carbon 前先确认它**有没有跑这道检查**：它没跑 type-check，所以「carbon 这么写没报错」
  不代表我们这么写也没报错。类型能力上要自己补，不能照搬它的"看起来没事"。

## 待核
- 全局化后若后续页面出现同名类，需要靠前缀区分（当前三个页面前缀各不相同，安全）。
- `wechat.d.ts` 是按需补的：以后再用 `wx.xxx` 而 `uni` 没封装的，要回来补声明。
