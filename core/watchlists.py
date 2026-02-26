"""
watchlists.py — Preset ticker watchlists for SwingTrader AI v4.3
"""

WATCHLISTS = {
    "mega_cap": {
        "label": "Mega Cap Tech",
        "tickers": ["AAPL", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "AVGO", "TSM", "ORCL"]
    },
    "growth": {
        "label": "Growth & Momentum",
        "tickers": ["PLTR", "CRWD", "SNOW", "DDOG", "NET", "SHOP", "SQ", "COIN", "MSTR", "RKLB"]
    },
    "semis": {
        "label": "Semiconductors",
        "tickers": ["NVDA", "AMD", "AVGO", "QCOM", "MU", "MRVL", "KLAC", "LRCX", "AMAT", "SMCI"]
    },
    "energy_commodities": {
        "label": "Energy & Commodities",
        "tickers": ["XOM", "CVX", "CEG", "VST", "FSLR", "GLD", "SLV", "USO", "UNG", "FCX"]
    },
    "sp500_leaders": {
        "label": "S&P 500 Leaders",
        "tickers": ["AAPL", "NVDA", "MSFT", "AMZN", "META", "GOOGL", "BRK-B", "LLY", "JPM", "V",
                     "UNH", "XOM", "MA", "COST", "HD", "PG", "JNJ", "ABBV", "CRM", "NFLX"]
    },
    "full_scan": {
        "label": "Full Scan (Top 30)",
        "tickers": ["AAPL", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "AVGO", "PLTR", "CRWD",
                     "AMD", "COIN", "SNOW", "NET", "SHOP", "SQ", "CEG", "VST", "FSLR", "SMCI",
                     "MRVL", "MU", "QCOM", "LLY", "JPM", "NFLX", "CRM", "COST", "RKLB", "MSTR"]
    }
}

def get_watchlist(name: str):
    return WATCHLISTS.get(name, WATCHLISTS["mega_cap"])

def list_watchlists():
    return {k: v["label"] for k, v in WATCHLISTS.items()}
