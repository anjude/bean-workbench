# 02-13 弃用告警：getSystemInfoSync → getWindowInfo / getAppBaseInfo

> 豆哥贴开发者工具告警：`wx.getSystemInfoSync is deprecated`，问要不要改。

## 判断：改
- 微信把 `getSystemInfoSync` 标记为停止维护，推荐按用途拆成
  `getSystemSetting` / `getAppAuthorizeSetting` / `getDeviceInfo` / `getWindowInfo` / `getAppBaseInfo`。
- 我们 4 处调用**只取两类信息**：窗口尺寸与状态栏（so-custom、index ×2）、系统主题（useTheme）。
  正好对应 `getWindowInfo` 与 `getAppBaseInfo`，替换是同名字段，无语义差异。
- 成本极低：类型齐全（`@dcloudio/types` 的 `GetWindowInfoResult` 有 windowWidth/windowHeight/statusBarHeight；
  `GetAppBaseInfoResult` 有 `theme?: string`），`uni.*` 是跨端封装（H5/支付宝等端同样可用），改完 type-check 直接过。
- 不加回退分支：`wx.getWindowInfo` 要求基础库 ≥ 2.20.1（2022 年初），现网客户端早已远超，
  再写「探测不到就回退旧 API」是第二套解法（豆哥明确反对叠加）。

## 改了什么
| 文件 | 原 | 现 |
|---|---|---|
| `components/so-custom.vue` | `uni.getSystemInfoSync()` | `uni.getWindowInfo()` |
| `pages/index/index.vue`（导航高度） | `uni.getSystemInfoSync()` | `uni.getWindowInfo()` |
| `pages/index/index.vue`（模块可视高度） | `uni.getSystemInfoSync()` | `uni.getWindowInfo()` |
| `composables/useTheme.ts` | `uni.getSystemInfoSync() as { theme?: string }` | `uni.getAppBaseInfo()`（顺带去掉 `as`，类型里本来就有 `theme`） |

`uni.getMenuButtonBoundingClientRect()` **未弃用**，胶囊几何仍用它，不动。

## 验证
- type-check + build:mp-weixin 通过。
- 产物确认（BSD grep 要用 `-E`，`\|` 交替不生效，前面统计踩过一次）：
  `components/so-custom.js` 1 处 getWindowInfo、`pages/index/index.js` 2 处、`composables/useTheme.js` 1 处 getAppBaseInfo，
  业务代码已无 getSystemInfoSync。
- **告警不会 100% 消失**：`common/vendor.js` 里还有 9 处 getSystemInfoSync，是 uni-app 框架/uni-ui 内部在调，
  只能等框架升级，我们改不了。

## 约定
- 以后取窗口信息用 `uni.getWindowInfo()`，取系统主题/宿主信息用 `uni.getAppBaseInfo()`，
  不要再写 `uni.getSystemInfoSync()`。设备型号等用 `uni.getDeviceInfo()`。
