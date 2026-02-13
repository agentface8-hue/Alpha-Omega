from typing import Any, Dict, Optional
import yfinance as yf
import pandas as pd
from agents.base_agent import BaseAgent
from langchain_core.messages import HumanMessage

class HistorianAgent(BaseAgent):
    """
    The Historian: Quantitative Agent.
    Analyzes historical price action, identifying fractal patterns and cyclical correlations.
    """
    def __init__(self, llm_backend: str = "google"):
        super().__init__(
            name="The Historian",
            role="Quantitative Analyst",
            goal="Analyze historical market data to identify trends, patterns, and support/resistance levels.",
            llm_backend=llm_backend
        )

    def fetch_historical_data(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """
        Fetches historical data using yfinance.
        """
        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(period=period)
            if history.empty:
                print(f"Warning: No data found for {symbol}")
            return history
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()

    def calculate_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates basic technical indicators (SMA, RSI, MACD).
        """
        if df.empty:
            return df
        
        # Simple Moving Averages
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()

        # RSI (Relative Strength Index)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        return df

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Executes the Historian's analysis workflow.
        """
        symbol = context.get("symbol")
        if not symbol:
            return "Error: No symbol provided for analysis."

        # 1. Fetch Data
        data = self.fetch_historical_data(symbol)
        
        # 2. Process Data
        data_with_indicators = self.calculate_technical_indicators(data)
        
        # 3. Formulate Insight
        recent_data = data_with_indicators.tail(5).to_string()
        
        prompt = f"""
        Analyze the following recent market data for {symbol}:
        
        {recent_data}
        
        Task: {task}
        
        Identify:
        1. Current Trend (Bullish/Bearish/Neutral)
        2. Key Support/Resistance Levels
        3. Any significant patterns (Golden Cross, Divergence, etc.)
        """
        
        response = self.query_llm(prompt)
        return response
