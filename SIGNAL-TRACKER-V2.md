# SIGNAL TRACKER v2.0 — TECHNICAL REFERENCE
# Location: C:\Users\asus\Alpha-Omega-System\SIGNAL-TRACKER-V2.md
# Last Updated: 2026-02-27

## OVERVIEW
Signal Tracker v2.0 is the paper-trading engine for Alpha-Omega.
It tracks signals from entry to exit with full audit trail.
File: `core/signal_tracker.py` (1046 lines)

---

## 15 GAPS FIXED (from v1.0)

| # | Gap | Fix |
|---|-----|-----|
| 1 | No indicator snapshot at entry | `_fetch_indicator_snapshot()` captures 79 data points |
| 2 | Autopilot threw away conviction data | `scan_data` parameter on `create_turbo_signal()` |
| 3 | No market context | VIX/SPY/regime saved at entry AND close |
| 4 | No close-time snapshot | Full exit context captured |
| 5 | yfinance price delay | Staleness detection (stale flag) |
| 6 | No gap detection | `_detect_gap_fill()` with realistic fills |
| 7 | No market hours awareness | `_is_us_market_open()` prevents false triggers |
| 8 | No slippage modeling | Gap fills use actual price, not target |
| 9 | No data validation | Zero/negative/NaN price rejection |
| 10 | No MAE tracking | Max Adverse Excursion per signal |
| 11 | No MFE tracking | Max Favorable Excursion per signal |
| 12 | No time-of-day analysis | Entry/close session recorded |
| 13 | No case reports | JSON reports in signals/reports/ |
| 14 | No conviction accuracy | Stats split by winners vs losers |
| 15 | Fixed % turbo targets | ATR-based (0.5×ATR for SL/TP1) |

## SIGNAL SCHEMA (full fields)

### Entry Fields
```python
"id": str                    # 8-char hex UUID
"ticker": str                # "AAPL", "BTC"
"asset_type": str            # "stock" or "crypto"
"entry_price": float
"entry_time": str            # ISO8601
"conviction": int            # 0-100 (from scan or 0 for manual turbo)
"heat": str                  # "Hot", "Warm", "TURBO", "CRYPTO"
"sl": float                  # Stop loss (entry - 0.5×ATR)
"tp1": float                 # Take profit 1 (entry + 0.5×ATR)
"tp2": float                 # Take profit 2 (entry + 1.0×ATR)
"tp3": float                 # Take profit 3 (entry + 1.5×ATR)
"rr": float                  # Risk:reward ratio
"regime": str                # Market regime at entry
"tas": str                   # Trend Alignment Score "3/4"
"trend": str                 # "BULL"/"BEAR"/"TURBO"
"pillar_scores": dict        # {p1:80, p2:65, ...}
"ta_note": str               # Technical note from scanner
"entry_market_context": {
    "vix": float,
    "spy_close": float,
    "spy_change_pct": float,
    "regime": str,           # "Trending Bull"/"Choppy"/"Trending Bear"/"High-Vol Event"
    "timestamp": str
}
"entry_snapshot": dict       # 79 indicators (RSI, ATR, EMAs, cloud, etc.)
"entry_session": str         # "regular"/"premarket"/"afterhours"/"closed"
"target_method": str         # "atr" or "pct_fallback"
"atr_at_entry": float        # ATR14 value
"price_stale_at_entry": bool
"price_delay_warning": str   # "near-realtime" or "15-20min delayed"
```

### Tracking Fields (updated every check_signals cycle)
```python
"status": str                # "OPEN" → then final status
"current_price": float       # Latest price
"pnl_pct": float             # Current P&L %
"highest_price": float       # Track for MFE
"lowest_price": float        # Track for MAE
"mae_pct": float             # Max drawdown from entry
"mfe_pct": float             # Max gain from entry
"tp1_hit": bool              # TP1 reached?
"tp2_hit": bool
"tp3_hit": bool
"tp1_hit_time": str|null     # Timestamp when hit
"tp2_hit_time": str|null
"tp3_hit_time": str|null
"bars_held": int             # Days since entry
```

### Close Fields (set when signal closes)
```python
"closed_at": str             # ISO8601 timestamp
"close_reason": str          # "TP1 hit at $X" / "SL hit" / "manual close"
"close_price": float         # Actual fill (may differ from target due to gaps)
"close_snapshot": {
    "price": float,
    "pnl_pct": float,
    "mae_pct": float,
    "mfe_pct": float,
    "bars_held": int,
    "highest_price": float,
    "lowest_price": float,
    "slippage_pct": float
}
"close_market_context": dict # Same structure as entry_market_context
"close_session": str
"gap_info": dict|null        # Gap detection details
"slippage_pct": float        # Difference between target and actual fill
```

## CLOSE LOGIC (in check_signals)

### Close conditions (checked every cycle):
1. **STOPPED_OUT**: current_price <= SL (stocks: only during market hours)
2. **TP3_HIT**: current_price >= TP3
3. **TP2_HIT**: current_price >= TP2 (if TP3 not hit)
4. **TP1_HIT**: current_price >= TP1 (recorded but doesn't close — signal stays open)
5. **TIMEOUT**: bars_held >= 30 days
6. **MANUAL_CLOSE**: User clicks X button
7. **GAP**: Price gaps through SL or TP → fills at open price (not target)

### Gap Detection:
- If prev_close > SL but current_price < SL → gapped down through SL
- Fill price = current_price (the open, not SL level)
- Slippage = |actual_fill - intended_target| / entry_price × 100

### Market Hours Protection (stocks only):
- Stocks: SL/TP only triggers during regular hours (9:30 AM - 4:00 PM ET)
- Premarket/afterhours prices are tracked but don't trigger closes
- Crypto: 24/7, no restrictions

## ATR-BASED TARGETS

### Calculation:
```python
ATR14 = 14-day Average True Range from yfinance (30 days daily data)

SL  = entry_price - 0.5 × ATR14    # ~87.5% win rate from backtester
TP1 = entry_price + 0.5 × ATR14    # 1:1 R:R
TP2 = entry_price + 1.0 × ATR14    # 2:1 R:R
TP3 = entry_price + 1.5 × ATR14    # 3:1 R:R
```

### Fallback (if ATR fetch fails):
```python
SL  = entry_price × 0.998   # -0.2%
TP1 = entry_price × 1.005   # +0.5%
TP2 = entry_price × 1.008   # +0.8%
TP3 = entry_price × 1.012   # +1.2%
target_method = "pct_fallback"
```

## REGIME CLASSIFICATION

Based on VIX level (from ^VIX):
```python
VIX > 30  → "High-Vol Event"
VIX > 25  → "Trending Bear"
VIX > 20  → "Choppy"
VIX <= 20 → "Trending Bull"
```

## STATS AGGREGATION (from closed signals)

```python
"win_rate": wins / total_closed × 100
"avg_pnl": average P&L% across all closed
"profit_factor": gross_profit / gross_loss
"avg_mae": average max drawdown
"avg_mfe": average max gain
"tp1_hit_rate": signals that hit TP1 / total_closed
"gap_affected_trades": count of trades with gap fills
"total_gap_slippage": sum of all slippage%
"avg_conviction_winners": avg conviction of winning trades
"avg_conviction_losers": avg conviction of losing trades
```

## CASE REPORT STRUCTURE

```json
{
    "report_version": "2.0",
    "signal_id": "abc123",
    "ticker": "AAPL",
    "entry": {
        "price": 270.0,
        "time": "2026-02-27T10:30:00",
        "session": "regular",
        "regime": "Trending Bull",
        "market_context": { "vix": 19.5, "spy_close": 689.3, ... },
        "conviction": 55,
        "pillar_scores": { "p1": 80, ... },
        "atr_at_entry": 5.2,
        "target_method": "atr",
        "snapshot": { ... }
    },
    "targets": { "sl": 267.4, "tp1": 272.6, "tp2": 275.2, "tp3": 277.8 },
    "exit": {
        "price": 272.8,
        "time": "2026-02-28T14:15:00",
        "status": "TP1_HIT",
        "reason": "TP1 hit at $272.60",
        "session": "regular",
        "market_context": { ... }
    },
    "performance": {
        "pnl_pct": 1.04,
        "mae_pct": -0.3,
        "mfe_pct": 1.1,
        "bars_held": 1,
        "gap_info": null,
        "slippage_pct": 0
    },
    "analysis": {
        "sl_review": "Trade never went below -0.3% — SL well placed.",
        "tp_review": "TP1 hit. Signal stayed open for potential TP2.",
        "conviction_note": "55% conviction WIN — lower conviction can work."
    }
}
```

---

**This document is the source of truth for Signal Tracker v2.0.**
**Always reference this before modifying signal_tracker.py.**
