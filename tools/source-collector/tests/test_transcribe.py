import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from workbench_source_collector import transcribe


class ModelRegistryTests(unittest.TestCase):
    def test_registry_pins_revisions_and_resolves_repo_aliases(self):
        models = transcribe.model_catalog()
        self.assertEqual(transcribe.DEFAULT_MODEL, "qwen3-asr-1.7b-8bit")
        self.assertEqual(transcribe.resolve_model("mlx-community/Qwen3-ASR-1.7B-8bit")[0], transcribe.DEFAULT_MODEL)
        self.assertEqual(len(models[transcribe.DEFAULT_MODEL]["revision"]), 40)
        self.assertIn("weight_sha256", models[transcribe.DEFAULT_MODEL])
        self.assertEqual(transcribe.resolve_model("whisper-large-v3-turbo")[1]["engine"], "mlx-whisper")

    def test_verify_requires_expected_size_and_hash(self):
        payload = b"local fixture model"
        spec = {"weight_file": "weights.bin", "weight_bytes": len(payload),
                "weight_sha256": hashlib.sha256(payload).hexdigest()}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "weights.bin").write_bytes(payload)
            with patch.object(transcribe, "model_catalog", return_value={"fixture": spec}), \
                 patch.object(transcribe, "resolve_model", return_value=("fixture", spec)):
                self.assertTrue(transcribe.verify_model("fixture", root))
                (root / "weights.bin").write_bytes(payload + b"bad")
                self.assertFalse(transcribe.verify_model("fixture", root))

    def test_model_cache_can_be_overridden(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict("os.environ", {"HR_MODEL_CACHE_DIR": tmp}):
            path = transcribe.model_path("qwen3-asr-1.7b-8bit")
            self.assertEqual(path, Path(tmp) / "qwen3-asr-1.7b-8bit" /
                             "a8379a2e2f9e313c9292cdf1af4055ab56d50d55")

    def test_qwen_adapter_normalizes_dict_segments_and_language_list(self):
        result = SimpleNamespace(
            segments=[{"start": 1.0, "end": 30.0, "text": "第一段"}, {"start": 30.0, "end": 45.0, "text": "第二段"}],
            language=["Chinese", "Chinese"],
        )
        model = SimpleNamespace(generate=lambda *args, **kwargs: result)
        with patch.object(transcribe, "available", return_value=True), \
             patch.object(transcribe, "download_model", return_value=Path("/models/qwen")), \
             patch.object(transcribe, "_align_cues", return_value=(result.segments, "word_aligned", {"alignment_status": "aligned"})), \
             patch("mlx_audio.stt.load", return_value=model):
            transcript = transcribe.transcribe("sample.wav", model="qwen3-asr-1.7b-8bit", language="Chinese")
        self.assertEqual(transcript.language, "Chinese")
        self.assertEqual(transcript.timestamp_quality, "word_aligned")
        self.assertEqual([cue["text"] for cue in transcript.cues], ["第一段", "第二段"])

    def test_restore_alignment_keeps_original_punctuation_and_text(self):
        items = [SimpleNamespace(text="你", start_time=0.1, end_time=0.3),
                 SimpleNamespace(text="好", start_time=0.3, end_time=0.5),
                 SimpleNamespace(text="世界", start_time=0.6, end_time=1.0)]
        restored = transcribe._restore_transcript_text(items, "你好，世界！")
        self.assertEqual("".join(cue["text"] for cue in restored), "你好，世界！")
        self.assertEqual(transcribe._content_key("".join(cue["text"] for cue in restored)), "你好世界")

    def test_missing_aligner_keeps_coarse_cues_without_dropping_transcript(self):
        cues = [{"start": 0.0, "end": 30.0, "text": "识别文本。"}]
        with patch.object(transcribe, "aligner_available", return_value=False):
            aligned, quality, metadata = transcribe._align_cues("sample.wav", cues, "Chinese")
        self.assertEqual(aligned, cues)
        self.assertEqual(quality, "coarse_chunk")
        self.assertEqual(metadata["alignment_status"], "aligner_unavailable")

    def test_aligned_caption_grouping_keeps_sentence_together_and_splits_long_clauses(self):
        items = [
            {"start": 0.0, "end": 0.2, "text": "这"},
            {"start": 0.2, "end": 0.4, "text": "是"},
            {"start": 0.4, "end": 0.8, "text": "完整句子。"},
            {"start": 1.0, "end": 9.2, "text": "这段内容比较长所以会延续到自然的逗号位置才换行，"},
            {"start": 9.4, "end": 11.2, "text": "但短句会继续保持完整，"},
            {"start": 11.4, "end": 12.2, "text": "最后结束。"},
        ]
        cues = transcribe._group_aligned_items(items)
        self.assertEqual([cue["text"] for cue in cues], [
            "这是完整句子。",
            "这段内容比较长所以会延续到自然的逗号位置才换行，",
            "但短句会继续保持完整，最后结束。",
        ])


if __name__ == "__main__":
    unittest.main()
