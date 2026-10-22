#!/usr/bin/env python3
"""公众号 API 工具。标准库实现；凭证和 token 保存在 Git 忽略的本地配置目录。"""
import argparse
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

API_BASE = 'https://api.weixin.qq.com/cgi-bin'
LOCAL_CONFIG = Path(__file__).resolve().parents[3] / 'local-config' / 'wechat'


def load_creds():
    appid, secret = os.getenv('WECHAT_APPID'), os.getenv('WECHAT_APPSECRET')
    if appid and secret:
        return appid, secret
    if appid or secret:
        raise ValueError('WECHAT_APPID 与 WECHAT_APPSECRET 必须同时配置')
    path = Path(os.getenv('WECHAT_KEY_FILE', str(LOCAL_CONFIG / 'credentials'))).expanduser()
    if path.stat().st_mode & 0o077:
        raise ValueError('凭证文件权限过宽，请设置 chmod 600')
    lines = [s.strip() for s in path.read_text().splitlines() if s.strip()]
    if len(lines) != 2:
        raise ValueError('凭证文件须为两行：AppID、AppSecret')
    return tuple(lines)


def private_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    tmp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as out:
            json.dump(data, out, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def request(url, payload=None, headers=None):
    req = urllib.request.Request(url, data=payload, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.load(response)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f'微信 HTTP {exc.code}；请求未自动重试') from None
    except (urllib.error.URLError, TimeoutError):
        raise RuntimeError('网络请求失败或超时；写操作结果可能未知，请先查后台，勿直接重试') from None
    if data.get('errcode', 0):
        raise RuntimeError(f"微信错误 {data['errcode']}：{data.get('errmsg', '')}")
    return data


def get_token(force=False):
    appid, secret = load_creds()
    cache_dir = LOCAL_CONFIG / 'token-cache'
    cache = cache_dir / (hashlib.sha256(appid.encode()).hexdigest()[:16] + '.json')
    if cache.exists() and not force:
        try:
            data = json.loads(cache.read_text())
            if time.time() < data['expires_at'] - 300 and not cache.stat().st_mode & 0o077:
                return data['access_token']
        except (ValueError, KeyError):
            pass
    params = urllib.parse.urlencode({'grant_type': 'client_credential', 'appid': appid, 'secret': secret})
    data = request(API_BASE + '/token?' + params)
    if 'access_token' not in data:
        raise RuntimeError('微信未返回 access_token')
    data['expires_at'] = time.time() + data.get('expires_in', 7200)
    private_json(cache, data)
    return data['access_token']


def api(endpoint, payload):
    url = API_BASE + '/' + endpoint + '?' + urllib.parse.urlencode({'access_token': get_token()})
    return request(url, json.dumps(payload, ensure_ascii=False).encode(), {'Content-Type': 'application/json'})


def upload(path, kind):
    path = Path(path)
    boundary = uuid.uuid4().hex
    # 固定 ASCII 文件名，避免 multipart 头注入及非 ASCII 文件名兼容问题。
    filename = 'image' + path.suffix.lower()
    mime = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
    if not mime.startswith('image/'):
        raise ValueError('上传文件必须是图片')
    body = (f'--{boundary}\r\nContent-Disposition: form-data; name="media"; filename="{filename}"\r\n'
            f'Content-Type: {mime}\r\n\r\n').encode() + path.read_bytes() + f'\r\n--{boundary}--\r\n'.encode()
    endpoint = 'material/add_material' if kind == 'cover' else 'media/uploadimg'
    params = {'access_token': get_token()}
    if kind == 'cover':
        params['type'] = 'image'
    data = request(API_BASE + '/' + endpoint + '?' + urllib.parse.urlencode(params), body,
                   {'Content-Type': 'multipart/form-data; boundary=' + boundary})
    if ('media_id' if kind == 'cover' else 'url') not in data:
        raise RuntimeError('微信未返回预期的素材 ID 或图片 URL')
    return data


def recorded_write(endpoint, payload, receipt, dry_run=False):
    fingerprint = hashlib.sha256(json.dumps([endpoint, payload], ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    if dry_run:
        return {'dry_run': True, 'endpoint': endpoint, 'payload': payload, 'fingerprint': fingerprint}
    receipt = Path(receipt)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    # 发请求前占用凭据文件；超时或进程中断后阻止自动重复写入。
    try:
        with receipt.open('x') as out:
            json.dump({'state': 'pending', 'endpoint': endpoint, 'fingerprint': fingerprint}, out)
    except FileExistsError:
        raise ValueError('回执已存在；先核对回执和公众号后台，禁止盲目重复提交') from None
    data = api(endpoint, payload)
    private_json(receipt, {'state': 'accepted', 'endpoint': endpoint, 'fingerprint': fingerprint,
                           'time': time.strftime('%Y-%m-%dT%H:%M:%S%z'), 'response': data})
    return data


def build_draft_article(title, author, content, digest, thumb_media_id,
                        need_open_comment=1, only_fans_can_comment=0):
    """构造标准图文草稿字段；微信接口的开关字段使用 0/1 数值。"""
    return {
        'title': title,
        'author': author,
        'content': content,
        'digest': digest,
        'thumb_media_id': thumb_media_id,
        'need_open_comment': need_open_comment,
        'only_fans_can_comment': only_fans_can_comment,
    }


def main():
    parser = argparse.ArgumentParser(description='公众号素材、草稿和发布工具')
    sub = parser.add_subparsers(dest='cmd', required=True)
    sub.add_parser('token', help='验证凭证并缓存 token；不打印 token')
    p = sub.add_parser('upload', help='上传封面或正文图片')
    p.add_argument('image')
    p.add_argument('--kind', choices=['cover', 'body'], default='cover')
    p = sub.add_parser('draft', help='新增草稿')
    p.add_argument('--title', required=True)
    p.add_argument('--author', default='豆小匠')
    p.add_argument('--content-file', required=True)
    p.add_argument('--digest', required=True, help='有吸引力的导读文案，不要求复述全文')
    p.add_argument('--thumb-media-id', required=True)
    p.add_argument('--need-open-comment', type=int, choices=(0, 1), default=1,
                   help='是否开启评论：1 开启，0 关闭（默认：1）')
    p.add_argument('--only-fans-can-comment', type=int, choices=(0, 1), default=0,
                   help='是否仅粉丝可评论：1 是，0 否（默认：0）')
    p.add_argument('--receipt', required=True, help='主题 publish/ 内的 JSON 回执路径')
    p.add_argument('--dry-run', action='store_true')
    p = sub.add_parser('draft-update', help='更新已有草稿中的单篇文章')
    p.add_argument('--media-id', required=True, help='已有草稿 media_id')
    p.add_argument('--index', type=int, default=0, help='草稿中的文章序号，从 0 开始')
    p.add_argument('--title', required=True)
    p.add_argument('--author', default='豆小匠')
    p.add_argument('--content-file', required=True)
    p.add_argument('--digest', required=True, help='有吸引力的导读文案，不要求复述全文')
    p.add_argument('--thumb-media-id', required=True)
    p.add_argument('--need-open-comment', type=int, choices=(0, 1), default=1,
                   help='是否开启评论：1 开启，0 关闭（默认：1）')
    p.add_argument('--only-fans-can-comment', type=int, choices=(0, 1), default=0,
                   help='是否仅粉丝可评论：1 是，0 否（默认：0）')
    p.add_argument('--receipt', required=True, help='使用新的主题 publish/ 回执路径')
    p.add_argument('--dry-run', action='store_true')
    p = sub.add_parser('draft-get', help='获取已有草稿详情')
    p.add_argument('--media-id', required=True)
    p = sub.add_parser('publish', help='提交发布；须已有用户发布授权')
    p.add_argument('--media-id', required=True)
    p.add_argument('--receipt', required=True)
    p.add_argument('--dry-run', action='store_true')
    p = sub.add_parser('status', help='查询异步发布结果')
    p.add_argument('--publish-id', required=True)
    args = parser.parse_args()
    if args.cmd == 'token':
        get_token()
        result = {'ok': True, 'message': '凭证有效，token 已缓存（未显示）'}
    elif args.cmd == 'upload':
        result = upload(args.image, args.kind)
    elif args.cmd == 'status':
        result = api('freepublish/get', {'publish_id': args.publish_id})
    elif args.cmd == 'draft-get':
        result = api('draft/get', {'media_id': args.media_id})
    elif args.cmd == 'publish':
        result = recorded_write('freepublish/submit', {'media_id': args.media_id}, args.receipt, args.dry_run)
    elif args.cmd in ('draft', 'draft-update'):
        content = Path(args.content_file).read_text()
        if not content.strip() or not args.thumb_media_id.strip() or not args.title.strip():
            raise ValueError('标题、正文、封面 ID 不能为空')
        if not args.digest.strip():
            raise ValueError('摘要不能为空；请提供有吸引力的导读文案')
        if args.only_fans_can_comment and not args.need_open_comment:
            raise ValueError('仅粉丝可评论必须先开启评论')
        article = build_draft_article(
            args.title, args.author, content, args.digest, args.thumb_media_id,
            args.need_open_comment, args.only_fans_can_comment)
        if args.cmd == 'draft-update':
            payload = {'media_id': args.media_id, 'index': args.index, 'articles': article}
            result = recorded_write('draft/update', payload, args.receipt, args.dry_run)
        else:
            result = recorded_write('draft/add', {'articles': [article]}, args.receipt, args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, RuntimeError) as exc:
        # 不打印请求 URL 或 traceback，避免把 token 和 AppSecret 带入日志。
        message = str(exc) if isinstance(exc, (ValueError, RuntimeError)) else f'本地文件操作失败：{exc.__class__.__name__}'
        raise SystemExit(message)
