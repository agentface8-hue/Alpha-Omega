from typing import Any, Dict, Optional
from agents.base_agent import BaseAgent

class MacroStrategistAgent(BaseAgent):
    """
    The Macro-Strategist: Global Macro Agent.
    Monitors geopolitical events, bond yields, and central bank policies.
    """
    def __init__(self, llm_backend: str = "google"):
        super().__init__(
            name="The Macro-Strategist",
            role="Macroeconomic Strategist",
            goal="Analyze global macroeconomic trends to determine market regime.",
            llm_backend=llm_backend
        )

    def fetch_macro_data(self) -> Dict[str, Any]:
        """
        Fetches real-time macro data using yfinance.
        """
        try:
            import yfinance as yf
            tickers = {
                "10Y_Yield": "^TNX",
                "2Y_Yield": "^IRX", # Approximate/proxy if 2Y not available directly, or use ^FVX (5Y). Using IRX (13 week) as proxy for short term for now or just mocked if needed. Actually ^IRX is 13 week. ^FVX is 5 year. 
                # Let's use ^TNX (10Y) and ^VIX. 2Y is often not free on Yahoo.
                "VIX": "^VIX"
            }
            
            data = {}
            for key, symbol in tickers.items():
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    data[key] = hist['Close'].iloc[-1]
                else:
                    data[key] = "N/A"
            
            # Contextual data (mocked for things YF doesn't have easily)
            data["Fed_Policy"] = "Data Dependent" 
            data["Geopolitics"] = "Monitor Global Headlines"
            
            return data
        except Exception as e:
            print(f"Error fetching macro data: {e}")
            return {}

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Executes the Macro-Strategist's analysis workflow.
        """
        # 1. Fetch Macro Data
        macro_data = self.fetch_macro_data()
        
        # 2. Analyze
        prompt = f"""
        Analyze the following macroeconomic data environment:
        
        - 10-Year Treasury Yield: {macro_data['10Y_Yield']}%
        - 2-Year Treasury Yield: {macro_data['2Y_Yield']}%
        - Yield Curve Status: {macro_data['Yield_Curve']}
        - Volatility Index (VIX): {macro_data['VIX']}
        - Federal Reserve Stance: {macro_data['Fed_Policy']}
        - Geopolitical Context: {macro_data['Geopolitics']}
        
        Task: {task}
        
        Determine:
        1. Current Market Regime (e.g., Inflationary, Deflationary, Stagflation, Goldilocks)
        2. Asset Allocation Bias (Risk-On vs. Risk-Off)
        3. Specific risks to the Equity market.
        """
        
        response = self.query_llm(prompt)
        return response
