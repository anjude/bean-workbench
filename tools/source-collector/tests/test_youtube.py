import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from workbench_source_collector import youtube
from workbench_source_collector.sources import parse_source
from workbench_source_collector.storage import Store
from workbench_source_collector.core import collect_job
from workbench_source_collector.transcribe import TranscriptResult


class YouTubeTests(unittest.TestCase):
    def test_input_and_single_video_playlist_link(self):
        for value in ('qU3fmidNbJE', 'https://youtu.be/qU3fmidNbJE?t=30',
                      'https://www.youtube.com/watch?v=qU3fmidNbJE&list=xxx',
                      'https://youtube.com/shorts/qU3fmidNbJE',
                      'https://youtube.com/embed/qU3fmidNbJE'):
            self.assertEqual(parse_source(value), ('youtube', 'qU3fmidNbJE', 1))
        self.assertEqual(parse_source('BV1yUHP6rEYD'), ('bilibili', 'BV1yUHP6rEYD', 1))
        for value in ('https://youtube.com.evil.test/watch?v=qU3fmidNbJE',
                      'https://youtube.com/playlist?list=xxx', 'bad', 'file:///qU3fmidNbJE'):
            with self.assertRaises(ValueError):
                youtube.parse_video_input(value)

    def test_json3_timing_and_empty_events(self):
        cues = youtube.parse_json3({'events': [
            {'tStartMs': 1200, 'dDurationMs': 3500, 'segs': [{'utf8': 'Hello'}, {'utf8': ' world'}]},
            {'tStartMs': 1000, 'dDurationMs': 0, 'segs': [{'utf8': '\n'}]},
            {'tStartMs': -1, 'dDurationMs': 30, 'segs': [{'utf8': 'invalid'}]},
        ]})
        self.assertEqual(cues, [{'start': 1.2, 'end': 4.7, 'text': 'Hello world'}])

    def test_platform_deduplication_and_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = Store(root / 'db')
            job, created = store.add_job('qU3fmidNbJE', 1, 'url', platform='youtube')
            self.assertTrue(created)
            self.assertFalse(store.add_job('qU3fmidNbJE', 1, 'url', platform='youtube')[1])
            self.assertTrue(store.add_job('qU3fmidNbJE', 1, 'url', platform='bilibili')[1])
            video = {'platform': 'youtube', 'content_id': 'qU3fmidNbJE', 'page': 1,
                     'title': 'Demo', 'author': 'Author', '_info': {'temporary_url': 'secret'}}
            subtitle = {'status': 'available', 'cues': [{'start': 0, 'end': 2, 'text': 'Hello'}],
                        'track': {'kind': 'platform_ai', 'language': 'en'}}
            with patch.object(youtube, 'get_video', return_value=video), patch.object(youtube, 'get_subtitle', return_value=subtitle), patch('workbench_source_collector.core.inbox_dir', return_value=root / 'inbox'):
                result = collect_job(store, job['id'])
            self.assertEqual(result['status'], 'ready_to_archive')
            data = json.loads((Path(result['result_path']) / 'source.json').read_text())
            self.assertEqual(data['platform'], 'youtube')
            self.assertEqual(data['content_id'], 'qU3fmidNbJE')
            self.assertTrue(data['review_required'])
            self.assertNotIn('_info', data)

    def test_caption_failure_falls_back_to_asr(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = Store(root / 'db')
            job, _ = store.add_job('qU3fmidNbJE', 1, 'url', platform='youtube')
            video = {'platform': 'youtube', 'page': 1, 'title': 'Demo', 'author': 'Author'}
            asr = TranscriptResult([{'start': 0, 'end': 30, 'text': 'ASR'}], 'mlx-audio',
                                   'mlx-community/Qwen3-ASR-1.7B-8bit', 'a8379a2e2f9e313c9292cdf1af4055ab56d50d55',
                                   'Chinese', 'coarse_chunk', {'language': 'auto', 'chunk_duration_seconds': 30.0})
            with patch.object(youtube, 'get_video', return_value=video), patch.object(youtube, 'get_subtitle', return_value={'status': 'fetch_failed', 'cues': [], 'track': None}), patch.object(youtube, 'download_audio') as download, patch('workbench_source_collector.core.data_dir', return_value=root), patch('workbench_source_collector.core.inbox_dir', return_value=root / 'inbox'), patch('workbench_source_collector.core.transcribe.available', return_value=True), patch('workbench_source_collector.core.transcribe.transcribe', return_value=asr):
                result = collect_job(store, job['id'], model='qwen3-asr-1.7b-8bit')
            download.assert_called_once()
            data = json.loads((Path(result['result_path']) / 'source.json').read_text())
            self.assertEqual(data['source_kind'], 'local_asr')
            self.assertEqual(data['platform_subtitle_status'], 'fetch_failed')
            self.assertEqual(data['transcription_model'], 'mlx-community/Qwen3-ASR-1.7B-8bit')
            self.assertEqual(data['transcription_timestamp_quality'], 'coarse_chunk')

    def test_empty_asr_does_not_make_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = Store(root / 'db')
            job, _ = store.add_job('qU3fmidNbJE', 1, 'url', platform='youtube')
            empty = TranscriptResult([], 'mlx-audio', 'mlx-community/Qwen3-ASR-1.7B-8bit',
                                     'a8379a2e2f9e313c9292cdf1af4055ab56d50d55', 'Chinese', 'coarse_chunk', {})
            with patch.object(youtube, 'get_video', return_value={'page': 1, 'title': 'Demo', 'author': ''}), patch.object(youtube, 'get_subtitle', return_value=None), patch.object(youtube, 'download_audio'), patch('workbench_source_collector.core.data_dir', return_value=root), patch('workbench_source_collector.core.transcribe.available', return_value=True), patch('workbench_source_collector.core.transcribe.transcribe', return_value=empty):
                result = collect_job(store, job['id'])
            self.assertEqual(result['status'], 'failed')
            self.assertIsNone(result['result_path'])

    def test_auto_translations_are_not_collected_as_original(self):
        client = MagicMock()
        client.urlopen.return_value.__enter__.return_value.read.return_value = json.dumps({'events': [{'tStartMs': 0, 'dDurationMs': 1000, 'segs': [{'utf8': 'Hi'}]}]}).encode()
        info = {'automatic_captions': {'zh': [{'ext': 'json3', 'url': 'https://example.com/?tlang=zh'}], 'en-orig': [{'ext': 'json3', 'url': 'https://example.com/?lang=en'}]}}
        with patch.object(youtube, '_ydl') as factory:
            factory.return_value.__enter__.return_value = client
            result = youtube.get_subtitle({'_info': info})
        self.assertEqual(result['track']['language'], 'en-orig')
        self.assertEqual(result['track']['kind'], 'platform_ai')
        client.urlopen.assert_called_once_with('https://example.com/?lang=en')

class YouTubeAccessTests(unittest.TestCase):
    def test_missing_public_streams_is_explicit_access_state(self):
        with patch.object(youtube, '_ydl') as factory:
            factory.return_value.__enter__.return_value.extract_info.return_value = {
                'id': 'qU3fmidNbJE', 'title': 'Demo', 'formats': [], 'subtitles': {}, 'automatic_captions': {}}
            with self.assertRaises(youtube.YouTubeAccessError):
                youtube.get_video('qU3fmidNbJE')

    def test_access_error_is_retryable_without_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp) / 'db')
            job, _ = store.add_job('qU3fmidNbJE', 1, 'url', platform='youtube')
            with patch.object(youtube, 'get_video', side_effect=youtube.YouTubeAccessError('登录验证')):
                result = collect_job(store, job['id'])
            self.assertEqual(result['status'], 'login_required')
            self.assertIsNone(result['result_path'])
            self.assertEqual(store.retry(job['id'])['status'], 'queued')
