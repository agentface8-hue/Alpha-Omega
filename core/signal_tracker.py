"""
signal_tracker.py — Live signal tracking for paper validation.
Records entry signals, monitors price vs SL/TP targets, tracks win rate.
Local JSON storage only (no external APIs).
"""
import os, json, datetime, uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
import yfinance as yf

SIGNALS_DIR = Path(__file__).parent.parent / "signals"
SIGNALS_DIR.mkdir(exist_ok=True)
SIGNALS_FILE = SIGNALS_DIR / "active_signals.json"
CLOSED_FILE = SIGNALS_DIR / "closed_signals.json"


def _load(path: Path) -> List[Dict]:
    if path.exists():
        return json.loads(path.read_text())
    return []

def _save(path: Path, data: List[Dict]):
    path.write_text(json.dumps(data, indent=2, default=str))


def record_signal(scan_result: Dict[str, Any], asset_type: str = "stock") -> List[Dict]:
    """Auto-record signals for tickers scoring >= 60% conviction."""
    active = _load(SIGNALS_FILE)
    active_tickers = {s["ticker"] for s in active}
    new_signals = []

    for r in scan_result.get("results", []):
        if r.get("hard_fail") or r.get("conviction_pct", 0) < 60:
            continue
        ticker = r["ticker"]
        if ticker in active_tickers:
            continue  # already tracking

        signal = {
            "id": str(uuid.uuid4())[:8],
            "ticker": ticker,
            "asset_type": asset_type,  # "stock" or "crypto"
            "entry_price": r["last_close"],
            "entry_time": datetime.datetime.utcnow().isoformat(),
            "conviction": r["conviction_pct"],
            "heat": r["heat"],
            "sl": r["sl"],
            "tp1": r["tp1"],
            "tp2": r["tp2"],
            "tp3": r["tp3"],
            "rr": r["rr"],
            "qty": r["qty"],
            "regime": scan_result.get("market_regime", ""),
            "tas": r["tas"],
            "trend": r["trend"],
            "pillar_scores": r.get("pillar_scores", {}),
            "status": "OPEN",
            "current_price": r["last_close"],
            "pnl_pct": 0,
            "highest_price": r["last_close"],
            "lowest_price": r["last_close"],
            "tp1_hit": False,
            "tp2_hit": False,
            "tp3_hit": False,
            "closed_at": None,
            "close_reason": None,
            "bars_held": 0,
        }
        active.append(signal)
        active_tickers.add(ticker)
        new_signals.append(signal)

    _save(SIGNALS_FILE, active)
    return new_signals


def check_signals() -> Dict[str, Any]:
    """Check all active signals against current prices. Update status."""
    active = _load(SIGNALS_FILE)
    closed = _load(CLOSED_FILE)
    if not active:
        return {"active": [], "closed": closed, "stats": _calc_stats(closed)}

    # Batch fetch prices
    tickers_to_check = []
    for s in active:
        sym = s["ticker"]
        if s["asset_type"] == "crypto" and not sym.endswith("-USD"):
            sym = f"{sym}-USD"
        tickers_to_check.append(sym)

    prices = {}
    # Use fast_info for real-time/live prices (not daily close)
    for sym in tickers_to_check:
        try:
            tk = yf.Ticker(sym)
            fi = tk.fast_info
            price = fi.get("lastPrice") or fi.get("last_price") or fi.get("previousClose", 0)
            if price and price > 0:
                prices[sym] = float(price)
                print(f"  [LIVE] {sym} = ${price:.4f}")
        except Exception as e:
            print(f"  [LIVE] {sym} fetch error: {e}")

    newly_closed = []
    still_active = []

    for s in active:
        sym = s["ticker"]
        lookup = f"{sym}-USD" if s["asset_type"] == "crypto" and not sym.endswith("-USD") else sym
        price = prices.get(lookup, s["current_price"])
        s["current_price"] = round(price, 4)
        s["bars_held"] += 1

        # Track high/low watermarks
        if price > s["highest_price"]:
            s["highest_price"] = round(price, 4)
        if price < s["lowest_price"]:
            s["lowest_price"] = round(price, 4)

        # P&L
        entry = s["entry_price"]
        s["pnl_pct"] = round((price - entry) / entry * 100, 2) if entry else 0

        # Check targets
        if price >= s["tp1"] and not s["tp1_hit"]:
            s["tp1_hit"] = True
        if price >= s["tp2"] and not s["tp2_hit"]:
            s["tp2_hit"] = True
        if price >= s["tp3"] and not s["tp3_hit"]:
            s["tp3_hit"] = True

        # Close conditions
        is_turbo = s.get("turbo", False)
        if price <= s["sl"]:
            s["status"] = "STOPPED_OUT"
            s["close_reason"] = f"SL hit at ${s['sl']}"
            s["closed_at"] = datetime.datetime.utcnow().isoformat()
            newly_closed.append(s)
        elif is_turbo and s["tp1_hit"]:
            s["status"] = "TP1_HIT"
            s["close_reason"] = f"Turbo TP1 hit at ${s['tp1']}"
            s["closed_at"] = datetime.datetime.utcnow().isoformat()
            newly_closed.append(s)
        elif s["tp3_hit"]:
            s["status"] = "TP3_HIT"
            s["close_reason"] = f"TP3 hit at ${s['tp3']}"
            s["closed_at"] = datetime.datetime.utcnow().isoformat()
            newly_closed.append(s)
        elif s["bars_held"] >= 30:
            # Auto-close after 30 bars (days) — timeout
            s["status"] = "TIMEOUT"
            s["close_reason"] = f"30-day timeout at ${price}"
            s["closed_at"] = datetime.datetime.utcnow().isoformat()
            newly_closed.append(s)
        else:
            still_active.append(s)

    # Save
    closed.extend(newly_closed)
    _save(SIGNALS_FILE, still_active)
    _save(CLOSED_FILE, closed)

    all_signals = still_active + closed
    stats = _calc_stats(closed)

    return {
        "active": still_active,
        "recently_closed": newly_closed,
        "closed": closed,
        "stats": stats,
    }


def close_signal(signal_id: str, reason: str = "manual") -> Optional[Dict]:
    """Manually close a signal."""
    active = _load(SIGNALS_FILE)
    closed = _load(CLOSED_FILE)
    target = None
    remaining = []
    for s in active:
        if s["id"] == signal_id:
            s["status"] = "MANUAL_CLOSE"
            s["close_reason"] = reason
            s["closed_at"] = datetime.datetime.utcnow().isoformat()
            target = s
            closed.append(s)
        else:
            remaining.append(s)
    _save(SIGNALS_FILE, remaining)
    _save(CLOSED_FILE, closed)
    return target


def get_all_signals() -> Dict[str, Any]:
    """Get all signals without price refresh (fast)."""
    active = _load(SIGNALS_FILE)
    closed = _load(CLOSED_FILE)
    return {
        "active": active,
        "closed": closed,
        "stats": _calc_stats(closed),
    }


def clear_all() -> Dict[str, str]:
    """Reset all signals (for testing)."""
    _save(SIGNALS_FILE, [])
    _save(CLOSED_FILE, [])
    return {"status": "cleared"}


def create_turbo_signal(symbol: str, asset_type: str = "stock") -> Dict:
    """Create a tight scalp signal for fast live testing.
    SL -0.2%, TP1 +0.3%, TP2 +0.5%, TP3 +0.8%. Closes at TP1 (not TP3)."""
    sym = symbol.upper()
    lookup = f"{sym}-USD" if asset_type == "crypto" and not sym.endswith("-USD") else sym
    try:
        tk = yf.Ticker(lookup)
        fi = tk.fast_info
        price = fi.get("lastPrice") or fi.get("last_price") or fi.get("previousClose", 0)
        if not price or price <= 0:
            return {"error": f"Could not fetch price for {lookup}"}
    except Exception as e:
        return {"error": str(e)}

    price = float(price)
    signal = {
        "id": str(uuid.uuid4())[:8],
        "ticker": sym,
        "asset_type": asset_type,
        "entry_price": round(price, 4),
        "entry_time": datetime.datetime.utcnow().isoformat(),
        "conviction": 0,
        "heat": "TURBO",
        "sl": round(price * 0.998, 4),
        "tp1": round(price * 1.003, 4),
        "tp2": round(price * 1.005, 4),
        "tp3": round(price * 1.008, 4),
        "rr": 1.5,
        "qty": 0,
        "regime": "turbo_scalp",
        "tas": "—",
        "trend": "TURBO",
        "pillar_scores": {},
        "status": "OPEN",
        "current_price": round(price, 4),
        "pnl_pct": 0,
        "highest_price": round(price, 4),
        "lowest_price": round(price, 4),
        "tp1_hit": False,
        "tp2_hit": False,
        "tp3_hit": False,
        "closed_at": None,
        "close_reason": None,
        "bars_held": 0,
        "turbo": True,
    }

    active = _load(SIGNALS_FILE)
    active.append(signal)
    _save(SIGNALS_FILE, active)
    return signal


def _calc_stats(closed: List[Dict]) -> Dict[str, Any]:
    """Calculate win/loss stats from closed signals."""
    if not closed:
        return {
            "total_closed": 0, "wins": 0, "losses": 0, "timeouts": 0,
            "win_rate": 0, "avg_pnl": 0, "best_trade": 0, "worst_trade": 0,
            "avg_bars_held": 0, "tp1_hit_rate": 0, "tp2_hit_rate": 0,
        }

    wins = [s for s in closed if s["pnl_pct"] > 0]
    losses = [s for s in closed if s["pnl_pct"] <= 0]
    timeouts = [s for s in closed if s["status"] == "TIMEOUT"]
    tp1_hits = [s for s in closed if s.get("tp1_hit")]
    tp2_hits = [s for s in closed if s.get("tp2_hit")]
    pnls = [s["pnl_pct"] for s in closed]
    bars = [s.get("bars_held", 0) for s in closed]

    return {
        "total_closed": len(closed),
        "wins": len(wins),
        "losses": len(losses),
        "timeouts": len(timeouts),
        "win_rate": round(len(wins) / len(closed) * 100, 1) if closed else 0,
        "avg_pnl": round(sum(pnls) / len(pnls), 2) if pnls else 0,
        "best_trade": round(max(pnls), 2) if pnls else 0,
        "worst_trade": round(min(pnls), 2) if pnls else 0,
        "avg_bars_held": round(sum(bars) / len(bars), 1) if bars else 0,
        "tp1_hit_rate": round(len(tp1_hits) / len(closed) * 100, 1) if closed else 0,
        "tp2_hit_rate": round(len(tp2_hits) / len(closed) * 100, 1) if closed else 0,
    }
