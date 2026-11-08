#!/usr/bin/env python3
"""通过后端上传本地图片，输出服务返回的 HTTPS URL。"""
import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[4]
ENDPOINTS = {
    'test': 'https://api.beanflow.top:8080/api/so/common/wx_upload',
    'live': 'https://api.beanflow.top/api/so/common/wx_upload',
}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def image_type(data):
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png', '.png'
    if data.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg', '.jpg'
    if data.startswith((b'GIF87a', b'GIF89a')):
        return 'image/gif', '.gif'
    if len(data) >= 12 and data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return 'image/webp', '.webp'
    raise ValueError('仅支持 PNG、JPEG、GIF、WebP 图片')

def main():
    parser = argparse.ArgumentParser(description='调用后端图片上传接口，输出 JSON 回执')
    parser.add_argument('image', type=pathlib.Path, help='待上传的本地图片路径')
    parser.add_argument('--env', choices=ENDPOINTS, required=True, help='明确选择 test 或 live')
    parser.add_argument('--token-file', type=pathlib.Path, default=ROOT / '.agents/local-config/image-upload/admin.jwt')
    args = parser.parse_args()
    try:
        token = args.token_file.read_text(encoding='utf-8').strip()
        if not token or '\n' in token or '\r' in token:
            raise ValueError('凭证文件为空或格式无效')
        with args.image.open('rb') as f:
            data = f.read(10 * 1024 * 1024 + 1)
        if len(data) > 10 * 1024 * 1024:
            raise ValueError('图片超过本工具 10 MiB 限制')
        mime, extension = image_type(data)
        boundary = 'upload' + uuid.uuid4().hex
        # 后端使用上传名构造临时路径，避免传入本机文件名和路径字符。
        filename = 'image-' + uuid.uuid4().hex + extension
        payload = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\nContent-Type: {mime}\r\n\r\n'.encode() + data + f'\r\n--{boundary}--\r\n'.encode())
        request = urllib.request.Request(ENDPOINTS[args.env], data=payload, headers={
            'Authorization': 'Bearer ' + token, 'Content-Type': 'multipart/form-data; boundary=' + boundary,
        }, method='POST')
        with urllib.request.build_opener(NoRedirect).open(request, timeout=30) as response:
            raw = response.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024:
                raise ValueError('上传响应超过大小限制')
            result = json.loads(raw)
        if not isinstance(result, dict) or not isinstance(result.get('data'), dict):
            raise ValueError('后端响应格式无效或没有图片数据')
        url = result['data'].get('url')
        if result.get('err_code') != 0 or not isinstance(url, str):
            raise ValueError('后端未返回成功及图片 URL，业务码：' + str(result.get('err_code')))
        parsed = urllib.parse.urlsplit(url)
        if parsed.scheme != 'https' or not parsed.hostname:
            raise ValueError('后端返回的图片地址不是有效 HTTPS URL')
        print(json.dumps({'environment': args.env, 'url': url}, ensure_ascii=False))
    except urllib.error.HTTPError as exc:
        print(f'上传失败：HTTP {exc.code}；请核对凭证及目标环境', file=sys.stderr)
        return 1
    except json.JSONDecodeError:
        print('上传失败：后端响应不是有效 JSON', file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f'上传失败：{exc}', file=sys.stderr)
        return 1
    except (OSError, urllib.error.URLError):
        print('上传失败：请检查图片、凭证文件及网络', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
