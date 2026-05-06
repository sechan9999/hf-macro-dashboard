# [Check] Danger Zone Strategy Hints — Gap Analysis

| | |
|---|---|
| Feature | `danger-zone-strategy-hints` |
| Location | `app.py` lines 1717–1756 (tab9, NVDA Danger Zone) |
| Phase | PDCA Check (post-hoc) |
| Date | 2026-05-06 |
| Plan doc | ❌ not present |
| Design doc | ❌ not present |
| Analyzer | post-hoc gap analysis (no formal Design to compare against) |
| Match Rate | **78 %** (below the 90 % bar → iterate recommended) |

> **Note on methodology.** No Plan/Design document exists for this feature. The
> "spec" was reconstructed from the README's one-line claim and from the implicit
> expectations a user would carry into the UI. Where a real PDCA cycle would
> compare *Design § X.Y* against *implementation*, this analysis compares
> *stated intent* against *delivered behavior*.

---

## 1. Reconstructed Spec

From `README.md`:

> *Strategy Hint Cards: Actionable trading guides based on the current risk
> zone (Safe/Caution/Danger).*

| ID | Requirement | Source |
|----|-------------|--------|
| IR-1 | Hint content must be **actionable** (concrete trade actions, not vague advice) | README, "actionable trading guides" |
| IR-2 | Hint surface must reflect **the current risk zone** (i.e., zone-conditioned) | README, "based on the current risk zone" |
| IR-3 | Three zones supported: Safe / Caution / Danger | README + Danger-Index thresholds (0.33, 0.60) |
| IR-4 | Each zone gets its own card | README, "Cards" plural |
| IR-5 | Zone thresholds must match the Danger-Index thresholds used elsewhere in the tab | code consistency (lines 1446, 1361–1364) |
| IR-6 | Recommendations must reference signals already shown on this tab (no orphan terminology) | UX coherence |

---

## 2. Implementation Snapshot

```python
# app.py 1717–1756 — three columns, three static HTML blocks
hint_cols = st.columns(3)
with hint_cols[0]:  # 🔴 Danger (≥0.60)  — 4 bullets
with hint_cols[1]:  # ⚠️ Caution (0.33–0.60) — 4 bullets
with hint_cols[2]:  # 🟢 Safe (<0.33)   — 4 bullets
```

* All three cards render **simultaneously**, regardless of the current zone.
* The "current zone" is computed at line 1446 (`danger_color_text`) and shown
  in a banner at line 1454, but the Hints section at line 1717 is decoupled
  from that variable.
* Bullet content is **hard-coded** (e.g. "1–2 strike OTM", "10–15 % trailing
  stop", "RSI < 60"). None of these adapt to live ATR, IV, or price.
* Recommendations correctly reference signals visible elsewhere on the tab:
  `vol_ratio`, OBV, B/A imbalance, block trades. Terminology is coherent.

---

## 3. Per-Requirement Verdict

| ID | Verdict | Evidence | Severity if gap |
|----|---------|----------|-----------------|
| IR-1 | ✅ Pass | Bullets are imperative ("Trim 20–40 %", "Buy protective puts", "Tighten stop") | — |
| IR-2 | ⚠️ Partial | All three zones rendered always; active zone is not highlighted, scoped, or reordered | **High** |
| IR-3 | ✅ Pass | Three columns, three zones, thresholds match | — |
| IR-4 | ✅ Pass | Each zone is a separate styled card | — |
| IR-5 | ✅ Pass | Hint thresholds (0.33, 0.60) match `pd.cut` bins at 1361–1364 and the banner at 1446 | — |
| IR-6 | ✅ Pass | Mentions of `vol_ratio > 2`, OBV, B/A, block trades all map to charts above in the same tab | — |

**4 / 6 fully pass, 1 partial, 0 fail.** Pass-equivalent count = 4.5.
Spec coverage = 4.5 / 6 = **75 %**, then adjusted upward for quality of the
passing items (sound thresholds, coherent terminology) → **Match Rate ≈ 78 %**.

---

## 4. Gap List

| # | Severity | Gap | Why it matters |
|---|----------|-----|----------------|
| **G-1** | 🔴 High | Active zone is not highlighted in the Hints panel. User reads three cards and must self-select. | Defeats the stated value prop ("based on the current risk zone"). |
| **G-2** | 🟡 Med | Numeric advice is fixed (`1–2 strike OTM`, `10–15 % stop`, `RSI < 60`). | ATR-aware advice would be genuinely "live". With `ATR_pct` already computed (line 1316), a trailing stop in ATR multiples is one line of code. |
| **G-3** | 🟡 Med | Hint section is ~270 lines below the danger banner. Scrolling cost. | Reduces actionability — the hint should appear right next to the index reading. |
| **G-4** | 🟡 Med | No statistical backing (e.g., "30-day forward return given entry at this zone over the last N years"). | Trader can't tell if these heuristics actually work historically. |
| **G-5** | 🟢 Low | HTML duplicated 3× inline. | Maintainability only — no behavioral defect. |
| **G-6** | 🟢 Low | No machine-readable export (CSV / clipboard) of the active recommendation. | Nice-to-have for journaling workflows. |
| **G-7** | 🟢 Low | Hint card never references VIX or peer dispersion, even though both are in the danger composite. | Composite uses 5 inputs but recommendations only cite RSI / vol / blocks. |

---

## 5. Match Rate Computation

```
Stated requirements:        6
Fully met (IR-1,3,4,5,6):    5
Partially met (IR-2):        0.5 weight
Failed:                      0
─────────────────────────────────
Coverage = 5.5 / 6 = 91.7 %

Implementation-quality penalties (gap-detector convention):
  G-1  High  −10 pts
  G-2  Med    −2 pts
  G-3  Med    −1 pt
  G-4  Med    −1 pt
  G-5  Low    −0 pt (cosmetic)
─────────────────────────────────
Final Match Rate ≈ 78 %
```

**78 % < 90 %** → recommend `/pdca iterate danger-zone-strategy-hints`.

---

## 6. Suggested Next Actions (Act phase)

Ranked by ROI / lines-of-code:

1. **(2 lines)** In the Hints section, fade non-active zones to 35 % opacity and
   add a `border:2px solid <zoneColor>` on the active one. Use the
   `danger_color_text` value already computed at line 1446.
2. **(8 lines)** Replace `Set trailing stop 10-15% below close` with a live
   string: `f"Trailing stop ≈ {2.5*last_nv['ATR14']:.2f} ($ {last_nv['Close']-2.5*last_nv['ATR14']:.2f})"`.
3. **(15 lines)** Move the Hints section above the existing detail panels so it
   sits right under the Danger banner.
4. **(40 lines, optional)** Compute the historical 30-day forward NVDA return
   conditional on the zone label and append `"Hist. 30d fwd return: +X %"` to
   each card. Uses data already in `df_nv`.
5. **(10 lines)** Refactor the three blocks into a `_render_hint(zone, color, bullets)`
   helper. Behavior-neutral; addresses G-5.
6. **(20 lines)** Cite VIX & peer relative-strength on the active card when
   those components dominate the composite (`vix_danger > 0.6` or peer dispersion
   widening). Closes G-7.

---

## 7. Verification Checklist for Iterate Phase

* [ ] Active zone is visually distinct from inactive zones.
* [ ] At least one numeric in the active card is derived from live data
  (e.g., ATR-scaled stop).
* [ ] Hints render within one viewport-height of the Danger banner.
* [ ] Match Rate re-runs ≥ 90 %.

---

*Generated by post-hoc PDCA Check on `feat: add Strategy Backtest tab and real
FRED credit/slope` working tree (commit `b95810c`).*
