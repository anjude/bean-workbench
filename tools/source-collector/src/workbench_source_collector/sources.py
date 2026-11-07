"""平台路由，CLI 和本机网页共用。"""
import re
from urllib.parse import urlparse
from . import bilibili, generic_video, local_file, xiaohongshu, youtube

ADAPTERS = {"bilibili": bilibili, "youtube": youtube, "generic_video": generic_video,
            "xiaohongshu": xiaohongshu, "local_file": local_file}


def parse_source(value, platform=None):
    if platform is None:
        cleaned = value.strip()
        host = (urlparse(cleaned).hostname or "").lower()
        if cleaned.lower().startswith("bv") or host.endswith("bilibili.com"):
            platform = "bilibili"
        elif re.fullmatch(r"[A-Za-z0-9_-]{11}", cleaned):
            platform = "youtube"
        elif host in ("youtube.com", "www.youtube.com", "youtu.be", "www.youtu.be", "m.youtube.com"):
            platform = "youtube"
        elif host == "xhslink.com" or host.endswith(".xhslink.com") or host == "xiaohongshu.com" or host.endswith(".xiaohongshu.com"):
            platform = "xiaohongshu"
        else:
            platform = "generic_video"
    if platform not in ADAPTERS:
        raise ValueError("支持 B 站、YouTube、小红书、通用视频链接和本地视频文件")
    content_id, page = ADAPTERS[platform].parse_video_input(value)
    return platform, content_id, page
