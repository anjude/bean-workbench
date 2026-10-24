import json
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

from .paths import data_dir


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    ACTIVE_STATUSES = ("queued", "fetching_metadata", "fetching_subtitles",
                       "downloading_audio", "transcribing")

    def __init__(self, db_path=None):
        self.db_path = str(db_path or (data_dir() / "collector.sqlite3"))
        self.initialize()

    def connect(self):
        connection = sqlite3.connect(self.db_path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    @contextmanager
    def session(self):
        db = self.connect()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def initialize(self):
        with self.session() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                platform TEXT NOT NULL,
                content_id TEXT NOT NULL,
                page INTEGER NOT NULL,
                url TEXT NOT NULL,
                title TEXT NOT NULL DEFAULT '',
                author TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL,
                source_kind TEXT,
                result_path TEXT,
                error TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(platform, content_id, page)
            )""")
            columns = {row[1] for row in db.execute("PRAGMA table_info(jobs)")}
            if "model_id" not in columns:
                db.execute("ALTER TABLE jobs ADD COLUMN model_id TEXT")
            if "requested_language" not in columns:
                db.execute("ALTER TABLE jobs ADD COLUMN requested_language TEXT")

    def add_job(self, bvid, page, url, platform="bilibili", model_id=None, requested_language=None):
        with self.session() as db:
            row = db.execute("SELECT * FROM jobs WHERE platform=? AND content_id=? AND page=?", (platform, bvid, page)).fetchone()
            if row:
                return dict(row), False
            job_id = str(uuid.uuid4())
            stamp = now()
            db.execute("INSERT INTO jobs(id, platform, content_id, page, url, model_id, requested_language, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, 'queued', ?, ?)",
                       (job_id, platform, bvid, page, url, model_id, requested_language, stamp, stamp))
            return dict(db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()), True

    def start_or_reuse_job(self, bvid, page, url, platform="bilibili", model_id=None, requested_language=None):
        """Start a new collection or reuse a finished job; reject a job already in progress."""
        with self.session() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT * FROM jobs WHERE platform=? AND content_id=? AND page=?",
                             (platform, bvid, page)).fetchone()
            if row:
                job = dict(row)
                if job["status"] in self.ACTIVE_STATUSES:
                    return job, False
                db.execute("""UPDATE jobs SET url=?, model_id=?, requested_language=?, status='queued', error=NULL,
                           updated_at=? WHERE id=?""",
                           (url, model_id, requested_language, now(), job["id"]))
                return dict(db.execute("SELECT * FROM jobs WHERE id=?", (job["id"],)).fetchone()), True

            job_id = str(uuid.uuid4())
            stamp = now()
            db.execute("""INSERT INTO jobs(id, platform, content_id, page, url, model_id,
                       requested_language, status, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, 'queued', ?, ?)""",
                       (job_id, platform, bvid, page, url, model_id, requested_language, stamp, stamp))
            return dict(db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()), True

    def update(self, job_id, **fields):
        allowed = {"title", "author", "status", "source_kind", "result_path", "error", "model_id", "requested_language"}
        fields = {key: value for key, value in fields.items() if key in allowed}
        fields["updated_at"] = now()
        query = ", ".join("{}=?".format(key) for key in fields)
        with self.session() as db:
            db.execute("UPDATE jobs SET {} WHERE id=?".format(query), tuple(fields.values()) + (job_id,))
            row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            return dict(row) if row else None

    def get(self, job_id):
        with self.connect() as db:
            row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            return dict(row) if row else None

    def list(self, limit=200):
        with self.session() as db:
            return [dict(row) for row in db.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,))]

    def recover_interrupted(self):
        """On process restart, make interrupted work retryable without losing saved results."""
        with self.session() as db:
            db.execute("UPDATE jobs SET status='queued', error='服务上次退出时任务未完成，可重新采集', updated_at=? WHERE status IN ('fetching_metadata', 'fetching_subtitles', 'downloading_audio', 'transcribing')", (now(),))
            return [dict(row) for row in db.execute("SELECT * FROM jobs WHERE status='queued' ORDER BY created_at")]

    def retry(self, job_id):
        with self.session() as db:
            changed = db.execute("UPDATE jobs SET status='queued', error=NULL, updated_at=? WHERE id=? AND status IN ('failed', 'transcription_unavailable', 'login_required')", (now(), job_id)).rowcount
            if not changed:
                return None
            row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
            return dict(row) if row else None
