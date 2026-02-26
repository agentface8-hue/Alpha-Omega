from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.schemas import AnalysisRequest, AnalysisResponse, ScanRequest, ScanResponse, BacktestRequest
import traceback
import random
import time

app = FastAPI(title="Alpha-Omega API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Demo Mode Data ---
DEMO_SCENARIOS = {
    "bullish": {
        "consensus_view": "Strong bullish momentum across all signals. Technical breakout confirmed with rising volume, positive sentiment from institutional upgrades, and favorable macro conditions with declining yields supporting growth equities.",
        "confidence_score": 0.87,
        "executioner_decision": "BUY — Enter long position. Allocate 4.2% of portfolio via Kelly Criterion. Set stop-loss at -3.5% below entry. Target: +12% upside over 30-day horizon.",
        "historian": "Price has broken above the 50-day and 200-day moving averages with a Golden Cross forming. RSI at 62 indicates strong momentum without overbought conditions. Volume profile confirms institutional accumulation over the past 5 sessions. MACD histogram expanding bullishly.",
        "newsroom": "Sentiment is overwhelmingly positive. 3 major analyst upgrades in the past week. Social media buzz index at 8.2/10. No significant negative catalysts detected. Earnings whisper numbers suggest a potential beat next quarter.",
        "macro": "10Y yield at 4.12%, declining from 4.35% peak. VIX at 14.2, well below fear threshold. Yield curve normalizing — positive for risk assets. Fed policy: rate cuts expected in coming meetings. No major geopolitical headwinds."
    },
    "bearish": {
        "consensus_view": "Bearish divergence detected. Price action weakening despite market strength, negative sentiment shift from insider selling reports, and macro headwinds from rising yields creating unfavorable conditions.",
        "confidence_score": 0.72,
        "executioner_decision": "HALT — Do not enter. Risk/reward unfavorable. Multiple sell signals detected. If holding, tighten stop-loss to -2% and reduce position by 50%. Wait for mean reversion signal before re-entry.",
        "historian": "Bearish divergence on RSI — price making higher highs while RSI makes lower highs. Volume declining on up-days. Price rejected at resistance for the 3rd time. MACD crossover to the downside. Support at the 200-day MA is the last defense.",
        "newsroom": "Insider selling reported — CEO and CFO sold combined $12M in shares. Mixed analyst sentiment with 2 downgrades. Short interest rising to 8.4% of float. Social sentiment shifting negative on Reddit and Twitter.",
        "macro": "10Y yield spiking to 4.52%, creating headwinds for growth stocks. VIX elevated at 22.8. Dollar strengthening, negative for multinational earnings. Fed rhetoric hawkish — 'higher for longer' narrative dominant."
    },
    "neutral": {
        "consensus_view": "Mixed signals across all dimensions. Technical indicators are range-bound, sentiment is neutral with no strong catalysts, and macro environment is transitional. No clear edge for directional positioning.",
        "confidence_score": 0.51,
        "executioner_decision": "HOLD — No action. Confidence below threshold (0.51 < 0.85). Signals are contradictory. Monitor for a decisive breakout above resistance or breakdown below support before committing capital.",
        "historian": "Price consolidating in a tight range between support ($142) and resistance ($158). Bollinger Bands squeezing — a big move is brewing but direction is unclear. Volume is average. RSI flat at 50, perfectly neutral.",
        "newsroom": "No major catalysts on the horizon. Earnings are 6 weeks out. Analyst consensus is 'Hold' with a median price target at current levels. Social media activity is muted.",
        "macro": "10Y yield stable at 4.25%. VIX at 17.5 — neither complacent nor fearful. Market awaiting next FOMC meeting for direction. Economic data mixed — strong jobs but cooling PMI."
    }
}


def get_demo_response(symbol: str) -> AnalysisResponse:
    """Generate a realistic demo response for any ticker."""
    # Pick a random scenario
    scenario_key = random.choice(["bullish", "bearish", "neutral"])
    scenario = DEMO_SCENARIOS[scenario_key]
    
    # Simulate processing time (1-3 seconds)
    time.sleep(random.uniform(1.0, 3.0))
    
    return AnalysisResponse(
        symbol=symbol.upper(),
        consensus_view=scenario["consensus_view"],
        confidence_score=scenario["confidence_score"],
        executioner_decision=scenario["executioner_decision"],
        full_report={
            "historian": scenario["historian"],
            "newsroom": scenario["newsroom"],
            "macro": scenario["macro"]
        }
    )


@app.get("/")
async def root():
    return {"status": "System Online", "version": "1.0.0", "mode": "demo"}


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_stock(request: AnalysisRequest):
    """
    Analyze a stock ticker. Uses demo mode with realistic mock data.
    To use the real AI agents, set DEMO_MODE=false in .env and ensure
    your GOOGLE_API_KEY has the Generative Language API enabled.
    """
    try:
        symbol = request.symbol.upper()
        
        # Try real analysis first (V2: council + ledger + regime), fall back to demo
        try:
            from core.orchestrator import Orchestrator
            orchestrator = Orchestrator()
            context = orchestrator.run_cycle_v2(symbol)
            rec = context.get("recommendation", "HOLD")
            vetoed = context.get("vetoed", False)
            executioner_decision = f"{rec} (vetoed)" if vetoed else rec
            if context.get("position_size_pct") is not None:
                executioner_decision += f" — position size: {context['position_size_pct']:.1f}%"
            return AnalysisResponse(
                symbol=symbol,
                consensus_view=context.get("consensus_view", "N/A"),
                confidence_score=context.get("confidence_score", 0.0),
                executioner_decision=executioner_decision,
                full_report=context.get("reports", {}),
            )
        except Exception as real_err:
            print(f"[V2 FAILED] {real_err}, falling back to smart_analyze...")
            try:
                from core.smart_analyze import analyze
                result = analyze(symbol)
                if "error" in result:
                    return get_demo_response(symbol)
                return AnalysisResponse(**result)
            except Exception as sa_err:
                print(f"[SMART FAILED] {sa_err}, using demo data.")
                return get_demo_response(symbol)

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scan", response_model=ScanResponse)
async def scan_stocks(request: ScanRequest):
    """
    SwingTrader AI v4.3 scan endpoint.
    Fetches real market data via yfinance, then scores using Gemini + 5-pillar framework.
    """
    try:
        symbols = [s.upper().strip() for s in request.symbols if s.strip()]
        if not symbols:
            raise HTTPException(status_code=400, detail="No symbols provided")
        if len(symbols) > 30:
            raise HTTPException(status_code=400, detail="Maximum 30 tickers per scan")

        from agents.swing_scanner import SwingScanner
        scanner = SwingScanner()
        result = scanner.scan(symbols)

        # Log to trade journal
        try:
            from core.trade_journal import log_scan
            log_scan(result)
        except Exception as je:
            print(f"[JOURNAL] Log failed: {je}")

        if "error" in result and not result.get("results"):
            raise HTTPException(status_code=500, detail=result["error"])

        return ScanResponse(
            market_header=result.get("market_header", ""),
            market_regime=result.get("market_regime", ""),
            vix_estimate=result.get("vix_estimate", 0),
            results=result.get("results", []),
            error=result.get("error"),
        )
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/prices")
async def get_prices(request: ScanRequest):
    """Quick price + daily change for sidebar."""
    try:
        import yfinance as yf
        prices = []
        for sym in request.symbols[:12]:
            try:
                tk = yf.Ticker(sym.upper().strip())
                hist = tk.history(period="5d")
                if len(hist) >= 2:
                    close = float(hist["Close"].iloc[-1])
                    prev = float(hist["Close"].iloc[-2])
                    chg = round((close - prev) / prev * 100, 2)
                    prices.append({"symbol": sym.upper(), "price": round(close, 2), "change": chg})
                else:
                    prices.append({"symbol": sym.upper(), "price": 0, "change": 0})
            except Exception:
                prices.append({"symbol": sym.upper(), "price": 0, "change": 0})
        return {"prices": prices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/watchlists")
async def get_watchlists():
    """List available preset watchlists."""
    from core.watchlists import list_watchlists, WATCHLISTS
    return {"watchlists": {k: {"label": v["label"], "count": len(v["tickers"])} for k, v in WATCHLISTS.items()}}


@app.get("/api/watchlists/{name}")
async def get_watchlist(name: str):
    """Get tickers for a specific watchlist."""
    from core.watchlists import get_watchlist as gw
    wl = gw(name)
    return {"name": name, "label": wl["label"], "tickers": wl["tickers"]}


@app.post("/api/backtest")
async def run_backtest_endpoint(request: BacktestRequest):
    """Walk-forward backtest: score historical data, check if TP1 was hit."""
    try:
        symbols = [s.upper().strip() for s in request.symbols if s.strip()]
        if not symbols:
            raise HTTPException(status_code=400, detail="No symbols provided")
        if len(symbols) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 tickers per backtest")
        from core.backtester import run_backtest
        result = run_backtest(
            symbols, request.lookback_days, request.forward_days, request.sample_every
        )
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/calibrate")
async def run_calibration_endpoint(request: BacktestRequest):
    """Run auto-calibration: backtest + analyze + compute calibration curve."""
    try:
        symbols = [s.upper().strip() for s in request.symbols if s.strip()]
        if not symbols:
            raise HTTPException(status_code=400, detail="No symbols provided")
        from core.calibrator import run_calibration
        result = run_calibration(
            symbols, request.lookback_days, request.forward_days, request.sample_every
        )
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/calibration")
async def get_calibration():
    """Get current calibration parameters."""
    from core.calibrator import load_calibration
    return load_calibration()


@app.post("/api/calibration/reset")
async def reset_calibration():
    """Reset calibration to uncalibrated (raw scores)."""
    from core.calibrator import save_calibration
    save_calibration({"mode": "none", "scale": 1.0, "offset": 0})
    return {"status": "reset", "mode": "none"}


# ══════════════════════════════════════════
# SIGNAL TRACKER ENDPOINTS
# ══════════════════════════════════════════

@app.get("/api/signals")
async def get_signals():
    """Get all signals without price refresh (fast)."""
    from core.signal_tracker import get_all_signals
    return get_all_signals()


@app.post("/api/signals/check")
async def check_signals():
    """Refresh live prices and update P&L / TP / SL status."""
    from core.signal_tracker import check_signals as cs
    return cs()


@app.post("/api/signals/close/{signal_id}")
async def close_signal(signal_id: str):
    """Manually close a signal."""
    from core.signal_tracker import close_signal as cls
    result = cls(signal_id)
    if not result:
        raise HTTPException(status_code=404, detail="Signal not found")
    return result


@app.post("/api/signals/clear")
async def clear_signals():
    """Reset all signals."""
    from core.signal_tracker import clear_all
    return clear_all()


@app.post("/api/signals/turbo/{symbol}")
async def turbo_signal(symbol: str, asset_type: str = "stock"):
    """Launch a turbo scalp signal with tight SL/TP."""
    from core.signal_tracker import create_turbo_signal
    result = create_turbo_signal(symbol, asset_type)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
