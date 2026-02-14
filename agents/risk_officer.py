from typing import Any, Dict, Optional
from agents.base_agent import BaseAgent, AgentVote, AgentClass, SignalDirection, ConfidenceBreakdown


class RiskOfficerAgent(BaseAgent):
    """
    The Risk Officer: Veto-capable agent.
    
    Evaluates portfolio impact, position sizing risk, and drawdown exposure.
    Has FINAL GATEKEEPING AUTHORITY — can veto any trade recommendation.
    """
    AGENT_CLASS = AgentClass.RISK

    def __init__(self, llm_backend: str = "google"):
        super().__init__(
            name="The Risk Officer",
            role="Chief Risk Officer",
            goal="Protect capital by evaluating position risk, portfolio exposure, and enforcing drawdown limits.",
            llm_backend=llm_backend
        )

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        symbol = context.get("symbol", "UNKNOWN")
        consensus_view = context.get("consensus_view", "")
        confidence_score = context.get("confidence_score", 0.5)
        agent_votes = context.get("agent_votes", {})
        
        # Build vote summary for risk assessment
        vote_summary = ""
        for name, vote in agent_votes.items():
            if hasattr(vote, 'signal'):
                vote_summary += f"  - {name}: {vote.signal} (conf: {vote.confidence:.2f})\n"

        prompt = f"""
        You are the Chief Risk Officer for an institutional trading desk.
        
        TRADE PROPOSAL:
        Symbol: {symbol}
        Consensus View: {consensus_view}
        Composite Confidence: {confidence_score}
        
        AGENT VOTES:
        {vote_summary}
        
        YOUR MANDATE:
        1. Evaluate if this trade should be APPROVED, DOWNSIZED, or VETOED.
        2. Assess concentration risk — is this position too large relative to portfolio?
        3. Check drawdown exposure — can we afford a -15% adverse move?
        4. Evaluate regime appropriateness — does this trade fit the current macro regime?
        
        OUTPUT FORMAT (these exact labels):
        RISK_DECISION: [APPROVE / DOWNSIZE / VETO]
        RISK_SCORE: [0.0-1.0 where 1.0 = maximum risk]
        MAX_POSITION_PCT: [0-100, maximum portfolio allocation %]
        DATA_QUALITY: [0.0-1.0]
        SIGNAL_ALIGNMENT: [0.0-1.0]
        REGIME_STABILITY: [0.0-1.0]
        PORTFOLIO_FIT: [0.0-1.0]
        VETO_REASON: [reason if VETO, otherwise "N/A"]
        RISK_RATIONALE: [detailed reasoning]
        """
        
        return self.query_llm(prompt)

    def vote(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentVote:
        raw = self.execute(task, context)
        
        # Parse structured output
        is_veto = "RISK_DECISION: VETO" in raw.upper() or "RISK_DECISION:VETO" in raw.upper()
        veto_reason = ""
        risk_score = 0.5
        position_cap = 10.0
        
        confidence_bd = ConfidenceBreakdown()
        
        for line in raw.split('\n'):
            line = line.strip()
            if line.startswith("RISK_SCORE:"):
                try: risk_score = float(line.split(":")[1].strip())
                except: pass
            elif line.startswith("MAX_POSITION_PCT:"):
                try: position_cap = float(line.split(":")[1].strip().replace('%', ''))
                except: pass
            elif line.startswith("VETO_REASON:"):
                veto_reason = line.split(":", 1)[1].strip()
            elif line.startswith("DATA_QUALITY:"):
                try: confidence_bd.data_quality = float(line.split(":")[1].strip())
                except: pass
            elif line.startswith("SIGNAL_ALIGNMENT:"):
                try: confidence_bd.signal_alignment = float(line.split(":")[1].strip())
                except: pass
            elif line.startswith("REGIME_STABILITY:"):
                try: confidence_bd.regime_stability = float(line.split(":")[1].strip())
                except: pass
            elif line.startswith("PORTFOLIO_FIT:"):
                try: confidence_bd.portfolio_fit = float(line.split(":")[1].strip())
                except: pass

        signal = SignalDirection.VETO if is_veto else SignalDirection.NEUTRAL
        
        return AgentVote(
            agent_name=self.name,
            agent_class=self.agent_class,
            signal=signal.value,
            confidence=confidence_bd.composite,
            confidence_breakdown=confidence_bd,
            rationale=raw,
            veto=is_veto,
            veto_reason=veto_reason if is_veto else "",
            position_cap=position_cap,
            metadata={"risk_score": risk_score}
        )
