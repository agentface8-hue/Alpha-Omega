from typing import Any, Dict, Optional
from agents.base_agent import BaseAgent
from config.settings import settings

class ExecutionerAgent(BaseAgent):
    """
    The Executioner: Risk/Trade Manager.
    Final decision-maker. Manages position sizing and ensures adherence to risk parameters.
    """
    def __init__(self, llm_backend: str = "google"):
        super().__init__(
            name="The Executioner",
            role="Risk Manager & Trader",
            goal="Execute trades with optimal sizing while strictly adhering to risk limits.",
            llm_backend=llm_backend
        )

    def calculate_kelly_criterion(self, win_prob: float, win_loss_ratio: float) -> float:
        """
        Calculates the Kelly Criterion fraction.
        f = (bp - q) / b
        b = win_loss_ratio
        p = win_prob
        q = 1 - p
        """
        if win_loss_ratio <= 0:
            return 0.0
        
        p = win_prob
        q = 1 - p
        b = win_loss_ratio
        
        kelly_f = (b * p - q) / b
        return max(0.0, kelly_f) # No shorting via negative Kelly for now, stick to sizing

    def check_circuit_breaker(self, current_equity: float, starting_equity: float) -> bool:
        """
        Checks if the max drawdown limit has been breached.
        Returns True if Circuit Breaker is TRIGGERED (Trading Halted).
        """
        if starting_equity <= 0:
            return False

        drawdown = (starting_equity - current_equity) / starting_equity
        if drawdown > settings.MAX_DRAWDOWN_LIMIT:
            print(f"CRITICAL: Circuit Breaker Triggered! Drawdown: {drawdown:.2%}")
            return True
        return False

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Executes the trade decision workflow.
        """
        analysis_summary = context.get("analysis_summary")
        confidence_score = context.get("confidence_score", 0.0)
        
        # Portfolio Context (defaults for now if not connected to brokerage)
        current_equity = context.get("current_equity", 100000.0)
        starting_equity = context.get("starting_equity", 100000.0)

        # 1. Check Circuit Breakers
        if self.check_circuit_breaker(current_equity, starting_equity):
             return "HALT: Circuit Breaker Triggered. Max Drawdown Exceeded."

        # 2. Check Confidence Threshold
        if confidence_score < settings.CONFIDENCE_THRESHOLD:
            return f"HOLD: Confidence score {confidence_score} is below threshold {settings.CONFIDENCE_THRESHOLD}."

        # 3. Position Sizing (Half-Kelly for safety)
        # Mocked estimated Win/Loss ratio from historical performance or synthesis
        win_loss_ratio = 2.0 
        kelly_fraction = self.calculate_kelly_criterion(confidence_score, win_loss_ratio)
        safe_fraction = kelly_fraction * 0.5 

        # 4. Generate Order
        symbol = context.get("symbol")
        action = "BUY" # Derived from analysis, assuming long only for this MVP
        
        prompt = f"""
        Review the trade setup:
        Symbol: {symbol}
        Action: {action}
        Confidence: {confidence_score}
        Kelly Fraction: {kelly_fraction:.2f}
        Safe Allocation (Half-Kelly): {safe_fraction:.2f}
        
        Thesis Summary:
        {analysis_summary}
        
        Task: {task}
        
        Output the final trade instruction formatted as a clear string.
        Include a brief justification for the sizing.
        """
        
        response = self.query_llm(prompt)
        return response
