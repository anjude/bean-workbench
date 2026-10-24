import json
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .sources import parse_source
from .core import collect_job
from .storage import Store


WEB_ROOT = Path(__file__).parent / "web"


class CollectorServer(ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, address, store):
        self.store = store
        self.worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="workbench-collector")
        super().__init__(address, Handler)
        for job in self.store.recover_interrupted():
            self.worker.submit(collect_job, self.store, job["id"])

    def server_close(self):
        super().server_close()
        self.worker.shutdown(wait=False, cancel_futures=True)


class Handler(BaseHTTPRequestHandler):
    server_version = "hr-source/0.1"

    def _local_request(self):
        host = self.headers.get("Host", "").split(":", 1)[0].lower()
        if host not in ("127.0.0.1", "localhost", "[::1]"):
            return False
        origin = self.headers.get("Origin")
        if origin:
            origin_host = (urlparse(origin).hostname or "").lower()
            if origin_host not in ("127.0.0.1", "localhost", "::1"):
                return False
        return True

    def _json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length < 1 or length > 1024 * 1024:
            raise ValueError("请求内容为空或超过 1 MB")
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self):
        if not self._local_request():
            return self._json({"error": "仅接受本机请求"}, 403)
        if self.path == "/api/jobs":
            return self._json({"jobs": self.server.store.list()})
        if self.path == "/" or self.path == "/index.html":
            body = (WEB_ROOT / "index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            return self.wfile.write(body)
        return self._json({"error": "没有这个路径"}, 404)

    def do_POST(self):
        if not self._local_request():
            return self._json({"error": "仅接受本机请求"}, 403)
        try:
            if self.path == "/api/jobs":
                payload = self._body()
                lines = payload.get("inputs", [])
                model_id = payload.get("model")
                if model_id is not None:
                    from .transcribe import resolve_model
                    model_id, _ = resolve_model(model_id)
                language = payload.get("language")
                if language not in (None, "", "Chinese", "English"):
                    raise ValueError("语言选项只支持自动、Chinese 或 English")
                if not isinstance(lines, list) or len(lines) > 2000:
                    raise ValueError("一次最多提交 2000 条链接")
                accepted, errors = [], []
                for value in lines:
                    try:
                        platform, bvid, page = parse_source(str(value))
                        job, started = self.server.store.start_or_reuse_job(
                            bvid, page, str(value).strip(), platform=platform,
                            model_id=model_id, requested_language=language or None)
                        if not started:
                            errors.append({"input": str(value), "error": "采集任务正在执行", "job_id": job["id"]})
                            continue
                        accepted.append({"job": job, "started": True})
                        self.server.worker.submit(collect_job, self.server.store, job["id"], model_id)
                    except Exception as exc:
                        errors.append({"input": str(value), "error": str(exc)})
                return self._json({"accepted": accepted, "errors": errors}, 202)
            if self.path.startswith("/api/jobs/") and self.path.endswith("/retry"):
                job_id = unquote(self.path.strip("/").split("/")[2])
                job = self.server.store.retry(job_id)
                if not job:
                    raise ValueError("任务不存在，或当前状态不支持重试")
                self.server.worker.submit(collect_job, self.server.store, job_id,
                                          model=job.get("model_id"))
                return self._json({"job": job}, 202)
            return self._json({"error": "没有这个路径"}, 404)
        except (ValueError, FileExistsError, json.JSONDecodeError) as exc:
            return self._json({"error": str(exc)}, 400)
        except Exception as exc:
            return self._json({"error": str(exc)}, 500)

    def log_message(self, fmt, *args):
        # Keep terminal logs useful without echoing potentially sensitive URLs.
        if args and str(args[0]).startswith("/api"):
            return
        super().log_message(fmt, *args)


def serve(host="127.0.0.1", port=8765, store=None):
    if host not in ("127.0.0.1", "localhost", "::1"):
        raise ValueError("本机网页只允许绑定 loopback 地址")
    server = CollectorServer((host, port), store or Store())
    print("工作台来源采集：http://{}:{}/".format(host, port))
    print("仅监听本机；按 Ctrl+C 停止。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n正在停止本地服务…")
    finally:
        server.server_close()
