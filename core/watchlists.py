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


# ── 11 GICS Sectors ──────────────────────────────────────────────────────────
SECTOR_WATCHLISTS = {
    "information_technology": {
        "label": "Information Technology",
        "etf": "XLK",
        "tickers": ["AAPL","MSFT","NVDA","AVGO","ORCL","CRM","ACN","ADBE","AMD","QCOM","TXN","INTC","NOW","INTU","IBM"]
    },
    "financials": {
        "label": "Financials",
        "etf": "XLF",
        "tickers": ["JPM","BAC","WFC","GS","MS","BLK","C","SCHW","AXP","COF","USB","PNC","TFC","ICE","CME"]
    },
    "health_care": {
        "label": "Health Care",
        "etf": "XLV",
        "tickers": ["LLY","UNH","JNJ","ABBV","MRK","TMO","ABT","DHR","PFE","BMY","AMGN","MDT","ISRG","GILD","CVS"]
    },
    "industrials": {
        "label": "Industrials",
        "etf": "XLI",
        "tickers": ["GE","CAT","RTX","HON","UNP","LMT","BA","DE","ETN","ITW","GD","FDX","UPS","MMM","EMR"]
    },
    "consumer_discretionary": {
        "label": "Consumer Discretionary",
        "etf": "XLY",
        "tickers": ["AMZN","TSLA","HD","MCD","NKE","LOW","SBUX","TJX","BKNG","CMG","ABNB","GM","F","ROST","DHI"]
    },
    "consumer_staples": {
        "label": "Consumer Staples",
        "etf": "XLP",
        "tickers": ["PG","KO","PEP","COST","WMT","PM","MO","MDLZ","CL","KHC","GIS","SYY","ADM","TSN","HRL"]
    },
    "energy": {
        "label": "Energy",
        "etf": "XLE",
        "tickers": ["XOM","CVX","COP","EOG","SLB","PXD","MPC","PSX","VLO","OXY","HES","HAL","DVN","FANG","BKR"]
    },
    "communication_services": {
        "label": "Communication Services",
        "etf": "XLC",
        "tickers": ["META","GOOGL","NFLX","DIS","TMUS","VZ","T","CHTR","EA","WBD","OMC","IPG","FOXA","PARA","LYV"]
    },
    "utilities": {
        "label": "Utilities",
        "etf": "XLU",
        "tickers": ["NEE","SO","DUK","AEP","CEG","SRE","D","EXC","PCG","XEL","ED","ETR","FE","PPL","AES"]
    },
    "materials": {
        "label": "Materials",
        "etf": "XLB",
        "tickers": ["LIN","APD","SHW","ECL","FCX","NEM","NUE","VMC","MLM","ALB","MOS","CF","IFF","PPG","FMC"]
    },
    "real_estate": {
        "label": "Real Estate",
        "etf": "XLRE",
        "tickers": ["PLD","AMT","EQIX","CCI","WELL","DLR","O","PSA","SPG","AVB","EQR","VICI","IRM","EXR","ARE"]
    }
}

SECTOR_ETFS = {k: v["etf"] for k, v in SECTOR_WATCHLISTS.items()}
