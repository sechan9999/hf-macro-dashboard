# 💹 US Equity HF Pulse — Strategy Specification

> **What this is.** A research/replication spec for a composite US-equity
> opportunity-side score, modelled on the same architecture as the existing
> NVDA Danger Zone (composite index → zone → Strategy Hint Cards). It blends
> six institutional signals taken from publicly-documented hedge-fund
> strategies and academic finance.
>
> **What this is NOT.** Investment advice. Past returns of cited factors do
> not guarantee future performance. All signals below have well-known failure
> modes — read §8.

| | |
|---|---|
| Feature ID | `us-equity-hf-pulse` |
| Counterpart | `danger-zone-strategy-hints` (NVDA, defensive side) |
| Direction | Long-side composite (which names + how aggressive) |
| Universe | S&P 500 (default), expandable to Russell 1000 |
| Frequency | Monthly rebalance, daily score refresh |
| Output | `pulse_score ∈ [0,1]` per ticker → 3 zones + Hint Cards |
| Status | Draft strategy doc — not yet implemented as a tab |

---

## 1. Why this exists

The Danger Zone tab tells you when **NVDA** is over-extended. It is purely
defensive. It does not tell you:

* what to *enter* on the long side,
* when the *broader market* is offering a positive risk-reward,
* or which *style* (momentum, quality, low-vol, trend) is currently working.

High-return systematic shops (AQR, Man AHL, Two Sigma, D.E. Shaw, Renaissance,
Citadel, Millennium, Bridgewater) do not run a single algorithm — they
*combine* a small number of well-attested factor signals, weighted by current
regime. The HF Pulse Index is a research replica of that approach: take six
of the most-published factor signals, compose them, and surface a single
score plus an actionable hint card per ticker.

---

## 2. Composite Index — formula

```
pulse_score = σ( 0.25·z(MOM_12_1)
              + 0.20·z(QMJ)
              + 0.15·z(TS_TREND)
              + 0.15·z(BAB)
              + 0.15·z(PEAD)
              + 0.10·z(INSIDER_NB) )
```

* `z(·)` = cross-sectional z-score within the universe at month *T*.
* `σ(·)` = logistic squash to `[0,1]` so the output mirrors the Danger Index
  scale.
* Weights are starting priors derived from each factor's published Sharpe
  (see §3); they should be re-fitted per regime in production.
* All inputs are computed using data observable at month *T*; the position is
  applied to month *T+1* returns (`.shift(1)`) — same no-lookahead protocol as
  the Strategy Backtest tab.

The composite is a **direction + conviction** number, not a price target:
high score = the cross-section of HF-style signals points to a name being
favoured *now*.

---

## 3. The six component signals

For each component: source paper, the public fund(s) that run something
close to it, the formula, and the data needed.

### 3.1 Cross-sectional momentum (12-1)

| | |
|---|---|
| Source | Jegadeesh & Titman (1993), *Journal of Finance* — "Returns to Buying Winners and Selling Losers" |
| Public users | AQR Momentum funds (e.g., AMOMX), iShares MTUM, BlackRock Style Advantage |
| Formula | `MOM = log(P_{t-1} / P_{t-12})` — past 12-month return excluding the most recent month |
| Data | yfinance monthly closes |
| Why the −1m skip | The prior month tends to *reverse*, especially in liquid US large-caps; skipping it removes the short-term-reversal noise that Jegadeesh-Titman document |
| Known failure mode | Momentum crashes after sharp regime flips (2009-Q1, 2020-Q2). See Daniel & Moskowitz (2016) *"Momentum Crashes"*. |

### 3.2 Quality Minus Junk (QMJ)

| | |
|---|---|
| Source | Asness, Frazzini & Pedersen (2019), *Review of Accounting Studies* — "Quality Minus Junk" |
| Public users | AQR Style Premia / Defensive Equity, iShares Quality Factor (QUAL) |
| Formula | Composite z-score of: profitability (gross profits / assets), growth (5y ΔROE), safety (low leverage, low earnings volatility, low beta), and payout (net buy-back yield) |
| Data | yfinance balance-sheet quarterly + cash flow + market cap |
| Intuition | Boring, profitable, low-debt firms outperform "junk" on a risk-adjusted basis, especially during drawdowns |
| Known failure mode | Pure quality lags during deep value rallies (2003, 2009, late 2020) |

### 3.3 Time-series trend (TS Mom)

| | |
|---|---|
| Source | Moskowitz, Ooi & Pedersen (2012), *Journal of Financial Economics* — "Time Series Momentum" |
| Public users | Man AHL, Winton, Two Sigma trend sleeves, AQR Managed Futures |
| Formula | Sign and magnitude of the t-statistic of the past 12-month excess return: `TS = mean / (vol/√12)` clipped to ±2 |
| Data | yfinance daily, vol-scaled |
| Why it matters | Captures persistent trends in a single name; complements cross-sectional momentum (which is relative) |
| Known failure mode | Trend-following had a brutal 2017-2019 drawdown ("trend winter"); recovered sharply in 2022 |

### 3.4 Betting Against Beta (BAB)

| | |
|---|---|
| Source | Frazzini & Pedersen (2014), *Journal of Financial Economics* — "Betting Against Beta" |
| Public users | AQR Defensive Equity, the academic BAB factor available on Pedersen's site |
| Formula | Long low-beta, short high-beta, beta-neutralised. As a single-name score: `BAB = -β_{60d}` z-scored |
| Data | yfinance daily, 60-day rolling regression vs SPY |
| Intuition | Leverage-constrained investors over-pay for high-beta names; low-beta delivers higher Sharpe |
| Known failure mode | When rates rise sharply, BAB underperforms (2022 was unusually mild for a hiking cycle) |

### 3.5 Post-Earnings Announcement Drift (PEAD)

| | |
|---|---|
| Source | Bernard & Thomas (1989), *Journal of Accounting Research* |
| Public users | Most quant L/S desks — Two Sigma, Cubist (Point72), Citadel Equities, D.E. Shaw |
| Formula | Standardised Unexpected Earnings (SUE) at last report, decayed over 60 trading days: `PEAD = SUE × exp(-days_since/60)` |
| Data | yfinance earnings calendar + actual vs estimate |
| Why it persists | Underreaction to earnings information, especially in mid-caps with light coverage |
| Known failure mode | Crowding in the most-followed names erodes drift; works better outside mega-caps |

### 3.6 Insider net buying

| | |
|---|---|
| Source | Cohen, Malloy & Pomorski (2012), *Journal of Finance* — "Decoding Inside Information" |
| Public users | Most fundamental L/S funds; multiple SEC-Form-4 ETFs (NFO, KNOW historically) |
| Formula | `INSIDER_NB = (insider_buys − insider_sells)$ / market_cap`, last 90 days, opportunistic-trade weighted (open-market only, exclude option exercises) |
| Data | SEC EDGAR Form 4 (free, public, somewhat slow to parse) |
| Why it works | Filters out routine sales; "opportunistic" insider buys carry the strongest signal per Cohen-Malloy-Pomorski |
| Known failure mode | Sparse for mega-caps where insiders own a small % of shares outstanding |

---

## 4. Zones — same shape as the Danger Index

Inverted relative to the Danger Zone (here higher = more attractive):

| Zone | Threshold | Interpretation |
|---|---|---|
| 🟢 **Aggressive Long** | `pulse_score ≥ 0.65` | All-or-most signals aligned positively. Top-decile names go in the high-conviction sleeve. |
| 🟡 **Neutral** | `0.35 ≤ pulse_score < 0.65` | Mixed picture. Equal-weight defensives, hedge with index puts. |
| 🔴 **Defensive** | `pulse_score < 0.35` | Most signals point away. Lean QMJ + BAB, raise cash, consider tactical short on the lowest-decile. |

The thresholds (0.35 / 0.65) mirror the Danger Index bands (0.33 / 0.60) for
visual consistency across the dashboard.

---

## 5. Strategy Hint Cards — Danger-Zone style

These render in three columns, with the **active zone highlighted** (the
exact gap that G-1 of the Danger-Zone analysis flagged — fix it once, here,
on launch).

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 🟢 Aggressive Long  (pulse ≥ 0.65)                                       │
│ • Concentrate top-decile (10–15 names) at full target weight             │
│ • Tilt into Momentum + TS-Trend leaders; skim Quality for ballast        │
│ • Trail stops at 2.5× ATR (live) — converts G-2 from Danger Zone fix     │
│ • Rebalance monthly; intra-month exit only on −2.5σ adverse move         │
└──────────────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────────┐
│ 🟡 Neutral  (0.35 ≤ pulse < 0.65)                                        │
│ • Equal-weight QMJ + BAB picks; cap any single name at 3 %               │
│ • Pair longs with SPY hedge to hold gross exposure ≤ 100 %               │
│ • Fade extremes: trim names at top decile, add at the bottom decile      │
│ • Watch the regime score (Macro tab); a flip into Risk-Off → degrade     │
└──────────────────────────────────────────────────────────────────────────┘
┌──────────────────────────────────────────────────────────────────────────┐
│ 🔴 Defensive  (pulse < 0.35)                                             │
│ • Reduce gross to 50–70 %; lean BAB / QMJ / cash                         │
│ • Optional tactical short of bottom-decile basket, ≤ 20 % gross          │
│ • Buy SPY / QQQ protective puts (1–2 strike OTM, 60-90d)                 │
│ • Hold until Macro regime exits Risk-Off AND pulse > 0.45 for 2 months   │
└──────────────────────────────────────────────────────────────────────────┘
```

**Card-rendering rules** (lessons learned from the Danger-Zone gap analysis,
§G-1 / §G-2):

1. The card matching the live `pulse_score` zone is rendered at full opacity
   with a 2 px coloured border. The other two render at 35 % opacity.
2. At least two numerics per active card are derived from live data
   (e.g. ATR-scaled stop, current decile size, days-since-regime-flip).
3. Hint cards sit immediately under the score banner, not at the bottom of
   the tab.

---

## 6. Backtest protocol

Same harness as the Strategy Backtest tab:

* **Walk-forward**: at month *T*, score the universe using only data
  observable at *T*; rebalance at the close; realise *T+1* monthly returns.
* **Long sleeve**: equal-weight top decile when `pulse_score ≥ 0.65`,
  else top-quintile only when zone is Neutral, else cash.
* **Short sleeve (optional)**: bottom decile when zone is Defensive.
* **Cost model**: 8 bps per unit turnover (S&P 500 large-caps, IB-grade
  execution, market impact ≈ 3 bps for liquid names).
* **Benchmarks**: SPY total return + an equal-weight blend of MTUM, QUAL,
  USMV, MOM (factor-ETF benchmark — captures whether the *combination*
  outperforms each sleeve in isolation).
* **Metrics**: Ann return, Sharpe, Sortino, Calmar, Max DD, capacity-aware
  turnover, beta vs SPY, alpha vs SPY, tail-correlation in the worst
  quintile of SPY months.
* **Robustness checks**:
  * Bootstrap the 6 weights ±25 % — Sharpe should not move > 0.3.
  * Walk-forward weight refit (rolling 5y CV) vs static weights — table both.
  * Sub-period split: `2005–2014`, `2014–2020`, `2020–today`.

---

## 7. Data sources & implementation path

| Need | Source | Cost | Latency |
|---|---|---|---|
| Daily / monthly OHLCV | yfinance | free | ~1 day |
| Quarterly fundamentals (QMJ inputs) | yfinance `Ticker.financials` + `quarterly_balance_sheet` | free | 1 day post-filing |
| Earnings calendar + actuals (PEAD) | yfinance `earnings_dates` + `earnings_history` | free | T+1 |
| Insider Form 4 | SEC EDGAR `https://www.sec.gov/cgi-bin/browse-edgar` (parse XBRL) | free | T+2 |
| Risk-free rate (BAB excess return) | FRED `DGS3MO` | free with key | daily |
| Universe membership | yfinance `^GSPC` constituents (or static list) | free | quarterly |

Suggested implementation sequence:

1. **Phase 1 (1 day)** — Implement signals 3.1, 3.2, 3.3, 3.4 using yfinance
   only; backtest against SPY. Wire as a new tab `📈 HF Pulse`.
2. **Phase 2 (2 days)** — Add 3.5 PEAD using yfinance earnings dates; run
   sub-period robustness.
3. **Phase 3 (3 days)** — Add 3.6 Insider Net Buying via EDGAR parser; cache
   to parquet (one-shot per ticker per day).
4. **Phase 4 (1 day)** — Wire Strategy Hint Cards with active-zone highlight,
   ATR-scaled stops, regime-aware messaging.

---

## 8. Risk, caveats, and where the literature is honest

* **Factor crowding.** AQR's Style Premia funds drew down ~25-30 % in
  2018-2020 even as the academic factors held up. When a strategy is well
  known, the alpha decays. Treat published Sharpes as a ceiling.
* **In-sample bias.** Every public factor was discovered on the same
  Compustat / CRSP history. Sub-period testing matters more than full-sample
  Sharpe.
* **Data-mining the weights.** Weights in §2 are starting priors — they
  should be refit walk-forward. A static weight chosen with hindsight will
  flatter the backtest by ~0.4 Sharpe.
* **Regime sensitivity.** Momentum crashes when the market reverses sharply
  (Q1-2009, Q2-2020). The *Macro & Rates* tab's regime score should gate
  position size: when `regime_score > +1.5σ`, halve the long sleeve.
* **Capacity.** Mid-cap insider/PEAD signals do not scale; they degrade
  fast above ~$100m AUM in a single sleeve. The dashboard prototype is fine,
  but do not project the backtest Sharpe linearly to size.
* **Survivorship.** S&P 500 membership is forward-looking. Use a
  point-in-time index file (CRSP, Norgate, or build one from S&P press
  releases) for honest backtests. yfinance's current-membership list will
  bias results upward by ~0.8-1.2 % per year.
* **Transaction-cost realism.** The 8 bps figure is for SPY-style large-caps.
  Bottom-decile shorts in small-caps incur 30-100 bps round-trip plus
  borrow. The short sleeve is the most dangerous part of the strategy on
  paper-vs-live divergence.
* **Survivor anecdote ≠ evidence.** Renaissance Medallion's reported
  long-run Sharpe (~6) is not replicable from public data. Treat fund
  marketing material as motivation, not as a target.

---

## 9. Mapping to the existing Macro Pulse dashboard

| Existing tab | Role under HF Pulse |
|---|---|
| 🌍 Macro & Rates | Provides the regime gate that scales the long sleeve |
| 🔍 Regime | Same — `regime_score > +1.5σ` halves long exposure |
| 🤖 Expected Returns (Ridge) | Cross-check on the directional signal; if Ridge disagrees with Pulse > 0.65, demote conviction |
| 📊 Strategy Backtest (new) | Use the same harness — feed Pulse-derived `target_w` into `run_strategy_backtest()` |
| 🔥 NVDA Danger Zone | Defensive counterpart — when Danger ≥ 0.6 *and* NVDA's Pulse < 0.35, system goes max-defensive on the name |

---

## 10. References

Academic (all published, peer-reviewed):

* Jegadeesh, N. & Titman, S. (1993). *Returns to Buying Winners and Selling
  Losers: Implications for Stock Market Efficiency.* Journal of Finance, 48(1).
* Asness, C., Frazzini, A. & Pedersen, L. H. (2019). *Quality Minus Junk.*
  Review of Accounting Studies. AQR working-paper version published at
  `aqr.com` under Insights → Research.
* Frazzini, A. & Pedersen, L. H. (2014). *Betting Against Beta.* Journal of
  Financial Economics, 111(1).
* Moskowitz, T., Ooi, Y. H. & Pedersen, L. H. (2012). *Time Series
  Momentum.* Journal of Financial Economics, 104(2).
* Bernard, V. & Thomas, J. (1989). *Post-Earnings-Announcement Drift:
  Delayed Price Response or Risk Premium?* Journal of Accounting Research,
  Supplement.
* Cohen, L., Malloy, C. & Pomorski, L. (2012). *Decoding Inside
  Information.* Journal of Finance, 67(3).
* Daniel, K. & Moskowitz, T. (2016). *Momentum Crashes.* Journal of
  Financial Economics, 122(2).
* Gatev, E., Goetzmann, W. & Rouwenhorst, K. G. (2006). *Pairs Trading:
  Performance of a Relative-Value Arbitrage Rule.* Review of Financial
  Studies, 19(3).

Public fund / industry sources (each fund publishes whitepapers and
quarterly letters on its own site — search by title):

* AQR Capital Management — "Style Premia" series; Asness's annual letters.
* Man Group — AHL trend-following commentary; "Views from the Floor"
  newsletter.
* Two Sigma — "Insights" research site.
* Bridgewater — "Daily Observations" excerpts; All Weather methodology
  whitepaper.
* Renaissance Technologies — most material is private; G. Zuckerman's *The
  Man Who Solved the Market* (2019) is the canonical popular-press account
  of Medallion's mechanics, and is the only credible secondary source.

---

## 11. Open questions / things to validate before building

* What's the universe-membership data source? Without point-in-time
  membership, the backtest is decorative. Decide before Phase 1.
* Are Form 4 parses cached? EDGAR rate-limits aggressively; a cold backtest
  over 20 years and 500 tickers needs > 100 k requests.
* Should the score be ticker-level only, or also a market-level aggregate
  (mean of top-decile pulse) shown as a single number on the home tab?
  The latter is the natural "macro pulse" sibling to the regime score.
* Is the `0.65 / 0.35` zone split the right one? An alternative is to use
  the *historical 80th / 20th percentile of the score itself*, refit
  monthly. Less interpretable, more honest.

---

*Authored 2026-05-06 as a planning artifact for a future `📈 HF Pulse` tab
in `app.py`. Sibling document: `docs/03-analysis/danger-zone-strategy-hints.analysis.md`.*
