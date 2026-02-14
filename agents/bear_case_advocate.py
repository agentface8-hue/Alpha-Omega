from typing import Any, Dict, Optional, List
from agents.base_agent import BaseAgent, AgentVote, AgentClass, SignalDirection


class BearCaseAdvocateAgent(BaseAgent):
    """
    The Bear Case Advocate: Blocking-capable adversarial agent.
    
    Builds the strongest possible counter-thesis against any bullish consensus.
    Generates 3-5 explicit failure scenarios with probability-weighted downsides.
    Can flag "HIGH RISK" to force the Synthesis Engine to downsize recommendations.
    """
    AGENT_CLASS = AgentClass.ADVERSARIAL

    def __init__(self, llm_backend: str = "google"):
        super().__init__(
            name="Bear Case Advocate",
            role="Chief Skeptic & Stress Tester",
            goal="Build the strongest possible counter-thesis and identify failure scenarios that others miss.",
            llm_backend=llm_backend
        )

    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        symbol = context.get("symbol", "UNKNOWN")
        consensus_view = context.get("consensus_view", "")
        reports = context.get("reports", {})
        
        reports_summary = ""
        for agent_name, report in reports.items():
            snippet = str(report)[:300]
            reports_summary += f"  [{agent_name}]: {snippet}...\n"

        prompt = f"""
        You are the Bear Case Advocate — the most ruthless skeptic on the trading desk.
        
        THE CONSENSUS for {symbol}:
        "{consensus_view}"
        
        AGENT REPORTS:
        {reports_summary}
        
        YOUR MISSION:
        1. Build the STRONGEST possible bear case against this trade.
        2. Identify exactly 3-5 failure scenarios with probability estimates.
        3. For each scenario, estimate the percentage downside.
        4. State whether you recommend BLOCKING this trade.
        
        OUTPUT FORMAT:
        BEAR_SIGNAL: [AGREE / CAUTION / BLOCK]
        BEAR_CONFIDENCE: [0.0-1.0, how confident you are in the bear case]
        
        FAILURE_SCENARIO_1: [description] | PROBABILITY: [%] | DOWNSIDE: [-%]
        FAILURE_SCENARIO_2: [description] | PROBABILITY: [%] | DOWNSIDE: [-%]
        FAILURE_SCENARIO_3: [description] | PROBABILITY: [%] | DOWNSIDE: [-%]
        
        BEAR_RATIONALE: [Your full counter-thesis]
        """
        
        return self.query_llm(prompt)

    def vote(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentVote:
        raw = self.execute(task, context)
        
        # Parse failure scenarios
        failure_scenarios = []
        for line in raw.split('\n'):
            line = line.strip()
            if line.startswith("FAILURE_SCENARIO_"):
                scenario = line.split(":", 1)[1].strip() if ":" in line else line
                failure_scenarios.append(scenario)

        # Parse signal
        is_block = "BEAR_SIGNAL: BLOCK" in raw.upper() or "BEAR_SIGNAL:BLOCK" in raw.upper()
        is_caution = "BEAR_SIGNAL: CAUTION" in raw.upper()
        
        bear_confidence = 0.5
        for line in raw.split('\n'):
            if line.strip().startswith("BEAR_CONFIDENCE:"):
                try: bear_confidence = float(line.split(":")[1].strip())
                except: pass

        if is_block:
            signal = SignalDirection.STRONG_SELL
        elif is_caution:
            signal = SignalDirection.SELL
        else:
            signal = SignalDirection.NEUTRAL

        return AgentVote(
            agent_name=self.name,
            agent_class=self.agent_class,
            signal=signal.value,
            confidence=bear_confidence,
            rationale=raw,
            dissent="BLOCKING: Trade risk exceeds acceptable threshold." if is_block else "",
            failure_scenarios=failure_scenarios,
            metadata={"is_blocking": is_block}
        )
