"""平台路由，CLI 和本机网页共用。"""
from urllib.parse import urlparse
from . import bilibili, youtube

ADAPTERS = {"bilibili": bilibili, "youtube": youtube}


def parse_source(value, platform=None):
    if platform is None:
        host = (urlparse(value.strip()).hostname or "").lower()
        platform = "bilibili" if value.strip().lower().startswith("bv") or host.endswith("bilibili.com") else "youtube"
    if platform not in ADAPTERS:
        raise ValueError("暂支持 bilibili 和 youtube")
    content_id, page = ADAPTERS[platform].parse_video_input(value)
    return platform, content_id, page
