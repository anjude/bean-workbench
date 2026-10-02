# 02-4 页面外壳约定 + profile 页（参考 carbon profile）

## 背景
豆哥问 `so-admin-switch.vue` 是什么，并指出 carbon 有 Switch 样式组件可参考、整个 profile 页可参考 carbon；
同时立了一条页面外壳约定：**所有页面必须包在 `so-page` 下，例外只有 profile 页与 settings 页**。

## so-admin-switch.vue 是什么
管理员 QA 工具：右下角悬浮胶囊，仅 `store.isAdmin` 可见，调 `store.setWbbb()` 切演示/真实模式。
它对应 carbon `cu-page.vue` 里的 `p-page__admin-card`（「切换模式」按钮）——carbon 把它放在门禁组件里，
superone 做成全局悬浮入口，挂在每个 `so-page` 内。**普通用户完全看不到，不影响生产。**
（profile 页的管理员面板是同一 store action 的第二处入口，不新增状态源。）

## 做了什么
1. 新增 `05-components/_cell.scss`（参考 carbon `p-system-config__item`）：
   `.so-cell`（行 + 分隔线，最后一行无线）+ `__content`/`__icon`（`--info` 变体）/`__text`(title/sub)/`__extra` + `hover-class="so-cell--hover"`。
2. 新增 `05-components/_switch.scss`：统一原生 `<switch>` 尺寸（scale .85）+ 右侧对齐。
   **color 属性写死 `#07c160` 不用 var()**——原生组件属性对 CSS 变量支持不稳（真机尤甚），而主色深浅同值，写死等价。
3. **settings 页**：按新约定去掉 `so-page` 包裹，改为自挂 `themeClass` 的 shell（同 carbon profile 的 `p-system-config-shell`）；
   列表行改用 `.so-cell`；「界面主题」右侧改为原生 `<switch>`（跟 carbon 一致，行本身不再绑 tap，避免与开关双触发）。
4. **新建 profile 页** `src/pages/profile/profile.vue`（carbon profile 同构，不包 so-page）：
   shell + `so-custom` 导航栏 → 用户信息卡（头像/昵称/ID，读 `store.userInfo`）→ 功能列表卡（设置，跳 settings）
   → 管理员面板卡（`v-if="store.isAdmin"`，真实模式 switch 调 `setWbbb`）。已在 `pages.json` 注册（`navigationStyle: custom`）。
5. **test-theme 页**改包 `<so-page>`（原先只用 `.so-page` 类、没用组件），满足「除 profile/settings 外包 so-page」。
6. 首页「我的」卡片加跳转到 profile（cards 项加 `url`，只有带 url 的才跳，其余仍是占位）。

## 结论
- 页面外壳约定落地：index / test-theme 包 `so-page`；profile / settings 自挂主题类、不包门禁。
- 高复用件继续收口：`button` / `card` / `cell` / `switch` 四件套，页面 scoped 只留布局与间距。
- 「设置项 + 右侧插槽」这一形态现在有 cell 统一件，后续新列表页直接复用，不再各写各的。

## 遇到的坑
- uni 的 `switch` `@change` 事件签名是 `Event`（没有 `SwitchChangeEvent` 类型），
  自定义 `{ detail: { value: boolean } }` 参数过不了 type-check。写法：`function onXxx(e: Event)`，
  函数内 `(e as unknown as { detail: { value: boolean } }).detail.value` 收窄。

## 验证
- `type-check` 通过；`build:mp-weixin` 成功；dist 新增 `pages/profile/`（js/json/wxml/wxss），`app.json` 已注册。
- `app.wxss` 确认含 `.so-cell` / `.so-cell--hover` / `.so-switch`。
- `profile.wxml` / `settings.wxml` 均含 `so-switch`。
- 页面包裹检查脚本确认：index ✓、test-theme ✓ 包 so-page；profile ✗、settings ✗（例外，符合约定）。

## 待核
- 真机整包重编译后目测：settings 主题开关、profile 页（管理员面板仅管理员可见）。
- profile 页当前只有「设置」一个功能入口，后续按业务补。

## 更正（2026-10-02 稍晚）：settings 页并入 profile，全站只留一个设置类页面
- 豆哥问「settings 和 profile 保留一个是不是够了」→ 是。两页加起来只有三个功能（主题/关于/管理员），且 carbon 只有 profile 无 settings。
- 决定：**保留 profile，删除 settings**。原 settings 的主题 switch 与「关于」两项并入 profile 的「偏好与信息」卡；profile 里那条自指的「设置」入口删除。
- 连带改动：`pages.json` 移除 settings 注册；首页底部按钮由「设置」改「我的」跳 profile（`.home__settings-btn` 改名 `.home__enter-btn`）；首页卡片去掉 url 与点击（避免同页两个入口指向 profile）。
- 页面外壳约定随之收紧：**例外只有 profile 一页**（原为 profile + settings）。
- 验证：删 dist 后整包重编译，type-check + build 通过；dist 只剩 index/profile/test-theme 三页，`app.json` 已无 settings；profile.wxml 含「界面主题」switch +「关于 SuperOne」+ 管理员「真实模式」switch。

## 更正二（2026-10-02）：profile 照抄 carbon + backup，不要自己精简
- 豆哥反馈「真实模式是什么鬼」→ 那个名字是我自己编的。carbon 与 backup 的管理员面板都是**两个 switch**：「切换场景」（只改本地显示模式）与「入口模式」（调 updateSystemInfo 写服务器）。已照抄这两个名字与语义，删掉自造的「真实模式」。
- 本轮 profile 页按 carbon `pages/profile/index.vue` + `uni-superone-backup/src/pages/profile/index.vue` 抄全：
  - 用户信息卡（仅 wbbb===1 显示）：头像可点换（chooseMedia → uploadImage → updateUser）、昵称点击内联编辑（blur 提交 updateUser）、分享主页（open-type=share + onShareAppMessage）、注册时间。
  - 菜单卡：联系客服（open-type=contact）、自定义链接菜单（读 systemConfig.linkMenu，点击复制链接）、重新登录（清 token → login → store.init）、界面主题（switch）。
  - 管理员面板（v-if isAdmin）：切换场景（本地改 systemConfig.wbbb）/ 入口模式（store.setWbbb 写服务器）/ 用户行为统计（picker 选天数 + 查询 + 表格，抄 carbon 的 statsTableData 计算）/ 链接管理（3 组 input + updateSystemInfo）/ 用户列表（getUserList + onReachBottom 分页）。
- 未抄：反馈页、新手引导、webview（superone 暂无对应页面/能力）；统计表格用原生 view 拼，没有 cu-empty-state/cu-input 就用原生 input 与占位文案。
- 契约能力核对（都能对上才敢抄）：`userApi.updateUser/getUserList`、`commonApi.updateSystemInfo(wbbb|linkMenu*)/getUserBehaviorStats`、`uploadImage`、`CacheManager.remove(TOKEN)` + `getLoginAdapter().login()`。
- 验证：type-check + build 通过；profile.wxml 含 联系客服/链接菜单/重新登录/界面主题/切换场景/入口模式/用户行为统计/链接管理/用户列表/分享主页。
