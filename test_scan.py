import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from core.conviction_engine import run_scan
r = run_scan(['AAPL','NVDA','TSLA','AMD','MSFT'])
print(f"Regime: {r['market_regime']} | Header: {r['market_header']}")
for t in r['results']:
    print(f"  {t['ticker']:5s} ${t['last_close']:>8} | {t['conviction_pct']:3d}% {t['heat']:7s} TAS={t['tas']} RR={t.get('rr','?')} HF={t['hard_fail']} {t.get('hard_fail_reason','')}")
