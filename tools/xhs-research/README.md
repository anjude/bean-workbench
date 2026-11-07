# 小红书内容研究工具

这组工具用于从公开笔记中学习内容形式，及保存人工挑选的参考作品。工作台通过 Git 子模块固定上游代码，保留其各自 LICENSE；首次检出后需要初始化子模块：

```sh
git submodule update --init --depth 1 tools/xhs-research/MediaCrawler tools/xhs-research/XHS-Downloader
```

| 项目 | 本地目录 | 许可与用途 |
| --- | --- | --- |
| [MediaCrawler](https://github.com/NanmiCoder/MediaCrawler) | `tools/xhs-research/MediaCrawler/` | 非商业学习使用许可证 1.1；仅少量学习研究，禁止商业用途和大规模采集。 |
| [XHS-Downloader](https://github.com/JoeanAmier/XHS-Downloader) | `tools/xhs-research/XHS-Downloader/` | GPL-3.0；按链接下载人工挑选的公开作品素材。 |

## 使用前

1. 先读子模块内的 README、LICENSE 和安全说明。上游会变化，定期更新前重新检查许可证与功能。
2. MediaCrawler 需要用户自行按上游文档安装依赖、登录并配置少量关键词采集；不要把 Cookie、登录态、凭证、代理配置提交到 Git。
3. XHS-Downloader 需要用户按上游说明启动，手动选择公开笔记链接；下载素材保留来源链接和作者标识，不直接改成自有素材发布。
4. 遇到登录验证、访问限制或频率限制立即停止，不启用代理池、指纹伪装、验证码规避等绕过措施。
5. 输出数据仅用于内容形式学习。MediaCrawler 的研究结果若要直接用于商业营销，先向作者确认是否需要书面授权；原帖内容、图片和评论仍受原作者及平台规则约束。

操作流程与预发布内容边界见 [xhs-tools-content-research](../../.agents/skills/xhs-tools-content-research/SKILL.md)。不在本目录放采集数据；按次保存精选样本到当前内容任务的 `content/`，记录来源链接与采集日期。
