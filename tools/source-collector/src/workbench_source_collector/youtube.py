"""使用 yt-dlp 读取 YouTube 公开视频、字幕及音频。"""
import json
import math
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse


class YouTubeAccessError(RuntimeError):
    pass


def parse_video_input(value):
    value = value.strip()
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
        return value, 1
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    parts = parsed.path.strip("/").split("/")
    video_id = ""
    if parsed.scheme in ("http", "https"):
        if host in ("youtu.be", "www.youtu.be"):
            video_id = parts[0]
        elif host in ("youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com"):
            if parsed.path == "/watch":
                video_id = parse_qs(parsed.query).get("v", [""])[0]
            elif len(parts) == 2 and parts[0] in ("shorts", "embed", "live"):
                video_id = parts[1]
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id):
        raise ValueError("请输入 YouTube 单个视频链接或 11 位视频 ID")
    return video_id, 1


def _ydl(**options):
    try:
        from yt_dlp import YoutubeDL
    except ImportError as exc:
        raise RuntimeError("YouTube 需要 Python 3.10+；请在采集器环境安装 pip install -e '.[youtube]'") from exc
    cookiefile = os.environ.get("HR_YOUTUBE_COOKIES_FILE") or os.environ.get("BEANNOTE_YOUTUBE_COOKIES_FILE")
    if cookiefile and not Path(cookiefile).expanduser().is_file():
        raise ValueError("HR_YOUTUBE_COOKIES_FILE 指定的 Cookie 文件不存在")
    return YoutubeDL({"cookiefile": str(Path(cookiefile).expanduser()) if cookiefile else None, "quiet": True, "noprogress": True, "noplaylist": True,
                      "socket_timeout": 30, "retries": 2, "fragment_retries": 2,
                      "js_runtimes": {"node": {}}, **options})


def get_video(content_id, page=1):
    url = "https://www.youtube.com/watch?v=" + content_id
    with _ydl(skip_download=True, ignore_no_formats_error=True) as ydl:
        info = ydl.extract_info(url, download=False)
    if not info or info.get("id") != content_id:
        raise ValueError("没有取得指定 YouTube 视频的信息")
    if not info.get("formats") and not info.get("subtitles") and not info.get("automatic_captions"):
        raise YouTubeAccessError("YouTube 未返回可用字幕或音频，当前请求可能需要登录验证。可通过 HR_YOUTUBE_COOKIES_FILE 指定自行导出的 Netscape Cookie 文件后重试")
    if info.get("is_live") or info.get("live_status") in ("is_live", "is_upcoming", "post_live"):
        raise ValueError("请等待直播结束并生成完整回放后再采集")
    if info.get("availability") in ("private", "premium_only", "subscriber_only", "needs_auth"):
        raise YouTubeAccessError("视频存在访问限制，当前会话无法采集")
    return {"platform": "youtube", "content_id": content_id, "page": 1,
            "title": info.get("title") or content_id,
            "author": info.get("uploader") or info.get("channel") or "",
            "duration_seconds": info.get("duration") or 0, "url": url,
            "published_at": datetime.fromtimestamp(info["timestamp"], timezone.utc).isoformat() if info.get("timestamp") else None, "_info": info}


def parse_json3(payload):
    cues = []
    for event in payload.get("events", []):
        text = "".join(segment.get("utf8", "") for segment in event.get("segs", [])).strip()
        start = float(event.get("tStartMs", 0)) / 1000
        duration = float(event.get("dDurationMs", 0)) / 1000
        if not text or not math.isfinite(start + duration) or start < 0 or duration <= 0:
            continue
        cues.append({"start": start, "end": start + duration, "text": text})
    return sorted(cues, key=lambda cue: cue["start"])


def get_subtitle(video):
    info = video["_info"]
    choices = []
    for automatic, tracks in ((False, info.get("subtitles") or {}), (True, info.get("automatic_captions") or {})):
        for language, formats in tracks.items():
            for track in formats:
                if track.get("ext") != "json3" or not track.get("url"):
                    continue
                # 自动字幕只取原始语言，不把平台机器翻译误标成原文。
                if automatic and "tlang" in parse_qs(urlparse(track["url"]).query):
                    continue
                rank = 0 if language.startswith("zh") else 1 if language.startswith("en") else 2
                choices.append(((automatic, rank, not language.endswith("-orig"), language), language, track))
    failed = False
    with _ydl() as ydl:
        for priority, language, track in sorted(choices, key=lambda item: item[0]):
            try:
                with ydl.urlopen(track["url"]) as response:
                    cues = parse_json3(json.loads(response.read().decode("utf-8")))
                if cues:
                    return {"status": "available", "cues": cues,
                            "track": {"language": language, "language_name": track.get("name", language),
                                      "kind": "platform_ai" if priority[0] else "platform_unknown"}}
            except Exception:
                failed = True
    return {"status": "fetch_failed" if failed else "unavailable", "cues": [], "track": None}


def download_audio(video, destination, max_bytes=512 * 1024 * 1024):
    if video["duration_seconds"] > 7200:
        raise ValueError("视频超过 120 分钟，超出本地转写保护阈值")
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".download")

    def limit(progress):
        if progress.get("downloaded_bytes", 0) > max_bytes:
            raise ValueError("音频下载超过 512 MB 上限")

    try:
        with _ydl(format="bestaudio[ext=m4a]/bestaudio", outtmpl=str(temporary),
                  max_filesize=max_bytes, progress_hooks=[limit]) as ydl:
            ydl.extract_info(video["url"], download=True)
        if not temporary.is_file() or not 1024 <= temporary.stat().st_size <= max_bytes:
            raise ValueError("未下载到完整音频文件")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
        Path(str(temporary) + ".part").unlink(missing_ok=True)
    return str(target)
