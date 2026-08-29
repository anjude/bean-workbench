#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""工作台结构检查。

跨平台，只依赖 Python 3 标准库，替代原先只给 Windows 用的 check-workbench.ps1。

检查三项：

1. 必需文件是否存在（含 business-repo 子仓的 AGENTS.md）。
2. `.agents/skills/` 下每个 skill 的目录名、`SKILL.md` 的 `name` 字段、编号规范三者是否一致。
3. 工作台自身 md 文档里的相对链接是否指向真实存在的文件。

skill 实体在工作台仓库里，由工作台 git 做版本管理；`~/.agents` 是指向 `.agents` 的外链，
供其他 Agent 工具和其他项目读取同一套 skill。结尾提示外链状态和 skill 未提交改动，不计入失败。
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

REQUIRED_FILES = [
    "AGENTS.md",
    "README.md",
    "docs/workspace.md",
    "docs/self-evolution.md",
    "docs/task-system.md",
    "docs/goals.md",
    "knowledge-base/README.md",
    "knowledge-base/common/README.md",
    "task/registry.md",
    "task/pain-points.md",
    "task/260614_workbench-init/README.md",
    ".agents/skills/wb-0001-router/SKILL.md",
    ".agents/skills/wb-0001-router/references/business-request-loop.md",
    ".agents/skills/wb-0001-router/references/business-generation-checklist.md",
    ".agents/skills/wb-0001-router/references/task-readme.md",
    ".agents/skills/wb-0001-router/references/task-review.md",
    ".agents/skills/wb-0101-skill-refactor/SKILL.md",
    ".agents/skills/wb-0101-skill-refactor/references/workbench-evolution.md",
    "business-repo/backend-superone/AGENTS.md",
    "business-repo/bt/AGENTS.md",
    "business-repo/frontend-investment-platform/AGENTS.md",
    "business-repo/frontend-contracts/AGENTS.md",
    "business-repo/frontend-superone/AGENTS.md",
    "business-repo/miniprogram-superone/AGENTS.md",
    "business-repo/uni-superone/AGENTS.md",
    "business-repo/uni-carbon-space/AGENTS.md",
    "business-repo/utools-bean-note/AGENTS.md",
    "business-repo/utools-bean-option/AGENTS.md",
    "business-repo/utools-superone/AGENTS.md",
]

SKILLS_DIR = ".agents/skills"

# 编号规范：{族群前缀}-{四位编号}-{能力后缀} 或 {族群前缀}-tools-{能力后缀}
SKILL_NAME_RE = re.compile(
    r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*-(?:\d{4}|tools)-[a-z0-9]+(?:-[a-z0-9]+)*$"
)

# 扫描 md 链接时跳过的目录：业务子仓与外部依赖的失效链接不由工作台负责
SCAN_SKIP_DIRS = {".git", "node_modules", "business-repo", "dist", ".workbuddy"}

LINK_RE = re.compile(r"\[[^\]]+\]\(([^)#]+)\)")


def read_frontmatter_name(skill_md: Path):
    """读取 SKILL.md frontmatter 里的 name 字段，取不到返回 None。"""
    try:
        lines = skill_md.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        matched = re.match(r"^name:\s*(.+?)\s*$", line)
        if matched:
            return matched.group(1)
    return None


def check_required_files(root: Path):
    problems = []

    for item in REQUIRED_FILES:
        if not (root / item).exists():
            if item.startswith("business-repo/"):
                problems.append(f"{item}（业务子仓未初始化？执行 git submodule update --init）")
            else:
                problems.append(item)
    return problems


def check_skill_naming(root: Path):
    problems = []
    skills_root = root / SKILLS_DIR
    if not skills_root.is_dir():
        return [f"缺少 skill 目录 {SKILLS_DIR}"]

    for skill_dir in sorted(p for p in skills_root.iterdir() if p.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            problems.append(f"{skill_dir.name}：缺少 SKILL.md")
            continue

        if not SKILL_NAME_RE.match(skill_dir.name):
            problems.append(f"{skill_dir.name}：目录名不符合编号规范")

        declared = read_frontmatter_name(skill_md)
        if declared is None:
            problems.append(f"{skill_dir.name}：SKILL.md frontmatter 里读不到 name 字段")
        elif declared != skill_dir.name:
            problems.append(f"{skill_dir.name}：SKILL.md 的 name 是 {declared}")
    return problems


def iter_markdown(root: Path):
    """遍历 md 文件，跟随目录符号链接。

    Path.rglob 不进入符号链接目录，一旦 `.agents` 或其子目录是链接，
    不跟随的话 skill 文档里的失效链接会全部漏检。用 real path 去重防止循环。
    """
    seen = set()
    stack = [root]

    while stack:
        current = stack.pop()
        real = current.resolve()
        if real in seen:
            continue
        seen.add(real)

        try:
            entries = sorted(current.iterdir())
        except OSError:
            continue

        for entry in entries:
            if entry.is_dir():
                if entry.name in SCAN_SKIP_DIRS:
                    continue
                stack.append(entry)
            elif entry.suffix == ".md":
                yield entry


def check_markdown_links(root: Path):
    problems = []
    for md_path in iter_markdown(root):
        if SCAN_SKIP_DIRS & set(md_path.relative_to(root).parts):
            continue
        try:
            text = md_path.read_text(encoding="utf-8")
        except OSError:
            continue
        rel_md = md_path.relative_to(root)
        for matched in LINK_RE.finditer(text):
            target = matched.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:", "<")):
                continue
            if not (md_path.parent / target.split("#")[0]).resolve().exists():
                problems.append(f"{rel_md} -> {target}")
    return problems


def warn_share_state(root: Path):
    """检查 `~/.agents` 外链状态，以及工作台里 skill 的未提交改动。

    外链断了不影响工作台本身，但其他项目和 Agent 工具就读不到 skill 了；
    skill 由工作台 git 跟踪，改完要跟工作台一起提交，这里提示一下别漏。
    """
    notes = []

    home_link = Path.home() / ".agents"
    expected = (root / ".agents").resolve()

    if not home_link.is_symlink():
        if home_link.exists():
            notes.append(f"~/.agents 是真实目录而非链接，其他项目读到的不是本工作台的 skill（{home_link}）")
        else:
            notes.append(
                f"~/.agents 不存在，其他项目读不到本工作台 skill；"
                f"执行 ln -s {expected} ~/.agents"
            )
    elif home_link.resolve() != expected:
        notes.append(f"~/.agents 指向 {home_link.readlink()}，不是本工作台的 {expected}")

    try:
        status = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--", ".agents"],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return notes

    if status.returncode == 0:
        changed = [line for line in status.stdout.splitlines() if line.strip()]
        if changed:
            notes.append(f"skill 有 {len(changed)} 项未提交改动，会随工作台一起提交（make commit）")
            notes.extend(f"    {line}" for line in changed[:10])
    return notes


def main():
    parser = argparse.ArgumentParser(description="工作台结构检查")
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parent.parent),
        help="工作台根目录，默认是脚本所在目录的上一级",
    )
    parser.add_argument(
        "--skip-links",
        action="store_true",
        help="跳过 md 相对链接检查（历史任务文档较多时可临时关闭）",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"工作台根目录不存在：{root}")
        return 1

    sections = [
        ("必需文件", check_required_files(root)),
        ("skill 命名", check_skill_naming(root)),
    ]
    if not args.skip_links:
        sections.append(("文档链接", check_markdown_links(root)))

    total = 0
    for index, (title, problems) in enumerate(sections, start=1):
        if problems:
            total += len(problems)
            print(f"[{index}/{len(sections)}] {title}：{len(problems)} 项问题")
            for problem in problems:
                print(f"  - {problem}")
        else:
            print(f"[{index}/{len(sections)}] {title}：通过")

    warnings = warn_share_state(root)
    if warnings:
        print("\n提示：skill 共享与版本状态")
        for line in warnings:
            print(f"  - {line}")

    if total:
        print(f"\n工作台结构检查未通过，共 {total} 项问题。")
        return 1

    print("\n工作台结构检查通过。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
