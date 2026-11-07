from __future__ import annotations

import base64
import io
import json
import os
import re
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


ROOT = Path(__file__).parent
WEB = ROOT / "web"
HOST = "127.0.0.1"
PORT = 8769


def image_configured() -> bool:
    return bool(os.environ.get("XHS_IMAGE_API_KEY") and os.environ.get("XHS_IMAGE_API_BASE_URL"))


class Handler(BaseHTTPRequestHandler):
    server_version = "GknowImageStudio/0.1"

    def local_request(self) -> bool:
        host = self.headers.get("Host", "").split(":", 1)[0].lower()
        if host not in ("127.0.0.1", "localhost"):
            return False
        origin = self.headers.get("Origin")
        if origin:
            origin_host = (origin.split("://", 1)[-1].split("/", 1)[0].split(":", 1)[0]).lower()
            if origin_host not in ("127.0.0.1", "localhost"):
                return False
        return True

    def send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def read_json(self, limit: int = 35 * 1024 * 1024) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length < 2 or length > limit:
            raise ValueError("请求内容为空或超出大小限制")
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self) -> None:
        if not self.local_request():
            return self.send_json({"error": "仅接受本机请求"}, 403)
        if self.path == "/api/config":
            return self.send_json({"imageGenerationReady": image_configured()})
        route = "/index.html" if self.path == "/" else self.path
        file_path = (WEB / route.lstrip("/")).resolve()
        if not file_path.is_relative_to(WEB.resolve()) or not file_path.is_file():
            return self.send_json({"error": "没有这个路径"}, 404)
        content_type = "text/html; charset=utf-8" if file_path.suffix == ".html" else "text/plain; charset=utf-8"
        if file_path.suffix == ".css":
            content_type = "text/css; charset=utf-8"
        elif file_path.suffix == ".js":
            content_type = "text/javascript; charset=utf-8"
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        if not self.local_request():
            return self.send_json({"error": "仅接受本机请求"}, 403)
        try:
            if self.path == "/api/generate-image":
                return self.generate_image(self.read_json(1024 * 1024))
            if self.path == "/api/export":
                return self.export_images(self.read_json())
            return self.send_json({"error": "没有这个路径"}, 404)
        except ValueError as exc:
            return self.send_json({"error": str(exc)}, 400)
        except Exception as exc:
            return self.send_json({"error": str(exc)}, 500)

    def generate_image(self, body: dict) -> None:
        api_key = os.environ.get("XHS_IMAGE_API_KEY")
        base_url = os.environ.get("XHS_IMAGE_API_BASE_URL", "").strip()
        model = os.environ.get("XHS_IMAGE_MODEL", "gpt-image-1")
        if not api_key or not base_url:
            return self.send_json({"error": "尚未配置生图服务。请按 local-studio/README.md 设置服务地址和密钥后重启。"}, 503)
        prompt = str(body.get("prompt", "")).strip()
        if not prompt or len(prompt) > 4000:
            raise ValueError("请填写 1 到 4000 字的画面描述")
        endpoint = base_url.rstrip("/") + "/images/generations"
        payload = {
            "model": model,
            "prompt": prompt,
            "size": "1024x1536",
            "n": 1,
            "response_format": "b64_json",
        }
        request = Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=180) as response:
                result = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read(1800).decode("utf-8", errors="replace")
            return self.send_json({"error": "生图服务返回错误（{}）：{}".format(exc.code, detail)}, 502)
        except (URLError, TimeoutError) as exc:
            return self.send_json({"error": "无法连接生图服务：{}".format(exc)}, 502)
        images = result.get("data") or []
        if not images:
            return self.send_json({"error": "生图服务没有返回图片"}, 502)
        image = images[0]
        if image.get("b64_json"):
            encoded = image["b64_json"]
        elif image.get("url"):
            with urlopen(image["url"], timeout=60) as response:
                encoded = base64.b64encode(response.read()).decode("ascii")
        else:
            return self.send_json({"error": "生图服务返回格式不受支持"}, 502)
        return self.send_json({"image": "data:image/png;base64," + encoded})

    def export_images(self, body: dict) -> None:
        pages = body.get("pages")
        if not isinstance(pages, list) or not pages or len(pages) > 30:
            raise ValueError("导出图片数量需在 1 到 30 张之间")
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
            for index, page in enumerate(pages, 1):
                name = re.sub(r"[^\w\-\u4e00-\u9fff]", "_", str(page.get("name", "图片")))[:40] or "图片"
                data_url = str(page.get("data", ""))
                if not data_url.startswith("data:image/png;base64,"):
                    raise ValueError("图片数据格式不正确")
                archive.writestr("{:02d}_{}.png".format(index, name), base64.b64decode(data_url.split(",", 1)[1]))
        blob = output.getvalue()
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Disposition", "attachment; filename*=UTF-8''xiaohongshu-images.zip")
        self.send_header("Content-Length", str(len(blob)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(blob)

    def log_message(self, fmt: str, *args: object) -> None:
        if args and str(args[0]).startswith(("/api", "\"/api")):
            return
        super().log_message(fmt, *args)


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print("鹅懂个啥小红书图片工坊：http://{}:{}/".format(HOST, PORT))
    print("仅监听本机；按 Ctrl+C 停止。")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
