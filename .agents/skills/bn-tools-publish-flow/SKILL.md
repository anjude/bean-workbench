---
name: bn-tools-publish-flow
description: 内容发布链路 skill，覆盖「编写定稿 → 排版 → 封面 → 草稿箱 → 发布记录」的机械流程。用户要给公众号发文、把初稿改成发布稿、排版推草稿箱、或发布链路报错排障（40164 / 40007 / 48001）时使用。只管流程与工具，不替用户做内容取舍。
---

# 内容发布链路：编写-排版-发布

beannote 选题定稿后，从发布稿到公众号草稿箱的机械链路。内容取舍（标题、结构、留哪些点、什么风格）归用户，本 skill 只保证链路完整、产物落盘、记录可查。

链路：初稿 → 发布稿 → 排版 → 封面 → 草稿箱 → 发布记录。产物全部落在选题目录 `task/beannote/topics/YYYY-MM-DD_主题/`。

## 一、编写定稿（初稿 → 发布稿）

1. 目录：选题目录下建 `草稿.md`（用户原文，原样留存）和 `发布稿.md`（定稿）；选题 `README.md` 用进度勾选跟踪，讨论过程进 `process/`。
2. 发布稿固定分节，顺序不动：

   ```text
   标题（H1）
   选题判断（写给谁 / 一句话结论 / 核心问题 / 标题定稿+备选 / 参考资料 / 事实风险）
   ---
   正文
   ---
   精彩引言 / 封面 prompt / 留言引导
   ```

3. 事实核实（定稿前必做，只核稿中出现的）：
   - 数字逐个核，能复算的当场算（复利、年限、比例）；
   - 引文查原话出处，后人发挥的句子在文中标注「本文测算」并与原话分清；
   - 时效数据（汇率、行情）查当日来源，正文写成约数；
   - 假设档位注明乐观/保守，不用单一乐观值讲故事。
4. 定稿后**停下等用户确认**，再进排版。内容层面的修改意见由用户提，不自行扩写。

## 二、排版

1. 切排版输入：从发布稿里抽出「标题 + 正文」另存为 `publish/body.md`。选题判断、封面 prompt、留言引导是内部元数据，不进排版。
2. 用 `oa-wechat-formatter`（用户级安装 skill）：

   ```bash
   python formatter.py body.md -t {模板} --seo -k "{关键词}"
   ```

   模板按账号调性选，一次发文一个模板。产物四份落在 `publish/`：`article.md`、`article_wechat.html`、`preview.html`、`*_seo.md`。
3. SEO 报告解读原则：
   - 搜一搜导向的项（标题长度、关键词密度）与账号风格冲突时不盲从；
   - 敏感词命中逐条人工判读，引文和专有名词常误报；
   - 配图项用来确认封面是否就绪，不因此给正文强塞插图。

## 三、封面

1. 封面 prompt 写在发布稿里，风格与账号既有封面保持一致。
2. ImageGen 生成横版大图，然后本地处理：

   ```bash
   # 居中裁 2.35:1（公众号封面比例），同时切掉右下角 AI 水印
   sips --cropToHeightWidth {高} {宽} 原图.png --out cover_235.png
   # 转 JPEG 控体积
   sips -s format jpeg -s formatOptions 85 cover_235.png --out cover.jpg
   ```

3. 排版 skill 的 `image_enhance.py` 依赖 Pillow，环境没有时用 sips（macOS 内置，零依赖），效果等价。

## 四、发布

1. 凭证（不硬编码、不进 Git）：
   - 密钥文件 `~/.wechat_pub_key`，两行（AppID、AppSecret），`chmod 600`；
   - 或环境变量 `WECHAT_APPID` / `WECHAT_APPSECRET`。
2. 前置检查：`python publish.py token`，验证凭证与 IP 白名单。
3. 上传封面换 `thumb_media_id`：`material/add_material?type=image`，multipart 上传 `cover.jpg`。当前 publisher skill 无素材上传能力，用一次性脚本顶替；稳定后并入 `task/beannote/script/` 或给 skill 补能力。
4. 推草稿箱：

   ```bash
   python publish.py draft \
     --title "{标题}" --author "{作者}" \
     --content-file publish/article_wechat.html \
     --digest "{摘要}" \
     --thumb-media-id "{封面 media_id}"
   ```

5. **draft/add 必须带 `thumb_media_id`**，缺封面报 `40007 invalid media_id`，与正文内容无关（最小 payload 可复现）。
6. 默认终点是草稿箱。群发（`freepublish/submit`）仅认证服务号可用，且必须用户明确授权后才调用。
7. 写 `发布记录.md`：平台 / 标题 / 作者 / 摘要 / 结果 / 草稿 media_id / 封面 media_id / 排版产物路径 / 排障记录 / 待办（后台确认 → 群发 → 回写发布时间与链接）。

## 五、排障速查

| 错误码 | 含义 | 处理 |
| --- | --- | --- |
| `40164` | IP 不在白名单 | 以微信报错里显示的 IP 为准加白名单。代理按目标主机粘住出口 IP，别信通用 IP 回显站（不同站点显示的可能不是同一个出口） |
| `40007` | draft/add 缺 thumb_media_id | 上传封面拿到 media_id 再提交 |
| `40013` / `40001` | AppID / 凭证无效 | 核对 AppID，必要时重置 AppSecret |
| `48001` | 无群发权限 | 订阅号 / 未认证号只能到草稿箱，由用户在后台手动群发 |
| `45009` | 接口调用超限 | 等配额恢复，不反复重试 |

## 六、边界

- 本 skill 只写工具、命令与排障，不写内容规则。bn 两代归档的教训：skill 一写细就变成流程，agent 开始替用户做归类、定结构。质量判定权在用户手上。
- 群发是对外动作，默认只到草稿箱；未经用户明确授权不调用群发接口。
- 凭证、token 不进任何文档；文档里写「见环境变量 X」或「见 `~/.wechat_pub_key`」。

## 输出要求

- 回报时给出：发布稿路径、排版产物路径、草稿 media_id、发布记录路径。
- 每个卡点写进发布记录的排障段，同一错误不重复排查两遍。
- 链路出现新的稳定经验（新错误码、工具变化），更新本 skill 而不是只记在单篇发布记录里。
