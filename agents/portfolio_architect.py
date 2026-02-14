from typing import Any, Dict, Optional
from agents.base_agent import BaseAgent, AgentVote, AgentClass, SignalDirection


class PortfolioArchitectAgent(BaseAgent):
    """
    The Portfolio Architect: Portfolio-level optimization agent.
    
    Evaluates how a proposed trade fits within the overall portfolio context.
    Handles exposure balancing (sector, factor, asset class), position sizing,
    and rebalancing recommendations.
    """
    AGENT_CLASS = AgentClass.RISK

    def __init__(self, llm_backend: str = "google"):
        super().__init__(
            name="Portfolio Architect",
            role="Portfolio Optimization Specialist",
            goal="Optimize portfolio-level risk-return by balancing exposures and sizing positions appropriately.",
            llm_backend=llm_backend
        )

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        symbol = context.get("symbol", "UNKNOWN")
        consensus_view = context.get("consensus_view", "")
        confidence_score = context.get("confidence_score", 0.5)
        portfolio = context.get("portfolio", {})
        
        portfolio_str = "No portfolio data available (standalone analysis)."
        if portfolio:
            holdings = portfolio.get("holdings", [])
            portfolio_str = f"Total Value: ${portfolio.get('total_value', 0):,.2f}\n"
            for h in holdings[:10]:
                portfolio_str += f"  {h.get('symbol', '?')}: {h.get('weight', 0):.1f}% (${h.get('value', 0):,.2f})\n"

        prompt = f"""
        You are the Portfolio Architect for an institutional investment desk.
        
        PROPOSED TRADE:
        Symbol: {symbol}
        Consensus: {consensus_view}
        Confidence: {confidence_score}
        
        CURRENT PORTFOLIO:
        {portfolio_str}
        
        YOUR MANDATE:
        1. Assess how this trade impacts overall portfolio diversification.
        2. Calculate optimal position size (as % of portfolio).
        3. Identify any sector/factor concentration risks.
        4. Suggest any rebalancing actions needed.
        
        OUTPUT FORMAT:
        PORTFOLIO_SIGNAL: [APPROVE / REDUCE / REJECT]
        OPTIMAL_SIZE_PCT: [0-100, optimal portfolio allocation %]
        SECTOR_RISK: [LOW / MEDIUM / HIGH]
        CORRELATION_CONCERN: [description or "none"]
        REBALANCE_ACTION: [action needed or "none"]
        PORTFOLIO_RATIONALE: [detailed reasoning]
        """
        
        return self.query_llm(prompt)

    def vote(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentVote:
        raw = self.execute(task, context)
        
        optimal_size = 5.0
        is_reject = "PORTFOLIO_SIGNAL: REJECT" in raw.upper()
        
        for line in raw.split('\n'):
            line = line.strip()
            if line.startswith("OPTIMAL_SIZE_PCT:"):
                try: optimal_size = float(line.split(":")[1].strip().replace('%', ''))
                except: pass

        signal = SignalDirection.VETO if is_reject else SignalDirection.NEUTRAL

        return AgentVote(
            agent_name=self.name,
            agent_class=self.agent_class,
            signal=signal.value,
            confidence=0.7,
            rationale=raw,
            veto=is_reject,
            veto_reason="Portfolio allocation rejected due to concentration/exposure risk." if is_reject else "",
            position_cap=optimal_size,
            metadata={"optimal_position_pct": optimal_size}
        )
