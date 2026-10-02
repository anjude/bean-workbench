# 02-12 对外品牌名：豆流便签

> 豆哥：「superone是我们内部的叫法，对外，这个小程序叫豆流便签。当然了，首页可以不显示这个title的」。

## 口径
- **对外 = 豆流便签**；**superone = 内部工程名**（组件前缀 `so-*`、storage key、logger、后端仓名、manifest）。
- 判断标准：用户看不看得见。看得见的用「豆流便签」，看不见的沿用 superone。

## 改了这些（对外可见）
| 位置 | 原 | 现 |
|---|---|---|
| 首页导航栏 | `#content` 插槽里的 SuperOne 标题 | **删掉**（豆哥定，首页不挂标题） |
| `pages.json` globalStyle / 首页 `navigationBarTitleText` | Superone | 豆流便签 |
| 演示页 hero eyebrow、海报 kicker、海报 footer | SuperOne | 豆流便签（统一走 `BRAND_NAME`） |
| 海报 canvas 品牌行 | SuperOne | 豆流便签（`usePosterShare` 兜底常量也改，防漏传露出内部名） |
| profile `onShareAppMessage` 分享标题 | SuperOne | 豆流便签 |

- 首页 `nav-title="豆流便签"`：custom 导航下不显示，但 `uni.setNavigationBarTitle` 会被调用，兜底保持对外名。
- 品牌名收成单一来源：演示页 `BRAND_NAME` 常量 + 海报 composable 的 `BRAND_NAME` 兜底，改名只动常量。

## 没改这些（内部标识）
- `so-*` 组件前缀、storage key（`superone:token` 等）、logger `[superone]`、`contract.ts` 的 `superoneHttpClient`、
  `manifest.json` 的 `name`、`test-theme` 调试页文案、契约仓与后端仓名。
- 理由：这些都是工程内部标识，改成中文名会让 key / 前缀 / 包名失去辨识度，且小程序真名由微信后台 + appid 决定，
  manifest 的 name 改了也不影响对外展示。

## 待定
- 小程序真名仍需在微信公众平台后台确认为「豆流便签」（代码里改不了）。
- `test-theme` 若哪天要上线，页面标题「SuperOne 风格」需一并换成对外名。
