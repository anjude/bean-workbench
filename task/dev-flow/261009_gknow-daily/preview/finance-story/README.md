# 理财人格 · 12题完整版预览

当前为12个股票现场与7种类型结果，另有双类型、分散和全跳过。前四题保持已确认稿；纸色墨线、阿白与金色主按钮沿用认可画风，新增logo与类型形象。正式结果只展示类型、正文与另一面，不显示答案回看。

- [开始体验](http://127.0.0.1:5198/)
- [结果示例](http://127.0.0.1:5198/?screen=result)
- [双类型示例](http://127.0.0.1:5198/?screen=result&choices=CBABABCABADC)
- [完整方案](../../plans/理财人格-完整题库与类型结果.md)
- `identity/`是原静态视觉初稿；当前真实页面在根地址

## 启动与验证

工作台根目录执行`node task/dev-flow/261009_gknow-daily/preview/finance-story/server.mjs`，端口5198。预览消费真实业务Vue和控制器；定位参数只用于浏览器，不进入生产逻辑。

验证脚本：`verify_stock_assessment.cjs`（12题与评分）、`verify_stock_full_browser.cjs`（真实流程与截图）、`verify_paper_poster.cjs`（实际海报绘制函数与Canvas）。截图在`ui/stock-full/`。运行脚本需要playwright；资产生成`build_identity_assets.cjs`另需sharp，均使用本机已有运行时依赖，不新增业务依赖。

`build_identity_assets.cjs`由业务仓SVG生成PNG插画与分享卡；SVG原设计来源在`identity/build.py`。

历史`verify_stock_samples.cjs`、`verify_quiz.cjs`和`verify_browser.cjs`对应旧版，不适用于当前版本。微信分享、相册和端上SVG由真机验收，浏览器仅验证页面与绘制，不能替代原生能力验收。
