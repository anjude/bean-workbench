import copy
import json
from pathlib import Path
import tempfile
import unittest

import investment as app


ROOT = Path(__file__).parent / "examples"
NOW = app.instant("2026-10-26T14:05:00+00:00", "now")


class InvestmentTests(unittest.TestCase):
    def setUp(self):
        self.portfolio = app.load(ROOT / "portfolio.json")
        self.market = app.load(ROOT / "market.json")
        self.actions = app.load(ROOT / "candidates.json")

    def test_stock_count_not_duplicated_by_two_options(self):
        result = app.aggregate(self.portfolio, self.market, NOW)
        self.assertEqual(result["symbols"]["DEMO"]["stock_shares"], app.Decimal(100))
        self.assertEqual(result["symbols"]["DEMO"]["stock_value"], app.Decimal(5200))
        self.assertEqual(result["symbols"]["DEMO"]["stock_pnl"], app.Decimal(700))
        self.assertEqual(result["put_gross"], app.Decimal(5000))

    def test_roll_credit_separate_from_old_position_loss(self):
        result = app.analyze_action(self.actions["actions"][2], self.portfolio, NOW)
        self.assertEqual(result["cash_flow"], app.Decimal(98))
        self.assertEqual(result["realized_pnl"], app.Decimal(-102))
        self.assertEqual(result["gross_change"], app.Decimal(-200))
        self.assertEqual(result["portfolio_put_gross_after"], app.Decimal(4800))
        self.assertEqual(result["new_leg_breakeven_before_fees"], app.Decimal(44))
        self.assertEqual(result["expiry_change_days"], 7)

    def test_roll_with_quantity_change_uses_separate_leg_units(self):
        action = copy.deepcopy(self.actions["actions"][2])
        action["new_contract"]["quantity"] = "2"
        result = app.analyze_action(action, self.portfolio, NOW)
        self.assertEqual(result["cash_flow"], app.Decimal(498))
        self.assertEqual(result["gross_change"], app.Decimal(4600))

    def test_missing_premium_and_fees_stay_unknown(self):
        self.portfolio["positions"][1]["entry_premium"] = None
        action = copy.deepcopy(self.actions["actions"][1])
        del action["closing_fees"]
        result = app.analyze_action(action, self.portfolio, NOW)
        self.assertIsNone(result["realized_pnl"])
        self.assertIsNone(result["cash_flow"])
        self.assertEqual(result["cash_flow_before_fees"], app.Decimal(-300))

    def test_funding_deducts_close_cost_without_counting_pending_credit(self):
        other = copy.deepcopy(self.portfolio["positions"][1])
        other.update(id="other-put", strike="48")
        self.portfolio["positions"].append(other)
        self.portfolio["account"]["cash_for_assignment"] = "9900"
        result = app.analyze_action(self.actions["actions"][2], self.portfolio, NOW)
        self.assertEqual(result["portfolio_put_gross_after"], app.Decimal(9600))
        self.assertEqual(result["cash_for_assignment_after_debits"], app.Decimal(9598))
        self.assertEqual(result["funding"], "shortfall")

    def test_existing_call_reserves_coverage(self):
        action = copy.deepcopy(self.actions["actions"][3])
        action["new_contract"]["right"] = "C"
        result = app.analyze_action(action, self.portfolio, NOW)
        self.assertEqual(result["coverage"], "uncovered")
        self.assertTrue(result["warnings"])

    def test_roll_call_releases_old_coverage(self):
        action = copy.deepcopy(self.actions["actions"][2])
        action["position_id"] = "demo-call"
        action["new_contract"]["right"] = "C"
        result = app.analyze_action(action, self.portfolio, NOW)
        self.assertEqual(result["coverage"], "covered")

    def test_missing_quotes_generate_report_with_explicit_gaps(self):
        result = app.report(self.portfolio, {}, {}, {}, NOW)
        self.assertIn("not_checked", result)
        self.assertIn("缺少旧仓 ask", result)
        self.assertNotIn("未来无事件。", result)

    def test_quote_quality_frozen_stale_future(self):
        quote = dict(self.market["underlyings"]["DEMO"])
        quote["status"] = "frozen"
        self.assertEqual(app.quote_quality(quote, NOW), "frozen")
        quote["status"] = "realtime"
        self.assertEqual(app.quote_quality(quote, NOW + app.timedelta(hours=1)), "stale")
        self.assertEqual(app.quote_quality(quote, NOW - app.timedelta(hours=1)), "future")

    def test_expiry_days_use_us_calendar_date(self):
        result = app.aggregate(self.portfolio, {}, app.instant("2026-10-27T00:30:00+08:00", "now"))
        self.assertEqual(result["expiries"]["2026-10-30"]["dte"], 4)

    def test_event_scope_horizon_and_unknown_time(self):
        events = app.load(ROOT / "events.json")
        events["items"].append({**events["items"][1], "id": "other", "symbols": ["OTHER"]})
        selected = app.future_events(events, {"DEMO"}, NOW, 14)
        self.assertEqual(len(selected), 2)
        self.assertIn("时间待确认", selected[0][2])
        self.assertEqual(app.future_events(events, {"DEMO"}, NOW, 0), [])

    def test_bad_inputs_rejected(self):
        for bad in ("NaN", "Infinity", "-1", True):
            with self.assertRaises(app.InputError):
                app.number(bad, "amount")
        duplicate = copy.deepcopy(self.portfolio)
        duplicate["positions"].append(duplicate["positions"][0])
        with self.assertRaises(app.InputError):
            app.validate_portfolio(duplicate)
        q = {**self.market["underlyings"]["DEMO"], "bid": "5", "ask": "4"}
        with self.assertRaises(app.InputError):
            app.validate_quote(q)
        with self.assertRaises(app.InputError):
            app.instant("2026-10-26T09:30:00", "no timezone")

    def test_snapshot_backups_and_private_permissions(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "portfolio.json"
            app.save_snapshot(self.portfolio, target)
            changed = copy.deepcopy(self.portfolio)
            changed["positions"][0]["quantity"] = "200"
            app.save_snapshot(changed, target)
            backups = list(Path(folder).glob("*.backup-*.json"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(app.load(backups[0])["positions"][0]["quantity"], "100")
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)

    def test_decision_idempotence_and_no_position_mutation(self):
        before = copy.deepcopy(self.portfolio)
        decision = app.load(ROOT / "decision.json")
        with tempfile.TemporaryDirectory() as folder:
            journal = Path(folder) / "decisions.jsonl"
            app.record_decision(decision, journal)
            with self.assertRaises(app.InputError):
                app.record_decision(decision, journal)
            self.assertEqual(len(journal.read_text().splitlines()), 1)
        self.assertEqual(before, self.portfolio)

    def test_repeated_reports_preserve_previous_analysis(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "latest.md"
            app.save_report("first", target)
            app.save_report("second", target)
            archive = list(Path(folder).glob("*.archive-*.md"))
            self.assertEqual(len(archive), 1)
            self.assertEqual(archive[0].read_text(), "first")
            self.assertEqual(target.read_text(), "second")


if __name__ == "__main__":
    unittest.main()
