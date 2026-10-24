import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from workbench_source_collector import bilibili
from workbench_source_collector.core import collect_job, to_srt
from workbench_source_collector.importer import import_zip
from workbench_source_collector.storage import Store
from workbench_source_collector.transcribe import TranscriptResult


class BilibiliInputTests(unittest.TestCase):
    def test_parse_bvid_and_page(self):
        self.assertEqual(bilibili.parse_video_input("BV1yUHP6rEYD"), ("BV1yUHP6rEYD", 1))
        self.assertEqual(bilibili.parse_video_input("https://www.bilibili.com/video/BV1yUHP6rEYD/?p=2"), ("BV1yUHP6rEYD", 2))

    def test_reject_invalid_input_and_page(self):
        with self.assertRaises(bilibili.BilibiliError):
            bilibili.parse_video_input("https://example.com/not-a-video")
        with self.assertRaises(bilibili.BilibiliError):
            bilibili.parse_video_input("BV1yUHP6rEYD?p=x")
        with self.assertRaises(bilibili.BilibiliError):
            bilibili.parse_video_input("https://example.com/video/BV1yUHP6rEYD")

    def test_srt_formats_milliseconds(self):
        self.assertEqual(to_srt([{"start": 59.9996, "end": 60.25, "text": "你好"}]),
                         "1\n00:01:00,000 --> 00:01:00,250\n你好\n")


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.temp.name) / "test.sqlite3")

    def tearDown(self):
        self.temp.cleanup()

    def test_unique_bvid_page_and_interrupted_recovery(self):
        first, created = self.store.add_job("BV1yUHP6rEYD", 1, "BV1yUHP6rEYD", model_id="whisper-tiny",
                                            requested_language="English")
        duplicate, duplicate_created = self.store.add_job("BV1yUHP6rEYD", 1, "BV1yUHP6rEYD")
        self.assertTrue(created)
        self.assertFalse(duplicate_created)
        self.assertEqual(first["id"], duplicate["id"])
        self.assertEqual(first["model_id"], "whisper-tiny")
        self.assertEqual(first["requested_language"], "English")
        self.store.update(first["id"], status="transcribing")
        pending = self.store.recover_interrupted()
        self.assertEqual(pending[0]["status"], "queued")

    def test_collect_saves_platform_subtitle_source_package(self):
        job, _ = self.store.add_job("BV1yUHP6rEYD", 1, "BV1yUHP6rEYD")
        video = {"bvid": "BV1yUHP6rEYD", "page": 1, "title": "测试视频", "author": "作者", "duration_seconds": 61, "url": "https://www.bilibili.com/video/BV1yUHP6rEYD/", "aid": 1, "cid": 2}
        subtitle = {"status": "available", "cues": [{"start": 0, "end": 1.2, "text": "测试字幕"}], "track": {"kind": "platform_unknown", "language": "zh-CN"}}
        with patch("workbench_source_collector.core.bilibili.get_video", return_value=video), patch("workbench_source_collector.core.bilibili.get_subtitle", return_value=subtitle), patch("workbench_source_collector.core.inbox_dir", return_value=Path(self.temp.name) / "inbox"):
            result = collect_job(self.store, job["id"])
        self.assertEqual(result["status"], "ready_to_archive")
        folder = Path(result["result_path"])
        metadata = json.loads((folder / "source.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["schema_version"], 1)
        self.assertEqual(metadata["source_kind"], "platform_unknown")
        self.assertFalse(metadata["review_required"])
        self.assertIn("测试字幕", (folder / "字幕.srt").read_text(encoding="utf-8"))

    def test_no_platform_caption_runs_local_asr_and_labels_result(self):
        job, _ = self.store.add_job("BV1yUHP6rEYD", 1, "BV1yUHP6rEYD")
        video = {"bvid": "BV1yUHP6rEYD", "page": 1, "title": "测试视频", "author": "作者", "duration_seconds": 61, "url": "https://www.bilibili.com/video/BV1yUHP6rEYD/", "aid": 1, "cid": 2}
        login_notice = {"status": "login_required", "cues": [], "track": None}
        asr = TranscriptResult([{"start": 2.0, "end": 32.0, "text": "本地识别"}], "mlx-audio",
                               "mlx-community/Qwen3-ASR-1.7B-8bit", "a8379a2e2f9e313c9292cdf1af4055ab56d50d55",
                               "Chinese", "coarse_chunk", {"language": "auto", "chunk_duration_seconds": 30.0})
        with patch("workbench_source_collector.core.bilibili.get_video", return_value=video), patch("workbench_source_collector.core.bilibili.get_subtitle", return_value=login_notice), patch("workbench_source_collector.core.transcribe.available", return_value=True), patch("workbench_source_collector.core.data_dir", return_value=Path(self.temp.name)), patch("workbench_source_collector.core.bilibili.download_audio", return_value=str(Path(self.temp.name) / "audio.m4a")), patch("workbench_source_collector.core.transcribe.transcribe", return_value=asr), patch("workbench_source_collector.core.inbox_dir", return_value=Path(self.temp.name) / "inbox"):
            result = collect_job(self.store, job["id"])
        self.assertEqual(result["status"], "ready_to_archive")
        self.assertEqual(result["source_kind"], "local_asr")
        metadata = json.loads((Path(result["result_path"]) / "source.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["transcription_model"], "mlx-community/Qwen3-ASR-1.7B-8bit")
        self.assertEqual(metadata["transcription_engine"], "mlx-audio")
        self.assertEqual(metadata["transcription_timestamp_quality"], "coarse_chunk")
        self.assertEqual(metadata["transcription_language"], "Chinese")
        self.assertTrue(metadata["review_required"])
        self.assertEqual(metadata["platform_subtitle_status"], "login_required")



class ExtensionImportTests(unittest.TestCase):
    def test_imports_legacy_extension_zip_to_v1_and_deduplicates(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            store = Store(root / "jobs.sqlite3")
            inbox = root / "inbox"
            zip_path = root / "extension.zip"
            legacy = {"bvid": "BV1yUHP6rEYD", "page": 1, "source": "local-asr", "model": "Xenova/whisper-small",
                      "device": "wasm", "collectedAt": "2026-10-24T14:05:10.538Z", "cueCount": 1,
                      "subtitleStart": 0, "subtitleEnd": 2.4,
                      "video": {"bvid": "BV1yUHP6rEYD", "page": 1, "pages": 1, "title": "样本视频", "author": "作者", "duration": 3,
                                "url": "https://www.bilibili.com/video/BV1yUHP6rEYD/"}}
            base = "BV1yUHP6rEYD_P1_样本视频"
            with ZipFile(str(zip_path), "w") as archive:
                archive.writestr(base + "/来源.json", json.dumps(legacy, ensure_ascii=False))
                archive.writestr(base + "/字幕.srt", "1\n00:00:00,000 --> 00:00:02,400\n测试\n")
                archive.writestr(base + "/正文.txt", "测试\n")
                archive.writestr("manifest.csv", "ignored")

            result = import_zip(zip_path, store=store, inbox=inbox)
            self.assertEqual("ready_to_archive", result[0]["status"])
            package = Path(result[0]["package"])
            metadata = json.loads((package / "source.json").read_text(encoding="utf-8"))
            self.assertEqual(1, metadata["schema_version"])
            self.assertEqual("local_asr", metadata["source_kind"])
            self.assertEqual("Transformers.js", metadata["transcription_engine"])
            self.assertTrue(metadata["review_required"])
            self.assertEqual(1, len(store.list()))

            duplicate = import_zip(zip_path, store=store, inbox=inbox)
            self.assertEqual("duplicate", duplicate[0]["status"])
            self.assertEqual(1, len(store.list()))


if __name__ == "__main__":
    unittest.main()
