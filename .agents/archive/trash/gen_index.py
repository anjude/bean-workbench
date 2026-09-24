#!/usr/bin/env python3
"""从各篇 manifest.yaml 重建 topics/索引.md，并校验 status 与目录名前缀一致。

用法：python3 business-repo/beannote/script/gen_index.py
不依赖第三方库，自带极简 YAML 解析，仅覆盖 manifest 用到的字段形态。
"""
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..", "topics")
dirpat = re.compile(r"^(?:(done|drop)-)?(\d{4})-(\d{2})-(\d{2})_(.+)$")


def strip_comment(s):
    """去掉行尾注释，保留引号内的 #。"""
    out, quote = [], None
    for ch in s:
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            out.append(ch)
            continue
        if ch == "#":
            break
        out.append(ch)
    return "".join(out).rstrip()


def unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return "" if v in ("null", "~", "[]") else v


def parse(path):
    data, cur_map, cur_list, pending = {}, None, None, None
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        s = strip_comment(line).strip()
        if not s or s.startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        if s.startswith("- "):
            item = unquote(s[2:])
            if pending is not None:
                data[pending] = cur_list = [item]
                cur_map, pending = None, None
            elif cur_list is not None:
                cur_list.append(item)
            continue
        if ":" not in s:
            continue
        k, _, v = s.partition(":")
        k, v = k.strip(), v.strip()
        if indent == 0:
            cur_map = cur_list = None
            if v.startswith("[") and v.endswith("]"):
                data[k] = [unquote(x) for x in v[1:-1].split(",") if x.strip()]
                pending = None
            elif v == "":
                pending, data[k] = k, None
            else:
                data[k], pending = unquote(v), None
        else:
            if v.startswith("[") and v.endswith("]"):
                val = [unquote(x) for x in v[1:-1].split(",") if x.strip()]
            else:
                val = unquote(v)
            if pending is not None:
                cur_map = {}
                data[pending] = cur_map
                pending = None
            if cur_map is not None:
                cur_map[k] = val
            else:
                data[k] = val
    return data


rows = {"在制": [], "已发布": [], "已归档": []}
warn = []
for month_dir in sorted(os.listdir(ROOT)) + [""]:
    base = ROOT if month_dir == "" else os.path.join(ROOT, month_dir)
    if month_dir and not re.fullmatch(r"\d{4}-\d{2}", month_dir):
        continue
    if not os.path.isdir(base):
        continue
    for name in sorted(os.listdir(base)):
        p = os.path.join(base, name)
        if not os.path.isdir(p) or re.fullmatch(r"\d{4}-\d{2}", name):
            continue
        mf = os.path.join(p, "manifest.yaml")
        if not os.path.exists(mf):
            warn.append(f"{name}: 缺 manifest.yaml")
            continue
        d = parse(mf)
        status = d.get("status") or "在制"
        prefix = "done" if name.startswith("done-") else \
                 "drop" if name.startswith("drop-") else ""
        expect = {"done": "已发布", "drop": "已归档"}.get(prefix, "在制")
        if status != expect:
            warn.append(f"{name}: status={status} 但目录前缀暗示 {expect}")
        m = dirpat.match(name)
        date = m.group(2) + "-" + m.group(3) + "-" + m.group(4) if m else "?"
        rel = f"{month_dir}/{name}/" if month_dir else f"{name}/"
        rows.setdefault(status, []).append((
            date, d.get("topic") or name, d.get("platform") or "",
            " ".join(d.get("slots") or []), d.get("next") or "", rel))

for k in rows:
    rows[k].sort(key=lambda r: (r[0], r[1]))

out = ["# 选题索引", "",
       "状态看板，由各篇 `manifest.yaml` 派生，改 manifest 后重跑生成，不要手改本表。",
       "当前月选题在 `topics/` 根，往月的在 `topics/YYYY-MM/`。", ""]
for k in ["在制", "已发布", "已归档"]:
    out += [f"## {k}（{len(rows[k])}）", "",
            "| 日期 | 主题 | 平台 | 已完成槽位 | 下一步 | 目录 |",
            "|---|---|---|---|---|---|"]
    for date, topic, plat, slots, nxt, rel in rows[k]:
        out.append(f"| {date} | {topic} | {plat} | {slots} | {nxt} | `{rel}` |")
    out.append("")

out += [
    "## 槽位含义", "",
    "| 槽位 | 文件 | 内容 |", "|---|---|---|",
    "| 01 | `01_大纲.md` | 内容层三件事：选题方向 + 事实依据 + 逻辑脉络（含骨架）。不含写法，落笔前生产闸门 |",
    "| 02 | `02_脚本.md` | 读者推进节奏、图文分页结构 |",
    "| 03 | `03_正文.md` | 跨平台纯享长文 |",
    "| 04 | `04_发布稿.md` | 公众号终版 |",
    "| 05 | `05_检查清单.md` | 发布前自检 |",
    "| 06 | `06_复盘.md` | 数据表现、原因分析、规则沉淀 |",
    "",
    "槽位按需生成，不为空流程造文件。缺哪号就是卡在哪步。", "",
    "## 状态与前缀", "",
    "| status | 目录前缀 | 说明 |", "|---|---|---|",
    "| 在制 | 无 | 含只有大纲、还没动笔的 |",
    "| 已发布 | `done-` | 两边必须一致 |",
    "| 已归档 | `drop-` | 废弃或过期，不进数据统计 |",
    "",
    "发布后数据填 `data/发布记录总表.csv`，本表不重复记录。", "",
]
open(os.path.join(ROOT, "索引.md"), "w", encoding="utf-8").write("\n".join(out))
print("索引已重建：", {k: len(v) for k, v in rows.items()})
for w in warn:
    print("!!", w)
