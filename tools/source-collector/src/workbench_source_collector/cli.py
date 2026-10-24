import argparse
import json
import sys

from .sources import parse_source
from .core import collect_job
from .importer import import_zip
from .server import serve
from .storage import Store


def main():
    parser = argparse.ArgumentParser(prog="hr-source", description="工作台来源采集工具")
    sub = parser.add_subparsers(dest="command")
    collect = sub.add_parser("collect", help="采集 B 站或 YouTube 视频字幕")
    collect.add_argument("url", help="视频链接或平台视频 ID")
    collect.add_argument("--retry", action="store_true", help="重试该来源的失败或受限任务")
    collect.add_argument("--platform", choices=["bilibili", "youtube"])
    from . import transcribe
    collect.add_argument("--model", default=None,
                         help="无平台字幕时使用的 ASR 模型；默认 Qwen3-ASR")
    collect.add_argument("--language", choices=["Chinese", "English"], default=None, help="ASR 语言提示；默认由模型自动判断")
    models = sub.add_parser("models", help="查看、下载与校验本机 ASR/时间轴模型")
    models.add_argument("action", choices=["list", "download"])
    models.add_argument("model_id", nargs="?")
    sub.add_parser("jobs", help="查看本机采集任务")
    migrate = sub.add_parser("migrate-legacy", help="显式迁移旧 beannote 采集数据，保留旧目录")
    migrate.add_argument("--from-dir", required=True)
    retry = sub.add_parser("retry", help="重试失败或缺少本地转写依赖的任务")
    retry.add_argument("job_id")
    import_parser = sub.add_parser("import-zip", help="导入 Chrome 插件导出的来源 ZIP")
    import_parser.add_argument("zip_path", help="插件下载的来源 ZIP")
    web = sub.add_parser("serve", help="启动本机采集工作台网页")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.command == "serve":
        serve(args.host, args.port)
        return
    if args.command == "migrate-legacy":
        from .migration import migrate_legacy
        print(json.dumps(migrate_legacy(args.from_dir), ensure_ascii=False, indent=2))
        return
    if args.command == "models":
        if args.action == "list":
            print(json.dumps(transcribe.list_models(), ensure_ascii=False, indent=2))
        elif not args.model_id:
            parser.error("models download 需要提供模型 ID")
        else:
            print(json.dumps({"model": args.model_id, "path": str(transcribe.download_model(args.model_id)),
                              "verified": transcribe.verify_model(args.model_id)}, ensure_ascii=False, indent=2))
        return
    store = Store()
    if args.command == "collect":
        platform, bvid, page = parse_source(args.url, args.platform)
        model_id = transcribe.resolve_model(args.model)[0] if args.model else None
        job, started = store.start_or_reuse_job(bvid, page, args.url, platform=platform, model_id=model_id,
                                                 requested_language=args.language)
        if not started:
            print(json.dumps({"error": "采集任务正在执行", "job": job}, ensure_ascii=False, indent=2), file=sys.stderr)
            raise SystemExit(1)
        result = collect_job(store, job["id"], model=model_id)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if result["status"] in ("failed", "transcription_unavailable", "login_required"):
            raise SystemExit(1)
    elif args.command == "jobs":
        print(json.dumps(store.list(), ensure_ascii=False, indent=2))
    elif args.command == "retry":
        job = store.retry(args.job_id)
        if not job:
            parser.error("任务不存在，或当前状态不支持重试")
        print(json.dumps(collect_job(store, args.job_id, model=job.get("model_id")), ensure_ascii=False, indent=2))
    elif args.command == "import-zip":
        print(json.dumps(import_zip(args.zip_path, store=store), ensure_ascii=False, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
