"""ASR 模型注册表与统一转写结果契约；各推理库由适配器隔离。"""
import hashlib
import importlib
import importlib.util
import json
import os
import re
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .paths import workbench_root


CATALOG_PATH = Path(__file__).with_name("model-catalog.json")
DEFAULT_MODEL = "qwen3-asr-1.7b-8bit"
DEFAULT_ALIGNER = "qwen3-forced-aligner-0.6b-8bit"


@dataclass(frozen=True)
class TranscriptResult:
    cues: List[dict]
    engine: str
    model: str
    revision: str
    language: Optional[str]
    timestamp_quality: str
    options: Dict[str, object]

    def metadata(self):
        result = asdict(self)
        result.pop("cues", None)
        return result


def model_catalog():
    return json.loads(CATALOG_PATH.read_text(encoding="utf-8"))["models"]


def resolve_model(model=None):
    model = model or os.environ.get("HR_ASR_MODEL") or DEFAULT_MODEL
    catalog = model_catalog()
    if model not in catalog:
        aliases = {entry["repo_id"]: key for key, entry in catalog.items()}
        model = aliases.get(model, model)
    if model not in catalog:
        raise ValueError("未知 ASR 模型 {!r}，可选：{}".format(model, ", ".join(catalog)))
    return model, catalog[model]


def model_root():
    override = os.environ.get("HR_MODEL_CACHE_DIR")
    return Path(override).expanduser() if override else workbench_root() / ".agents/local-config/models/asr"


def model_path(model=None):
    model_id, spec = resolve_model(model)
    return model_root() / model_id / spec["revision"]


def verify_model(model=None, path=None):
    model_id, spec = resolve_model(model)
    root = Path(path or model_path(model_id))
    if not root.is_dir():
        return False
    weight = root / spec["weight_file"]
    if not weight.is_file() or weight.stat().st_size != spec["weight_bytes"]:
        return False
    digest = hashlib.sha256()
    with weight.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest() == spec["weight_sha256"]


def download_model(model=None):
    model_id, spec = resolve_model(model)
    target = model_path(model_id)
    if verify_model(model_id, target):
        return target
    from huggingface_hub import snapshot_download

    target.parent.mkdir(parents=True, exist_ok=True)
    downloaded = Path(snapshot_download(repo_id=spec["repo_id"], revision=spec["revision"], local_dir=target))
    if not verify_model(model_id, downloaded):
        raise RuntimeError("模型权重未通过 SHA256/文件大小核验：{}".format(model_id))
    return downloaded


def available(model=None):
    try:
        _, spec = resolve_model(model)
        importlib.import_module(spec["engine_module"])
        return True
    except (ImportError, ValueError):
        return False


def aligner_available(model=None):
    try:
        _, spec = resolve_model(model or DEFAULT_ALIGNER)
        return spec["engine"] == "mlx-audio-aligner" and importlib.util.find_spec(spec["engine_module"]) is not None
    except (ImportError, ValueError):
        return False


def _restore_transcript_text(items, text):
    """把对齐器去掉的标点和空格放回时间轴单元。"""
    restored = []
    cursor = 0
    for item in items:
        raw_token = str(item.text)
        at = text.find(raw_token, cursor)
        if at < 0:
            continue
        gap = text[cursor:at]
        if restored:
            restored[-1]["text"] += gap
        else:
            raw_token = gap + raw_token
        restored.append({"start": float(item.start_time), "end": float(item.end_time), "text": raw_token})
        cursor = at + len(str(item.text))
    if restored:
        restored[-1]["text"] += text[cursor:]
    return restored


def _content_key(text):
    return "".join(char.casefold() for char in text if char.isalnum())


def _group_aligned_items(items, offset=0.0):
    cues = []
    current = None
    sentence_end = re.compile(r"[。！？!?；;][”’）】》]*$")
    clause_end = re.compile(r"[，,、][”’）】》]*$")
    max_clause_chars = 48
    max_clause_seconds = 8.0
    for item in items:
        if not item["text"].strip():
            continue
        if current is None:
            current = {"start": item["start"] + offset, "end": item["end"] + offset, "text": item["text"]}
        else:
            current["end"] = item["end"] + offset
            current["text"] += item["text"]
        duration = current["end"] - current["start"]
        if sentence_end.search(current["text"]) or (
            clause_end.search(current["text"])
            and (len(current["text"]) >= max_clause_chars or duration >= max_clause_seconds)
        ):
            cues.append(current)
            current = None
    if current:
        cues.append(current)
    return cues


def _align_cues(audio_path, cues, language, aligner_id=None):
    aligner_id = aligner_id or DEFAULT_ALIGNER
    if not aligner_available(aligner_id):
        return cues, "coarse_chunk", {"alignment_status": "aligner_unavailable", "aligner_model": aligner_id}
    _, spec = resolve_model(aligner_id)
    checkpoint = model_path(aligner_id)
    weight = checkpoint / spec["weight_file"]
    if not weight.is_file():
        return cues, "coarse_chunk", {"alignment_status": "aligner_not_installed", "aligner_model": spec["repo_id"]}
    if not verify_model(aligner_id, checkpoint):
        return cues, "coarse_chunk", {"alignment_status": "aligner_integrity_failed", "aligner_model": spec["repo_id"]}
    from mlx_audio.stt import load
    aligner = load(str(checkpoint))
    aligned_cues = []
    with tempfile.TemporaryDirectory(prefix="hr-align-") as tmp:
        for index, cue in enumerate(cues):
            start, end, text = float(cue["start"]), float(cue["end"]), str(cue["text"]).strip()
            if not text or end <= start:
                continue
            if end - start > spec["max_audio_seconds"]:
                raise ValueError("ASR 分段超过强制对齐器的 5 分钟输入限制")
            wav = Path(tmp) / "{:04d}.wav".format(index)
            subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-i", str(audio_path),
                            "-t", str(end - start), "-ac", "1", "-ar", "16000", "-y", str(wav)],
                           check=True, capture_output=True)
            result = aligner.generate(audio=str(wav), text=text, language=language or "Chinese")
            items = _restore_transcript_text(result.items, text)
            if _content_key("".join(item["text"] for item in items)) != _content_key(text):
                return cues, "coarse_chunk", {"alignment_status": "alignment_text_mismatch", "aligner_model": spec["repo_id"]}
            duration = end - start
            if any(item["start"] < 0 or item["end"] < item["start"] or item["end"] > duration + 0.2
                   for item in items):
                return cues, "coarse_chunk", {"alignment_status": "alignment_timestamp_invalid", "aligner_model": spec["repo_id"]}
            aligned_cues.extend(_group_aligned_items(items, offset=start))
    if not aligned_cues:
        raise RuntimeError("强制对齐器没有返回有效时间戳")
    return aligned_cues, "word_aligned", {"alignment_status": "aligned", "aligner_model": spec["repo_id"],
                                             "aligner_revision": spec["revision"],
                                             "alignment_unit": "word_or_cjk_character"}


def list_models():
    return [{"id": key, "role": value.get("role", "asr"), "engine": value["engine"], "repo_id": value["repo_id"],
             "revision": value["revision"], "path": str(model_path(key)),
             "timestamp_quality": value["timestamp_quality"],
             "runtime_available": aligner_available(key) if value["engine"] == "mlx-audio-aligner" else available(key),
             "installed": verify_model(key)}
            for key, value in model_catalog().items()]


def transcribe(audio_path, model=None, language=None):
    model_id, spec = resolve_model(model)
    if not available(model_id):
        raise RuntimeError("未安装 {} 推理依赖；请按 tools/source-collector/README.md 重建 ASR 环境".format(spec["engine"]))
    checkpoint = download_model(model_id)
    if spec["engine"] == "mlx-audio":
        from mlx_audio.stt import load
        engine = load(str(checkpoint))
        result = engine.generate(str(audio_path), language=language, chunk_duration=spec["chunk_duration"],
                                 max_tokens=spec["max_tokens"], verbose=False)
        def field(item, key):
            return item.get(key) if isinstance(item, dict) else getattr(item, key, None)
        cues = [{"start": float(field(item, "start")), "end": float(field(item, "end")),
                 "text": str(field(item, "text") or "").strip()}
                for item in result.segments if str(field(item, "text") or "").strip()]
        detected_language = field(result, "language")
        if isinstance(detected_language, (list, tuple)):
            languages = list(dict.fromkeys(str(item) for item in detected_language if item))
            detected_language = languages[0] if len(languages) == 1 else ", ".join(languages) or None
        options = {"language": language or "auto", "chunk_duration_seconds": spec["chunk_duration"]}
        timestamp_quality = "coarse_chunk"
    elif spec["engine"] == "mlx-whisper":
        import mlx_whisper
        result = mlx_whisper.transcribe(str(audio_path), path_or_hf_repo=str(checkpoint),
                                        language=language, word_timestamps=False)
        cues = [{"start": float(item["start"]), "end": float(item["end"]), "text": item["text"].strip()}
                for item in result.get("segments", []) if item.get("text", "").strip()]
        detected_language = result.get("language")
        options = {"language": language or "auto", "task": "transcribe"}
        timestamp_quality = "model_segment"
    else:
        raise ValueError("尚无 {} 推理适配器".format(spec["engine"]))
    alignment_options = {}
    if spec["engine"] == "mlx-audio" and cues:
        cues, timestamp_quality, alignment_options = _align_cues(audio_path, cues, detected_language or language)
    options.update(alignment_options)
    return TranscriptResult(cues=cues, engine=spec["engine"], model=spec["repo_id"],
                            revision=spec["revision"], language=detected_language,
                            timestamp_quality=timestamp_quality, options=options)
