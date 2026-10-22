#!/usr/bin/env python3
"""
微信公众号文章自动排版核心脚本
输入：Markdown 文本 或 JSON blocks（LLM 预处理输出）
内置 5 套模板 + 自定义 JSON 配置
输出：微信兼容 HTML + 预览页面 + Markdown 原始版本
"""

import json
import re
import os
from html import escape

# ============================================================
# 1. 内置模板定义
# ============================================================

TEMPLATES = {
    "微信绿": {
        "name": "微信绿", "accent_color": "#009874",
        "heading_color": "#009874", "emphasis_color": "#009874",
        "quote_bg": "#effaf4", "card_bg": "#f6fbf8",
        "description": "微信绿主题，绿色点缀与深绿文字，适用于 beannote 公众号默认样式"
    },
    "经典红": {
        "name": "经典红", "accent_color": "#c0392b",
        "heading_color": "#8f2d25", "emphasis_color": "#c0392b",
        "quote_bg": "#fef5f5", "card_bg": "#fafafa",
        "description": "稳重经典，红色强调，适用于通用文章和培训内容（默认）"
    },
    "商务蓝": {
        "name": "商务蓝", "accent_color": "#2c5aa0",
        "heading_color": "#234a7a", "emphasis_color": "#2c5aa0",
        "quote_bg": "#f0f4ff", "card_bg": "#f8f9fa",
        "description": "专业可靠，蓝色基调，适用于商业分析和行业报告"
    },
    "清新绿": {
        "name": "清新绿", "accent_color": "#27ae60",
        "heading_color": "#1e6b42", "emphasis_color": "#218c53",
        "quote_bg": "#f0faf4", "card_bg": "#f8f9fa",
        "description": "自然清新，绿色点缀，适用于学习方法和知识科普"
    },
    "优雅紫": {
        "name": "优雅紫", "accent_color": "#8e44ad",
        "heading_color": "#63327a", "emphasis_color": "#8e44ad",
        "quote_bg": "#f8f0ff", "card_bg": "#f8f9fa",
        "description": "文艺雅致，紫色调性，适用于文化评论和创意内容"
    },
    "温暖橙": {
        "name": "温暖橙", "accent_color": "#e67e22",
        "heading_color": "#9a4c0b", "emphasis_color": "#c96b15",
        "quote_bg": "#fef5ee", "card_bg": "#fafafa",
        "description": "温暖活泼，橙色氛围，适用于职场故事和生活随笔"
    }
}

DEFAULT_TEMPLATE = "微信绿"

DEFAULT_STYLE = {
    "font": {
        "title_size": "24px", "heading_size": "19px", "subheading_size": "17px",
        "body_size": "15px", "quote_size": "14px", "note_size": "13px",
        "body_color": "#333333", "heading_color": "#1a1a1a",
        "emphasis_color": "#c0392b", "note_color": "#999999",
        "body_weight": "normal", "heading_weight": "bold",
        "line_height": "1.9", "letter_spacing": "1px"
    },
    "spacing": {
        "paragraph_margin": "16px", "padding_left_right": "1px",
        "section_margin_top": "24px", "image_margin": "24px",
        "heading_bottom_margin": "8px", "list_item_margin": "8px"
    },
    "image": {"border_radius": "8px", "border": "none", "alignment": "center"},
    "card": {"border_radius": "8px", "border_width": "2px", "use_shadow": False},
    "title_style": "default",
    "heading_numbering": False
}


# ============================================================
# 2. Markdown 解析器
# ============================================================

class MarkdownParser:
    """Markdown 解析器：只处理标准 Markdown，输出统一 blocks 结构"""

    @staticmethod
    def extract_title(text):
        m = re.search(r'^#\s+(.+?)(?:\n|$)', text, re.MULTILINE)
        return m.group(1).strip() if m else None

    @staticmethod
    def parse(text):
        """Markdown → blocks list"""
        blocks = []
        lines = text.split('\n')
        i = 0
        in_code = False
        code_buf = []
        para_buf = []
        list_type = None
        list_buf = []

        def flush_para():
            nonlocal para_buf
            if para_buf:
                blocks.append({"type": "paragraph", "content": '\n'.join(para_buf)})
                para_buf = []

        def flush_list():
            nonlocal list_buf, list_type
            if list_buf and list_type:
                blocks.append({"type": f"{list_type}_list", "items": list_buf.copy()})
                list_buf = []
                list_type = None

        while i < len(lines):
            line = lines[i]

            if line.startswith('```'):
                if in_code:
                    blocks.append({"type": "code", "content": '\n'.join(code_buf)})
                    code_buf = []
                    in_code = False
                else:
                    in_code = True
                    code_buf = []
                i += 1
                continue
            if in_code:
                code_buf.append(line)
                i += 1
                continue

            s = line.strip()
            if not s:
                flush_para()
                flush_list()
                i += 1
                continue

            hm = re.match(r'^(#{1,6})\s+(.+)$', line)
            if hm:
                flush_para()
                flush_list()
                blocks.append({"type": f"heading_{len(hm.group(1))}", "content": hm.group(2).strip()})
                i += 1
                continue

            qm = re.match(r'^>\s*(.*)$', line)
            if qm:
                flush_para()
                flush_list()
                q_lines = [qm.group(1)]
                i += 1
                while i < len(lines):
                    n = re.match(r'^>\s*(.*)$', lines[i])
                    if n:
                        q_lines.append(n.group(1))
                        i += 1
                    else:
                        break
                blocks.append({"type": "quote", "content": '\n'.join(q_lines)})
                continue

            um = re.match(r'^[-*]\s+(.+)$', line)
            if um:
                flush_para()
                if list_type != "unordered":
                    flush_list()
                    list_type = "unordered"
                list_buf.append(um.group(1))
                i += 1
                continue

            om = re.match(r'^(\d+)\.\s+(.+)$', line)
            if om:
                flush_para()
                if list_type != "ordered":
                    flush_list()
                    list_type = "ordered"
                list_buf.append(om.group(2))
                i += 1
                continue

            if re.match(r'^(-{3,}|\*{3,}|_{3,})\s*$', line):
                flush_para()
                flush_list()
                blocks.append({"type": "divider"})
                i += 1
                continue

            im = re.search(r'!\[([^\]]*)\]\(([^)]+)\)', line)
            if im and line.strip().startswith('!['):
                flush_para()
                flush_list()
                blocks.append({"type": "image", "alt": im.group(1) or "插图", "src": im.group(2)})
                i += 1
                continue

            # 表格检测（GFM: | a | b | 后跟 |---|---| 分隔行）
            if s.startswith('|') and s.count('|') >= 2:
                nxt = lines[i + 1].strip() if i + 1 < len(lines) else ''
                if '-' in nxt and '|' in nxt and re.match(r'^[|\s:\-]+$', nxt):
                    header_cells = [c.strip() for c in s.strip().strip('|').split('|')]
                    i += 2  # 跳过表头行和分隔行
                    rows = []
                    while i < len(lines):
                        tl = lines[i].strip()
                        if not tl.startswith('|'):
                            break
                        if '-' in tl and re.match(r'^[|\s:\-]+$', tl):
                            i += 1
                            continue
                        rows.append([c.strip() for c in tl.strip().strip('|').split('|')])
                        i += 1
                    blocks.append({"type": "table", "headers": header_cells, "rows": rows})
                    continue

            para_buf.append(line)
            i += 1

        flush_para()
        flush_list()
        if in_code and code_buf:
            blocks.append({"type": "code", "content": '\n'.join(code_buf)})
        return blocks


# ============================================================
# 3. Blocks 校验与标题去重
# ============================================================

def parse_input(text, title=None):
    """统一入口：识别输入类型并解析为 blocks + title"""
    # JSON blocks 直接输入
    if text.strip().startswith('[') and text.strip().endswith(']'):
        try:
            blocks = json.loads(text)
            if isinstance(blocks, list):
                t = title or extract_title_from_blocks(blocks)
                return blocks, t
        except json.JSONDecodeError:
            pass

    # Markdown 输入
    t = title or MarkdownParser.extract_title(text)
    blocks = MarkdownParser.parse(text)

    # 标题去重
    if t and blocks and blocks[0]["type"] in ("heading_1", "heading_2", "heading_3"):
        if blocks[0].get("content") == t:
            blocks = blocks[1:]
    return blocks, t


def extract_title_from_blocks(blocks):
    for b in blocks:
        if b["type"] == "heading_1":
            return b["content"]
    return None


def validate_blocks(blocks):
    """校验 blocks 结构是否合法"""
    valid_types = {"heading_1", "heading_2", "heading_3", "paragraph", "quote",
                   "unordered_list", "ordered_list", "image", "code", "divider"}
    for i, b in enumerate(blocks):
        if not isinstance(b, dict):
            raise ValueError(f"block[{i}] 必须是 dict")
        if b.get("type") not in valid_types:
            raise ValueError(f"block[{i}] type='{b.get('type')}' 不受支持，可选: {valid_types}")
        if b["type"] in ("unordered_list", "ordered_list") and "items" not in b:
            raise ValueError(f"block[{i}] 列表类型缺少 'items' 字段")
        if b["type"] == "image" and "src" not in b:
            raise ValueError(f"block[{i}] 图片类型缺少 'src' 字段")
    return True


# ============================================================
# 4. HTML 生成器
# ============================================================

class WeChatHTMLGenerator:
    """微信兼容 HTML 生成器"""

    def __init__(self, template_name=DEFAULT_TEMPLATE, custom_config=None):
        self.template = dict(TEMPLATES.get(template_name, TEMPLATES[DEFAULT_TEMPLATE]))
        for key in ("accent_color", "heading_color", "emphasis_color", "quote_bg", "card_bg"):
            if custom_config and key in custom_config:
                self.template[key] = custom_config[key]
        self.config = self._merge_config(custom_config)
        custom_font = (custom_config or {}).get("font", {})
        for key in ("heading_color", "emphasis_color"):
            if key not in custom_font:
                self.config["font"][key] = self.template[key]

    def _merge_config(self, custom):
        config = json.loads(json.dumps(DEFAULT_STYLE))
        if not custom:
            return config
        for key in ("font", "spacing", "image", "card"):
            if key in custom:
                config[key].update(custom[key])
        if "title_style" in custom:
            config["title_style"] = custom["title_style"]
        if "heading_numbering" in custom:
            config["heading_numbering"] = custom["heading_numbering"]
        return config

    def _inline_text(self, text):
        text = escape(text, quote=False)
        emphasis_color = self.config["font"]["emphasis_color"]
        text = re.sub(r'\*\*(.+?)\*\*', rf'<strong style="color:{emphasis_color};font-weight:bold;">\1</strong>', text)
        text = re.sub(r'__(.+?)__', rf'<strong style="color:{emphasis_color};font-weight:bold;">\1</strong>', text)
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
        text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'<em>\1</em>', text)
        text = re.sub(r'`(.+?)`', r'<code style="background:#f5f5f5;padding:2px 6px;border-radius:3px;font-size:14px;color:#c0392b;">\1</code>', text)
        text = re.sub(r'\[(.+?)\]\((.+?)\)', rf'<span style="color:{self.template["accent_color"]};text-decoration:underline;">\1</span>', text)
        return text

    def _cn_num(self, index):
        nums = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"]
        return nums[index - 1] if 1 <= index <= 10 else str(index)

    def generate_block(self, block, hi):
        f, s, t, tag = self.config["font"], self.config["spacing"], self.template, "section"
        bt = block["type"]

        if bt == "heading_1":
            return (
                f'<{tag} style="padding:{s["section_margin_top"]} {s["padding_left_right"]} 0 {s["padding_left_right"]};">\n'
                f'  <h1 style="font-size:{f["title_size"]};font-weight:{f["heading_weight"]};color:{f["heading_color"]};line-height:1.5;margin:0 0 {s["heading_bottom_margin"]} 0;letter-spacing:{f["letter_spacing"]};">{self._inline_text(block["content"])}</h1>\n'
                f'  <section style="width:40px;height:3px;background:{t["accent_color"]};border-radius:2px;margin-bottom:20px;"></section>\n'
                f'</{tag}>'
            )

        if bt == "heading_2":
            num = ""
            if self.config["heading_numbering"]:
                n = self._cn_num(hi)
                num = f'<span style="display:inline-block;width:28px;height:28px;background:{t["accent_color"]};color:#fff;font-size:14px;font-weight:bold;border-radius:50%;text-align:center;line-height:28px;margin-right:10px;vertical-align:middle;">{n}</span>'
            return (
                f'<{tag} style="padding:{s["section_margin_top"]} {s["padding_left_right"]} 0 {s["padding_left_right"]};">\n'
                f'  <h2 style="margin:0 0 {s["heading_bottom_margin"]} 0;">\n'
                f'    {num}'
                f'    <span style="font-size:{f["heading_size"]};font-weight:{f["heading_weight"]};color:{f["heading_color"]};vertical-align:middle;">{self._inline_text(block["content"])}</span>\n'
                f'  </h2>\n'
                f'</{tag}>'
            )

        if bt == "heading_3":
            return (
                f'<{tag} style="padding:{s["section_margin_top"]} {s["padding_left_right"]} 0 {s["padding_left_right"]};">\n'
                f'  <h3 style="font-size:{f["subheading_size"]};font-weight:{f["heading_weight"]};color:{f["heading_color"]};line-height:1.7;margin:0 0 {s["heading_bottom_margin"]} 0;">{self._inline_text(block["content"])}</h3>\n'
                f'</{tag}>'
            )

        if bt == "paragraph":
            return (
                f'<{tag} style="padding:0 {s["padding_left_right"]} 0 {s["padding_left_right"]};">\n'
                f'  <p style="font-size:{f["body_size"]};color:{f["body_color"]};line-height:{f["line_height"]};margin:0 0 {s["paragraph_margin"]} 0;letter-spacing:{f["letter_spacing"]};">{self._inline_text(block["content"])}</p>\n'
                f'</{tag}>'
            )

        if bt == "quote":
            return (
                f'<{tag} style="padding:0 {s["padding_left_right"]} 0 {s["padding_left_right"]};">\n'
                f'  <blockquote style="background:{t["quote_bg"]};border-left:4px solid {t["accent_color"]};border-radius:0 8px 8px 0;padding:16px 20px;margin:0 0 {s["paragraph_margin"]} 0;">\n'
                f'    <p style="font-size:{f["quote_size"]};color:#666;line-height:{f["line_height"]};margin:0;letter-spacing:{f["letter_spacing"]};">{self._inline_text(block["content"])}</p>\n'
                f'  </blockquote>\n'
                f'</{tag}>'
            )

        if bt in ("unordered_list", "ordered_list"):
            tag_l = "ul" if bt == "unordered_list" else "ol"
            items_html = '\n'.join(
                f'    <li style="font-size:{f["body_size"]};color:{f["body_color"]};line-height:{f["line_height"]};margin:0 0 {s["list_item_margin"]} 0;">{self._inline_text(item)}</li>'
                for item in block["items"]
            )
            return (
                f'<{tag} style="padding:0 {s["padding_left_right"]} 0 {s["padding_left_right"]};">\n'
                f'  <{tag_l} style="padding:0 0 0 24px;margin:0 0 {s["paragraph_margin"]} 0;">\n'
                f'{items_html}\n'
                f'  </{tag_l}>\n'
                f'</{tag}>'
            )

        if bt == "image":
            return (
                f'<{tag} style="padding:0 {s["padding_left_right"]} 0 {s["padding_left_right"]};">\n'
                f'  <section style="text-align:center;margin:{s["image_margin"]} 0;">\n'
                f'    <img src="{escape(block["src"], quote=True)}" alt="{escape(block["alt"], quote=True)}" style="max-width:100%;height:auto;border-radius:{self.config["image"]["border_radius"]};display:block;margin:0 auto;border:{self.config["image"]["border"]};">\n'
                f'  </section>\n'
                f'</{tag}>'
            )

        if bt == "code":
            return (
                f'<{tag} style="padding:0 {s["padding_left_right"]} 0 {s["padding_left_right"]};">\n'
                f'  <pre style="background:#f5f5f5;border-left:4px solid {t["accent_color"]};border-radius:0 8px 8px 0;padding:16px 20px;margin:0 0 {s["paragraph_margin"]} 0;overflow-x:auto;">\n'
                f'    <code style="font-size:13px;color:#555;line-height:1.6;font-family:monospace;white-space:pre-wrap;">{escape(block["content"])}</code>\n'
                f'  </pre>\n'
                f'</{tag}>'
            )

        if bt == "divider":
            return (
                f'<{tag} style="padding:0 {s["padding_left_right"]} 0 {s["padding_left_right"]};">\n'
                f'  <hr style="border:none;border-top:1px solid #eee;margin:10px 0;">\n'
                f'</{tag}>'
            )

        if bt == "table":
            th_cells = ''.join(
                f'<th style="border:1px solid #e0e0e0;padding:8px 12px;background:{t["card_bg"]};font-weight:bold;color:{f["heading_color"]};font-size:{f["body_size"]};text-align:left;">{self._inline_text(h)}</th>'
                for h in block["headers"]
            )
            tr_rows = []
            for row in block["rows"]:
                tds = ''.join(
                    f'<td style="border:1px solid #e0e0e0;padding:8px 12px;font-size:{f["body_size"]};color:{f["body_color"]};line-height:{f["line_height"]};text-align:left;">{self._inline_text(c)}</td>'
                    for c in row
                )
                tr_rows.append(f'    <tr>{tds}</tr>')
            rows_html = '\n'.join(tr_rows)
            return (
                f'<{tag} style="padding:0 {s["padding_left_right"]} 0 {s["padding_left_right"]};">\n'
                f'  <table style="border-collapse:collapse;width:100%;margin:0 0 {s["paragraph_margin"]} 0;font-family:inherit;">\n'
                f'    <thead><tr>{th_cells}</tr></thead>\n'
                f'    <tbody>\n{rows_html}\n    </tbody>\n'
                f'  </table>\n'
                f'</{tag}>'
            )

        return ""

    def generate(self, blocks, article_title=None, include_title=True):
        f, s, t = self.config["font"], self.config["spacing"], self.template
        hi = 0
        body_parts = []
        for block in blocks:
            if block["type"] == "heading_2":
                hi += 1
            body_parts.append(self.generate_block(block, hi))
        body_html = '\n\n'.join(body_parts)

        title_html = ""
        if article_title and include_title:
            title_html = (
                f'  <section style="padding:30px {s["padding_left_right"]} 10px {s["padding_left_right"]};">\n'
                f'    <h1 style="font-size:{f["title_size"]};font-weight:{f["heading_weight"]};color:{f["heading_color"]};line-height:1.5;margin:0 0 16px 0;text-align:center;letter-spacing:2px;">{escape(article_title)}</h1>\n'
                f'    <section style="width:40px;height:3px;background:{t["accent_color"]};border-radius:2px;margin:0 auto 20px auto;"></section>\n'
                f'  </section>'
            )

        return (
            f'<section style="margin:0 auto;max-width:677px;padding:0;font-family:-apple-system,BlinkMacSystemFont,\'Helvetica Neue\',\'PingFang SC\',\'Microsoft YaHei\',sans-serif;">\n'
            f'{title_html}\n'
            f'{body_html}\n'
            f'</section>'
        )

    def generate_preview_page(self, blocks, article_title, template_name):
        """生成预览 HTML 页面（只嵌当前模板，不含 JS 切换逻辑）"""
        t = self.template
        f = self.config["font"]
        content_html = self.generate(blocks, article_title, include_title=False)
        title_preview = ""
        if article_title:
            title_preview = (
                f'<div class="preview-title" style="padding:30px {self.config["spacing"]["padding_left_right"]} 10px {self.config["spacing"]["padding_left_right"]};">'
                f'<h1 style="font-size:{f["title_size"]};font-weight:{f["heading_weight"]};color:{f["heading_color"]};line-height:1.5;margin:0 0 16px 0;text-align:center;letter-spacing:2px;">{escape(article_title)}</h1>'
                f'<div style="width:40px;height:3px;background:{t["accent_color"]};border-radius:2px;margin:0 auto 20px auto;"></div>'
                f'</div>'
            )
        summary = (
            f'模板：{template_name} | '
            f'强调色：{t["accent_color"]} | '
            f'正文字号：{self.config["font"]["body_size"]} | '
            f'行高：{self.config["font"]["line_height"]}'
        )

        return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>排版预览 - {escape(article_title or "文章")}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif}}
.toolbar{{position:fixed;top:0;left:0;right:0;z-index:100;background:#fff;border-bottom:1px solid #e0e0e0;padding:12px 24px;display:flex;align-items:center;gap:16px;box-shadow:0 2px 8px rgba(0,0,0,0.08)}}
.toolbar button{{padding:8px 24px;font-size:14px;font-weight:600;border:none;border-radius:6px;cursor:pointer;background:#07c160;color:#fff}}
.toolbar button:hover{{background:#06ad56}}
.toolbar .info{{font-size:12px;color:#999;margin-left:auto}}
.note{{font-size:12px;color:#aaa}}
.preview-container{{max-width:720px;margin:80px auto 40px;background:#fff;border-radius:12px;box-shadow:0 1px 6px rgba(0,0,0,0.1);overflow:hidden}}
.preview-header{{background:#fafafa;padding:16px 24px;font-size:13px;color:#888;border-bottom:1px solid #f0f0f0}}
.copy-toast{{position:fixed;bottom:40px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,0.8);color:#fff;padding:12px 24px;border-radius:8px;font-size:14px;opacity:0;transition:opacity 0.3s;z-index:200}}
.copy-toast.show{{opacity:1}}
@media(max-width:600px){{.toolbar{{flex-wrap:wrap;padding:10px 12px;gap:8px}}.preview-container{{margin:100px 8px 20px}}}}
</style>
</head>
<body>
<div class="toolbar">
  <span style="font-size:14px;font-weight:600;color:#333;">预览</span>
  <button id="copyBtn" onclick="copyToWeChat()">复制正文到微信编辑器</button>
  <span class="note">仅复制正文；到公众号编辑器正文区域粘贴</span>
  <span class="info">{summary}</span>
</div>
<div class="preview-container">
  <div class="preview-header">微信公众号排版预览</div>
  {title_preview}
  <div id="article-content" style="background:#fff;">{content_html}</div>
</div>
<div class="copy-toast" id="toast">正文已复制！请到公众号编辑器正文区域粘贴</div>
<script>
function copyToWeChat(){{
  var el=document.getElementById('article-content');
  var r=document.createRange();r.selectNodeContents(el);
  var s=window.getSelection();s.removeAllRanges();s.addRange(r);
  var ok=false;
  try{{ok=document.execCommand('copy')}}catch(e){{}}
  s.removeAllRanges();
  var btn=document.getElementById('copyBtn');
  var t=document.getElementById('toast');
  if(ok){{btn.textContent='已复制';btn.style.background='#95ec69';t.classList.add('show');setTimeout(function(){{t.classList.remove('show');btn.textContent='复制正文到微信编辑器';btn.style.background='#07c160'}},3000)}}
  else{{t.textContent='复制失败，请手动 Ctrl+C';t.classList.add('show');setTimeout(function(){{t.classList.remove('show')}},3000)}}
}}
</script>
</body>
</html>'''


# ============================================================
# 5. 主流程函数
# ============================================================

def format_article(input_text, template_name=DEFAULT_TEMPLATE, custom_config=None, output_dir=None, title=None):
    """
    主流程：解析 → 排版 → 输出

    input_text: Markdown 文本 或 JSON blocks 字符串
    title: 可选标题元数据（不写入微信正文 HTML）
    """
    if output_dir is None:
        output_dir = os.getcwd()

    blocks, article_title = parse_input(input_text, title)

    generator = WeChatHTMLGenerator(template_name, custom_config)
    # 微信草稿接口单独接收 title，content HTML 只放正文。
    wechat_html = generator.generate(blocks, article_title, include_title=False)
    preview_html = generator.generate_preview_page(blocks, article_title, template_name)

    # Markdown 版本（保留内容副本）
    md_lines = []
    if article_title:
        md_lines.append(f"# {article_title}\n")
    for b in blocks:
        bt = b["type"]
        if bt.startswith("heading_"):
            md_lines.append(f"{'#' * int(bt[-1])} {b['content']}\n")
        elif bt == "paragraph":
            md_lines.append(f"{b['content']}\n")
        elif bt == "quote":
            for line in b["content"].split('\n'):
                md_lines.append(f"> {line}")
            md_lines.append("")
        elif bt in ("unordered_list", "ordered_list"):
            for i, item in enumerate(b["items"]):
                p = "- " if bt == "unordered_list" else f"{i+1}. "
                md_lines.append(f"{p}{item}")
            md_lines.append("")
        elif bt == "image":
            md_lines.append(f"![{b.get('alt', '插图')}]({b['src']})\n")
        elif bt == "code":
            md_lines.append(f"```\n{b['content']}\n```\n")
        elif bt == "table":
            md_lines.append("| " + " | ".join(b["headers"]) + " |")
            md_lines.append("| " + " | ".join("---" for _ in b["headers"]) + " |")
            for row in b["rows"]:
                md_lines.append("| " + " | ".join(row) + " |")
            md_lines.append("")
        elif bt == "divider":
            md_lines.append("---\n")

    os.makedirs(output_dir, exist_ok=True)
    prefix = "article"
    md_path = os.path.join(output_dir, f"{prefix}.md")
    wechat_path = os.path.join(output_dir, f"{prefix}_wechat.html")
    preview_path = os.path.join(output_dir, "preview.html")

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines).strip() + '\n')
    with open(wechat_path, 'w', encoding='utf-8') as f:
        f.write(wechat_html)
    with open(preview_path, 'w', encoding='utf-8') as f:
        f.write(preview_html)

    return {
        "article_md": md_path,
        "wechat_html": wechat_path,
        "preview_html": preview_path,
        "title": article_title or "未命名文章",
        "template": template_name,
        "blocks_count": len(blocks),
        "blocks": blocks,
        "config": generator.config
    }


# ============================================================
# 6. CLI 入口
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="微信公众号文章自动排版工具")
    parser.add_argument("input", help="Markdown 文件路径或文本")
    parser.add_argument("-t", "--template", default=DEFAULT_TEMPLATE,
                        choices=list(TEMPLATES.keys()),
                        help=f"样式模板名称（默认：{DEFAULT_TEMPLATE}）")
    parser.add_argument("-c", "--config", help="自定义样式配置文件路径（JSON）")
    parser.add_argument("-o", "--output-dir", help="输出目录（默认：当前目录）")
    parser.add_argument("--list-templates", action="store_true", help="列出可用模板")
    parser.add_argument("--blocks", help="JSON blocks 文件路径（直接跳过解析）")
    parser.add_argument("--title", help="文章标题元数据；不写入微信正文 HTML")
    parser.add_argument("--seo", action="store_true",
                        help="排版完成后追加 SEO 检查（标题诊断/正文密度/排版合规/敏感词），生成 *_seo.md 报告")
    parser.add_argument("-k", "--keyword", help="核心关键词（配合 --seo 启用关键词密度与布局分析）")

    args = parser.parse_args()

    if args.list_templates:
        print("可用模板：")
        for name, info in TEMPLATES.items():
            print(f"  {name}: {info['description']}")
        return

    input_text = ""
    if args.blocks:
        with open(args.blocks, 'r', encoding='utf-8') as f:
            input_text = f.read()
    elif os.path.isfile(args.input):
        with open(args.input, 'r', encoding='utf-8') as f:
            input_text = f.read()
    else:
        input_text = args.input

    custom_config = None
    if args.config:
        with open(args.config, 'r', encoding='utf-8') as f:
            custom_config = json.load(f)

    result = format_article(
        input_text=input_text,
        template_name=args.template,
        custom_config=custom_config,
        output_dir=args.output_dir,
        title=args.title
    )

    print(f"排版完成！")
    print(f"  标题：{result['title']}")
    print(f"  模板：{result['template']}")
    print(f"  内容块数：{result['blocks_count']}")
    print(f"  Markdown版本：{result['article_md']}")
    print(f"  微信HTML：{result['wechat_html']}")
    print(f"  预览页面：{result['preview_html']}")

    if args.seo:
        import seo_check
        report = seo_check.run_seo(
            blocks=result["blocks"],
            title=result["title"],
            config=result["config"],
            keyword=args.keyword
        )
        report_md = seo_check.generate_report_md(report)
        seo_path = result["wechat_html"].replace("_wechat.html", "_seo.md")
        with open(seo_path, "w", encoding="utf-8") as f:
            f.write(report_md)
        print(f"  SEO报告：{seo_path}")
        title_score = report["title"]["total"]
        layout_score = report["layout"]["score"]
        sens_clean = report["sensitive"]["clean"]
        print(f"  SEO概览：标题诊断 {title_score}/100 ｜ 排版检查 {layout_score}/100 ｜ "
              f"敏感词 {'通过' if sens_clean else '命中风险'}")


if __name__ == "__main__":
    main()
