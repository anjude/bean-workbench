"""离线验证发布边界，不读取真实凭证、不请求微信。"""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('bn_publish', Path(__file__).parents[1] / 'publish.py')
pub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pub)


class PublishTests(unittest.TestCase):
    def test_draft_fields_use_account_defaults(self):
        article = pub.build_draft_article('标题', '豆小匠', '<p>正文</p>', '引人继续看的导读', 'cover-id')
        self.assertEqual(article, {
            'title': '标题',
            'author': '豆小匠',
            'content': '<p>正文</p>',
            'digest': '引人继续看的导读',
            'thumb_media_id': 'cover-id',
            'need_open_comment': 1,
            'only_fans_can_comment': 0,
        })

    def test_draft_fields_allow_comment_override(self):
        article = pub.build_draft_article('标题', '作者', '<p>正文</p>', '导读', 'cover-id', 0, 1)
        self.assertEqual(article['need_open_comment'], 0)
        self.assertEqual(article['only_fans_can_comment'], 1)

    def test_dry_run_does_not_touch_network_or_receipt(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(pub, 'api') as api:
            receipt = Path(tmp) / 'receipt.json'
            result = pub.recorded_write('draft/add', {'articles': []}, receipt, True)
            self.assertTrue(result['dry_run'])
            self.assertFalse(receipt.exists())
            api.assert_not_called()

    def test_success_records_response_and_blocks_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(pub, 'api', return_value={'media_id': 'mock'}) as api:
            receipt = Path(tmp) / 'receipt.json'
            pub.recorded_write('draft/add', {}, receipt)
            self.assertEqual(json.loads(receipt.read_text())['response']['media_id'], 'mock')
            self.assertEqual(receipt.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(ValueError):
                pub.recorded_write('draft/add', {}, receipt)
            self.assertEqual(api.call_count, 1)

    def test_timeout_keeps_pending_and_blocks_retry(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(pub, 'api', side_effect=RuntimeError('timeout')) as api:
            receipt = Path(tmp) / 'receipt.json'
            with self.assertRaises(RuntimeError):
                pub.recorded_write('draft/add', {}, receipt)
            self.assertEqual(json.loads(receipt.read_text())['state'], 'pending')
            with self.assertRaises(ValueError):
                pub.recorded_write('draft/add', {}, receipt)
            self.assertEqual(api.call_count, 1)

    def test_cache_is_private_account_scoped_and_reused(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(pub, 'LOCAL_CONFIG', Path(tmp)), patch.object(pub, 'load_creds', return_value=('account-a', 'secret')), patch.object(pub, 'request', return_value={'access_token': 'mock-token', 'expires_in': 7200}) as request:
            self.assertEqual(pub.get_token(), 'mock-token')
            self.assertEqual(pub.get_token(), 'mock-token')
            self.assertEqual(request.call_count, 1)
            cache = list((Path(tmp) / 'token-cache').glob('*.json'))[0]
            self.assertEqual(cache.stat().st_mode & 0o777, 0o600)
            with patch.object(pub, 'load_creds', return_value=('account-b', 'other-secret')):
                pub.get_token()
            self.assertEqual(request.call_count, 2)

    def test_local_credentials_and_explicit_override(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(pub, 'LOCAL_CONFIG', Path(tmp)), patch.dict(pub.os.environ, {}, clear=True):
            credentials = Path(tmp) / 'credentials'
            pub.private_json(Path(tmp) / 'placeholder.json', {})
            credentials.write_text('mock-app\nmock-secret\n')
            credentials.chmod(0o600)
            self.assertEqual(pub.load_creds(), ('mock-app', 'mock-secret'))
            other = Path(tmp) / 'other-key'
            other.write_text('other-app\nother-secret\n')
            other.chmod(0o600)
            with patch.dict(pub.os.environ, {'WECHAT_KEY_FILE': str(other)}):
                self.assertEqual(pub.load_creds(), ('other-app', 'other-secret'))
            credentials.chmod(0o644)
            with self.assertRaises(ValueError):
                pub.load_creds()

    def test_cover_and_body_upload_use_different_endpoints(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(pub, 'get_token', return_value='mock-token'), patch.object(pub, 'request', side_effect=[{'media_id': 'mock'}, {'url': 'mock-url'}]) as request:
            path = Path(tmp) / '封面.jpg'
            path.write_bytes(b'image-fixture')
            pub.upload(path, 'cover')
            pub.upload(path, 'body')
            self.assertIn('/material/add_material?', request.call_args_list[0].args[0])
            self.assertIn('/media/uploadimg?', request.call_args_list[1].args[0])
            self.assertIn(b'name="media"', request.call_args_list[0].args[1])


if __name__ == '__main__':
    unittest.main()
