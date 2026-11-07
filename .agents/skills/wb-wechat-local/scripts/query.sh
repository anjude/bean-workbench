#!/bin/sh
set -u
umask 077

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
WORKBENCH_ROOT=$(CDPATH= cd -- "$SCRIPT_DIR/../../../../" && pwd)
LOCAL_DIR="$WORKBENCH_ROOT/.agents/local-config/wechat-reader"
READER_HOME="$LOCAL_DIR/home"
WX="$LOCAL_DIR/bin/wx"
CACHE_DIR="$READER_HOME/.wx-cli/cache"

case "${1:-}" in
  sessions|contacts|history|search) ;;
  *)
    printf '%s\n' "用法: $0 {sessions|contacts|history|search} [参数...]" >&2
    exit 2
    ;;
esac

if [ ! -x "$WX" ]; then
  printf '%s\n' "本机 wx CLI 不存在: $WX" >&2
  exit 1
fi
if [ ! -f "$LOCAL_DIR/all_keys.json" ]; then
  printf '%s\n' "本机密钥尚未配置。请先完成一次本机密钥提取。" >&2
  exit 1
fi

export HOME="$READER_HOME"
cd "$LOCAL_DIR" || exit 1
mkdir -p "$CACHE_DIR"
chmod 700 "$READER_HOME" "$READER_HOME/.wx-cli" "$CACHE_DIR"

cleanup() {
  "$WX" daemon stop >/dev/null 2>&1 || :
  if "$WX" daemon status 2>&1 | /usr/bin/grep -E '运行中|running' >/dev/null; then
    printf '%s\n' "wx daemon 仍在运行，未删除解密缓存: $CACHE_DIR" >&2
    return 1
  fi
  if [ -d "$CACHE_DIR" ]; then
    /bin/rm -rf -- "$CACHE_DIR" || {
      printf '%s\n' "无法删除解密缓存: $CACHE_DIR" >&2
      return 1
    }
  fi
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

"$WX" "$@"
