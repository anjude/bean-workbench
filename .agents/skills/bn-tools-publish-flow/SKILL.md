---
name: bn-tools-publish-flow
description: 内容排版与发布 skill，覆盖「排版 → 封面 → 草稿箱 → 发布记录」的机械链路。用户要把确认过的发布稿排版成公众号格式、推草稿箱，或发布链路报错排障（40164 / 40007 / 48001）时使用。只管排版与发布的工具操作，不碰内容。
---

# 内容发布链路：排版-发布

用户确认过的发布稿（.md）之后的机械链路：排版 → 封面 → 草稿箱 → 发布记录。内容是用户的领域，本 skill 只把稿子变成公众号草稿箱里的稿件，并把过程记录留全。

产物落在选题目录 `task/beannote/topics/YYYY-MM-DD_主题/` 下。

## 一、排版

1. 切排版输入：从发布稿里抽出「标题 + 正文」另存为 `publish/body.md`。发布稿里的元数据节（选题判断、留言引导、封面 prompt 等）不进入排版。
2. 用 `oa-wechat-formatter`（用户级安装 skill）：

   ```bash
   python formatter.py body.md -t {模板} --seo -k "{关键词}"
   ```

   模板由用户指定或按账号既有模板。产物四份落在 `publish/`：`article.md`、`article_wechat.html`、`preview.html`、`*_seo.md`。
3. SEO 报告解读原则：
   - 搜一搜导向的项（标题长度、关键词密度）与账号风格冲突时不盲从；
   - 敏感词命中逐条人工判读，引文和专有名词常误报；
   - 配图项用来确认封面是否就绪，不因此给正文强塞插图。

## 二、封面

1. 封面来源二选一：发布稿里的封面 prompt，或用户直接提供的图片。
2. 走 prompt 时：ImageGen 生成横版大图，然后本地处理：

   ```bash
   # 居中裁 2.35:1（公众号封面比例），同时切掉右下角 AI 水印
   sips --cropToHeightWidth {高} {宽} 原图.png --out cover_235.png
   # 转 JPEG 控体积
   sips -s format jpeg -s formatOptions 85 cover_235.png --out cover.jpg
   ```

3. 排版 skill 的 `image_enhance.py` 依赖 Pillow，环境没有时用 sips（macOS 内置，零依赖），效果等价。

## 三、发布

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

## 四、排障速查

| 错误码 | 含义 | 处理 |
| --- | --- | --- |
| `40164` | IP 不在白名单 | 以微信报错里显示的 IP 为准加白名单。代理按目标主机粘住出口 IP，别信通用 IP 回显站（不同站点显示的可能不是同一个出口） |
| `40007` | draft/add 缺 thumb_media_id | 上传封面拿到 media_id 再提交 |
| `40013` / `40001` | AppID / 凭证无效 | 核对 AppID，必要时重置 AppSecret |
| `48001` | 无群发权限 | 订阅号 / 未认证号只能到草稿箱，由用户在后台手动群发 |
| `45009` | 接口调用超限 | 等配额恢复，不反复重试 |

## 五、边界

- 本 skill 只对「排版 → 封面 → 草稿箱」的机械链路负责：切输入、跑工具、传封面、写记录、排障。
- 内容怎么写是用户的事：选题、结构、标题、事实、风格、留删，本 skill 不预设规则、不代做判断、不置喙。
- 群发是对外动作，默认只到草稿箱；未经用户明确授权不调用群发接口。
- 凭证、token 不进任何文档；文档里写「见环境变量 X」或「见 `~/.wechat_pub_key`」。

## 输出要求

- 回报链路状态：发布稿路径、排版产物路径、草稿 media_id、发布记录路径。
- 不评价内容好坏，不主动改内容。
- 每个卡点写进发布记录的排障段，同一错误不重复排查两遍。
- 链路出现新的稳定经验（新错误码、工具变化），更新本 skill 而不是只记在单篇发布记录里。
