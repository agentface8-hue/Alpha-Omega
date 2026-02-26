import json, sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
from core.backtester import run_backtest

# Full test: 10 stocks, 180 days lookback, 15-day forward, weekly sample
result = run_backtest(
    ["AAPL", "NVDA", "MSFT", "GOOGL", "META", "AMZN", "TSLA", "AMD", "CRM", "NFLX"],
    lookback_days=180, forward_days=15, sample_every=5
)

print("\n" + "="*60)
print("FULL BACKTEST RESULTS (10 stocks x 180 days)")
print("="*60)
s = result["summary"]
print(f"Signals: {s['total_signals']} | Wins: {s['total_wins']} | Win Rate: {s['overall_win_rate']}%")
print(f"TP1 Hit Rate: {s['overall_tp1_rate']}% | Avg P&L: {s['avg_pnl']}%")
print(f"Best: {s['best_trade']['symbol']} {s['best_trade']['date']} +{s['best_trade']['pnl']}%")
print(f"Worst: {s['worst_trade']['symbol']} {s['worst_trade']['date']} {s['worst_trade']['pnl']}%")

print("\n--- ACCURACY BY CONVICTION BRACKET ---")
print(f"  {'Bracket':10} | {'Count':>5} | {'Win%':>6} | {'TP1%':>6} | {'TP2%':>6} | {'Avg P&L':>8} | {'Avg Days':>8} | {'MaxDD':>7}")
print("  " + "-"*82)
for b in result["brackets"]:
    if b["count"] > 0:
        print(f"  {b['label']:10} | {b['count']:5} | {b['win_rate']:5.1f}% | {b['tp1_rate']:5.1f}% | {b['tp2_rate']:5.1f}% | {b['avg_pnl']:+7.2f}% | {b['avg_days']:7.1f}d | {b['avg_drawdown']:+6.2f}%")

print("\n--- CALIBRATION CHECK ---")
for g in result.get("accuracy_gap", []):
    icon = "OK" if g["verdict"] == "CALIBRATED" else "!!" if "OVER" in g["verdict"] else "<<"
    print(f"  {icon} {g['bracket']:10} | Score says {g['expected']:.0f}% | Actual TP1: {g['actual_tp1_rate']:.1f}% | Gap: {g['gap']:+.1f}%  {g['verdict']}")
