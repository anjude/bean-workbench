---
name: bn-tools-format-flow
description: 把已选定的公众号稿件转成微信 HTML、预览页和 Markdown 副本；支持五套模板、自定义样式、本地 SEO 与词表检查、封面裁切。不负责文章内容取舍或上传发布。
---

# 公众号排版

执行代码随本 skill 落盘，不依赖用户级安装或外部排版网站。下列命令在工作台根目录执行；从其他目录调用时按本 skill 的实际位置解析 scripts/。

## 排版

从选题的发布稿单独提取标题与正文：只将正文写入 `publish/body.md`，标题作为元数据通过 `--title` 传入；内部说明、封面提示词、讨论记录不进入正文。微信草稿接口有独立标题字段，因此 `article_wechat.html` 只包含正文，不在 HTML 中重复放标题；本地预览可单独显示标题以模拟阅读页；预览页复制按钮只复制正文 HTML，与接口使用的正文内容一致。仅当留言引导本身属于用户确认的正文时保留。免责声明统一放在置顶留言，不放进文章 HTML；正文只排版对读者有用的内容。置顶留言单独保存为可直接复制的文案。模块约定见 [文章公共模块](../bn-tools-writing-style/references/article-modules.md)。

```bash
ARTICLE_TITLE="文章标题"
python3 .agents/skills/bn-tools-format-flow/scripts/formatter.py "$TOPIC/publish/body.md" \
  --title "$ARTICLE_TITLE" -t 微信绿 -o "$TOPIC/publish" --seo -k 复利
```

`TOPIC` 为当前选题目录。输出固定为 `article.md`、`article_wechat.html`、`preview.html` 和可选的 `article_seo.md`，再次执行会覆盖这些排版产物。原始发布稿不改。重新排版只更新本地文件，不会修改已入草稿箱或已设置定时发布的远端稿件；如远端已有稿件，生成新版本后交由 `bn-tools-publish-flow` 核对并同步。

- 模板：微信绿、经典红、商务蓝、清新绿、优雅紫、温暖橙；beannote 默认使用微信绿，其他主题沿用用户指定或账号已有模板。
- 自定义样式用 `-c config.json`；可覆盖配色、font、spacing、image、card、heading_numbering 等，字段见 [排版参数与检查边界](references/layout.md)。
- 输入支持 Markdown 或 JSON blocks。纯文本和 HTML 先核对内容并转成 Markdown/blocks；脚本不直接解析任意 HTML。表格、列表、公式、图片和出处在预览中逐项核对，特别检查移动端宽度与文字丢失。
- SEO 分数与词表命中仅为本地提示，不作为自动改标题、加图、改观点或通过审核的依据。详见上述 reference。

## 图片

### 公众号封面风格

- 封面不必概括整篇文章。优先从文章重点中挑一个有意思、具体、能形成画面的切口，例如反差、意外、动作、人物反应或某个鲜活细节，让封面成为引人点开的视觉钩子。
- 画面可以幽默、夸张或带一点戏剧性，不必每次都用抽象隐喻；但读者应能看出这个有趣画面与文章重点有关。生成后用一句话说清画面切口；若必须额外解释才能建立关联，就换一个更具体的画面。
- 构图保持清楚，优先突出一个视觉钩子；可按创意需要安排人物和道具，不必机械限制主体数量。缩略图下仍能先看到关键动作、表情或反差。
- 投资、理财等主题不直接出现钱币、钞票、K 线、走势图、金融终端等理财符号；从文章真正要表达的感受或逻辑出发，选择含蓄的视觉隐喻。
- 视觉方向以有表现力的绘画笔触为主，保留手绘质感，不限定东西方画派；抽象程度以不妨碍读懂主题关系为限。不要模仿某位在世艺术家的具体风格。
- 不套固定物件、构图或配色；根据每篇文章重新选择有趣切口，避免系列封面变成同一张图换主题。
- 默认不在图上主动添加标题、文字、数字、Logo 或水印；用户另有要求时再添加。素材自带的必要来源或 AI 标识按图片工具规则保留。
- 以上是账号的默认视觉方向，不要求所有题材都用同一种画派细分、色板或构图。生图时按主题具体化隐喻，同时遵守图片工具的 skill。
- 可参考 [外部封面样本的可读性原则](references/cover-visual-reference.md)：学习如何从文章切出具体、有趣、带情绪或戏剧感的画面，不复用原图或套用对方的具体素材。

```bash
python3 .agents/skills/bn-tools-format-flow/scripts/image_enhance.py 原图.png 封面.jpg --cover-crop --ratio 2.35
```

图片工具需要 Pillow；排版和检查仅需 Python 标准库。当前系统 Python 缺 Pillow，可用桌面依赖工具返回的 Python 运行时（本轮已验证），不要把该运行时的机器绝对路径写死到脚本。macOS 无 Pillow 时可用 `sips --cropToHeightWidth 高 宽 原图 --out 输出图` 和 `sips -s format jpeg -s formatOptions 85 输出图 --out 封面.jpg`。先按原图尺寸计算居中裁切范围，2.35:1 是当前工作台封面默认值，可按实际展示位调整。保留原图和必要的来源、AI 标识信息，不把去除标识作为裁切目标。

正文图片先用 `bn-tools-publish-flow` 上传取得微信 URL，再回填排版输入并重跑；本地路径或占位符不能作为最终入库图片。需要生成新图时使用当前环境的生图工具，遵循该工具的 skill。

## 交付

报告发布稿、HTML、预览和检查报告的位置，说明排版中无法保真的元素。用户已授权入草稿箱时接 `bn-tools-publish-flow`，并将实际结果写回选题。

整条链路的模式、输入输出与二次开发缺口见 [生产发布流程](../bn-tools-publish-flow/references/production-flow.md)，理解或改造跨环节流程时读取。
