"""本地视频文件的校验、音轨提取与转写输入。"""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from urllib.parse import quote


VIDEO_EXTENSIONS = {".3gp", ".avi", ".flv", ".m4v", ".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".ts", ".webm", ".wmv"}
MAX_VIDEO_BYTES = 2 * 1024 * 1024 * 1024
MAX_DURATION_SECONDS = 2 * 60 * 60
MAX_AUDIO_BYTES = 512 * 1024 * 1024


def _digest(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_video_input(value):
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        raise ValueError("本地视频文件不存在或不是普通文件")
    if path.suffix.lower() not in VIDEO_EXTENSIONS:
        raise ValueError("暂不识别该视频扩展名；支持 MP4、MOV、MKV、WebM、AVI 等常见格式")
    if path.stat().st_size < 1 or path.stat().st_size > MAX_VIDEO_BYTES:
        raise ValueError("视频文件为空或超过 2 GB 限制")
    return _digest(path), 1


def get_video(content_id, page=1, source_url=None):
    path = Path(source_url or "").expanduser().resolve()
    if not path.is_file():
        raise ValueError("原始本地视频文件已不存在")
    if _digest(path) != content_id:
        raise ValueError("本地视频文件在排队期间发生变化，请重新提交")
    if path.stat().st_size > MAX_VIDEO_BYTES:
        raise ValueError("视频文件超过 2 GB 限制")
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        raise RuntimeError("本地视频转写需要 FFmpeg 工具集（ffmpeg 与 ffprobe）；请先安装 FFmpeg")
    try:
        result = subprocess.run(
            [ffprobe, "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_type",
             "-of", "json", str(path)], check=True, capture_output=True, text=True, timeout=30)
        streams = json.loads(result.stdout).get("streams", [])
    except (subprocess.SubprocessError, json.JSONDecodeError) as exc:
        raise ValueError("ffprobe 无法读取这个视频文件：{}".format(exc)) from exc
    if not streams:
        raise ValueError("文件中没有可读取的视频流")
    try:
        result = subprocess.run(
            [ffprobe, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
             str(path)], check=True, capture_output=True, text=True, timeout=30)
        duration = float(result.stdout.strip())
    except (subprocess.SubprocessError, ValueError) as exc:
        raise ValueError("无法读取视频时长：{}".format(exc)) from exc
    if duration <= 0 or duration > MAX_DURATION_SECONDS:
        raise ValueError("视频时长须在 2 小时以内")
    title = path.stem
    if title.startswith(content_id + "-"):
        title = title[len(content_id) + 1:]
    return {"platform": "local_file", "content_id": content_id, "page": page,
            "title": title or content_id[:12], "author": "", "duration_seconds": duration,
            "url": "local-file:" + quote(path.name), "_video_path": str(path)}


def get_subtitle(video):
    return None


def download_audio(video, destination, max_bytes=MAX_AUDIO_BYTES):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("本地视频转写需要 FFmpeg 工具集（ffmpeg 与 ffprobe）；请先安装 FFmpeg")
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
