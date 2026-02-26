"""
conviction_engine.py — SwingTrader AI v4.3 Conviction Scoring Engine
Pure math/logic implementation of the 5-pillar framework.
No LLM calls — deterministic scoring from market data.
"""
from typing import Dict, Any, List


def score_ticker(data: Dict[str, Any], regime: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply full v4.3 5-pillar scoring to a single ticker's market data.
    Returns enriched data with conviction_pct, pillar_scores, heat, hard_fail, etc.
    """
    if "error" in data:
        return {**data, "hard_fail": True, "hard_fail_reason": data["error"],
                "conviction_pct": 0, "heat": "Cold", "trend": "MIXED",
                "pillar_scores": {"p1": 0, "p2": 0, "p3": 0, "p4": 0, "p5": 0}}

    tf = data.get("tf_breakdown", {})
    tf_daily = tf.get("tf_daily", "MIXED")
    tf_weekly = tf.get("tf_weekly", "MIXED")
    tf_65m = tf.get("tf_65m", "MIXED")
    tf_240m = tf.get("tf_240m", "MIXED")
    tas_str = data.get("tas", "0/4")
    tas_num = int(tas_str.split("/")[0]) if "/" in tas_str else 0
    ma150_pos = data.get("ma150_position", "below")
    cloud_pos = data.get("cloud_position", "below")
    vol_ratio = data.get("vol_ratio", 1.0)
    vol_dir = data.get("vol_direction", "NEUTRAL")
    rr = data.get("rr", 0)
    coiling = data.get("coiling", False)
    body_pct = data.get("body_pct", 0.5)
    is_doji = data.get("is_doji", False)
    long_upper_wick = data.get("long_upper_wick", False)
    bull_body = data.get("bull_body", False)
    close = data.get("last_close", 0)
    earnings = data.get("earnings_warning", "Clear")
    min_rr = regime.get("min_rr", 2.5)

    hard_fail = False
    hard_fail_reason = ""
    caps = []  # conviction caps to apply at the end
    ta_notes = []

    # ══════════════════════════════════════════════════
    # PHASE 1: MTF GATE (runs BEFORE any pillar scoring)
    # ══════════════════════════════════════════════════

    # Weekly BEAR + Daily BEAR → HARD FAIL
    if tf_weekly == "BEAR" and tf_daily == "BEAR":
        hard_fail = True
        hard_fail_reason = "Weekly BEAR + Daily BEAR → HARD FAIL"

    # Below 150MA + Weekly BEAR → HARD FAIL
    if ma150_pos == "below" and tf_weekly == "BEAR" and not hard_fail:
        hard_fail = True
        hard_fail_reason = "Below 150MA + Weekly BEAR → HARD FAIL"

    # TAS 0/4 → HARD FAIL
    if tas_num == 0 and not hard_fail:
        hard_fail = True
        hard_fail_reason = f"TAS {tas_str} — Full bear alignment → HARD FAIL"

    # TAS-based caps
    if tas_num == 2:
        caps.append(65)
        ta_notes.append(f"TAS {tas_str} split signal → cap 65%")
    if tas_num == 1:
        caps.append(55)
        ta_notes.append(f"TAS {tas_str} bear dominance → cap 55%")

    # Weekly BEAR + Daily BULL → cap 65%
    if tf_weekly == "BEAR" and tf_daily == "BULL":
        caps.append(65)
        ta_notes.append("Weekly BEAR + Daily BULL → cap 65% watchlist")

    # Below 150MA alone → cap 70%
    if ma150_pos == "below" and tf_weekly != "BEAR":
        caps.append(70)
        ta_notes.append("Below 150MA → cap 70%")

    # MIXED Daily → cap 70%
    if tf_daily == "MIXED":
        caps.append(70)
        ta_notes.append("MIXED Daily trend → cap 70%")

    if hard_fail:
        return _build_result(data, regime, 0, {"p1": 0, "p2": 0, "p3": 0, "p4": 0, "p5": 0},
                             True, hard_fail_reason, ta_notes)

    # ══════════════════════════════════════════════════
    # P1 — Trend & Cloud (25%)
    # ══════════════════════════════════════════════════
    p1 = 80 if tf_daily == "BULL" else 55 if tf_weekly == "BULL" else 30

    # P1-CS Cloud bonus/penalty
    if cloud_pos == "above":
        p1 = min(p1 + 5, 100)
        ta_notes.append("Above cloud → P1 +5%")
    elif cloud_pos == "inside":
        caps.append(65)
        ta_notes.append("Inside cloud → cap 65%")
    elif cloud_pos == "below":
        hard_fail = True
        hard_fail_reason = "Below Ichimoku cloud → HARD FAIL"
        return _build_result(data, regime, 0, {"p1": 0, "p2": 0, "p3": 0, "p4": 0, "p5": 0},
                             True, hard_fail_reason, ta_notes)

    p1 = max(0, min(100, p1))

    # ══════════════════════════════════════════════════
    # P2 — Price Structure Quality (25%)
    # ══════════════════════════════════════════════════
    p2 = 50
    if coiling:
        p2 += 20
        ta_notes.append("Coiling detected → P2 +20")
    if body_pct > 0.5:
        p2 += 10
    if bull_body and close > data.get("entry_low", 0):
        p2 += 10
    if is_doji:
        p2 -= 10

    # Yellow Candle Exhaustion check
    yellow_candle = (long_upper_wick and body_pct < 0.15
                     and vol_ratio > 1.8 and len(data.get("confluence_zones", [])) > 0)
    if yellow_candle:
        caps.append(60)
        ta_notes.append("Yellow Candle Exhaustion → cap 60%")

    p2 = max(0, min(100, p2))

    # ══════════════════════════════════════════════════
    # P3 — Institutional Flow (20%) [v4.3]
    # ══════════════════════════════════════════════════
    if vol_dir == "ACCUMULATION" and tas_num >= 3:
        p3 = 85
        ta_notes.append("Accumulation on aligned trend → P3 STRONG")
    elif vol_dir == "DISTRIBUTION":
        p3 = 55
        ta_notes.append("Distribution signal → P3 MODERATE")
    elif vol_ratio < 1.5:
        p3 = 35
        ta_notes.append(f"Vol ratio {vol_ratio}x < 1.5 → P3 WEAK")
    elif tas_num <= 2 and vol_ratio > 1.5:
        p3 = 40
        ta_notes.append("Counter-trend vol → P3 WEAK")
    else:
        p3 = 60

    # Climax Reversal Risk
    if vol_ratio > 3.0 and tas_num <= 2:
        ta_notes.append(f"⚠ Climax Reversal Risk (vol {vol_ratio}x, TAS {tas_str})")
        p3 = min(p3, 35)

    # ══════════════════════════════════════════════════
    # P4 — Risk/Reward Geometry (20%)
    # ══════════════════════════════════════════════════
    if rr < min_rr:
        hard_fail = True
        hard_fail_reason = f"R:R {rr}:1 below regime min {min_rr}:1 → INSTANT FAIL"
        return _build_result(data, regime, 0, {"p1": p1, "p2": p2, "p3": p3, "p4": 0, "p5": 0},
                             True, hard_fail_reason, ta_notes)

    p4 = 90 if rr >= 3.0 else 80 if rr >= 2.5 else 70 if rr >= 2.0 else 50

    # ══════════════════════════════════════════════════
    # P5 — Catalyst & Timing (10%)
    # ══════════════════════════════════════════════════
    p5 = 80  # default
    if "HARD FAIL" in earnings:
        hard_fail = True
        hard_fail_reason = f"Earnings {earnings} → HARD FAIL"
        return _build_result(data, regime, 0, {"p1": p1, "p2": p2, "p3": p3, "p4": p4, "p5": 0},
                             True, hard_fail_reason, ta_notes)
    elif "Half size" in earnings:
        p5 = 50
        ta_notes.append(f"Earnings {earnings} → half size")

    # ══════════════════════════════════════════════════
    # CONVICTION SYNTHESIS
    # ══════════════════════════════════════════════════
    pillar_scores = {"p1": p1, "p2": p2, "p3": p3, "p4": p4, "p5": p5}
    raw_cv = round(p1 * 0.25 + p2 * 0.25 + p3 * 0.20 + p4 * 0.20 + p5 * 0.10)

    # Apply all caps
    conviction = raw_cv
    for cap in caps:
        conviction = min(conviction, cap)

    return _build_result(data, regime, conviction, pillar_scores, False, "", ta_notes)


def _build_result(data: Dict, regime: Dict, conviction: int, pillars: Dict,
                  hard_fail: bool, hard_fail_reason: str, ta_notes: List[str]) -> Dict[str, Any]:
    """Assemble the final scored result for one ticker."""
    # Heat classification
    if hard_fail:
        heat = "Cold"
    elif conviction >= 75:
        heat = "TOP"
    elif conviction >= 60:
        heat = "Hot"
    elif conviction >= 45:
        heat = "Neutral"
    else:
        heat = "Cold"

    # Overall trend
    tf = data.get("tf_breakdown", {})
    bulls = sum(1 for v in tf.values() if v == "BULL")
    trend = "BULL" if bulls >= 3 else "BEAR" if bulls <= 1 else "MIXED"

    return {
        "ticker": data.get("symbol", "?"),
        "name": data.get("name", ""),
        "sector": data.get("sector", ""),
        "last_close": data.get("last_close", 0),
        "last_date": data.get("last_date", ""),
        "stale": False,
        "mkt_cap_b": data.get("mkt_cap_b", 0),
        "conviction_pct": conviction,
        "heat": heat,
        "trend": trend,
        "tas": data.get("tas", "0/4"),
        "ma150_position": data.get("ma150_position", "below"),
        "tf_breakdown": data.get("tf_breakdown", {}),
        "entry_low": data.get("entry_low", 0),
        "entry_high": data.get("entry_high", 0),
        "sl": data.get("sl", 0),
        "tp1": data.get("tp1", 0),
        "tp2": data.get("tp2", 0),
        "tp3": data.get("tp3", 0),
        "qty": data.get("qty", 0),
        "vol_ratio": data.get("vol_ratio", 0),
        "vol_direction": data.get("vol_direction", "NEUTRAL"),
        "earnings_warning": data.get("earnings_warning", "Clear"),
        "hard_fail": hard_fail,
        "hard_fail_reason": hard_fail_reason,
        "coiling": data.get("coiling", False),
        "pillar_scores": pillars,
        "confluence_zones": data.get("confluence_zones", []),
        "fvg_zones": [],
        "ta_note": " · ".join(ta_notes) if ta_notes else f"TAS {data.get('tas','?')}. RSI {data.get('rsi',50)}.",
        "plan": "",
        "rsi": data.get("rsi", 50),
    }


def run_scan(symbols: List[str]) -> Dict[str, Any]:
    """
    Full v4.3 scan: fetch data → score each ticker → sort by conviction.
    Returns the complete JSON matching SwingTrader v4.3 output schema.
    """
    from core.market_data import fetch_market_regime, fetch_multiple_tickers

    print(f"[SCAN] Fetching market regime...")
    regime = fetch_market_regime()
    print(f"[SCAN] Regime: {regime['regime']} | VIX: {regime['vix']}")

    print(f"[SCAN] Fetching data for {len(symbols)} tickers...")
    raw_data = fetch_multiple_tickers(symbols)

    print(f"[SCAN] Scoring with v4.3 5-pillar framework...")
    results = []
    for data in raw_data:
        scored = score_ticker(data, regime)
        results.append(scored)

    # Sort: non-fails by conviction desc, hard-fails at bottom
    non_fails = sorted([r for r in results if not r["hard_fail"]],
                       key=lambda x: x["conviction_pct"], reverse=True)
    fails = [r for r in results if r["hard_fail"]]
    sorted_results = non_fails + fails

    # Generate plan for top 3
    for i, r in enumerate(sorted_results[:3]):
        if not r["hard_fail"]:
            r["plan"] = (f"Entry: decisive close ${r['entry_low']}-${r['entry_high']} in final 30min. "
                         f"SL: ${r['sl']} (ATR triple-guard). "
                         f"TP1: ${r['tp1']} (exit 40%, move SL to BE). "
                         f"TP2: ${r['tp2']} (exit 45%). R:R {r.get('rr', '?')}:1.")

    # Market header
    spy_chg = regime.get("spy_change_pct", 0)
    direction = "up" if spy_chg > 0 else "down"
    header = (f"SPY {direction} {abs(spy_chg)}% at ${regime.get('spy_close',0)}. "
              f"VIX at {regime['vix']} — {regime['regime']} regime. "
              f"Min R:R requirement: {regime['min_rr']}:1.")

    return {
        "market_header": header,
        "market_regime": regime["regime"],
        "vix_estimate": regime["vix"],
        "results": sorted_results
    }
