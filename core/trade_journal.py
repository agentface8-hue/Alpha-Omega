"""
trade_journal.py — Logs scan results for self-calibration.
Uses Supabase if available, falls back to local JSON.
"""
import os, json, datetime
from pathlib import Path
from typing import Dict, Any, List

JOURNAL_DIR = Path(__file__).parent.parent / "journal"
JOURNAL_DIR.mkdir(exist_ok=True)

try:
    from supabase import create_client
    SUPABASE_URL = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
except Exception:
    supabase = None


def log_scan(scan_result: Dict[str, Any]) -> bool:
    """Log a full scan. Supabase if available, else local JSON."""
    now = datetime.datetime.utcnow().isoformat()
    rows = []
    for r in scan_result.get("results", []):
        rows.append({
            "scanned_at": now,
            "ticker": r.get("ticker"),
            "price_at_scan": r.get("last_close"),
            "conviction_pct": r.get("conviction_pct"),
            "heat": r.get("heat"),
            "hard_fail": r.get("hard_fail"),
            "trend": r.get("trend"),
            "tas": r.get("tas"),
            "rr": r.get("rr", 0),
            "regime": scan_result.get("market_regime"),
            "pillar_scores": r.get("pillar_scores", {}),
        })
    if not rows:
        return False
    # Try Supabase first
    if supabase:
        try:
            db_rows = [{**r, "pillar_scores": json.dumps(r["pillar_scores"])} for r in rows]
            supabase.table("trade_journal").insert(db_rows).execute()
            print(f"[JOURNAL] Logged {len(rows)} scans to Supabase")
            return True
        except Exception as e:
            print(f"[JOURNAL] Supabase failed ({e}), using local JSON")
    # Fallback: local JSON
    date_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    path = JOURNAL_DIR / f"scan_{date_str}.json"
    existing = json.loads(path.read_text()) if path.exists() else []
    existing.extend(rows)
    path.write_text(json.dumps(existing, indent=2, default=str))
    print(f"[JOURNAL] Logged {len(rows)} scans to {path}")
    return True
