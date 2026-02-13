from typing import Any, Dict, Optional, List
from agents.base_agent import BaseAgent

class NewsroomAgent(BaseAgent):
    """
    The Newsroom: NLP Sentiment Agent.
    Processes real-time news to detect sentiment and nuance.
    """
    def __init__(self, llm_backend: str = "google"):
        super().__init__(
            name="The Newsroom",
            role="Sentiment Analyst",
            goal="Analyze news headlines and social sentiment to gauge market psychology.",
            llm_backend=llm_backend
        )

    def fetch_news(self, symbol: str) -> List[str]:
        """
        Fetches real-time news using yfinance.
        """
        try:
            import yfinance as yf
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            headlines = []
            for item in news:
                title = item.get('title')
                link = item.get('link')
                if title:
                    headlines.append(f"{title} ({link})")
            
            return headlines[:10] # Return top 10 news items
        except Exception as e:
            print(f"Error fetching news for {symbol}: {e}")
            return [f"Error fetching news for {symbol}."]

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Executes the Newsroom's analysis workflow.
        """
        symbol = context.get("symbol")
        if not symbol:
            return "Error: No symbol provided for analysis."

        # 1. Fetch News
        news_items = self.fetch_news(symbol)
        news_str = "\n".join([f"- {item}" for item in news_items])

        # 2. Analyze Sentiment
        prompt = f"""
        Analyze the following latest news headlines for {symbol}:
        
        {news_str}
        
        Task: {task}
        
        Provide:
        1. Overall Sentiment Score (0-10, where 10 is extremely bullish)
        2. Key Nuances (e.g., tone, hidden risks)
        3. Potential Market Impact (Short-term vs. Long-term)
        """
        
        response = self.query_llm(prompt)
        return response
