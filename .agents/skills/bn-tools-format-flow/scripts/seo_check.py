#!/usr/bin/env python3
"""本地文章检查：标题、关键词、排版与词表提示。评分是启发式提示，不代表平台审核结论。"""

import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_SKILL_DIR = os.path.dirname(_HERE)
_SENSITIVE_PATH = os.path.join(_SKILL_DIR, "references", "sensitive-words.json")

# ============================================================
# 评分标准（SEO 自有常量，单一来源，不重复定义 formatter 配置）
# ============================================================

TITLE_DIMS = {
    "关键词精准度": 25,
    "标题长度": 15,
    "情绪触发": 20,
    "搜索意图匹配": 20,
    "点击吸引力": 20,
}

# 关键词密度区间（%），(下限, 上限, 判定, 建议)
DENSITY_BANDS = [
    (0.0, 1.0, "关键词不足", "增加自然出现次数"),
    (1.0, 2.0, "偏低", "适当增加"),
    (2.0, 5.0, "最佳", "保持"),
    (5.0, 8.0, "偏高", "适当减少，避免堆砌"),
    (8.0, 100.0, "关键词堆砌", "立即减少，有惩罚风险"),
]

# 排版检查各项满分（合计 100）
LAYOUT_ITEMS = [
    ("正文字号", 10, "15-16px"),
    ("正文字色", 5, "#333 或 #3f3f3f"),
    ("行间距", 10, "1.6-1.8 倍"),
    ("段间距", 10, "15-20px"),
    ("对齐", 5, "左对齐为主"),
    ("小标题层级", 10, "使用 H2/H3 且含关键词"),
    ("重点标注", 10, "加粗不超过正文 20%"),
    ("首尾结构", 15, "首段导语 + 尾段总结 + CTA"),
    ("配图密度", 15, "每 300-500 字配 1 张图"),
]


# ============================================================
# 工具
# ============================================================

def _blocks_text(blocks):
    """把 blocks 拼回纯文本，用于密度统计（忽略图片/代码/分隔线）。"""
    parts = []
    for b in blocks:
        t = b.get("type")
        if t in ("paragraph", "quote") or t in ("heading_1", "heading_2", "heading_3"):
            parts.append(b.get("content", ""))
        elif t in ("unordered_list", "ordered_list"):
            parts.extend(b.get("items", []))
    return "\n".join(parts)


def _to_int(px, default):
    m = re.sub(r"\D", "", str(px))
    return int(m) if m else default


def _to_float(val, default):
    m = re.sub(r"[^0-9.]", "", str(val))
    try:
        return float(m) if m else default
    except ValueError:
        return default


# ============================================================
# 1. 标题诊断（满分 100）
# ============================================================

def diagnose_title(title, keyword=None):
    title = title or ""
    dims = dict(TITLE_DIMS)
    length = len(title)

    # 标题长度（24-28 字为佳，前 22 字最关键）
    if 24 <= length <= 28:
        len_score = dims["标题长度"]
    elif 20 <= length < 24 or 28 < length <= 32:
        len_score = round(dims["标题长度"] * 0.7)
    else:
        len_score = round(dims["标题长度"] * 0.4)

    # 关键词精准度
    if keyword:
        if keyword in title:
            kw_score = dims["关键词精准度"]
            if title.find(keyword) > 22:
                kw_score = round(dims["关键词精准度"] * 0.8)  # 未前置
        else:
            kw_score = round(dims["关键词精准度"] * 0.3)
    else:
        kw_score = round(dims["关键词精准度"] * 0.6)

    # 情绪触发：数字 / 悬念 / 对比冲突 / 痛点
    emotion = 0
    if re.search(r"\d", title):
        emotion += 1
    if re.search(r"[？?]", title):
        emotion += 1
    if re.search(r"[：:]|——|vs|VS|对比|区别|揭秘|为什么|为何|如何", title):
        emotion += 1
    if re.search(r"避免|警惕|别|千万别|必看|指南|方法|秘籍|干货|一文", title):
        emotion += 1
    emotion_score = min(dims["情绪触发"], round(dims["情绪触发"] * (emotion / 3)))

    # 搜索意图匹配：关键词命中即视为意图高度匹配，按维度满分计
    intent_score = dims["搜索意图匹配"] if keyword else round(dims["搜索意图匹配"] * 0.6)

    # 点击吸引力：数字 / 稀缺利益 / 悬念
    attract = 0
    if re.search(r"\d", title):
        attract += 1
    if re.search(r"独家|首发|干货|免费|限时|必看|一文|彻底|终于|秘籍", title):
        attract += 1
    if re.search(r"[？?]", title):
        attract += 1
    attract_score = min(dims["点击吸引力"], round(dims["点击吸引力"] * (attract / 3)))

    total = kw_score + len_score + emotion_score + intent_score + attract_score

    suggestions = []
    if not (24 <= length <= 28):
        suggestions.append(f"标题 {length} 字，建议 24-28 字（前 22 字最关键）")
    if keyword and keyword not in title:
        suggestions.append(f"标题未含核心关键词「{keyword}」，建议前置到前 22 字")
    if emotion == 0:
        suggestions.append("标题缺情绪触发（数字/悬念/痛点/对比），点击率偏低")
    if attract == 0:
        suggestions.append("标题缺差异化或利益承诺，吸引力弱")

    return {
        "total": total,
        "title_length": length,
        "keyword": keyword,
        "dimensions": {
            "关键词精准度": kw_score,
            "标题长度": len_score,
            "情绪触发": emotion_score,
            "搜索意图匹配": intent_score,
            "点击吸引力": attract_score,
        },
        "suggestions": suggestions,
    }


# ============================================================
# 2. 正文优化（关键词布局 + 密度）
# ============================================================

def analyze_content(blocks, title, keyword):
    full = _blocks_text(blocks)
    total_chars = len(re.sub(r"\s", "", full))

    lead = ""
    for b in blocks:
        if b["type"] == "paragraph":
            lead = re.sub(r"\s", "", b["content"])[:100]
            break
    tail = ""
    for b in reversed(blocks):
        if b["type"] == "paragraph":
            tail = re.sub(r"\s", "", b["content"])[-100:]
            break
    htext = " ".join(b["content"] for b in blocks if b["type"] in ("heading_2", "heading_3"))

    report = {
        "keyword": keyword,
        "total_chars": total_chars,
        "density": 0.0,
        "keyword_count": 0,
        "band": "",
        "band_advice": "",
        "checks": {},
    }

    if keyword:
        count = full.count(keyword)
        density = round(count / total_chars * 100, 2) if total_chars else 0.0
        report["density"] = density
        report["keyword_count"] = count
        for lo, hi, name, advice in DENSITY_BANDS:
            if lo <= density < hi:
                report["band"] = name
                report["band_advice"] = advice
                break
        report["checks"] = {
            "标题含关键词": keyword in (title or ""),
            "首段含关键词": keyword in lead,
            "小标题含关键词": keyword in htext,
            "尾段含关键词": keyword in tail,
        }

    images = [b for b in blocks if b["type"] == "image"]
    report["image_count"] = len(images)
    if keyword:
        report["images_missing_alt_keyword"] = [
            b.get("alt", "") for b in images if keyword not in (b.get("alt", "") or "")
        ]
    else:
        report["images_missing_alt_keyword"] = []

    report["word_count"] = total_chars
    return report


# ============================================================
# 3. 排版检查（满分 100，对照当前模板 config + 实际结构）
# ============================================================

def check_layout(config, blocks):
    config = config or {}
    f = config.get("font", {})
    s = config.get("spacing", {})

    body_size = _to_int(f.get("body_size", "15px"), 15)
    body_color = (f.get("body_color", "#333333") or "").lower()
    line_height = _to_float(f.get("line_height", "1.9"), 1.9)
    para_margin = _to_int(s.get("paragraph_margin", "16px"), 16)

    # 加粗占比
    total_chars = 0
    bold_chars = 0
    for b in blocks:
        c = b.get("content", "") or " ".join(b.get("items", []))
        total_chars += len(c)
        for m in re.findall(r"\*\*(.+?)\*\*", c):
            bold_chars += len(m)
    bold_ratio = (bold_chars / total_chars) if total_chars else 0.0

    # 配图密度
    img_count = len([b for b in blocks if b["type"] == "image"])
    body_char_count = len(re.sub(r"\s", "", _blocks_text(blocks)))
    per_img = (body_char_count / img_count) if img_count else 0

    h2h3 = [b for b in blocks if b["type"] in ("heading_2", "heading_3")]
    has_lead = any(b["type"] == "paragraph" for b in blocks[:3])
    has_tail = any(b["type"] == "paragraph" for b in blocks[-3:])

    items = []

    def judge(name, full_score, ok, partial, value):
        if ok:
            items.append((name, "达标", full_score, value))
            return full_score
        if partial:
            half = round(full_score * 0.7)
            items.append((name, "注意", half, value))
            return half
        items.append((name, "偏离", 0, value))
        return 0

    score = 0
    score += judge("正文字号", 10, 15 <= body_size <= 16,
                   body_size in (14, 17), f"{body_size}px（标准15-16px）")
    score += judge("正文字色", 5, body_color in ("#333333", "#3f3f3f", "#333", "#3f3f3f"),
                   False, body_color or "未设置")
    score += judge("行间距", 10, 1.6 <= line_height <= 1.8,
                   line_height > 1.8, f"{line_height}（标准1.6-1.8）")
    score += judge("段间距", 10, 15 <= para_margin <= 20,
                   para_margin in (12, 21, 22), f"{para_margin}px（标准15-20px）")
    # 对齐默认左对齐，固定达标
    items.append(("对齐", "达标", 5, "左对齐为主"))
    score += 5
    score += judge("小标题层级", 10, len(h2h3) > 0, False,
                   f"{len(h2h3)} 个 H2/H3" if h2h3 else "未使用 H2/H3")
    score += judge("重点标注", 10, bold_ratio <= 0.2, False,
                   f"加粗占比 {round(bold_ratio*100)}%（标准≤20%）")
    score += judge("首尾结构", 15, has_lead and has_tail, has_lead or has_tail,
                   "导语段+总结段齐全" if (has_lead and has_tail) else "首尾不完整")
    # 配图密度：无图不扣分（可能用户未配图），只在有图时评估
    if img_count == 0:
        items.append(("配图密度", "跳过", 15, "全文无图（若需配图见 6.1）"))
        score += 15
    else:
        score += judge("配图密度", 15, 300 <= per_img <= 500, 200 <= per_img < 600,
                       f"每 {round(per_img)} 字 1 图（标准300-500）")

    return {"score": score, "max_score": 100, "items": items}


# ============================================================
# 4. 词表提示（分级敏感词）
# ============================================================

def load_sensitive_words():
    try:
        with open(_SENSITIVE_PATH, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {"auto_scan": [], "manual_review": []}


def scan_sensitive_words(text):
    text = text or ""
    data = load_sensitive_words()
    hits = []
    for grp in data.get("auto_scan", []):
        words = grp.get("words", [])
        found = [w for w in words if w and w in text]
        if found:
            hits.append({
                "level": grp.get("level"),
                "category": grp.get("category"),
                "penalty": grp.get("penalty"),
                "words": found,
            })
    manual = [
        {"level": m.get("level"), "category": m.get("category"),
         "penalty": m.get("penalty"), "note": m.get("note")}
        for m in data.get("manual_review", [])
    ]
    has_high = any(h["level"] in ("极高风险", "高风险") for h in hits)
    return {"hits": hits, "manual_review": manual, "has_high_risk": has_high,
            "clean": len(hits) == 0}


# ============================================================
# 5. 编排入口（纯函数，不依赖 formatter）
# ============================================================

def run_seo(blocks, title=None, config=None, keyword=None):
    full = _blocks_text(blocks)
    return {
        "title": diagnose_title(title, keyword),
        "content": analyze_content(blocks, title, keyword),
        "layout": check_layout(config, blocks),
        "sensitive": scan_sensitive_words(full + " " + (title or "")),
        "keyword": keyword,
    }


def run_seo_from_markdown(text, keyword=None, template_name="微信绿",
                          custom_config=None, title=None):
    """便捷入口：直接吃 Markdown，内部用 formatter 解析。"""
    sys.path.insert(0, _HERE)
    from formatter import parse_input, WeChatHTMLGenerator
    blocks, t = parse_input(text, title)
    config = WeChatHTMLGenerator(template_name, custom_config).config
    return run_seo(blocks, t, config, keyword)


# ============================================================
# 6. 报告生成（Markdown）
# ============================================================

def generate_report_md(report):
    title_r = report["title"]
    content_r = report["content"]
    layout_r = report["layout"]
    sens_r = report["sensitive"]
    kw = report.get("keyword") or "（未指定）"

    L = []
    L.append("# 微信公众号 SEO 检查报告\n")
    L.append(f"- 核心关键词：`{kw}`")
    L.append(f"- 标题：`{title_r.get('title_length')} 字`｜正文 `{content_r.get('word_count', 0)}` 字")
    L.append("")

    # 一、标题诊断
    L.append("## 一、标题诊断（满分 100）\n")
    L.append(f"**总分：{title_r['total']} / 100**\n")
    L.append("| 维度 | 得分 | 满分 |")
    L.append("|------|------|------|")
    for k, v in title_r["dimensions"].items():
        L.append(f"| {k} | {v} | {TITLE_DIMS[k]} |")
    L.append("")
    if title_r["suggestions"]:
        L.append("**优化建议：**")
        for s in title_r["suggestions"]:
            L.append(f"- {s}")
        L.append("")

    # 二、正文优化
    L.append("## 二、正文优化（关键词布局）\n")
    if kw and kw != "（未指定）":
        L.append(f"- 关键词密度：**{content_r['density']}%**（{content_r['band']}｜{content_r['band_advice']}）")
        L.append(f"- 出现次数：{content_r['keyword_count']} 次｜正文 {content_r['word_count']} 字")
        L.append("")
        L.append("| 布局位置 | 是否命中 |")
        L.append("|----------|----------|")
        for k, v in content_r["checks"].items():
            L.append(f"| {k} | {'✅' if v else '❌'} |")
        L.append("")
        if content_r["images_missing_alt_keyword"]:
            L.append(f"- 图片 ALT 缺关键词：{content_r['images_missing_alt_keyword']}")
            L.append("")
    else:
        L.append("> 未指定核心关键词，跳过关键词密度分析。指定 `-k/--keyword` 可启用。\n")

    # 三、排版检查
    L.append("## 三、排版检查（满分 100）\n")
    L.append(f"**得分：{layout_r['score']} / 100**\n")
    L.append("| 检查项 | 结果 | 得分 | 说明 |")
    L.append("|--------|------|------|------|")
    for name, status, sc, value in layout_r["items"]:
        L.append(f"| {name} | {status} | {sc} | {value} |")
    L.append("")

    # 四、敏感词检测
    L.append("## 四、词表提示\n")
    if sens_r["clean"]:
        L.append("✅ 自动扫描未命中本地提示词。\n")
    else:
        L.append("⚠️ **自动扫描命中以下词：**\n")
        L.append("| 提示等级 | 类别 | 复核说明 | 命中词 |")
        L.append("|----------|------|------|--------|")
        for h in sens_r["hits"]:
            L.append(f"| {h['level']} | {h['category']} | {h['penalty']} | {', '.join(h['words'])} |")
        L.append("")
    L.append("**需人工复核项（脚本不自动判定）：**\n")
    for m in sens_r["manual_review"]:
        L.append(f"- {m['level']} · {m['category']}（{m['penalty']}）：{m['note']}")
    L.append("")

    L.append("## 五、适用边界\n")
    L.append("本报告使用本地启发式规则，不代表微信审核结论、法律判定或搜索排名。")
    L.append("词表命中须结合上下文核查；未命中也不代表已经通过事实审核。")
    return "\n".join(L)


# ============================================================
# 7. 独立 CLI
# ============================================================

def main():
    import argparse
    p = argparse.ArgumentParser(description="文章 SEO 检查（标题/正文/排版/敏感词）")
    p.add_argument("input", help="Markdown 文件路径或文本")
    p.add_argument("-k", "--keyword", help="核心关键词")
    p.add_argument("-t", "--template", default="微信绿", help="模板名（仅用于读取字号等配置）")
    p.add_argument("-c", "--config", help="自定义样式 JSON 路径")
    p.add_argument("--title", help="标题覆盖")
    p.add_argument("-o", "--output", help="报告输出路径（默认打印到终端）")
    args = p.parse_args()

    if os.path.isfile(args.input):
        with open(args.input, "r", encoding="utf-8") as fh:
            text = fh.read()
    else:
        text = args.input

    custom = None
    if args.config:
        with open(args.config, "r", encoding="utf-8") as fh:
            custom = json.load(fh)

    report = run_seo_from_markdown(text, args.keyword, args.template, custom, args.title)
    md = generate_report_md(report)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(md)
        print(f"SEO 报告已写入：{args.output}")
    else:
        print(md)


if __name__ == "__main__":
    main()
