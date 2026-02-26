import requests, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
r = requests.post('http://127.0.0.1:8000/api/analyze', json={'symbol': 'AAPL'})
d = r.json()
print(f"Symbol: {d['symbol']}")
print(f"Confidence: {d['confidence_score']}")
print(f"Decision: {d['executioner_decision'][:100]}")
print(f"Consensus: {d['consensus_view'][:100]}")
print(f"Historian: {d['full_report'].get('historian','')[:100]}")
