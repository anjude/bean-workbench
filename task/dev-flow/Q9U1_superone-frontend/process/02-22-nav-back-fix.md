# 02-22 导航返回键失效：onBack 兜底的两层坑

> 豆哥：「修复了吗，问题还是存在」。

## 结论先说

`so-custom` 的返回键一共三层问题，本轮修了最核心的两层，并在 H5 真机浏览器里回归验证通过：

1. **初版实现押错兜底**（`uni.navigateBack({ fail })`）：uni-h5 无历史可退时仍走 success，
   fail 永不触发；微信小程序栈深 1 时 fail 也不可靠。→ 改回 backup / carbon 的**同步查栈**模式。
2. **工作区里已有一版修复把 `__wxConfig` 作为兜底条件**：`__wxConfig` 是小程序独有全局，
   H5 上 `typeof __wxConfig !== 'undefined'` 恒为 false，整个兜底键失效 → H5 直达/刷新页返回键仍然全哑。
3. **（未修，另案处理）`so-page` 把默认插槽整体门控**：app 初始化失败 / loading / 锁定态时
   导航栏连同业务内容一起不渲染，错误屏只剩「重试」，没有任何返回出口。

## 最终 onBack（so-custom.vue）

```ts
function onBack() {
  // @ts-ignore
  if (typeof getCurrentPages === 'function' && getCurrentPages().length > 1) {
    uni.navigateBack({ delta: 1 })
    return
  }
  uni.reLaunch({ url: '/pages/index/index' })
}
```

与 backup `cu-custom.BackPage` 的差异：不读 `__wxConfig.pages[0]`，fallback 直接硬编码
`/pages/index/index`（pages.json 首个页面就是它，与 onHome 一致），换取 H5 / 跨端可用性。

**关键认知**：`getCurrentPages` 不是小程序独占——uni-h5 有 polyfill（`uni-h5.es.js`
内部多处使用，H5 实测 `typeof window.getCurrentPages === 'function'`），所以「同步查栈 +
reLaunch 兜底」在两端都成立；`__wxConfig` 才是小程序独占，不能进兜底条件。

## 浏览器实测（H5，dev server + 指针事件模拟点击）

| 场景 | 修复前 | 修复后 |
|---|---|---|
| 栈深 ≥2（index → profile 后点返回） | navigateBack 正常 | ✅ 正常，回到上一页 |
| H5 直达/刷新 profile（栈深 1） | 无反应，控制台干净 | ✅ reLaunch 到 `#/`（首页） |
| mock 栈空（防御分支） | — | ✅ reLaunch 到 `#/` |

验证脚本要点：直接改 `location.hash` 模拟直达，刷新后 uni 栈长实测为 1
（`getCurrentPages()` 返回 `['pages/profile/profile']`），点击后 hash 变为 `#/`。

## 顺带发现（未修，值得单开一条）

- **`so-page` 门控吃掉导航栏**：`store.ready / failed / isReal` 任一不满足时默认插槽不渲染，
  `so-custom` 在插槽里 → 错误屏只有「重试」没有返回。topic-detail 页内那个
  「error && !topic → 返回按钮」的分支（topic-detail/index.vue:11-14）也因此变成 unreachable
  （它在被门控的默认插槽里）。要让错误屏有返回出口，得把导航栏挪到门控外或给 so-page 加 error 插槽契约。
- **H5 dev 下 app init 必失败**：`develop` 环境 baseURL 是 `https://api.beanflow.top:8080`，
  H5 跨域/网络不通 → 所有被 so-page 门控的页面永远停在「网络请求失败 / 重试」。
  mp-weixin 无 CORS 不受此限。想在 H5 调通要么 proxy 要么放开 CORS。
  App.vue 有现成的 `envType = 'debug'`（本地代理 `so.proxy.beanflow.top:82`）注释开关。

## 验证

- `npm run type-check` 通过。
- H5 浏览器实测两条路径均符合预期（见上表）。
- mp-weixin 端行为与 backup 已生产验证的 BackPage 同构，待豆哥在 devtools 里顺手回归
  （重点：编译模式直达 topic-detail 后点返回，应 reLaunch 回首页）。
