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
                "2Y_Yield": "^IRX", # Approximate/proxy if 2Y not available directly
                "VIX": "^VIX"
            }
            
            data = {}
            for key, symbol in tickers.items():
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1d")
                    if not hist.empty:
                        # Yahoo Finance usually provides yields as index values (e.g. 4.5 for 4.5%)
                        data[key] = hist['Close'].iloc[-1]
                    else:
                        data[key] = 0.0 # Default to 0.0 instead of "N/A" to allow math
                except Exception as e:
                    print(f"Warning: Could not fetch {key}: {e}")
                    data[key] = 0.0

            # Calculate Yield Curve (10Y - 2Y)
            # Note: ^IRX is 13-week T-Bill, used here as short-term proxy if 2Y unavail.
            # ideally we'd want ^FVX (5Y) or actual 2Y. Assuming data[key] are floats.
            try:
                data['Yield_Curve'] = data.get('10Y_Yield', 0.0) - data.get('2Y_Yield', 0.0)
            except Exception:
                data['Yield_Curve'] = 0.0
            
            # Contextual data (mocked for things YF doesn't have easily)
            data["Fed_Policy"] = "Data Dependent" 
            data["Geopolitics"] = "Monitor Global Headlines"
            
            return data
        except Exception as e:
            print(f"Error fetching macro data: {e}")
            # Return safe defaults to prevent downstream crashes
            return {
                "10Y_Yield": 0.0,
                "2Y_Yield": 0.0,
                "VIX": 0.0,
                "Yield_Curve": 0.0,
                "Fed_Policy": "Unknown",
                "Geopolitics": "Unknown"
            }

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
