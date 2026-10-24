"""Import legacy Chrome extension ZIP exports into source package v1."""
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from .core import _safe_name
from .paths import inbox_dir
from .storage import Store

MAX_MEMBER_SIZE = 20 * 1024 * 1024
MAX_ARCHIVE_SIZE = 100 * 1024 * 1024


def _read_member(archive, name):
    info = archive.getinfo(name)
    if info.file_size > MAX_MEMBER_SIZE:
        raise ValueError("来源 ZIP 单个文件超过 20 MB：{}".format(name))
    return archive.read(name)


def _standard_metadata(legacy, srt):
    if not isinstance(legacy, dict):
        raise ValueError("旧来源 JSON 顶层必须是对象")
    video = legacy.get("video") or {}
    if not isinstance(video, dict):
        raise ValueError("旧来源 JSON 的 video 字段必须是对象")
    bvid = legacy.get("bvid") or video.get("bvid")
    page = legacy.get("page") or video.get("page") or 1
    if not isinstance(bvid, str) or not re.fullmatch(r"BV[0-9A-Za-z]+", bvid):
        raise ValueError("旧来源 JSON 缺少有效 BV 号")
    try:
        page = int(page)
    except (TypeError, ValueError):
        raise ValueError("旧来源 JSON 的分 P 无效")
    if page < 1:
        raise ValueError("旧来源 JSON 的分 P 必须大于零")

    legacy_kind = legacy.get("source")
    source_kind = "local_asr" if legacy_kind == "local-asr" else "platform_unknown"
    cues = srt.decode("utf-8-sig").count("-->")
    return {
        "schema_version": 1,
        "platform": "bilibili",
        "content_id": bvid,
        "bvid": bvid,
        "aid": video.get("aid"),
        "cid": video.get("cid"),
        "page": page,
        "page_count": video.get("pages"),
        "url": video.get("url") or "https://www.bilibili.com/video/{}/?p={}".format(bvid, page),
        "title": video.get("title") or legacy.get("title") or bvid,
        "author": video.get("author") or legacy.get("author") or "",
        "published_at": None,
        "collected_at": legacy.get("collectedAt") or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "duration_seconds": video.get("duration"),
        "source_kind": source_kind,
        "language": None,
        "transcription_engine": "Transformers.js" if source_kind == "local_asr" else None,
        "transcription_model": legacy.get("model") if source_kind == "local_asr" else None,
        "cue_count": legacy.get("cueCount") if isinstance(legacy.get("cueCount"), int) else cues,
        "coverage_start_seconds": legacy.get("subtitleStart"),
        "coverage_end_seconds": legacy.get("subtitleEnd"),
        "review_required": source_kind == "local_asr",
        "collector": "workbench-source-collector-extension",
        "collector_device": legacy.get("device"),
        "subtitle_track": legacy.get("track"),
        "legacy_status": legacy.get("status"),
    }


def import_zip(zip_path, store=None, inbox=None):
    """Import all successful legacy source packages; never overwrite existing jobs/files."""
    zip_path = Path(zip_path)
    store = store or Store()
    inbox = Path(inbox or inbox_dir())
    results = []
    try:
        archive = ZipFile(str(zip_path))
    except (OSError, BadZipFile) as exc:
        raise ValueError("无法读取来源 ZIP：{}".format(exc))

    with archive:
        if sum(item.file_size for item in archive.infolist()) > MAX_ARCHIVE_SIZE:
            raise ValueError("来源 ZIP 解压后超过 100 MB")
        files = {item.filename for item in archive.infolist() if not item.is_dir()}
        metadata_paths = sorted(name for name in files if Path(name).name == "来源.json")
        if not metadata_paths:
            raise ValueError("ZIP 中未找到 Chrome 插件来源包（来源.json）")

        for metadata_path in metadata_paths:
            parent = str(Path(metadata_path).parent)
            srt_path = str(Path(parent) / "字幕.srt")
            txt_path = str(Path(parent) / "正文.txt")
            if srt_path not in files or txt_path not in files:
                results.append({"status": "invalid", "package": parent, "error": "缺少字幕.srt 或 正文.txt"})
                continue
            try:
                legacy = json.loads(_read_member(archive, metadata_path).decode("utf-8-sig"))
                srt = _read_member(archive, srt_path)
                txt = _read_member(archive, txt_path)
                meta = _standard_metadata(legacy, srt)
                job, created = store.add_job(meta["content_id"], meta["page"], meta["url"])
                if not created:
                    results.append({"status": "duplicate", "package": parent, "job_id": job["id"]})
                    continue
                name = "{}-p{}-{}".format(meta["content_id"], meta["page"], _safe_name(meta["title"]))
                destination = inbox / name
                if destination.exists():
                    store.update(job["id"], status="failed", error="待归档目录已存在，未覆盖")
                    results.append({"status": "duplicate", "package": parent, "error": "待归档目录已存在，未覆盖"})
                    continue
                destination.mkdir(parents=True)
                try:
                    (destination / "source.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
                    (destination / "字幕.srt").write_bytes(srt)
                    (destination / "正文.txt").write_bytes(txt)
                except Exception:
                    shutil.rmtree(str(destination), ignore_errors=True)
                    store.update(job["id"], status="failed", error="写入导入资料包失败")
                    raise
                store.update(job["id"], title=meta["title"], author=meta["author"], source_kind=meta["source_kind"], status="ready_to_archive", result_path=str(destination))
                results.append({"status": "ready_to_archive", "package": str(destination), "job_id": job["id"]})
            except (ValueError, UnicodeError, json.JSONDecodeError) as exc:
                results.append({"status": "invalid", "package": parent, "error": str(exc)})
    return results
