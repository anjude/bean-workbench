"""验证续接事件、首轮分叉、最小消息、去重和失败恢复；不创建真实会话。"""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "continue_session", Path(__file__).resolve().parents[1] / "continue-session.py"
)
flow = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(flow)


class FakeProxy:
    def __init__(self):
        self.calls = []
        self.first_statuses = ["completed"]
        self.bootstrap_statuses = ["completed"]
        self.standalone = False
        self.fail_method = None

    def request(self, method, params):
        self.calls.append((method, params))
        if method == self.fail_method:
            raise RuntimeError("simulated request failure")
        if method == "thread/turns/list":
            if params["threadId"] == "new-session":
                status = self.bootstrap_statuses.pop(0) if len(self.bootstrap_statuses) > 1 else self.bootstrap_statuses[0]
                return {"data": [{"id": "seed", "status": status}]}
            if params["sortDirection"] == "asc":
                status = self.first_statuses.pop(0) if len(self.first_statuses) > 1 else self.first_statuses[0]
                return {"data": [{"id": "first", "status": status}]}
            return {"data": [{"id": "current", "status": "inProgress"}]}
        if method == "thread/fork":
            return {"thread": {"id": "new-session"}}
        if method == "thread/read":
            return {"thread": {"name": "工作台维护"}}
        if method == "thread/items/list":
            return {"data": [
                {"type": "userMessage", "content": [{"text": "调整钩子规则"}]},
                {"type": "agentMessage", "text": "不应复制的最新进展"},
            ]}
        if method == "thread/list":
            return {"data": [{"name": "工作台维护-调整钩子规则-02"}]}
        return {}

    def close(self):
        pass


class ContinuationTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"CODEX_HOME": self.folder.name})
        self.env.start()
        self.proxy = FakeProxy()

    def tearDown(self):
        self.env.stop()
        self.folder.cleanup()

    def run_event(self, event, request=None):
        output = io.StringIO()
        with patch.object(flow.sys, "argv", ["continue-session.py"]), \
             patch.object(flow, "read_event", return_value=event), \
             patch.object(flow, "request_continuation", request or unittest.mock.Mock()) as invoke, \
             contextlib.redirect_stdout(output):
            self.assertEqual(flow.main(), 0)
        return output.getvalue(), invoke

    def test_first_precompact_starts_without_a_counter_and_allows_old_turn(self):
        event = {"session_id": "old", "hook_event_name": "PreCompact", "cwd": "/repo"}
        output, invoke = self.run_event(event)
        self.assertEqual(json.loads(output), {"continue": True})
        invoke.assert_called_once_with("old", "/repo", "pre_compact")

    def test_hook_error_does_not_stop_compaction(self):
        output, _ = self.run_event(
            {"session_id": "old", "hook_event_name": "PreCompact"},
            unittest.mock.Mock(side_effect=RuntimeError("failed")),
        )
        self.assertTrue(json.loads(output)["continue"])

    def test_postcompact_has_no_side_effect(self):
        output, invoke = self.run_event({"session_id": "old", "hook_event_name": "PostCompact"})
        self.assertEqual(output, "")
        invoke.assert_not_called()

    def test_busy_worker_lock_does_not_block_the_hook(self):
        path = flow.state_path("old")
        with path.with_suffix(".lock").open("a") as lock:
            flow.fcntl.flock(lock.fileno(), flow.fcntl.LOCK_EX)
            with patch.object(flow, "start_worker") as start:
                result = flow.request_continuation("old", "/repo", "pre_compact")
                self.assertEqual(result["status"], "pending")
                start.assert_not_called()

    def test_repeated_auto_and_manual_requests_share_one_child(self):
        with patch.object(flow, "start_worker", return_value=True) as start:
            flow.request_continuation("old", "/repo", "pre_compact")
            result = flow.request_continuation("old", "/repo", "manual")
            self.assertEqual(result["status"], "pending")
            start.assert_called_once()
        flow.save_state(flow.state_path("old"), {"forked_thread_id": "new", "context_seeded": True})
        with patch.object(flow, "start_worker") as start:
            self.assertEqual(flow.request_continuation("old", "/repo", "manual")["forked_thread_id"], "new")
            start.assert_not_called()

    def test_fork_uses_first_turn_while_current_turn_is_running(self):
        path = flow.state_path("old")
        state = {}
        with patch.object(flow, "AppServerProxy", return_value=self.proxy):
            flow.make_branch("old", "/repo", state, path)
        fork = next(p for m, p in self.proxy.calls if m == "thread/fork")
        self.assertEqual(fork["lastTurnId"], "first")
        seed = next(p for m, p in self.proxy.calls if m == "turn/start")
        self.assertEqual(seed["input"], [{"type": "text", "text": flow.continuation_prompt("old")}])
        self.assertNotIn("不应复制", seed["input"][0]["text"])
        self.assertNotIn("调整钩子规则", seed["input"][0]["text"])
        self.assertNotIn("/repo", seed["input"][0]["text"])
        self.assertEqual(state["new_thread_name"], "工作台维护-调整钩子规则-03")

    def test_only_first_turn_may_require_waiting(self):
        self.proxy.first_statuses = ["inProgress", "completed"]
        with patch.object(flow, "AppServerProxy", return_value=self.proxy), patch.object(flow.time, "sleep") as sleep:
            flow.make_branch("old", "/repo", {}, flow.state_path("old"))
        sleep.assert_called_once_with(flow.POLL_SECONDS)

    def test_name_failure_resumes_existing_child_instead_of_forking_again(self):
        self.proxy.fail_method = "thread/name/set"
        with patch.object(flow, "AppServerProxy", return_value=self.proxy):
            self.assertEqual(flow.worker("old", "/repo"), 1)
            self.proxy.fail_method = None
            self.assertEqual(flow.worker("old", "/repo"), 0)
        self.assertEqual(sum(m == "thread/fork" for m, _ in self.proxy.calls), 1)
        self.assertTrue(flow.load_state(flow.state_path("old"))["context_seeded"])

    def test_uncertain_seed_does_not_resend_or_create_another_child(self):
        self.proxy.fail_method = "turn/start"
        with patch.object(flow, "AppServerProxy", return_value=self.proxy):
            self.assertEqual(flow.worker("old", "/repo"), 1)
        with patch.object(flow, "start_worker") as start:
            result = flow.request_continuation("old", "/repo", "manual")
            self.assertEqual(result["status"], "needs_review")
            self.assertEqual(result["forked_thread_id"], "new-session")
            start.assert_not_called()

    def test_private_server_stays_alive_until_bootstrap_finishes(self):
        self.proxy.standalone = True
        self.proxy.bootstrap_statuses = ["inProgress", "completed"]
        state = {}
        with patch.object(flow, "AppServerProxy", return_value=self.proxy), patch.object(flow.time, "sleep") as sleep:
            flow.make_branch("old", "/repo", state, flow.state_path("old"))
        sleep.assert_called_once_with(flow.POLL_SECONDS)
        self.assertEqual(state["bootstrap_status"], "completed")

    def test_failed_private_bootstrap_is_reported_without_duplicate_seed(self):
        self.proxy.standalone = True
        self.proxy.bootstrap_statuses = ["failed"]
        with patch.object(flow, "AppServerProxy", return_value=self.proxy):
            self.assertEqual(flow.worker("old", "/repo"), 1)
        result = flow.request_continuation("old", "/repo", "manual")
        self.assertEqual(result["status"], "needs_review")
        self.assertEqual(result["bootstrap_status"], "failed")
        self.assertEqual(sum(m == "turn/start" for m, _ in self.proxy.calls), 1)

    def test_manual_cli_uses_same_flow(self):
        with patch.object(flow.sys, "argv", ["script", "--manual", "--session-id", "old", "--cwd", "/repo"]), \
             patch.object(flow, "request_continuation", return_value={"status": "pending"}) as invoke, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(flow.main(), 0)
        invoke.assert_called_once_with("old", "/repo", "manual")


if __name__ == "__main__":
    unittest.main()
