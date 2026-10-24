# 工作台来源资料包格式 v1

本格式供来源采集器、主题目录和后续导入器交换资料。字幕文本只作材料，不代表逐字核实；机器转写必须标明处理引擎。时间统一使用 ISO 8601 UTC，时间轴以秒为单位。

## 标准目录

```text
<来源目录>/
├── source.json      # 必需：统一来源元数据
├── 字幕.srt          # 有时间轴字幕时提供
└── 正文.txt          # 有字幕时提供的纯文本副本
```

音频、视频、数据库和模型缓存不属于标准来源包，不应随主题资料提交。原始媒体暂存于本机工具数据目录；若未来因核查需要归档，应由用户单独选择。

## source.json

```json
{
  "schema_version": 1,
  "platform": "bilibili",
  "content_id": "BV1yUHP6rEYD",
  "page": 1,
  "url": "https://www.bilibili.com/video/BV1yUHP6rEYD/",
  "title": "视频标题",
  "author": "作者名称",
  "published_at": null,
  "collected_at": "2026-10-24T14:00:00+00:00",
  "duration_seconds": 721,
  "source_kind": "platform_unknown",
  "language": "zh-CN",
  "transcription_engine": null,
  "transcription_model": null,
  "cue_count": 42,
  "coverage_start_seconds": 0,
  "coverage_end_seconds": 720.5,
  "review_required": false
}
```

### 字段

| 字段 | 必需 | 说明 |
| --- | --- | --- |
| `schema_version` | 是 | 本格式版本，当前为 `1` |
| `platform` | 是 | 来源平台标识：`bilibili` 或 `youtube` |
| `content_id`、`page` | 是 | 平台内容 ID 与分 P；去重键为平台 + ID + 分 P |
| `url` | 是 | 规范化原始链接 |
| `title`、`author` | 是 | 采集到的来源元信息 |
| `published_at` | 否 | 平台发布时间，未知时为 `null` |
| `collected_at` | 是 | 采集时间，ISO 8601 UTC |
| `duration_seconds` | 否 | 当前分 P 时长 |
| `source_kind` | 是 | `platform_author`、`platform_ai`、`platform_unknown`、`local_asr` 或 `human_edit` |
| `language` | 否 | 字幕语言标签 |
| `transcription_engine`、`transcription_model` | 否 | 非平台原字幕时记录实际引擎和模型；未知填 `null` |
| `cue_count`、`coverage_start_seconds`、`coverage_end_seconds` | 否 | 字幕条数与时间覆盖范围；覆盖范围不等于内容完整性证明 |
| `review_required` | 是 | 平台自动字幕、机器转写或人工修订未经核实时为 `true` |

未知字段可扩展；导入器应忽略不认识的可选字段。不要把“没有公开字幕”和“字幕需要登录”写成同一来源类型；这是采集任务状态，不是字幕来源类型。

## Chrome 插件现状与兼容

当前 Chrome 插件的 ZIP 使用 `来源.json`，并保留旧版 Job 结构字段；本地 Python 工具输出 `source.json` 并按上述字段记录。Python 采集器的 `import-zip` 命令可读取插件 ZIP 内的 `来源.json`、字幕与纯文本并转换到 v1；重复 BV/分 P 会跳过，导入结果仍需用户显式选择主题后归档。`manifest.csv` 仅作批量清单，不覆盖单条 JSON 的来源字段。


YouTube 的 `content_id` 是 11 位视频 ID，`page` 固定为 1；目录名前缀为 `youtube-`。B 站原目录名和字段保持兼容。平台临时签名地址、Cookie 和 yt-dlp 原始提取结果不进入来源 JSON。
