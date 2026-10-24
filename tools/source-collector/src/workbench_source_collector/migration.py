"""显式迁移旧采集器数据，保留原目录以便回滚。"""
import shutil
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path

from .paths import data_dir, inbox_dir


def migrate_legacy(legacy_dir, target_dir=None, sources_dir=None):
    legacy = Path(legacy_dir).expanduser().resolve()
    target = Path(target_dir or data_dir()).resolve()
    sources = Path(sources_dir or inbox_dir()).resolve()
    old_db = legacy / 'collector.sqlite3'
    new_db = target / 'collector.sqlite3'
    if not old_db.is_file():
        raise ValueError('旧目录中没有 collector.sqlite3')
    if new_db.exists():
        raise FileExistsError('新任务库已存在，停止迁移以免覆盖；已迁移过时无需再执行')
    if target == legacy or sources.is_relative_to(legacy):
        raise ValueError('迁移目标必须与旧数据目录分离')
    target.mkdir(parents=True, exist_ok=True, mode=0o700)
    sources.mkdir(parents=True, exist_ok=True)
    copied = []
    with tempfile.TemporaryDirectory(prefix='migration-', dir=target) as temp:
        staged = Path(temp) / 'collector.sqlite3'
        with closing(sqlite3.connect(old_db)) as old, closing(sqlite3.connect(staged)) as new:
            active = old.execute("SELECT COUNT(*) FROM jobs WHERE status IN ('fetching_metadata','fetching_subtitles','downloading_audio','transcribing')").fetchone()[0]
            if active:
                raise ValueError('旧任务仍在处理，请先停止旧采集服务并等待任务结束')
            old.backup(new)
        try:
            for parent, destination in ((legacy / 'inbox', sources), (legacy / 'audio', target / 'audio')):
                if not parent.exists():
                    continue
                for child in parent.iterdir():
                    output = destination / child.name
                    if output.exists():
                        raise FileExistsError('目标已存在，未覆盖：{}'.format(output))
                    destination.mkdir(parents=True, exist_ok=True)
                    copied.append(output)
                    if child.is_dir():
                        shutil.copytree(child, output)
                    else:
                        shutil.copy2(child, output)
            with closing(sqlite3.connect(staged)) as db:
                rows = db.execute('SELECT id,result_path FROM jobs').fetchall()
                for job_id, result_path in rows:
                    if result_path:
                        path = Path(result_path).resolve()
                        if path.is_relative_to(legacy / 'inbox'):
                            updated = sources / path.relative_to(legacy / 'inbox')
                            if not updated.is_dir():
                                raise ValueError('来源包缺失：{}'.format(path))
                            db.execute('UPDATE jobs SET result_path=? WHERE id=?', (str(updated), job_id))
                db.commit()
                db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                db.execute("PRAGMA journal_mode=DELETE")
            staged.rename(new_db)
            return {'job_count': len(rows), 'database': str(new_db), 'sources': str(sources), 'legacy_preserved': str(legacy)}
        except Exception:
            for path in reversed(copied):
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink(missing_ok=True)
            raise
