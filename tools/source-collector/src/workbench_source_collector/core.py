import json
import re
from datetime import datetime, timezone
from pathlib import Path

from . import bilibili
from .sources import ADAPTERS
from .youtube import YouTubeAccessError
from . import transcribe
from .paths import data_dir, inbox_dir
from .storage import Store


def _stamp(seconds):
    ms = max(0, int(round(float(seconds) * 1000)))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "{:02}:{:02}:{:02},{:03}".format(h, m, s, ms)


def to_srt(cues):
    return "\n\n".join("{}\n{} --> {}\n{}".format(index, _stamp(cue["start"]), _stamp(cue["end"]), cue["text"])
                         for index, cue in enumerate(cues, 1)) + ("\n" if cues else "")


def _safe_name(value):
    value = re.sub(r"[\\/:*?\"<>|\x00-\x1f]+", "_", value).strip(" ._")
    return value[:100] or "未命名来源"


def _save_package(job, video, cues, track, source_kind, subtitle_status=None, asr_result=None):
    collected_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    platform = job["platform"]
    content_id = job["content_id"]
    prefix = content_id if platform == "bilibili" else platform + "-" + content_id
    folder_name = "{}-p{}-{}".format(prefix, video["page"], _safe_name(video["title"]))
    folder = inbox_dir() / folder_name
    folder.mkdir(parents=True, exist_ok=True)
    metadata = {key: value for key, value in video.items() if not key.startswith("_")}
    metadata.update({"schema_version": 1, "platform": platform, "content_id": content_id,
                     "published_at": video.get("published_at"), "collected_at": collected_at, "source_kind": source_kind,
                     "language": (track or {}).get("language"), "subtitle_track": track,
                     "platform_subtitle_status": subtitle_status or ("available" if track else "unavailable"),
                     "transcription_engine": asr_result.engine if asr_result else None,
                     "transcription_model": asr_result.model if asr_result else None,
                     "transcription_revision": asr_result.revision if asr_result else None,
                     "transcription_language": asr_result.language if asr_result else None,
                     "transcription_timestamp_quality": asr_result.timestamp_quality if asr_result else None,
                     "transcription_options": asr_result.options if asr_result else None,
                     "cue_count": len(cues),
                     "coverage_start_seconds": cues[0]["start"] if cues else None,
                     "coverage_end_seconds": cues[-1]["end"] if cues else None,
                     "review_required": source_kind in ("local_asr", "platform_ai", "human_edit")})
    (folder / "source.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
    (folder / "字幕.srt").write_text(to_srt(cues), encoding="utf-8")
    (folder / "正文.txt").write_text("\n".join(cue["text"] for cue in cues) + "\n", encoding="utf-8")
    return str(folder)


def collect_job(store, job_id, model=None):
    job = store.get(job_id)
    if not job:
        raise ValueError("找不到采集任务")
    try:
        store.update(job_id, status="fetching_metadata", error=None)
        adapter = ADAPTERS[job["platform"]]
        video = adapter.get_video(job["content_id"], int(job["page"]))
        store.update(job_id, title=video["title"], author=video["author"], status="fetching_subtitles")
        subtitle = adapter.get_subtitle(video)
        subtitle_status = subtitle.get("status") if subtitle else "unavailable"
        source_kind = "platform_unknown"
        track = None
        cues = subtitle["cues"] if subtitle else []
        if subtitle:
            track = subtitle.get("track")
            source_kind = track.get("kind", "platform_unknown") if track else "platform_unknown"
        asr_result = None
        if not cues:
            selected_model, _ = transcribe.resolve_model(model or job.get("model_id"))
            if not transcribe.available(selected_model):
                return store.update(job_id, status="transcription_unavailable",
                                    error="未取得匿名可用字幕{}。所选模型推理依赖缺失或当前平台不支持；请按 README 安装对应 ASR 环境后重试。".format("（平台提示字幕需要登录，本工具不读取登录凭据）" if subtitle_status == "login_required" else ""))
            audio_dir = data_dir() / "audio"
            audio_name = "{}-p{}.m4a".format(job["content_id"], video["page"]) if job["platform"] == "bilibili" else "youtube-{}.audio".format(job["content_id"])
            audio_path = audio_dir / audio_name
            if not audio_path.exists() or audio_path.stat().st_size < 1024:
                store.update(job_id, status="downloading_audio")
                adapter.download_audio(video, audio_path)
            store.update(job_id, status="transcribing")
            store.update(job_id, model_id=selected_model)
            asr_result = transcribe.transcribe(str(audio_path), model=selected_model,
                                               language=job.get("requested_language"))
            cues = asr_result.cues
            if not cues:
                return store.update(job_id, status="failed", error="本地转写没有返回字幕片段")
            source_kind = "local_asr"
            track = None
        result_path = _save_package(job, video, cues, track, source_kind, subtitle_status, asr_result)
        return store.update(job_id, status="ready_to_archive", source_kind=source_kind, result_path=result_path)
    except YouTubeAccessError as exc:
        return store.update(job_id, status="login_required", error=str(exc))
    except Exception as exc:
        return store.update(job_id, status="failed", error=str(exc))
