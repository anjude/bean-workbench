import tempfile
import unittest
from pathlib import Path

from workbench_source_collector.storage import Store
from workbench_source_collector.migration import migrate_legacy


class MigrationTests(unittest.TestCase):
    def fixture(self, root):
        old = root / 'legacy'
        old.mkdir()
        store = Store(old / 'collector.sqlite3')
        package = old / 'inbox' / 'sample'
        package.mkdir(parents=True)
        (package / '正文.txt').write_text('资料')
        (old / 'audio').mkdir()
        (old / 'audio' / 'sample.m4a').write_bytes(b'audio')
        job, _ = store.add_job('BV1yUHP6rEYD', 1, 'url')
        store.update(job['id'], status='ready_to_archive', result_path=str(package))
        return old, store, job

    def test_migration_preserves_original_and_rewrites_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old, store, job = self.fixture(root)
            target, sources = root / 'runtime', root / 'sources'
            result = migrate_legacy(old, target, sources)
            self.assertEqual(result['job_count'], 1)
            migrated = Store(target / 'collector.sqlite3').get(job['id'])
            self.assertEqual(migrated['result_path'], str((sources / 'sample').resolve()))
            self.assertEqual((sources / 'sample/正文.txt').read_text(), '资料')
            self.assertEqual((old / 'audio/sample.m4a').read_bytes(), (target / 'audio/sample.m4a').read_bytes())
            self.assertTrue(Path(store.get(job['id'])['result_path']).exists())
            with self.assertRaises(FileExistsError):
                migrate_legacy(old, target, sources)

    def test_collision_leaves_existing_material_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old, _, _ = self.fixture(root)
            sources = root / 'sources'
            (sources / 'sample').mkdir(parents=True)
            (sources / 'sample/正文.txt').write_text('existing')
            with self.assertRaises(FileExistsError):
                migrate_legacy(old, root / 'runtime', sources)
            self.assertEqual((sources / 'sample/正文.txt').read_text(), 'existing')
            self.assertFalse((root / 'runtime/collector.sqlite3').exists())

    def test_reject_active_jobs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old, store, job = self.fixture(root)
            store.update(job['id'], status='transcribing')
            with self.assertRaises(ValueError):
                migrate_legacy(old, root / 'runtime', root / 'sources')
