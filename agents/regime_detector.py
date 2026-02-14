from typing import Any, Dict, Optional
from agents.base_agent import BaseAgent, AgentVote, AgentClass, SignalDirection


class RegimeDetectorAgent(BaseAgent):
    """
    The Regime Detector: Market regime classification agent.
    
    Identifies the current market regime (risk-on, risk-off, stagflation, crisis, momentum)
    and dynamically adjusts recommended agent weights based on the detected regime.
    """
    AGENT_CLASS = AgentClass.ADVERSARIAL

    REGIME_WEIGHTS = {
        "RISK_ON": {"historian": 1.0, "newsroom": 0.8, "macro": 0.6, "contrarian": 0.5},
        "RISK_OFF": {"historian": 0.6, "newsroom": 1.0, "macro": 1.0, "contrarian": 0.9},
        "CRISIS": {"historian": 0.3, "newsroom": 0.5, "macro": 1.0, "contrarian": 1.0},
        "STAGFLATION": {"historian": 0.5, "newsroom": 0.7, "macro": 1.0, "contrarian": 0.8},
        "MOMENTUM": {"historian": 1.0, "newsroom": 0.6, "macro": 0.5, "contrarian": 0.4},
    }

    def __init__(self, llm_backend: str = "google"):
        super().__init__(
            name="Regime Detector",
            role="Market Regime Analyst",
            goal="Classify the current market regime and adjust agent weighting for optimal decision-making.",
            llm_backend=llm_backend
        )

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        symbol = context.get("symbol", "UNKNOWN")
        macro_data = context.get("macro_data", {})
        reports = context.get("reports", {})

        macro_summary = ""
        for k, v in macro_data.items():
            macro_summary += f"  {k}: {v}\n"

        prompt = f"""
        You are a Market Regime Analyst specializing in regime detection.
        
        CURRENT MACRO DATA:
        {macro_summary}
        
        CONTEXT: Analyzing trade for {symbol}
        
        YOUR TASK:
        1. Classify the current market regime into EXACTLY one of:
           RISK_ON | RISK_OFF | CRISIS | STAGFLATION | MOMENTUM
        2. Assess regime stability — how likely is the regime to change soon?
        3. Flag any regime transition signals.
        
        OUTPUT FORMAT:
        REGIME: [RISK_ON / RISK_OFF / CRISIS / STAGFLATION / MOMENTUM]
        REGIME_STABILITY: [0.0-1.0, where 1.0 = very stable]
        TRANSITION_RISK: [LOW / MEDIUM / HIGH]
        REGIME_SIGNAL: [BUY / NEUTRAL / SELL — based on regime favorability for equities]
        REGIME_RATIONALE: [detailed explanation]
        """
        
        return self.query_llm(prompt)

    def vote(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentVote:
        raw = self.execute(task, context)
        
        # Parse regime
        detected_regime = "RISK_ON"
        regime_stability = 0.5
        agent_weights = self.REGIME_WEIGHTS.get("RISK_ON", {})
        
        for line in raw.split('\n'):
            line = line.strip()
            if line.startswith("REGIME:"):
                regime_val = line.split(":")[1].strip().upper()
                for key in self.REGIME_WEIGHTS:
                    if key in regime_val:
                        detected_regime = key
                        agent_weights = self.REGIME_WEIGHTS[key]
                        break
            elif line.startswith("REGIME_STABILITY:"):
                try: regime_stability = float(line.split(":")[1].strip())
                except: pass

        # Map regime to signal
        regime_signal_map = {
            "RISK_ON": SignalDirection.BUY,
            "MOMENTUM": SignalDirection.STRONG_BUY,
            "RISK_OFF": SignalDirection.SELL,
            "CRISIS": SignalDirection.STRONG_SELL,
            "STAGFLATION": SignalDirection.NEUTRAL,
        }
        
        signal = regime_signal_map.get(detected_regime, SignalDirection.NEUTRAL)

        return AgentVote(
            agent_name=self.name,
            agent_class=self.agent_class,
            signal=signal.value,
            confidence=regime_stability,
            rationale=raw,
            metadata={
                "detected_regime": detected_regime,
                "agent_weights": agent_weights,
                "regime_stability": regime_stability
            }
        )
