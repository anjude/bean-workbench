---
name: bn-0301-publish-flow
description: |
  beannote 发布 skill。成稿通过审稿后推公众号草稿箱。
  含正文转微信 HTML、封面、草稿接口调用、发布登记与目录改名。
agent_created: true
---

# 发布（03 阶段）

## 这一步在做什么

| | |
|---|---|
| 用户在这一步说什么 | "发吧"、"推草稿箱" |
| agent 做什么 | 正文转微信 HTML、封面、调草稿接口、登记发布记录、目录加 `done-` 前缀、更新索引 |
| 产物 | `media_id` + `data/发布记录总表.csv` 一行 + `topics/done-{日期}_{主题}/` |
| 停下等什么 | 推送前显式确认；只进草稿箱，群发必须用户手动操作 |

上游交接物：`bn-0201-review-flow` 说"可以发"的成稿
下游指向：`bn-0302-retro-flow`（有反馈时）

通用交互规则（一次最多问 3 个问题、每步结束必须停、先给判断再解释、不辩解）见 `bn-tools-content-context`。

---

成稿通过发布检查后，可直接推到公众号**草稿箱**（非群发，需在公众号后台手动点发布）。能力由 `backend-superone` 的草稿接口提供，不用在后台手贴 HTML。

**前置（一次性）**
- 后端 `configs/config.yaml` 已配好公众号 appid/secret；服务器出网 IP 已加进公众号后台「IP 白名单」（否则微信报 45166）。
- 调用需 JWT：`Authorization: Bearer <token>`。base 地址与 token 写在 `references/公众号草稿发布-本地配置.md`（本地、含密钥、不进 git，需用户自己建）。该文件不存在时，先向用户索要 base 地址与 token，不要臆造。

**请求映射（POST `{BASE_URL}/api/so/wechat/article/draft`）**

| 字段 | 来源 | 说明 |
|---|---|---|
| `title` | 必填 | 文章标题 |
| `content` | 正文 HTML | 直接传微信格式 HTML；或传 `content_markdown` 由后端 goldmark 转 |
| `content_markdown` | 正文 MD | 与 `content` 二选一；后端转 HTML，样式较朴素 |
| `author` | 选填 | 作者名 |
| `digest` | 选填 | 摘要，用于转发卡片 |
| `content_source_url` | 选填 | 原文链接 |
| `cover_url` | 封面外链 | 与 `thumb_media_id` 二选一；传外链则后端下载→上传素材拿 `thumb_media_id` |
| `thumb_media_id` | 封面素材 id | 若已有永久素材 id 直接传 |
| `auto_upload_images` | bool 默认 true | 正文里的外链 `<img>` 自动下载→传微信图床→回填微信 URL |
| `need_open_comment` / `only_fans_can_comment` | int 0/1，选填 | 评论开关 |

响应：`{ "media_id": "草稿 media_id" }`。拿到 media_id 即代表草稿已在公众号后台草稿箱。

**调用（curl 模板，变量取自本地配置）**
```bash
curl -sS -X POST "${BASE_URL}/api/so/wechat/article/draft" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "文章标题",
    "author": "豆小匠",
    "digest": "一句话摘要",
    "content": "<html>...微信格式正文...</html>",
    "cover_url": "https://example.com/cover.jpg",
    "auto_upload_images": true
  }'
```
- 若封面已用 `material/image` 接口提前上传，可改传 `"thumb_media_id": "..."` 替代 `cover_url`。
- 多图文、内容安全预审留了扩展位（结构体已支持数组），暂未启用。

**注意**：此接口只进草稿箱，**不群发**。群发需在公众号后台手动操作（订阅号无群发权限）。

---

## 发布后登记

1. 目录改名：`topics/[YYYY-MM/]{日期}_{主题}/` → `topics/[YYYY-MM/]done-{日期}_{主题}/`，同层改名不搬家，月份目录不动
2. 改 `manifest.yaml`：`status` 改「已发布」、`published` 填发布日、`slots` 补全、`next` 改「复盘（如有反馈）」；`status` 与目录前缀必须一致
3. 重跑 `topics/索引.md` 生成脚本（由 manifest 派生），不手改
4. 在 `data/发布记录总表.csv` 补一行：日期、标题、形式、栏目、状态、曝光、点赞、收藏、评论、涨粉、链接、备注

---

## 参考资源

| 文件 | 用途 |
|---|---|
| `references/公众号草稿发布-本地配置.md` | base 地址与 JWT（本地、含密钥、不进 git，需用户自己建） |
| `bn-tools-content-context` | 目录、状态前缀、索引维护 |
