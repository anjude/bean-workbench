# 鹅懂个啥 · 小红书图片工坊

本机运行的图文图片编辑网站。添加封面、问答、微信对话、知识普及页面，编辑文案；Canvas 统一排成 1080 × 1440 PNG。AI 生图服务未配置时可上传本地画面素材继续排版。

## 启动

需要 Python 3.9+，不需要安装额外依赖：

```sh
cd task/dev-flow/261010_gknow-content-studio/local-studio
python3 app.py
```

然后打开 <http://127.0.0.1:8769>。按 `Ctrl+C` 停止。

## AI 生图配置

生图服务走本地 Python 后端适配，密钥不下发到网页。将服务配置在启动命令的环境变量中；`XHS_IMAGE_API_BASE_URL` 填 OpenAI-compatible API 根地址（例如以 `/v1` 结尾），`XHS_IMAGE_MODEL` 填服务支持的图像模型名：

```sh
XHS_IMAGE_API_BASE_URL='https://你的服务地址/v1' \
XHS_IMAGE_API_KEY='你的密钥' \
XHS_IMAGE_MODEL='你的图像模型名' \
python3 app.py
```

适配端调用 `{XHS_IMAGE_API_BASE_URL}/images/generations`，提交描述和竖图尺寸，读取 Base64 或图片 URL 响应。服务商若不兼容此接口，需要增加一个对应 provider adapter。图片提示词和图片请求会发送到配置的生图服务；不配置时不会向外发送。

## 当前能力

- 一篇帖子支持多页，可分别选择封面、问答、微信对话、知识普及模板。
- Canvas 实时绘制，可逐页下载 PNG 或导出包含整组图片的 ZIP。
- AI 生成背景素材后与 Canvas 文字/卡片版式合成；也可从本机上传图片。
- 页面文案和图片保存在当前浏览器 IndexedDB；没有内容云同步或发布功能。
- 页面只绑定 `127.0.0.1`，并校验本机 Host/Origin。
- 公开笔记学习、人工挑选素材下载和预发布包准备的工作流见工作台 skill：[xhs-tools-content-research](../../../../.agents/skills/xhs-tools-content-research/SKILL.md)。

微信对话模板绘制为聊天气泡风格的内容卡，不复刻微信真实界面；模板提示其为情景对话演绎。
