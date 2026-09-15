# bn skill 族群归档（2026-09-14）

## 为什么归档

bn 族群要重建。新的一套从 workflow 骨架起步，用「黄金」这个主题一步步跑，跑通一段写一段。这里的旧版只作参考，不再维护、不再被调用。

重建期结束后，确认无用的部分再删；有用的机制（如草稿接口配置、manifest 约定）会搬进新版，不在这里改。

## 归档内容

| 目录 | 原职责 |
|---|---|
| `bn-0000-think-flow` | 思考：追问本质 |
| `bn-0100-shape-flow` | 梳理：读厚→读薄 |
| `bn-0200-express-flow` | 表达：分享人视角成稿（含 `references/表达红线.md`） |
| `bn-0301-review-flow` | 收敛：反馈归层 |
| `bn-0302-publish-flow` | 发布（含 `references/公众号草稿发布-本地配置.md`） |
| `bn-0303-retro-flow` | 复盘 |
| `bn-tools-content-context` | 目录/槽位/状态约定（机制层） |
| `bn-tools-knowledge-base` | 知识库条目整理（机制层） |

两个 tools skill 是机制不是 workflow。重建期暂时从 `skills/` 移除了，需要时从这里整份拷回去。注意 `manifest模板.yaml`、目录前缀与槽位约定、`gen_index.py` 都依赖 `bn-tools-content-context`。

## 注意

- 本目录不在 `.agents/skills/` 下，不受 `make check` 的命名与链接校验约束。
- 归档内的旧 skill 名与新版重名，别直接拷回去覆盖。
