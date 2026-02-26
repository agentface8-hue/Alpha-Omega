"""
smart_analyze.py — Real analysis using market data + conviction scoring.
No LLM needed — generates analysis narratives from real data.
"""
from core.market_data import fetch_ticker_data, fetch_market_regime
from core.conviction_engine import score_ticker


def analyze(symbol: str) -> dict:
    """Full analysis for a single ticker using real market data."""
    regime = fetch_market_regime()
    data = fetch_ticker_data(symbol)
    if "error" in data:
        return {"error": data["error"], "symbol": symbol}
    scored = score_ticker(data, regime)
    tf = data.get("tf_breakdown", {})

    # Build Historian report (technical)
    historian = (
        f"{symbol} is trading at ${data['last_close']} with TAS {data['tas']} "
        f"({'all timeframes bullish' if scored['tas']=='4/4' else 'mixed signals across timeframes'}). "
        f"Daily: {tf.get('tf_daily','?')}, Weekly: {tf.get('tf_weekly','?')}, "
        f"4H: {tf.get('tf_240m','?')}, 65m: {tf.get('tf_65m','?')}. "
        f"Price is {'above' if data['ma150_position']=='above' else 'below'} the 150MA (${data['ma150_value']}). "
        f"RSI at {data['rsi']} — {'overbought territory' if data['rsi']>70 else 'oversold territory' if data['rsi']<30 else 'neutral zone'}. "
        f"ATR: ${data['atr']}. "
        f"{'Coiling pattern detected — compression before expansion.' if data['coiling'] else ''} "
        f"Ichimoku cloud position: {data['cloud_position']}. "
        f"Volume ratio: {data['vol_ratio']}x average ({data['vol_direction']})."
    )

    # Build Newsroom report (sentiment proxy from data)
    earnings = data.get("earnings_warning", "Clear")
    newsroom = (
        f"Earnings status: {earnings}. "
        f"Sector: {data['sector']}. Market cap: ${data['mkt_cap_b']}B. "
        f"Volume direction analysis shows {data['vol_direction']} pattern "
        f"({'institutional buying pressure detected' if data['vol_direction']=='ACCUMULATION' else 'possible institutional selling' if data['vol_direction']=='DISTRIBUTION' else 'no clear institutional signal'}). "
        f"Body percentage: {data['body_pct']:.1%} "
        f"({'strong conviction candle' if data['body_pct']>0.6 else 'indecisive candle' if data['body_pct']<0.2 else 'moderate conviction'}). "
        f"{'Doji detected — market indecision.' if data['is_doji'] else ''} "
        f"{'Long upper wick — selling pressure at highs.' if data['long_upper_wick'] else ''}"
    )

    # Build Macro report
    macro = (
        f"VIX at {regime['vix']} — market regime: {regime['regime']}. "
        f"SPY at ${regime.get('spy_close',0)} ({'up' if regime.get('spy_change_pct',0)>0 else 'down'} "
        f"{abs(regime.get('spy_change_pct',0))}% today). "
        f"Minimum R:R requirement for this regime: {regime['min_rr']}:1. "
        f"{'Risk-on environment favoring growth equities.' if regime['regime']=='Trending Bull' else ''}"
        f"{'Choppy conditions — tighter stops and higher conviction needed.' if regime['regime']=='Choppy / Range' else ''}"
        f"{'Elevated volatility — reduce position sizes.' if regime['regime']=='High-Vol Event' else ''}"
    )

    # Build consensus + decision
    cv = scored["conviction_pct"]
    hf = scored["hard_fail"]
    if hf:
        decision = f"HALT — {scored['hard_fail_reason']}. Do not enter."
        consensus = f"Analysis blocked by hard fail gate: {scored['hard_fail_reason']}."
    elif cv >= 75:
        decision = (f"BUY — Strong conviction at {cv}%. Entry: ${scored['entry_low']}-${scored['entry_high']}. "
                    f"SL: ${scored['sl']} (ATR triple-guard). TP1: ${scored['tp1']}. R:R {scored.get('rr','?')}:1. "
                    f"Position: {scored['qty']} shares ($75 risk).")
        consensus = f"Strong bullish alignment across {scored['tas']} timeframes with {cv}% conviction."
    elif cv >= 60:
        decision = (f"BUY (cautious) — Moderate conviction at {cv}%. Entry: ${scored['entry_low']}-${scored['entry_high']}. "
                    f"SL: ${scored['sl']}. TP1: ${scored['tp1']}. Consider half position.")
        consensus = f"Moderately bullish with caveats. {scored['ta_note']}"
    else:
        decision = f"HOLD — Conviction {cv}% below threshold. Monitor for setup improvement."
        consensus = f"Insufficient conviction for entry. {scored['ta_note']}"

    confidence = cv / 100.0

    return {
        "symbol": symbol,
        "consensus_view": consensus,
        "confidence_score": confidence,
        "executioner_decision": decision,
        "full_report": {
            "historian": historian,
            "newsroom": newsroom,
            "macro": macro
        }
    }
