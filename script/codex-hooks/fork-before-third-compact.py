#!/usr/bin/env python3
"""Stop before the third compaction, then fork and seed a continuation thread."""

from __future__ import annotations

import fcntl
import json
import os
import re
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
    folder = root / "state" / "compact-fork"
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
        self.process = subprocess.Popen(
            ["codex", "app-server", "proxy"], stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
            encoding="utf-8", bufsize=1,
        )
        assert self.process.stdin is not None and self.process.stdout is not None
        self.stdin, self.stdout = self.process.stdin, self.process.stdout
        self.seq = 0
        result = self.request("initialize", {"clientInfo": {
            "name": "compact_fork_hook", "title": "Compact Fork Hook", "version": "2.0.0"
        }})
        if "error" in result:
            self.close()
            raise RuntimeError("app-server initialization failed")
        self.notify("initialized", {})

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


def thread_items(proxy: AppServerProxy, session_id: str, turn_id: str) -> list[dict[str, Any]]:
    result = proxy.request("thread/items/list", {"threadId": session_id, "turnId": turn_id, "limit": 1000})
    data = result.get("data", [])
    return [item for item in data if isinstance(item, dict)]


def compact_title(text: str, fallback: str) -> str:
    value = re.sub(r"\s+", " ", text).strip()
    value = re.sub(r"[`*_#]", "", value)
    value = value[:24].rstrip(" ，。；：、")
    return value or fallback


def next_name(proxy: AppServerProxy, task_name: str, summary: str) -> str:
    result = proxy.request("thread/list", {"limit": 100})
    threads = result.get("data", [])
    prefix = f"{task_name}-{summary}-"
    numbers = []
    for entry in threads:
        name = entry.get("name") or entry.get("title") or ""
        match = re.fullmatch(re.escape(prefix) + r"(\d+)", name)
        if match:
            numbers.append(int(match.group(1)))
    return prefix + f"{max([1, *numbers]) + 1:02d}"


def latest_turns(proxy: AppServerProxy, session_id: str) -> list[dict[str, Any]]:
    return proxy.request("thread/turns/list", {
        "threadId": session_id, "limit": 1, "sortDirection": "desc", "itemsView": "full"
    }).get("data", [])


def make_branch(session_id: str, cwd: str, event: dict[str, Any], state: dict[str, Any]) -> str:
    proxy = AppServerProxy()
    try:
        deadline = time.monotonic() + MAX_WAIT_SECONDS
        newest: dict[str, Any] = {}
        while time.monotonic() < deadline:
            turns = latest_turns(proxy, session_id)
            if turns:
                newest = turns[0]
                if newest.get("status") in {"completed", "interrupted", "failed"}:
                    break
            time.sleep(POLL_SECONDS)
        else:
            raise RuntimeError("old turn did not finish before timeout")

        first = proxy.request("thread/turns/list", {
            "threadId": session_id, "limit": 1, "sortDirection": "asc"
        }).get("data", [])
        if not first or not first[0].get("id"):
            raise RuntimeError("first turn is unavailable")
        first_turn_id = first[0]["id"]
        fork = proxy.request("thread/fork", {"threadId": session_id, "lastTurnId": first_turn_id, "cwd": cwd})
        new_id = fork.get("thread", {}).get("id")
        if not new_id:
            raise RuntimeError("fork did not return a thread id")

        items = thread_items(proxy, session_id, newest.get("id", "")) if newest.get("id") else []
        user_text = ""
        assistant_text = ""
        for item in items:
            role = str(item.get("type", item.get("role", ""))).lower()
            value = text_from_item(item)
            if role in {"user_message", "usermessage", "user", "input"} and value:
                user_text = value
            elif role in {"agent_message", "agentmessage", "assistant", "assistant_message"} and value:
                assistant_text = value
        recent_request = user_text or str(event.get("last_user_message", "(请从旧会话最近内容确认)"))
        progress = assistant_text or str(state.get("latest_progress", "(旧会话最近可见进展未能从 app-server 读取)"))
        old_meta = proxy.request("thread/read", {"threadId": session_id})
        old_thread = old_meta.get("thread", {})
        old_title = str(old_thread.get("name") or old_thread.get("title") or state.get("task_name", "任务"))
        task_name = compact_title(old_title, "任务")
        summary = compact_title(recent_request, "续接")
        name = next_name(proxy, task_name, summary)
        proxy.request("thread/name/set", {"threadId": new_id, "name": name})
        handoff = (
            "自动续接上下文：\n"
            f"- 老会话 ID：{session_id}\n- 工作目录：{cwd}\n"
            f"- 最近用户请求：\n{recent_request}\n"
            f"- 老会话最终答复或最近可见进展：\n{progress}\n"
            "请先读取必要的任务文件和 wb-handoff。若任务正式记录中已有用户对会话续接及"
            "特定定时任务迁移的明确授权，先按记录核对数据，再使用应用的 automation_update 工具"
            "迁移并核验这些任务：只处理仍绑定老会话的已授权 ID，保留时间、状态和其他设置；"
            "已绑定本会话则跳过，绑定第三个会话或更新失败时不要覆盖或声称完成。"
            "不要直接修改自动化配置文件，不迁移未授权任务，不自动归档旧会话。"
            "完成已授权迁移或报告具体失败后，简短确认已接收上下文并等待用户下一条输入；"
            "不要自行重做日报、交易或扩大任务。"
        )
        proxy.request("turn/start", {
            "threadId": new_id, "cwd": cwd,
            "input": [{"type": "text", "text": handoff}],
        })
        state.update({"forked_thread_id": new_id, "new_thread_name": name})
        return new_id
    finally:
        proxy.close()


def worker(session_id: str, cwd: str) -> int:
    path = state_path(session_id)
    lock_path = path.with_suffix(".lock")
    try:
        with lock_path.open("a", encoding="utf-8") as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            state = load_state(path)
            if state.get("forked_thread_id"):
                return 0
            new_id = make_branch(session_id, cwd, state.get("event", {}), state)
            save_state(path, state)
            print(f"新会话已创建并注入续接上下文：{state.get('new_thread_name')} ({new_id})")
        return 0
    except Exception as error:
        with lock_path.open("a", encoding="utf-8") as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            state = load_state(path)
            state["worker_error"] = type(error).__name__
            save_state(path, state)
        return 1


def start_worker(session_id: str, cwd: str) -> bool:
    log = state_path(session_id).with_suffix(".log")
    with log.open("a", encoding="utf-8") as output:
        process = subprocess.Popen(
            [sys.executable, str(Path(__file__).resolve()), "--worker", session_id, cwd],
            stdin=subprocess.DEVNULL, stdout=output, stderr=output,
            start_new_session=True, close_fds=True,
        )
    return process.pid > 0


def main() -> int:
    if len(sys.argv) == 4 and sys.argv[1] == "--worker":
        return worker(sys.argv[2], sys.argv[3])
    event = read_event()
    session_id = event.get("session_id")
    hook = event.get("hook_event_name")
    if not isinstance(session_id, str) or not session_id:
        return 0
    path = state_path(session_id)
    lock_path = path.with_suffix(".lock")
    with lock_path.open("a", encoding="utf-8") as lock_file:
        os.chmod(lock_path, 0o600)
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        state = load_state(path)
        if hook == "PostCompact":
            state["completed_compactions"] = int(state.get("completed_compactions", 0)) + 1
            save_state(path, state)
            return 0
        if hook != "PreCompact" or state.get("forked_thread_id") or state.get("continuation_started"):
            return 0
        if int(state.get("completed_compactions", 0)) < 2:
            return 0
        cwd = event.get("cwd") if isinstance(event.get("cwd"), str) else os.getcwd()
        state.update({"continuation_started": True, "event": event, "cwd": cwd})
        save_state(path, state)
        if not start_worker(session_id, cwd):
            state["continuation_started"] = False
            save_state(path, state)
            return 0
        sys.stdout.write(json.dumps({
            "continue": False,
            "stopReason": "third compaction stopped; background continuation started",
            "systemMessage": "已拦截第三次压缩并停止当前轮。后台续接程序会等待当前轮保存或中断，然后从第一轮分叉、注入最近交接上下文并命名新会话。新会话会等待你的下一条输入；旧会话及工作目录保持不变。",
        }, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
