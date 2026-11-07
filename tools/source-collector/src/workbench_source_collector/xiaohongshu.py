"""使用工作台接入的 XHS-Downloader 获取公开视频文件，再复用本地 ASR。"""
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from .paths import data_dir, workbench_root


VIDEO_EXTENSIONS = {".3gp", ".avi", ".flv", ".m4v", ".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".ts", ".webm", ".wmv"}
MAX_VIDEO_BYTES = 2 * 1024 * 1024 * 1024
MAX_AUDIO_BYTES = 512 * 1024 * 1024
MAX_DURATION_SECONDS = 2 * 60 * 60
requires_local_asr = True


def parse_video_input(value):
    value = value.strip()
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    allowed = host == "xhslink.com" or host.endswith(".xhslink.com") or host == "xiaohongshu.com" or host.endswith(".xiaohongshu.com")
    if parsed.scheme not in ("http", "https") or not allowed:
        raise ValueError("请输入小红书笔记链接或 xhslink 分享链接")
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return digest, 1


def _downloader():
    configured = os.environ.get("HR_XHS_DOWNLOADER_PYTHON")
    if configured:
        python = Path(configured).expanduser()
    else:
        repo = workbench_root() / "tools/xhs-research/XHS-Downloader"
        python = repo / ".venv/bin/python"
    if not python.is_file():
        raise RuntimeError("小红书下载需要安装 XHS-Downloader 依赖；请按 tools/source-collector/README.md 的安装步骤配置，或设置 HR_XHS_DOWNLOADER_PYTHON")
    return python


def get_video(content_id, page=1, source_url=None):
    url = source_url or ""
    video_dir = data_dir() / "downloads" / "xiaohongshu" / content_id
    video_dir.mkdir(parents=True, exist_ok=True)
    repo = workbench_root() / "tools/xhs-research/XHS-Downloader"
    script = repo / "main.py"
    if not script.is_file():
        raise RuntimeError("工作台未找到 tools/xhs-research/XHS-Downloader 子模块")
    settings_dir = data_dir() / "xiaohongshu-settings" / "volume"
    settings_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    settings_path = settings_dir / "settings.json"
    settings_path.write_text(json.dumps({"cookie": "", "proxy": None, "proxy_download": False,
                                         "work_path": str(video_dir.parent), "folder_name": content_id,
                                         "video_cover_download": False}, ensure_ascii=False), encoding="utf-8")
    cmd = [_downloader(), str(script), "--url", url, "--work_path", str(video_dir.parent),
           "--folder_name", content_id, "--video_cover_download", "false", "--settings", str(settings_path)]
    try:
        result = subprocess.run(cmd, cwd=repo, check=False, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("小红书视频下载超过 10 分钟，已停止") from exc
    if result.returncode:
        detail = (result.stderr or result.stdout or "").strip().replace(url, "[原链接]")[-800:]
        raise RuntimeError("XHS-Downloader 下载失败（退出码 {}）{}".format(result.returncode, "：" + detail if detail else ""))
    candidates = sorted(path for path in video_dir.rglob("*")
                        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS)
    if not candidates:
        raise ValueError("小红书链接没有下载到视频文件；请确认它是公开视频笔记且包含视频")
    if len(candidates) > 1:
        candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    video_path = candidates[0]
    if video_path.stat().st_size > MAX_VIDEO_BYTES:
        raise ValueError("小红书视频超过 2 GB 限制")
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise RuntimeError("小红书视频转写需要 FFmpeg 工具集（ffmpeg 与 ffprobe）；请先安装 FFmpeg")
    try:
        probe = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(video_path)],
            check=True, capture_output=True, text=True, timeout=30)
        duration = float(probe.stdout.strip())
    except (subprocess.SubprocessError, ValueError) as exc:
        raise ValueError("无法读取小红书视频时长：{}".format(exc)) from exc
    if duration <= 0 or duration > MAX_DURATION_SECONDS:
        raise ValueError("小红书视频时长须在 2 小时以内")
    title = video_path.stem or content_id[:12]
    return {"platform": "xiaohongshu", "content_id": content_id, "page": page,
            "title": title, "author": "", "duration_seconds": duration, "url": url,
            "_video_path": str(video_path)}


def get_subtitle(video):
    return None


def download_audio(video, destination, max_bytes=MAX_AUDIO_BYTES):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("小红书视频转写需要 FFmpeg；请先安装 FFmpeg")
    target = Path(destination)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp.m4a")
    try:
        subprocess.run(
            [ffmpeg, "-nostdin", "-v", "error", "-i", video["_video_path"], "-map", "0:a:0",
             "-vn", "-ac", "1", "-ar", "16000", "-c:a", "aac", "-b:a", "64k", "-y", str(temporary)],
            check=True, capture_output=True, text=True, timeout=1200)
        if not temporary.is_file() or not 1024 <= temporary.stat().st_size <= max_bytes:
            raise ValueError("未能提取出有效音频，或提取后的音频超过 512 MB")
        temporary.replace(target)
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip()[-800:]
        raise ValueError("FFmpeg 提取音频失败{}".format("：" + detail if detail else "")) from exc
    finally:
        temporary.unlink(missing_ok=True)
    return str(target)
