#!/usr/bin/env python3
"""首次压缩前或手动请求时，从首轮末尾创建续接会话；旧会话继续运行。"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

POLL_SECONDS = 2
MAX_WAIT_SECONDS = 1800


def read_event() -> dict[str, Any]:
    try:
        value = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return {}
    return value if isinstance(value, dict) else {}


def state_path(session_id: str) -> Path:
    root = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    folder = root / "state" / "session-continuation"
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(folder, 0o700)
    return folder / f"{session_id}.json"


def load_state(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_state(path: Path, state: dict[str, Any]) -> None:
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    os.chmod(temporary, 0o600)
    temporary.replace(path)


class AppServerProxy:
    def __init__(self) -> None:
        cli = os.environ.get("CODEX_APP_RUNTIME_CLI_PATH") or shutil.which("codex")
        if not cli:
            raise RuntimeError("codex executable is unavailable in the hook environment")
        root = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
        shared_socket = root / "app-server-control" / "app-server-control.sock"
        modes = [False, True] if shared_socket.exists() else [True]
        for standalone in modes:
            self.standalone = standalone
            command = [cli, "app-server", "--listen", "stdio://"] if standalone else [cli, "app-server", "proxy"]
            self.process = subprocess.Popen(
                command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, text=True, encoding="utf-8", bufsize=1,
            )
            assert self.process.stdin is not None and self.process.stdout is not None
            self.stdin, self.stdout = self.process.stdin, self.process.stdout
            self.seq = 0
            try:
                self.request("initialize", {
                    "clientInfo": {"name": "session_continuation_hook", "title": "Session Continuation Hook", "version": "3.0.0"},
                    "capabilities": {"experimentalApi": True},
                })
                self.notify("initialized", {})
                return
            except Exception:
                self.close()
                if standalone:
                    raise

    def notify(self, method: str, params: dict[str, Any]) -> None:
        self.stdin.write(json.dumps({"method": method, "params": params}) + "\n")
        self.stdin.flush()

    def request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        self.seq += 1
        ident = self.seq
        self.stdin.write(json.dumps({"id": ident, "method": method, "params": params}) + "\n")
        self.stdin.flush()
        for line in self.stdout:
            try:
                response = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(response, dict) and response.get("id") == ident:
                if "error" in response:
                    raise RuntimeError(f"app-server request failed: {method}")
                return response.get("result", {})
        raise RuntimeError(f"app-server ended before replying to {method}")

    def close(self) -> None:
        try:
            self.stdin.close()
            self.process.wait(timeout=2)
        except (OSError, subprocess.TimeoutExpired):
            self.process.terminate()


def text_from_item(item: dict[str, Any]) -> str:
    content = item.get("content")
    if isinstance(content, list):
        return "\n".join(str(part.get("text", "")) for part in content if isinstance(part, dict))
    for key in ("text", "message", "summary"):
        if isinstance(item.get(key), str):
            return item[key]
    return ""


def compact_title(text: str, fallback: str) -> str:
    value = re.sub(r"\s+", " ", text).strip()
    value = re.sub(r"[`*_#]", "", value)
    return value[:24].rstrip(" ，。；：、") or fallback


def next_name(proxy: AppServerProxy, task_name: str, summary: str) -> str:
    result = proxy.request("thread/list", {"limit": 100})
    prefix = f"{task_name}-{summary}-"
    numbers = []
    for entry in result.get("data", []):
        name = entry.get("name") or entry.get("title") or ""
        match = re.fullmatch(re.escape(prefix) + r"(\d+)", name)
        if match:
            numbers.append(int(match.group(1)))
    return prefix + f"{max([1, *numbers]) + 1:02d}"


def continuation_prompt(session_id: str) -> str:
    # 只传旧 ID 与读取 handoff 的指令，不附带近期请求、答复或工作目录等上下文。
    return f"老会话 ID：{session_id}\n请按 wb-handoff 的会话续接规则，读取对应任务最新的 handoff 文件。"


def recent_summary(proxy: AppServerProxy, session_id: str) -> str:
    """近期请求仅用于保留命名习惯，不写入新会话的消息。"""
    try:
        turns = proxy.request("thread/turns/list", {
            "threadId": session_id, "limit": 1, "sortDirection": "desc"
        }).get("data", [])
        if not turns or not turns[0].get("id"):
            return "续接"
        items = proxy.request("thread/items/list", {
            "threadId": session_id, "turnId": turns[0]["id"], "limit": 1000
        }).get("data", [])
        for item in reversed(items):
            role = str(item.get("type", item.get("role", ""))).lower()
            if role in {"user_message", "usermessage", "user", "input"}:
                value = text_from_item(item)
                if value:
                    return compact_title(value, "续接")
    except RuntimeError:
        pass
    return "续接"


def make_branch(session_id: str, cwd: str, state: dict[str, Any], path: Path) -> str:
    proxy = AppServerProxy()
    try:
        new_id = state.get("forked_thread_id")
        if not new_id:
            deadline = time.monotonic() + MAX_WAIT_SECONDS
            while True:
                first = proxy.request("thread/turns/list", {
                    "threadId": session_id, "limit": 1, "sortDirection": "asc"
                }).get("data", [])
                # 首轮已结束即可分叉，不等待当前轮结束，也不阻断当前轮。
                if first and first[0].get("id") and first[0].get("status") in {"completed", "interrupted", "failed"}:
                    first_turn_id = first[0]["id"]
                    break
                if time.monotonic() >= deadline:
                    raise RuntimeError("first turn did not finish before timeout")
                time.sleep(POLL_SECONDS)
            fork = proxy.request("thread/fork", {
                "threadId": session_id, "lastTurnId": first_turn_id, "cwd": cwd
            })
            new_id = fork.get("thread", {}).get("id")
            if not new_id:
                raise RuntimeError("fork did not return a thread id")
            # 先持久化子会话 ID；改名或启动失败时复用，避免重复分叉。
            state["forked_thread_id"] = new_id
            save_state(path, state)

        if not state.get("new_thread_name"):
            old_thread = proxy.request("thread/read", {"threadId": session_id}).get("thread", {})
            task_name = compact_title(str(old_thread.get("name") or old_thread.get("title") or "任务"), "任务")
            name = next_name(proxy, task_name, recent_summary(proxy, session_id))
            proxy.request("thread/name/set", {"threadId": new_id, "name": name})
            state["new_thread_name"] = name
            save_state(path, state)

        if not state.get("seed_attempted"):
            # 启动结果不明时不自动重发消息；--status 会明确暴露待核状态。
            state["seed_attempted"] = True
            save_state(path, state)
            result = proxy.request("turn/start", {
                "threadId": new_id, "cwd": cwd,
                "input": [{"type": "text", "text": continuation_prompt(session_id)}],
            })
            state["seed_turn_id"] = result.get("turn", {}).get("id")
            state["context_seeded"] = True
            save_state(path, state)
        elif not state.get("context_seeded"):
            raise RuntimeError("continuation turn outcome is unknown; inspect the existing child before retrying")
        if getattr(proxy, "standalone", False):
            wait_for_bootstrap(proxy, str(new_id), state, path)
        return str(new_id)
    finally:
        proxy.close()


def wait_for_bootstrap(proxy: AppServerProxy, new_id: str, state: dict[str, Any], path: Path) -> None:
    """独立服务不能在 turn/start 后立即退出，否则接手、置顶等操作会被中止。"""
    deadline = time.monotonic() + MAX_WAIT_SECONDS
    while time.monotonic() < deadline:
        turns = proxy.request("thread/turns/list", {
            "threadId": new_id, "limit": 1, "sortDirection": "desc"
        }).get("data", [])
        if turns and (not state.get("seed_turn_id") or turns[0].get("id") == state["seed_turn_id"]):
            status = turns[0].get("status")
            if status in {"completed", "interrupted", "failed"}:
                state["bootstrap_status"] = status
                save_state(path, state)
                if status != "completed":
                    raise RuntimeError(f"new session bootstrap ended with status: {status}")
                return
        time.sleep(POLL_SECONDS)
    raise RuntimeError("new session bootstrap did not finish before timeout")


def worker(session_id: str, cwd: str) -> int:
    path = state_path(session_id)
    with path.with_suffix(".lock").open("a", encoding="utf-8") as lock_file:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        state = load_state(path)
        if state.get("context_seeded"):
            return 0
        try:
            new_id = make_branch(session_id, cwd, state, path)
            state.pop("worker_error", None)
            print(f"新会话已创建：{state.get('new_thread_name')} ({new_id})")
            return 0
        except Exception as error:
            state["worker_error"] = str(error)
            return 1
        finally:
            state["continuation_started"] = False
            save_state(path, state)


def start_worker(session_id: str, cwd: str) -> bool:
    log = state_path(session_id).with_suffix(".log")
    with log.open("a", encoding="utf-8") as output:
        os.chmod(log, 0o600)
        process = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--worker", session_id, cwd],
            stdin=subprocess.DEVNULL, stdout=output, stderr=output,
            start_new_session=True, close_fds=True,
        )
    return process.pid > 0


def request_continuation(session_id: str, cwd: str, trigger: str) -> dict[str, Any]:
    path = state_path(session_id)
    with path.with_suffix(".lock").open("a", encoding="utf-8") as lock_file:
        os.chmod(path.with_suffix(".lock"), 0o600)
        try:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return {"status": "pending", "state_file": str(path)}
        state = load_state(path)
        if state.get("context_seeded"):
            return {"status": "needs_review" if state.get("worker_error") else "ready", **state}
        if state.get("continuation_started"):
            return {"status": "pending", **state}
        if state.get("seed_attempted") and not state.get("context_seeded"):
            return {"status": "needs_review", **state}
        state.update({"source_thread_id": session_id, "cwd": cwd, "trigger": trigger,
                      "continuation_started": True})
        state.pop("worker_error", None)
        save_state(path, state)
        try:
            if not start_worker(session_id, cwd):
                raise RuntimeError("background worker did not start")
        except Exception as error:
            state.update({"continuation_started": False, "worker_error": str(error)})
            save_state(path, state)
            return {"status": "failed", **state}
        return {"status": "pending", "state_file": str(path)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", nargs=2, metavar=("SESSION_ID", "CWD"))
    parser.add_argument("--manual", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--session-id", default=os.environ.get("CODEX_THREAD_ID"))
    parser.add_argument("--cwd", default=os.getcwd())
    args = parser.parse_args()
    if args.worker:
        return worker(*args.worker)
    if args.manual or args.status:
        if not args.session_id:
            parser.error("manual/status mode requires --session-id or CODEX_THREAD_ID")
        if args.manual:
            result = request_continuation(args.session_id, args.cwd, "manual")
        else:
            state = load_state(state_path(args.session_id))
            status = ("needs_review" if state.get("context_seeded") and state.get("worker_error") else
                      "ready" if state.get("context_seeded") else
                      "pending" if state.get("continuation_started") else
                      "needs_review" if state.get("seed_attempted") else
                      "failed" if state.get("worker_error") else "not_started")
            result = {"status": status, **state}
        print(json.dumps(result, ensure_ascii=False))
        return 0

    event = read_event()
    session_id = event.get("session_id")
    if event.get("hook_event_name") != "PreCompact" or not isinstance(session_id, str) or not session_id:
        return 0
    try:
        cwd = event.get("cwd") if isinstance(event.get("cwd"), str) else os.getcwd()
        request_continuation(session_id, cwd, "pre_compact")
    except Exception:
        # 钩子失败也不阻断旧会话；后台详细状态见 state/log。
        pass
    print(json.dumps({"continue": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
