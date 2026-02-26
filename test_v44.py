import json, sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
from core.conviction_engine import run_scan

r = run_scan(["AAPL", "NVDA", "TSLA", "AMD", "MSFT"])
print(f"\nRegime: {r['market_regime']} | VIX: {r['vix_estimate']}")
print(f"{r['market_header']}\n")
for x in r["results"]:
    fail = f"FAIL: {x['hard_fail_reason']}" if x["hard_fail"] else ""
    note = x["ta_note"][:100] if not x["hard_fail"] else ""
    print(f"{x['ticker']:6} {x['conviction_pct']:3}% {x['heat']:8} TAS:{x['tas']} R:R {x['rr']}:1  {fail}{note}")
