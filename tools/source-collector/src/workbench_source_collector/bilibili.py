"""面向公开可访问视频的 B 站元信息和字幕读取。"""
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


BV_RE = re.compile(r"(?i)BV[0-9A-Za-z]{10}")
BASE = "https://api.bilibili.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/131 Safari/537.36",
    "Referer": "https://www.bilibili.com/",
    "Accept": "application/json, text/plain, */*",
}


class BilibiliError(Exception):
    pass


def parse_video_input(value):
    value = value.strip()
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme or parsed.netloc:
        host = (parsed.hostname or "").lower()
        if not any(host == base or host.endswith("." + base) for base in ("bilibili.com", "bilibili.tv")):
            raise BilibiliError("只接受 B 站视频链接或 BV 号")
    elif "/" in value or "\\" in value:
        raise BilibiliError("请输入 B 站视频链接或 BV 号")
    match = BV_RE.search(value)
    if not match:
        raise BilibiliError("请输入 B 站 BV 号或视频链接")
    page = 1
    if parsed.query:
        query = urllib.parse.parse_qs(parsed.query)
        try:
            page = max(1, int(query.get("p", ["1"])[0]))
        except (TypeError, ValueError):
            raise BilibiliError("链接中的分 P 参数无效")
    return "BV" + match.group(0)[2:], page


def _get_json(url, timeout=25):
    request = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise BilibiliError("访问 B 站失败：{}".format(exc))
    if payload.get("code") != 0:
        raise BilibiliError("B 站接口返回 {}：{}".format(payload.get("code"), payload.get("message", "未知错误")))
    return payload.get("data") or {}


def get_video(bvid, page):
    data = _get_json(BASE + "/x/web-interface/view?" + urllib.parse.urlencode({"bvid": bvid}))
    rights = data.get("rights") or {}
    if data.get("is_upower_exclusive") or rights.get("ugc_pay") or rights.get("arc_pay"):
        raise BilibiliError("视频存在付费或专属访问限制，已停止采集")
    pages = data.get("pages") or []
    part = next((item for item in pages if int(item.get("page", 0)) == page), None)
    if not part:
        raise BilibiliError("视频没有第 {} P".format(page))
    title = data.get("title", "未命名视频")
    if len(pages) > 1:
        title = "{} · P{} {}".format(title, page, part.get("part", ""))
    return {
        "platform": "bilibili",
        "bvid": data.get("bvid", bvid),
        "aid": data.get("aid"),
        "cid": part.get("cid"),
        "page": page,
        "page_count": len(pages),
        "title": title,
        "author": (data.get("owner") or {}).get("name", ""),
        "duration_seconds": int(part.get("duration", 0)),
        "url": "https://www.bilibili.com/video/{}/{}".format(data.get("bvid", bvid), "?p={}".format(page) if page > 1 else ""),
    }


def get_subtitle(video):
    params = urllib.parse.urlencode({"aid": video["aid"], "cid": video["cid"]})
    data = _get_json(BASE + "/x/player/v2?" + params)
    tracks = ((data.get("subtitle") or {}).get("subtitles") or [])
    tracks = [track for track in tracks if not track.get("is_lock") and track.get("subtitle_url")]
    if not tracks:
        if data.get("need_login_subtitle") or (data.get("subtitle") or {}).get("need_login_subtitle"):
            return {"status": "login_required", "cues": [], "track": None}
        return None
    tracks.sort(key=lambda track: (0 if str(track.get("lan", "")).startswith(("zh", "ai-zh")) else 1,
                                  1 if track.get("ai_type") else 0))
    selected = tracks[0]
    url = selected["subtitle_url"]
    if url.startswith("//"):
        url = "https:" + url
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not any(host == base or host.endswith("." + base) for base in ("bilibili.com", "hdslb.com")):
        raise BilibiliError("字幕地址不是受支持的 B 站域名")
    raw = _get_json(url)
    cues = []
    for item in raw.get("body", []):
        text = str(item.get("content", "")).strip()
        if text and item.get("from") is not None and item.get("to") is not None:
            cues.append({"start": float(item["from"]), "end": float(item["to"]), "text": text})
    machine = bool(selected.get("ai_type")) or str(selected.get("lan", "")).startswith("ai-")
    return {
        "status": "available",
        "cues": cues,
        "track": {
            "language": selected.get("lan"),
            "language_name": selected.get("lan_doc"),
            "kind": "platform_ai" if machine else "platform_unknown",
        },
    }


def download_audio(video, destination, max_bytes=512 * 1024 * 1024):
    """Download a public AAC stream without reading browser cookies."""
    if int(video.get("duration_seconds", 0)) > 7200:
        raise BilibiliError("单个分 P 超过 120 分钟，超出首版本地转写保护阈值")
    query = urllib.parse.urlencode({"bvid": video["bvid"], "cid": video["cid"], "fnval": 16, "qn": 16, "fourk": 0})
    data = _get_json(BASE + "/x/player/playurl?" + query)
    duration_ms = int(data.get("timelength", 0))
    if data.get("is_preview") or (duration_ms and duration_ms / 1000 < video["duration_seconds"] - max(3, video["duration_seconds"] * .02)):
        raise BilibiliError("播放接口只返回部分音频，无法作为完整转写来源")
    tracks = sorted(((data.get("dash") or {}).get("audio") or []), key=lambda item: int(item.get("bandwidth", 0)))
    if not tracks:
        raise BilibiliError("没有取得可用的公开音频流")
    track = tracks[0]
    urls = [track.get("baseUrl") or track.get("base_url")]
    urls += track.get("backupUrl") or track.get("backup_url") or []
    errors = []
    target = Path(destination)
    for url in urls:
        if not url:
            continue
        parsed = urllib.parse.urlparse(url)
        host = (parsed.hostname or "").lower()
        allowed = ("bilivideo.com", "bilivideo.cn", "bilivideo.net", "bilibili.com", "hdslb.com")
        if parsed.scheme != "https" or not any(host == base or host.endswith("." + base) for base in allowed):
            continue
        request = urllib.request.Request(url, headers=HEADERS)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(request, timeout=180) as response:
                declared = int(response.headers.get("Content-Length", "0") or 0)
                if declared > max_bytes:
                    raise BilibiliError("音频超过 512 MB 上限")
                total = 0
                with target.open("wb") as output:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        total += len(chunk)
                        if total > max_bytes:
                            raise BilibiliError("音频下载超过 512 MB 上限")
                        output.write(chunk)
            if total < 1024:
                raise BilibiliError("下载到的音频为空或不完整")
            return str(target)
        except BilibiliError:
            target.unlink(missing_ok=True)
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            target.unlink(missing_ok=True)
            errors.append(str(exc))
    raise BilibiliError("下载公开音频失败：{}".format("；".join(errors) or "没有有效音频地址"))
