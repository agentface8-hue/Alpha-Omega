"""
swing_scanner.py — SwingTrader AI v4.3 Scanner Agent
Bridges market_data (yfinance) + conviction_engine (5-pillar scoring)
into the Alpha-Omega agent framework.
"""
from typing import Dict, Any, List
from core.conviction_engine import run_scan


class SwingScanner:
    """
    SwingTrader AI v4.3 scanning agent.
    Fetches real market data via yfinance and scores
    using the deterministic 5-pillar conviction framework.
    """

    def __init__(self):
        self.name = "SwingTrader AI"
        self.version = "4.3"

    def scan(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Run a full v4.3 scan on the given symbols.
        Returns structured JSON matching the SwingTrader output schema.
        """
        try:
            result = run_scan(symbols)
            return result
        except Exception as e:
            return {
                "market_header": "Scan failed",
                "market_regime": "Unknown",
                "vix_estimate": 0,
                "results": [],
                "error": str(e)
            }
