#!/usr/bin/env python3
"""本地只读投资分析：使用明确输入生成可追溯报告，不连接券商。"""

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import uuid
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo


class InputError(ValueError):
    pass


def number(value, name, optional=False, positive=False):
    if value is None and optional:
        return None
    if value is None or isinstance(value, bool):
        raise InputError(name + " 必须为明确的有限数字")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise InputError(name + " 不是有效数字")
    if not result.is_finite() or result < 0 or (positive and result <= 0):
        raise InputError(name + " 必须为有限非负数" + ("且大于零" if positive else ""))
    return result


def instant(value, name):
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        raise InputError(name + " 必须为 ISO 时间")
    if result.utcoffset() is None:
        raise InputError(name + " 必须包含时区")
    return result


def text_required(value, name):
    if not isinstance(value, str) or not value.strip():
        raise InputError(name + " 必须为非空文本")
    return value


def load(path):
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)


def validate_position(p):
    for key in ("id", "symbol", "asset", "side"):
        text_required(p.get(key), "position." + key)
    q = number(p.get("quantity"), "quantity", positive=True)
    if p["asset"] == "stock":
        if p["side"] != "long":
            raise InputError("MVP 正股仅支持 long")
        number(p.get("average_cost"), "average_cost", optional=True)
    elif p["asset"] == "option":
        if p["side"] != "short" or p.get("right") not in ("P", "C"):
            raise InputError("MVP 期权仅支持 short P/C")
        if q != q.to_integral_value():
            raise InputError("期权张数必须为整数")
        number(p.get("strike"), "strike", positive=True)
        number(p.get("multiplier"), "multiplier", positive=True)
        try:
            date.fromisoformat(p["expiry"])
        except (KeyError, ValueError, TypeError):
            raise InputError("expiry 必须为 YYYY-MM-DD")
        number(p.get("entry_premium"), "entry_premium", optional=True)
        number(p.get("opening_fees"), "opening_fees", optional=True)
    else:
        raise InputError("asset 仅支持 stock/option")


def validate_portfolio(data):
    if data.get("schema_version") != 1 or data.get("currency") != "USD":
        raise InputError("MVP 需要 schema_version=1、currency=USD")
    instant(data.get("as_of"), "portfolio.as_of")
    text_required(data.get("source"), "portfolio.source")
    if not isinstance(data.get("positions"), list):
        raise InputError("positions 必须为列表")
    ids = set()
    for p in data["positions"]:
        validate_position(p)
        if p["id"] in ids:
            raise InputError("重复仓位 ID: " + p["id"])
        ids.add(p["id"])
    account = data.get("account", {})
    number(account.get("cash_for_assignment"), "cash_for_assignment", optional=True)
    return data


def validate_quote(q):
    text_required(q.get("source"), "quote.source")
    instant(q.get("as_of"), "quote.as_of")
    if q.get("status") not in ("realtime", "delayed", "frozen", "frozen_delayed", "user_verified"):
        raise InputError("quote.status 无效")
    for key in ("bid", "ask", "last", "previous_close", "volume", "open_interest", "iv"):
        number(q.get(key), "quote." + key, optional=True)
    if q.get("bid") is not None and q.get("ask") is not None:
        if number(q["ask"], "ask") < number(q["bid"], "bid"):
            raise InputError("ask 不得小于 bid")


def quote_quality(q, as_of, max_age_minutes=15):
    if not q:
        return "missing"
    validate_quote(q)
    age = (as_of - instant(q["as_of"], "quote.as_of")).total_seconds()
    if age < 0:
        return "future"
    if q["status"] in ("frozen", "frozen_delayed"):
        return q["status"]
    if age > max_age_minutes * 60:
        return "stale"
    return q["status"]


def validate_market(market):
    for group in ("underlyings", "options"):
        if not isinstance(market.get(group, {}), dict):
            raise InputError("market." + group + " 必须为对象")
        for q in market.get(group, {}).values():
            validate_quote(q)


def aggregate(portfolio, market, as_of):
    validate_portfolio(portfolio)
    validate_market(market)
    report_date = as_of.astimezone(ZoneInfo("America/New_York")).date()
    result = {"symbols": {}, "expiries": {}, "put_gross": Decimal(0), "put_contracts": Decimal(0)}
    for p in portfolio["positions"]:
        row = result["symbols"].setdefault(p["symbol"], {
            "stock_shares": Decimal(0), "stock_reported": False, "put_gross": Decimal(0),
            "put_shares": Decimal(0), "call_shares": Decimal(0), "stock_value": None,
            "stock_cost": Decimal(0), "stock_cost_complete": True, "stock_pnl": None,
        })
        q = number(p["quantity"], "quantity")
        if p["asset"] == "stock":
            row["stock_shares"] += q
            row["stock_reported"] = True
            cost = number(p.get("average_cost"), "average_cost", optional=True)
            if cost is None:
                row["stock_cost_complete"] = False
            else:
                row["stock_cost"] += cost * q
        else:
            shares = q * number(p["multiplier"], "multiplier")
            bucket = result["expiries"].setdefault(p["expiry"], {
                "put_gross": Decimal(0), "put_contracts": Decimal(0), "put_shares": Decimal(0),
                "dte": (date.fromisoformat(p["expiry"]) - report_date).days,
            })
            if p["right"] == "P":
                gross = shares * number(p["strike"], "strike")
                row["put_gross"] += gross
                row["put_shares"] += shares
                bucket["put_gross"] += gross
                bucket["put_contracts"] += q
                bucket["put_shares"] += shares
                result["put_gross"] += gross
                result["put_contracts"] += q
            else:
                row["call_shares"] += shares
    for symbol, row in result["symbols"].items():
        quote = market.get("underlyings", {}).get(symbol, {})
        last = number(quote.get("last"), "last", optional=True)
        if row["stock_reported"] and last is not None:
            row["stock_value"] = row["stock_shares"] * last
            if row["stock_cost_complete"]:
                row["stock_pnl"] = row["stock_value"] - row["stock_cost"]
    return result


def analyze_action(action, portfolio, as_of, max_age_minutes=15):
    kind = action.get("kind")
    if kind not in ("new", "roll", "close", "hold"):
        raise InputError("action.kind 仅支持 new/roll/close/hold")
    text_required(action.get("id"), "action.id")
    positions = {p["id"]: p for p in portfolio["positions"]}
    old = positions.get(action.get("position_id"))
    if kind != "new" and (not old or old["asset"] != "option"):
        raise InputError("操作需要已有期权 position_id")
    r = {"id": action["id"], "kind": kind, "missing": [], "warnings": [], "cash_flow": None,
         "realized_pnl": None, "old_put_gross": Decimal(0), "new_put_gross": Decimal(0),
         "net_credit_is_profit": False}
    if kind == "hold":
        r["warnings"].append("继续保留现有到期义务；本项不生成新成交现金流")
        return r
    close_cost = Decimal(0)
    open_credit = Decimal(0)
    fees = Decimal(0)
    fees_known = True
    if old:
        units = number(old["quantity"], "quantity") * number(old["multiplier"], "multiplier")
        if old["right"] == "P":
            r["old_put_gross"] = number(old["strike"], "strike") * units
        q = action.get("close_quote")
        if not q or q.get("ask") is None:
            r["missing"].append("旧仓买回 ask")
        else:
            quality = quote_quality(q, as_of, max_age_minutes)
            if quality not in ("realtime", "user_verified"):
                r["warnings"].append("旧仓报价为 " + quality + "，仅供条件情景")
            close_cost = number(q["ask"], "ask") * units
            r["close_cost"] = close_cost
        closing_fees = number(action.get("closing_fees"), "closing_fees", optional=True)
        if closing_fees is None:
            r["missing"].append("平仓费用（可明确填 0）")
            fees_known = False
        else:
            fees += closing_fees
        original = number(old.get("entry_premium"), "entry_premium", optional=True)
        opening_fees = number(old.get("opening_fees"), "opening_fees", optional=True)
        if original is not None and opening_fees is not None and closing_fees is not None and "close_cost" in r:
            r["realized_pnl"] = original * units - close_cost - opening_fees - closing_fees
    new = action.get("new_contract")
    if kind in ("new", "roll"):
        if not new:
            raise InputError("新开/roll 需要 new_contract")
        validate_position(new)
        if new["asset"] != "option":
            raise InputError("候选合约必须为 option")
        if date.fromisoformat(new["expiry"]) < as_of.astimezone(ZoneInfo("America/New_York")).date():
            raise InputError("新仓到期日已过")
        if kind == "roll":
            if new["symbol"] != old["symbol"] or new["right"] != old["right"]:
                raise InputError("MVP roll 要求同标的同 Put/Call 类型")
            r["expiry_change_days"] = (date.fromisoformat(new["expiry"]) - date.fromisoformat(old["expiry"])).days
        units = number(new["quantity"], "quantity") * number(new["multiplier"], "multiplier")
        r["new_contract"] = new
        if new["right"] == "P":
            r["new_put_gross"] = number(new["strike"], "strike") * units
        else:
            stocks = [p for p in positions.values() if p["asset"] == "stock" and p["symbol"] == new["symbol"]]
            shares = sum((number(p["quantity"], "quantity") for p in stocks), Decimal(0))
            reserved = sum((number(p["quantity"], "quantity") * number(p["multiplier"], "multiplier")
                            for p in positions.values() if p["asset"] == "option" and p["right"] == "C"
                            and p["symbol"] == new["symbol"] and p["id"] != action.get("position_id")), Decimal(0))
            r["coverage"] = "unknown" if not stocks else ("covered" if shares - reserved >= units else "uncovered")
            if r["coverage"] != "covered":
                r["warnings"].append("新 Call 正股覆盖为 " + r["coverage"] + "，不可认定为 covered call")
        q = action.get("open_quote")
        if not q or q.get("bid") is None:
            r["missing"].append("新仓卖出 bid")
        else:
            quality = quote_quality(q, as_of, max_age_minutes)
            if quality not in ("realtime", "user_verified"):
                r["warnings"].append("新仓报价为 " + quality + "，仅供条件情景")
            open_credit = number(q["bid"], "bid") * units
            r["open_credit"] = open_credit
            if new["right"] == "P":
                r["new_leg_breakeven_before_fees"] = number(new["strike"], "strike") - number(q["bid"], "bid")
        opening_fees = number(action.get("opening_fees"), "opening_fees", optional=True)
        if opening_fees is None:
            fees_known = False
            r["missing"].append("新仓费用（可明确填 0）")
        else:
            fees += opening_fees
        r["warnings"].append("接股/交股意愿和个人风险上限仍需用户确认")
    legs_known = (kind == "new" or "close_cost" in r) and (kind == "close" or "open_credit" in r)
    if legs_known:
        r["cash_flow_before_fees"] = open_credit - close_cost
        if fees_known:
            r["cash_flow"] = open_credit - close_cost - fees
    r["gross_change"] = r["new_put_gross"] - r["old_put_gross"]
    total = sum((number(p["strike"], "strike") * number(p["quantity"], "quantity") * number(p["multiplier"], "multiplier")
                 for p in positions.values() if p["asset"] == "option" and p["right"] == "P"), Decimal(0))
    r["portfolio_put_gross_after"] = total + r["gross_change"]
    account = portfolio.get("account", {})
    cash = number(account.get("cash_for_assignment"), "cash_for_assignment", optional=True)
    r["funding"] = "unknown"
    if account.get("put_collateral") == "cash_secured" and cash is not None and legs_known and fees_known:
        r["cash_for_assignment_after_debits"] = cash - close_cost - fees
        r["funding"] = "covered" if r["cash_for_assignment_after_debits"] >= r["portfolio_put_gross_after"] else "shortfall"
    return r


def future_events(data, symbols, as_of, horizon_days):
    for key, coverage in data.get("coverage", {}).items():
        if coverage.get("status") not in ("not_checked", "checked", "partial"):
            raise InputError("event coverage.status 无效: " + key)
        if coverage["status"] in ("checked", "partial"):
            instant(coverage.get("checked_at"), "coverage.checked_at")
            if not coverage.get("source_urls") or not all(isinstance(url, str) and url.startswith(("https://", "http://")) for url in coverage["source_urls"]):
                raise InputError("已检查的事件覆盖需要 source_urls")
    items = []
    seen = set()
    for event in data.get("items", []):
        for key in ("id", "title", "publisher", "source_url"):
            text_required(event.get(key), "event." + key)
        if event["id"] in seen:
            raise InputError("重复 event.id")
        seen.add(event["id"])
        if not event["source_url"].startswith(("https://", "http://")):
            raise InputError("event.source_url 必须为网页链接")
        if event.get("scope") not in ("global", "symbol") or event.get("status") not in ("confirmed", "tentative"):
            raise InputError("event scope/status 无效")
        if event["scope"] == "symbol" and not event.get("symbols"):
            raise InputError("标的事件需要 symbols")
        if event["scope"] == "symbol" and not set(event["symbols"]).intersection(symbols):
            continue
        if event.get("starts_at"):
            dt = instant(event["starts_at"], "event.starts_at")
            include = as_of <= dt <= as_of + timedelta(days=horizon_days)
            label = dt.astimezone(ZoneInfo("Asia/Shanghai")).isoformat(timespec="minutes")
            sort_key = dt.timestamp()
        else:
            try:
                day = date.fromisoformat(event["date"])
                tz = ZoneInfo(event["timezone"])
            except (KeyError, ValueError):
                raise InputError("日期事件需要 date=YYYY-MM-DD 与 timezone")
            include = as_of.astimezone(tz).date() <= day <= (as_of + timedelta(days=horizon_days)).astimezone(tz).date()
            label = str(day) + "（" + event["timezone"] + "，时间待确认）"
            sort_key = datetime.combine(day, datetime.min.time(), tzinfo=tz).timestamp()
        if include:
            items.append((sort_key, event, label))
    return sorted(items, key=lambda item: item[0])


def money(value):
    return "未知" if value is None else format(value, ",.2f")


def cell(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def report(portfolio, market, events, actions, as_of, max_age_minutes=15, horizon_days=14):
    summary = aggregate(portfolio, market, as_of)
    if instant(portfolio["as_of"], "portfolio.as_of") > as_of:
        raise InputError("仓位报送时间晚于分析时间")
    rows = summary["symbols"]
    lines = ["# " + ("演示数据 · " if portfolio.get("demo") else "") + "投资分析报告", "", "- 分析时间：" + as_of.astimezone(ZoneInfo("Asia/Shanghai")).isoformat(timespec="minutes"),
             "- 仓位报送时间：" + portfolio["as_of"] + "；来源：" + cell(portfolio["source"]),
             "- 口径：USD；合约张数/乘数分别记录；毛行权资金不等于保证金。", "",
             "## 1. 当前仓位分析", "", "- 卖 Put：" + str(summary["put_contracts"]) + " 张；全部按合约行权的毛额：$" + money(summary["put_gross"]),
             "- 现金与保证金覆盖：" + ("待按用户提供的现金担保规则核验" if portfolio.get("account", {}).get("cash_for_assignment") is None else "见用户现金池输入，不能替代券商保证金"),
             "- 已知成本/权利金不完整的仓位，不计算总盈亏。", "",
             "| 标的 | 已报正股 | 已知正股参考市值 | 正股参考浮盈亏（未计费用） | Put 毛行权资金 | Put 潜在新增股数 | Call 占用股数 |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for symbol, row in sorted(rows.items()):
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (cell(symbol), str(row["stock_shares"]) if row["stock_reported"] else "未报送", money(row["stock_value"]), money(row["stock_pnl"]), money(row["put_gross"]), row["put_shares"], row["call_shares"]))
    lines += ["", "| 到期日 | 剩余日历天（美东） | Put 张数 | Put 毛行权资金 |", "| --- | ---: | ---: | ---: |"]
    for expiry, row in sorted(summary["expiries"].items()):
        lines.append("| %s | %s | %s | %s |" % (expiry, row["dte"], row["put_contracts"], money(row["put_gross"])))
    soon = [row for row in summary["expiries"].values() if 0 <= row["dte"] <= 7]
    lines += ["", "- 未来 7 个日历天到期 Put 毛行权资金：$" + money(sum((row["put_gross"] for row in soon), Decimal(0)))]
    if any(row["dte"] < 0 for row in summary["expiries"].values()):
        lines.append("- 存在已过期但账本未结算的仓位；先核对到期、指派或平仓结果，未核实前保留为待处理义务。")
    if portfolio.get("snapshot_complete") is False:
        lines.append("- 仓位是用户报送的部分/待核快照；未报送持股不视为零，组合净值与集中度不可据此完整计算。")
    lines += ["", "## 2. 标的价格与事件", "", "价格变动只对应表内报价时点，不表示当前盘中价格；本次质量提示窗口为 %d 分钟。" % max_age_minutes, "",
              "| 标的 | last / 前收 | 相对前收 | 报价时间 | 状态/质量 | 来源 |", "| --- | --- | ---: | --- | --- | --- |"]
    for symbol in sorted(rows):
        q = market.get("underlyings", {}).get(symbol)
        if not q:
            lines.append("| %s | 未获取 | 未知 | — | missing | — |" % cell(symbol))
            continue
        last, prev = number(q.get("last"), "last", optional=True), number(q.get("previous_close"), "previous_close", optional=True)
        change = ((last / prev - 1) * 100) if last is not None and prev else None
        lines.append("| %s | %s / %s | %s | %s | %s | %s |" % (cell(symbol), money(last), money(prev), money(change) + "%" if change is not None else "未知", q["as_of"], quote_quality(q, as_of, max_age_minutes), cell(q["source"])))
    upcoming = future_events(events, set(rows), as_of, horizon_days)
    lines += ["", "未来 %d 天事件：" % horizon_days]
    if not upcoming:
        lines.append("- 当前事件文件没有匹配条目；这不代表未来无事件，检查覆盖范围如下。")
    for _, event, label in upcoming:
        lines.append("- %s：%s；范围 %s；%s；[%s](%s)" % (label, cell(event["title"]), cell("全局" if event["scope"] == "global" else ", ".join(event["symbols"])), event["status"], cell(event["publisher"]), event["source_url"]))
        if event.get("impact_note"):
            lines.append("  - 可能影响（分析推断）：" + cell(event["impact_note"]))
    coverage = events.get("coverage", {})
    for key in ["global"] + sorted(rows):
        c = coverage.get(key, {})
        lines.append("- 事件检查 %s：%s；检查时间 %s" % (key, c.get("status", "not_checked"), c.get("checked_at", "未检查")))
        if c.get("note"):
            lines.append("  - " + cell(c["note"]))
        for url in c.get("source_urls", []):
            lines.append("  - [核验来源](" + url + ")")
    lines += ["", "## 3. 持有、平仓、roll 与新开仓的可能性", "",
              "| 仓位 | 持有时的义务 | 内在价值状态（按表内标的 last） | 平仓/roll 的当前条件 |", "| --- | --- | --- | --- |"]
    for p in portfolio["positions"]:
        if p["asset"] != "option":
            continue
        units = number(p["quantity"], "quantity") * number(p["multiplier"], "multiplier")
        q = market.get("options", {}).get(p["id"])
        quality = quote_quality(q, as_of, max_age_minutes)
        ask = number(q.get("ask"), "ask", optional=True) if q else None
        obligation = ("可能接入 " if p["right"] == "P" else "可能交付 ") + str(units) + " 股；strike " + p["strike"] + "；" + p["expiry"]
        stock_quote = market.get("underlyings", {}).get(p["symbol"], {})
        last = number(stock_quote.get("last"), "last", optional=True)
        intrinsic_state = "未知"
        if last is not None:
            difference = number(p["strike"], "strike") - last if p["right"] == "P" else last - number(p["strike"], "strike")
            intrinsic_state = "价内" if difference > 0 else ("平值" if difference == 0 else "价外")
            intrinsic_state += "；历史/条件状态不等于到期必然指派"
        condition = "缺少旧仓 ask 和目标新合约报价" if ask is None else "买回成本（费用前）$%s；报价质量 %s；roll 仍需目标新合约" % (money(ask * units), quality)
        premium = number(p.get("entry_premium"), "entry_premium", optional=True)
        if premium is not None and ask is not None:
            condition += "；期权参考浮盈亏（开平费用前）$" + money((premium - ask) * units)
        lines.append("| %s | %s | %s | %s |" % (cell(p["id"]), obligation, intrinsic_state, condition))
    lines += ["", "本轮比较重点（条件提示）："]
    for p in portfolio["positions"]:
        if p["asset"] != "option":
            continue
        dte = (date.fromisoformat(p["expiry"]) - as_of.astimezone(ZoneInfo("America/New_York")).date()).days
        if 0 <= dte <= 7:
            choice = "继续持有并准备可能接股、按 ask 平仓、roll" if p["right"] == "P" else "继续持有并准备可能交股、按 ask 平仓、roll"
            lines.append("- %s：未来 7 天到期，比较 %s；需结合当时报价与用户意愿。" % (cell(p["id"]), choice))
    lines += ["", "新开仓需补充目标合约、卖出 bid、资金边界和接股/交股意愿；覆盖义务与期限可以先比较，适合度保持待确认。", ""]
    ids = set()
    for action in actions.get("actions", []):
        if action.get("id") in ids:
            raise InputError("重复候选操作 ID")
        ids.add(action.get("id"))
        r = analyze_action(action, portfolio, as_of, max_age_minutes)
        lines += ["### 候选 %s：%s" % (cell(r["id"]), r["kind"]), ""]
        if action.get("position_id"):
            lines.append("- 原仓位：" + cell(action["position_id"]))
        if r.get("new_contract"):
            new = r["new_contract"]
            lines.append("- 新合约：%s %s，strike %s，到期 %s，%s 张 × %s 乘数" % (cell(new["symbol"]), new["right"], new["strike"], new["expiry"], new["quantity"], new["multiplier"]))
        for key, price, label in [("close_quote", "ask", "旧仓买回报价"), ("open_quote", "bid", "新仓卖出报价")]:
            quote = action.get(key)
            if quote:
                lines.append("- %s：%s %s；%s；%s；质量 %s" % (label, price, quote.get(price, "缺失"), quote["as_of"], cell(quote["source"]), quote_quality(quote, as_of, max_age_minutes)))
        for key, label in [("close_cost", "旧仓买回成本（费用前）"), ("open_credit", "新仓收入（费用前）"), ("cash_flow_before_fees", "净现金流（费用前，正数为收入）"), ("cash_flow", "净现金流（扣已知费用）"), ("realized_pnl", "旧仓实现盈亏（含已知开平费用）"), ("gross_change", "Put 毛行权资金变化"), ("portfolio_put_gross_after", "操作后组合 Put 毛行权资金"), ("new_leg_breakeven_before_fees", "新 Put 单腿到期盈亏平衡价（费用前，不含旧仓盈亏）")]:
            if key in r:
                lines.append("- %s：%s" % (label, money(r[key])))
        if "expiry_change_days" in r:
            lines.append("- 新旧到期日相差：%s 天" % r["expiry_change_days"])
        if "funding" in r:
            lines.append("- 用户现金担保池覆盖：" + r["funding"])
        if "cash_for_assignment_after_debits" in r:
            lines.append("- 扣已知买回成本与费用后的现金池：%s；新收权利金未作为已结算资金计入。" % money(r["cash_for_assignment_after_debits"]))
        for message in r["missing"] + r["warnings"]:
            lines.append("- " + message)
        if r["kind"] == "roll":
            lines.append("- roll 的净收入不等于利润；继续持有与平仓也需要一并比较。")
        lines.append("")
    lines += ["## 4. 本轮待补与决定记录", "", "- 正股成本、期权原始权利金和费用未知时，对应盈亏保持未知。",
              "- 合约乘数为 assumed_standard 的记录需要与券商合约核对。",
              "- 当前报告是分析快照；用户决定和用户报送成交另记日志，本命令不改变仓位。", ""]
    return "\n".join(lines)


def write_private(path, content):
    path = Path(path)
    if not path.parent.exists():
        path.parent.mkdir(parents=True, mode=0o700)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=str(path.parent), delete=False) as stream:
        temporary = Path(stream.name)
        os.chmod(str(temporary), 0o600)
        stream.write(content)
    temporary.replace(path)
    os.chmod(str(path), 0o600)


def save_snapshot(data, destination):
    validate_portfolio(data)
    destination = Path(destination)
    if destination.exists():
        backup = destination.with_name(destination.stem + ".backup-" + uuid.uuid4().hex[:12] + destination.suffix)
        shutil.copyfile(str(destination), str(backup))
        os.chmod(str(backup), 0o600)
    write_private(destination, json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def save_report(content, destination):
    destination = Path(destination)
    if destination.exists():
        archive = destination.with_name(destination.stem + ".archive-" + uuid.uuid4().hex[:12] + destination.suffix)
        shutil.copyfile(str(destination), str(archive))
        os.chmod(str(archive), 0o600)
    write_private(destination, content)


def record_decision(data, journal):
    for key in ("id", "note", "source"):
        text_required(data.get(key), "decision." + key)
    instant(data.get("as_of"), "decision.as_of")
    if data.get("kind") not in ("hold", "new", "roll", "close") or data.get("status") not in ("proposed", "decided", "user_reported_fill"):
        raise InputError("decision kind/status 无效")
    if data["status"] == "user_reported_fill":
        fill = data.get("fill", {})
        number(fill.get("price"), "fill.price")
        number(fill.get("quantity"), "fill.quantity", positive=True)
        instant(fill.get("as_of"), "fill.as_of")
    path = Path(journal)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if any(json.loads(line)["id"] == data["id"] for line in existing.splitlines() if line.strip()):
        raise InputError("重复 decision.id，拒绝重复记录")
    write_private(path, existing + json.dumps(data, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("report", help="生成仓位、事件和操作情景 Markdown")
    command.add_argument("--portfolio", required=True)
    command.add_argument("--market")
    command.add_argument("--events")
    command.add_argument("--candidates")
    command.add_argument("--as-of", help="含时区的分析时间，默认当前 UTC")
    command.add_argument("--quote-max-age-minutes", type=int, default=15)
    command.add_argument("--event-days", type=int, default=14)
    command.add_argument("--output")
    command = commands.add_parser("save-snapshot", help="校验并保存快照，已有文件自动备份")
    command.add_argument("--input", required=True)
    command.add_argument("--destination", required=True)
    command = commands.add_parser("record-decision", help="记录用户决定或报送成交，不改变仓位")
    command.add_argument("--input", required=True)
    command.add_argument("--journal", required=True)
    args = parser.parse_args()
    try:
        if args.command == "report":
            if args.quote_max_age_minutes <= 0 or args.event_days < 0:
                raise InputError("报价时效窗口需大于零，事件天数不得为负")
            as_of = instant(args.as_of, "as-of") if args.as_of else datetime.now(timezone.utc)
            content = report(load(args.portfolio), load(args.market) if args.market else {},
                             load(args.events) if args.events else {}, load(args.candidates) if args.candidates else {},
                             as_of, args.quote_max_age_minutes, args.event_days)
            if args.output:
                save_report(content, args.output)
                print(str(Path(args.output).resolve()))
            else:
                print(content)
        elif args.command == "save-snapshot":
            save_snapshot(load(args.input), args.destination)
            print(str(Path(args.destination).resolve()))
        else:
            record_decision(load(args.input), args.journal)
            print(str(Path(args.journal).resolve()))
    except (InputError, OSError, ValueError, TypeError, KeyError) as error:
        parser.exit(2, "输入错误：%s\n" % error)


if __name__ == "__main__":
    main()
