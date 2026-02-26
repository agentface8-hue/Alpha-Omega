import json, sys
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
from core.calibrator import run_calibration

result = run_calibration(
    ["AAPL", "NVDA", "MSFT", "GOOGL", "META", "AMZN", "TSLA", "AMD", "CRM", "NFLX"],
    lookback_days=180, forward_days=15, sample_every=5
)

print("\n" + "="*60)
print("RECOMMENDATIONS")
print("="*60)
for r in result.get("recommendation", []):
    print(f"  >> {r}")

print("\n" + "="*60)
print("CALIBRATION PREVIEW (raw -> calibrated)")
print("="*60)
for raw, cal in sorted(result.get("preview", {}).items(), reverse=True):
    print(f"  {raw}% -> {cal}%")
