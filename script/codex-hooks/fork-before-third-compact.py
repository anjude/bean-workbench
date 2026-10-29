#!/usr/bin/env python3
"""兼容已加载旧钩子路径的会话；实际使用首次压缩前续接规则。"""
from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).with_name("continue-session.py")), run_name="__main__")
