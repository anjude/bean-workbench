# 投资分析 MVP

通过当前聊天使用，Python 负责可重复的金额计算和本地 Markdown 报告；助手负责查证事件、解释风险和比较可选操作。无需外部依赖、网络服务或网页。

当前分析/报告入口为 [finance-tools-investment](../../.agents/skills/finance-tools-investment/SKILL.md)，计算器是其确定性计算工具。用户当前规则优先：日报正文只在会话、按要求才保存；事件放决策层最前，健康明细在阅读层；不扣手续费，历史成本与现金金额不是日常预算分析必补项。下面 CLI 的费用/现金校验能力仍供其他明确情景使用，不覆盖当前用户约定。

## 已实现

1. 当前仓位：正股和期权分开汇总，按标的/到期日统计 Put 毛行权资金、潜在新增股数、Call 覆盖义务；有成本/报价时计算对应参考盈亏。
2. 标的与事件：展示来源、报价时间、相对前收变动、数据质量；未来 14 天全局/标的事件及核验覆盖范围。
3. 操作情景：继续持有、平仓、新开仓、roll；按 bid 卖出、ask 买回，分别列旧仓盈亏、新仓现金流、毛行权资金和期限变化。
4. 录入与留存：JSON 快照校验/备份，用户决定和用户报送成交保存 JSONL；记录决定不会自动改仓位。

当前仅支持 USD、多头正股和卖出 Put/Call。合约乘数必须明确提供；示例数量仅为虚构。报价缺失、冻结或延迟时，报告仍生成并提示对应结论不足；数据自动接入暂缓。

## 在聊天里使用

- “分析当前仓位”：读取本机私有快照、现有行情和事件文件，运行报告，再结合缺项解释风险。
- “比较这笔 Put 平仓和 roll”：将用户指定的候选合约与有来源/时点的报价写入候选文件，分别计算；同时保留继续持有选项。
- “这笔已经成交”：先记录用户报送成交，再基于明确成交信息更新仓位快照；保持旧版本备份。
- “本周有哪些事件”：助手查官方来源，把已确认/待确认事件写入事件文件；无法完成的范围保留 not_checked/partial。

不会因为缺少一项数据就把整份报告停掉；没有成本/权利金就不算净盈亏，没有接股资金就不判定现金覆盖，没有查事件就不称“无事件”。

## 跑虚构示例

在工作台根目录运行：

```bash
python3 tools/investment-analysis/investment.py report \
  --portfolio tools/investment-analysis/examples/portfolio.json \
  --market tools/investment-analysis/examples/market.json \
  --events tools/investment-analysis/examples/events.json \
  --candidates tools/investment-analysis/examples/candidates.json \
  --as-of 2026-10-26T14:05:00+00:00
```

示例的 roll：旧 Put 买回 300 美元，新 Put 收入 400 美元，新增开平费用合计 2 美元，所以净现金流 +98；原权利金为 200 美元、旧开仓费用 1 美元，旧仓实现盈亏为 −102。两者必须分别展示。

## 本机真实输入

真实仓位和生成的报告放在 Git 忽略目录 `.agents/local-config/investment-analysis/`，目录权限 700、文件 600。

```bash
python3 tools/investment-analysis/investment.py report \
  --portfolio .agents/local-config/investment-analysis/portfolio.json \
  --market .agents/local-config/investment-analysis/market.json \
  --events .agents/local-config/investment-analysis/events.json \
  --output .agents/local-config/investment-analysis/reports/latest.md
```

省略行情、事件或候选参数即可生成带缺项标记的报告。`--as-of` 可复现历史分析时点；`--quote-max-age-minutes` 默认 15，仅用于数据质量提示；`--event-days` 默认 14。

## 输入约定

完整格式见 `examples/`。

- `portfolio.json`：`schema_version=1`、`currency=USD`、用户报送时点 `as_of`、来源 `source`、唯一 ID 的 `positions`。正股 `average_cost`、期权 `entry_premium` 和费用未知时填 `null`。
- `account.cash_for_assignment`：用户确认可兑现全部 Put 行权义务的现金池（包含已预留部分），不是券商 BuyingPower。仅在 `put_collateral=cash_secured` 时用它判断毛额覆盖；不计算券商保证金。
- `market.json`：`underlyings` 按 ticker 索引，`options` 按仓位 ID 索引；每条必须有来源、含时区的 `as_of` 和 `status`。状态支持 `realtime/delayed/frozen/frozen_delayed/user_verified`；`user_verified` 只可用于用户明确提供并核对的报价。
- `events.json`：事件有全局/标的范围、来源 URL、发布方、`confirmed/tentative`；日期不明确到时刻时使用 `date` + `timezone`。`coverage` 用 `not_checked/partial/checked` 记录每个范围是否查证；已查范围需要 `checked_at` 和 `source_urls`。
- `candidates.json`：操作类型为 `hold/close/roll/new`。旧合约买回使用 `close_quote.ask`，新合约卖出使用 `open_quote.bid`。新旧仓数量可不同；MVP roll 要求同标的同 Put/Call。费用未知时只输出费用前现金流。
- 金额和价格推荐使用十进制字符串；使用 Decimal 计算。负数量、NaN/Infinity、无时区时间、重复 ID、ask 小于 bid 会报错。

## 更新快照与记录决定

```bash
python3 tools/investment-analysis/investment.py save-snapshot \
  --input /本机/确认后的组合.json \
  --destination .agents/local-config/investment-analysis/portfolio.json

python3 tools/investment-analysis/investment.py record-decision \
  --input /本机/用户决定.json \
  --journal .agents/local-config/investment-analysis/decisions.jsonl
```

已有快照自动备份。决定记录需要唯一 ID、时点、来源、说明和 `proposed/decided/user_reported_fill` 状态；最后一类还需用户报送的成交价格、数量和时间。重复 ID 拒绝写入。命令串行使用，仓位变化始终通过确认后的快照更新。

## 验证

```bash
python3 -m unittest discover -s tools/investment-analysis -p 'test_*.py' -v
```

重点核验资金聚合、股票不重复计数、roll 净收入与盈亏分离、Call 覆盖、缺项、时间/事件筛选及快照备份。数据源时效和合约身份仍需独立核对。
