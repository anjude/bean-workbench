# 02-3 统一高复用组件样式（button / card）

## 背景
carbon 有专门 `05-components/button.css`（base reset + primary/secondary + active + disabled），
superone 的 `05-components/` 此前是空目录（仅 .gitkeep），按钮/卡片外观散落在各页面 scoped 里重复写。
目标：参考 carbon 把高复用外观收口成统一件，页面 scoped 只留布局与间距。

## 做了什么
1. 新增 `src/styles/05-components/_button.scss`
   - `.so-btn`（base：flex 居中、min-height 88rpx、padding、圆角、去边框、透明底）
   - `.so-btn-primary`（绿底白字）/ `.so-btn-secondary`（描边绿字）
   - `:active`（opacity .85 + scale .98）、`[disabled]` 态
   - 品牌绿处保留硬编码兜底再叠 `var()`：规避真机微信基础库对 `background` 里 var() 支持不稳
2. 新增 `src/styles/05-components/_card.scss`
   - `.so-card`（`--so-bg-elevated` 表面 + `radius-lg` + overflow hidden，默认不内边距）
   - `.so-card--pad`（需要内边距时叠加）
3. `index.scss` 接入 button / card。
4. 现有 UI 改用统一件：
   - `pages/index/index.vue` 设置按钮 → `so-btn so-btn-primary`（scoped 只剩 margin-top）
   - `components/so-page.vue` 重试按钮 → `so-btn so-btn-secondary`（scoped 只收窄成小号描边）
   - `pages/index/index.vue` 功能卡片 → `so-card so-card--pad`
   - `pages/settings/settings.vue` 设置卡片 → `so-card`
5. 补 `06-utilities/_colors.scss` 缺失项：`.so-bg-elevated`、`.so-text-disabled`（扫描发现被引用但未定义）。

## 结论
- 高复用外观归 `05-components`，页面 scoped 只保留「这一页特有的布局/间距」——避免同一套外观在多处各写一遍。
- **工具类的定义缺口要用扫描查**，不能靠肉眼：写脚本比对「模板里用到的 `so-*`」与「styles 里定义的 `so-*`」，
  本次就扫出 `so-bg-elevated` / `so-text-disabled` 两个有引用无定义的坑。

## 被推翻的判断
- 上一轮把「浅色下首页卡片看不见」归因为**白卡白底**（elevated 浅色=#fff 与 base 同色）。
  实际更根本的原因是 **`.so-bg-elevated` 这个工具类根本没定义**，卡片压根没有背景色（透明），
  铺的是页面底色。加 `--so-bg-secondary` 页面底只是缓解，真正修复是补上工具类 + `.so-card` 统一表面。
- 之前判断「原生 button 的 var() 是主因」只对了一半：改成 `view` + 硬编码兜底仍值得保留，
  但统一件里已经内置兜底，页面不再各写各的。

## 验证
- `type-check` 通过；`build:mp-weixin` 成功。
- `dist/build/mp-weixin/app.wxss` 确认含 `.so-btn` / `.so-btn-primary`（含 `#07c160` 兜底）/ `.so-btn-secondary` / `.so-card` / `.so-bg-elevated`。
- 页面 wxss 确认已瘦身：`.home__card` 只剩 flex、` .home__settings-btn` 只剩 margin-top、
  `.settings__card` 只剩 margin-bottom、`.so-page__retry` 只剩收窄尺寸。

## 待核
- 真机浅色模式目测（需整包重编译 + 重新真机预览，别走热重载）。
- 后续若有第二处列表行复用，再收口成 `05-components/_list.scss`（当前仅设置页一处，暂不建）。
