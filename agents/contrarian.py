from typing import Any, Dict, Optional
from agents.base_agent import BaseAgent

class ContrarianAgent(BaseAgent):
    """
    The Contrarian: Adversarial Agent.
    Finds flaws in the other agents' logic to prevent groupthink.
    """
    def __init__(self, llm_backend: str = "google"):
        super().__init__(
            name="The Contrarian",
            role="Devil's Advocate",
            goal="Challenge the consensus view and identify potential failure points.",
            llm_backend=llm_backend
        )

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Executes the Contrarian's challenge workflow.
        """
        consensus_view = context.get("consensus_view")
        if not consensus_view:
            return "Error: No consensus view provided to challenge."

        symbol = context.get("symbol", "the market")

        prompt = f"""
        Review the following consensus view on {symbol}:
        
        "{consensus_view}"
        
        Task: {task}
        
        Your Mission:
        1. Identify 3 flaws or overlooked risks in this thesis.
        2. Propose a "Bear Case" (if consensus is Bullish) or "Bull Case" (if consensus is Bearish).
        3. Highlight any potential "Illusion of Validity" or Cognitive Biases present in the analysis.
        
        Be ruthless but logical.
        """
        
        response = self.query_llm(prompt)
        return response
