import requests, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
r = requests.post('http://127.0.0.1:8000/api/scan', json={'symbols': ['AAPL','NVDA','CEG']})
d = r.json()
print("Regime:", d.get('market_regime'))
print("Header:", d.get('market_header'))
for t in d.get('results', []):
    tk = t.get('ticker','?')
    cv = t.get('conviction_pct', 0)
    ht = t.get('heat','?')
    hf = t.get('hard_fail', False)
    reason = t.get('hard_fail_reason','')
    tas = t.get('tas','?')
    print(f"  {tk}: {cv}% ({ht}) TAS={tas} HF={hf} {reason}")
