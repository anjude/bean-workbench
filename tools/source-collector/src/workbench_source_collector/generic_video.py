"""通过 yt-dlp 下载其 extractor 支持的公开视频音轨，统一走本地 ASR。"""
import hashlib
import ipaddress
from pathlib import Path
from urllib.parse import urlparse


def _ydl(**options):
    try:
        from yt_dlp import YoutubeDL
    except ImportError as exc:
        raise RuntimeError("通用公开视频下载需要 yt-dlp；请按 tools/source-collector/README.md 安装 YouTube 采集依赖") from exc
    return YoutubeDL({"quiet": True, "no_warnings": True, "noprogress": True,
                      "noplaylist": True, "socket_timeout": 30, "retries": 2,
                      "fragment_retries": 2, "js_runtimes": {"node": {}}, **options})


MAX_DURATION_SECONDS = 2 * 60 * 60
MAX_AUDIO_BYTES = 512 * 1024 * 1024


def parse_video_input(value):
    value = value.strip()
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("通用视频采集需要 http 或 https 视频链接")
    host = parsed.hostname.lower().rstrip(".")
    if host in ("localhost",) or host.endswith((".localhost", ".local")):
        raise ValueError("通用视频下载只接受公开网络域名")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        raise ValueError("通用视频下载只接受公开网络地址")
    return hashlib.sha256(value.encode("utf-8")).hexdigest(), 1


def get_video(content_id, page=1, source_url=None):
    url = source_url or ""
    try:
        with _ydl(skip_download=True, ignore_no_formats_error=True) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as exc:
        raise ValueError("通用下载器无法读取该链接：{}".format(exc)) from exc
    if not info or not info.get("formats"):
        raise ValueError("下载器没有找到可访问的视频或音频流")
    if info.get("is_live") or info.get("live_status") in ("is_live", "is_upcoming", "post_live"):
        raise ValueError("暂不采集直播或直播回放处理中的视频")
    if info.get("availability") in ("private", "premium_only", "subscriber_only", "needs_auth"):
        raise ValueError("视频存在访问限制，当前会话无法采集")
    duration = float(info.get("duration") or 0)
    if duration > MAX_DURATION_SECONDS:
        raise ValueError("视频超过 120 分钟，超出本地转写保护阈值")
    return {"platform": "generic_video", "content_id": content_id, "page": page,
            "title": info.get("title") or content_id[:12],
            "author": info.get("uploader") or info.get("channel") or "",
            "duration_seconds": duration, "url": info.get("webpage_url") or url,
            "_source_url": url}


def get_subtitle(video):
    return None


def download_audio(video, destination, max_bytes=MAX_AUDIO_BYTES):
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".download")

    def limit(progress):
        if progress.get("downloaded_bytes", 0) > max_bytes:
            raise ValueError("音频下载超过 512 MB 上限")

    try:
        with _ydl(format="bestaudio[ext=m4a]/bestaudio", outtmpl=str(temporary),
                  max_filesize=max_bytes, progress_hooks=[limit]) as ydl:
            ydl.extract_info(video["_source_url"], download=True)
        if not temporary.is_file() or not 1024 <= temporary.stat().st_size <= max_bytes:
            raise ValueError("未下载到完整音频文件")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
        Path(str(temporary) + ".part").unlink(missing_ok=True)
    return str(target)
