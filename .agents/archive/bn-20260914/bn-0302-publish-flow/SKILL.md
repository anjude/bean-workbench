---
name: bn-0302-publish-flow
description: |
  beannote 发布 skill。成稿通过收敛后推公众号草稿箱。
  含正文转微信 HTML、封面、草稿接口调用、发布登记与目录改名。只进草稿箱，不群发。
agent_created: true
---

# 发布（03 阶段）

| | |
|---|---|
| 用户在这一步说什么 | "发吧"、"推草稿箱" |
| agent 做什么 | 正文转微信 HTML、封面、调草稿接口、登记发布记录、目录加 `done-` 前缀、更新索引 |
| 产物 | `media_id` + `data/发布记录总表.csv` 一行 + `topics/done-{日期}_{主题}/` |
| 停下等什么 | 推送前显式确认；只进草稿箱，群发必须用户手动操作 |

上游：`bn-0301-review-flow` 说"可以了"的成稿
下游：`bn-0303-retro-flow`（有反馈时）

目录、槽位、状态前缀见 `bn-tools-content-context`。

---

## 草稿接口

能力由 `backend-superone` 提供，不用在后台手贴 HTML。

**前置（一次性）**

- 后端 `configs/config.yaml` 已配好公众号 appid/secret；服务器出网 IP 已加进公众号后台「IP 白名单」（否则微信报 45166）。
- 调用需 JWT：`Authorization: Bearer <token>`。base 地址与 token 写在 `references/公众号草稿发布-本地配置.md`（本地、含密钥、不进 git，需用户自己建）。该文件不存在时向用户索要，不要臆造。

**请求映射（POST `{BASE_URL}/api/so/wechat/article/draft`）**

| 字段 | 来源 | 说明 |
|---|---|---|
| `title` | 必填 | 文章标题 |
| `content` | 正文 HTML | 直接传微信格式 HTML；或传 `content_markdown` 由后端 goldmark 转 |
| `content_markdown` | 正文 MD | 与 `content` 二选一 |
| `author` | 选填 | 作者名 |
| `digest` | 选填 | 摘要，用于转发卡片 |
| `content_source_url` | 选填 | 原文链接 |
| `cover_url` | 封面外链 | 与 `thumb_media_id` 二选一；传外链则后端下载→上传素材 |
| `thumb_media_id` | 封面素材 id | 已有永久素材 id 时直接传 |
| `auto_upload_images` | bool 默认 true | 正文外链 `<img>` 自动转微信图床并回填 URL |
| `need_open_comment` / `only_fans_can_comment` | int 0/1，选填 | 评论开关 |

响应 `{ "media_id": "..." }` 即代表草稿已在公众号后台草稿箱。

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

此接口**只进草稿箱，不群发**。群发需在公众号后台手动操作（订阅号无群发权限）。

---

## 发布后登记

1. 目录改名：`topics/[YYYY-MM/]{日期}_{主题}/` → `topics/[YYYY-MM/]done-{日期}_{主题}/`，同层改名不搬家
2. 改 `manifest.yaml`：`status` 改「已发布」、`published` 填发布日、`slots` 补全、`next` 改「复盘（如有反馈）」；`status` 必须与目录前缀一致
3. 重跑 `topics/索引.md` 生成脚本（由 manifest 派生），不手改
4. `data/发布记录总表.csv` 补一行：日期、标题、形式、栏目、状态、曝光、点赞、收藏、评论、涨粉、链接、备注

## 参考资源

| 文件 | 用途 |
|---|---|
| `references/公众号草稿发布-本地配置.md` | base 地址与 JWT（本地、含密钥、不进 git，需用户自己建） |
| `bn-tools-content-context` | 目录、状态前缀、索引维护 |
